#!/usr/bin/env python3
"""Prepare a frozen pending-handoff experiment and capture qualified Codex exec runs.

Default operations are offline. No credential copying, arbitrary shell launch, model
installation, product write, or automatic claim of behavioral improvement. Filesystem
separation here is NOT a security boundary: an external host owner must qualify isolation.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from evaluate_writer_run import Invalid, load, regular, safe_path, save_new, sha, snapshot, parse_events

ROOT = Path(__file__).resolve().parents[1]
FLAGS = ('--json','--ephemeral','--ignore-user-config','--sandbox','--output-last-message')
ENV_KEYS = ('PATH','HOME','CODEX_HOME','LANG','LC_ALL','TZ','SYSTEMROOT')
PILOT_PROMPT = ('This is a capture qualification pilot, not a scored writing task. '
                'Read pilot.txt using a command, print its contents, create work/pilot-note.txt '
                'with the text capture check, and report what you actually did. Do not access '
                'any file or service outside this workspace. Do not alter pilot.txt.')

def tool_hashes() -> dict:
    return {name:sha(regular(ROOT/'scripts'/name)) for name in ('run_writer_pair.py','evaluate_writer_run.py')}

def doctor(codex: str = 'codex') -> dict:
    binary = shutil.which(codex)
    report = {'status':'BLOCKED','codex':None,'model_calls':0,'missing':[],
              'scope':'executable/help only; no login status or secret inspection',
              'controller_sha256':tool_hashes()}
    if not binary:
        report['missing']=['codex_executable']; return report
    path=Path(binary).resolve(); report['codex']=str(path); report['codex_sha256']=sha(regular(path))
    commands=[]
    for args in (['--version'],['exec','--help']):
        try:
            r=subprocess.run([str(path),*args],capture_output=True,text=True,timeout=10)
            commands.append({'argv':[str(path),*args],'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        except (OSError,subprocess.TimeoutExpired) as exc:
            report['missing']=['codex_probe']; report['error']=str(exc); return report
    report['commands']=commands
    report['version']=commands[0]['stdout'].strip()
    if any(c['exit']!=0 for c in commands) or not report['version'].startswith('codex-cli '):
        report['missing']=['recognized_codex_cli']; return report
    report['missing']=[f'cli_flag:{f}' for f in FLAGS if f not in commands[1]['stdout']]
    if not report['missing']: report['status']='EXECUTABLE_FOUND_NOT_QUALIFIED'
    return report

def prepare(spec_path: Path, roots: dict[str,Path], out: Path) -> dict:
    """Copy exact allowlisted files, not entire repos/history/evaluators."""
    spec=load(spec_path); out=out.absolute()
    if out.exists() or any(p.is_symlink() for p in [out,*out.parents]): raise Invalid('output must be new and non-symlinked')
    if any(out.resolve().is_relative_to(r.resolve()) for r in roots.values()): raise Invalid('output must be outside input checkouts')
    if spec.get('schema_version')!='writer-pair-experiment@1' or spec.get('scenario')!='pending':
        raise Invalid('only the frozen pending scenario is implemented; accepted needs its own admitted packet')
    order=spec.get('order')
    if not isinstance(order,list) or len(order)!=6 or any(order.count(a)!=3 for a in ('baseline','treatment')):
        raise Invalid('this bounded experiment requires exactly three runs per arm')
    if type(spec.get('timeout_seconds')) is not int or not 1<=spec['timeout_seconds']<=600:
        raise Invalid('bounded timeout required')
    task=regular(safe_path(roots['common'],spec['task']['path']))
    if sha(task)!=spec['task']['sha256']: raise Invalid('task digest mismatch')
    prepared={}
    for arm in ('baseline','treatment'):
        selected={}
        for item in [*spec['common_files'],*spec['arms'][arm]['files']]:
            target=item['target']; safe_path(out,target)
            if target in selected: raise Invalid('duplicate capsule destination')
            if any(part in {'.git','.codex','auth.json','.env'} or part.startswith('.env.') for name in (target,item['path']) for part in Path(name).parts):
                raise Invalid('history/config/credential files cannot enter a capsule')
            content=regular(safe_path(roots[item['root']],item['path']))
            if sha(content)!=item['sha256']: raise Invalid(f'source digest mismatch: {item["path"]}')
            selected[target]=content
        if 'AGENTS.md' not in selected or 'inputs/article.md' not in selected:
            raise Invalid('capsule needs explicit instructions and article')
        prepared[arm]=selected
    # Compare shared effective inputs, not a schema that only treatment understands.
    shared=[x['target'] for x in spec['common_files']]
    if any(prepared['baseline'][p]!=prepared['treatment'][p] for p in shared): raise Invalid('unequal common input')
    out.mkdir(parents=True)
    (out/'task.txt').write_bytes(task); (out/'experiment.json').write_bytes(regular(spec_path))
    for arm,selected in prepared.items():
        for target,content in selected.items():
            dest=safe_path(out/f'capsules/{arm}',target);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
    packet={'schema_version':'writer-packet@1','experiment_id':spec['experiment_id'],
        'scenario':'pending','execution_kind':spec.get('execution_kind','host_codex_exec'),
        'timeout_seconds':spec['timeout_seconds'],'controller_sha256':tool_hashes(),
        'task_sha256':sha(task),'experiment_sha256':sha(regular(spec_path)),
        'inputs':{arm:{p:sha(b) for p,b in files.items()} for arm,files in prepared.items()},
        'jobs':[{'id':f'run-{i+1:02d}','arm':arm} for i,arm in enumerate(order)],
        'source_revisions':{a:spec['arms'][a]['revision'] for a in ('baseline','treatment')},
        'pilot_counts_as_comparison':False,
        'isolation':'REQUIRES_EXTERNAL_HOST_QUALIFICATION; directories alone do not isolate reads'}
    save_new(out/'packet.json',packet)
    return {'status':'PREPARED','packet':str(out),'packet_sha256':sha(regular(out/'packet.json')),
            'writer_runs':0,'comparison':'NOT_RUN','next':'doctor; then externally authorize one pilot'}

def validate_packet(folder: Path, expected_sha: str) -> dict:
    if sha(regular(folder/'packet.json'))!=expected_sha: raise Invalid('packet digest changed')
    packet=load(folder/'packet.json')
    if packet['controller_sha256']!=tool_hashes(): raise Invalid('controller changed after preparation')
    if sha(regular(folder/'task.txt'))!=packet['task_sha256'] or sha(regular(folder/'experiment.json'))!=packet['experiment_sha256']:
        raise Invalid('task or experiment changed')
    for arm,files in packet['inputs'].items():
        observed=snapshot(folder/f'capsules/{arm}')
        if observed!={p:{'kind':'file','sha256':digest} for p,digest in files.items()}: raise Invalid('capsule content changed')
    return packet

def validate_host(approval_path: Path, expected_sha: str, packet_sha: str, report: dict) -> dict:
    if sha(regular(approval_path))!=expected_sha: raise Invalid('external host approval changed')
    host=load(approval_path)
    if host.get('schema_version')!='writer-host-approval@1' or host.get('packet_sha256')!=packet_sha:
        raise Invalid('host approval does not select this packet')
    for key in ('owner','isolation_evidence_ref','effective_config_ref','authentication_ref','model'):
        if not isinstance(host.get(key),str) or not host[key].strip(): raise Invalid(f'missing host field: {key}')
    if host.get('effects')!=['model-invocation','workspace-only-writes']: raise Invalid('effects must be explicitly bounded')
    if host.get('codex_sha256')!=report.get('codex_sha256') or host.get('codex_version')!=report.get('version'):
        raise Invalid('host approval targets another executable/version')
    expiry=datetime.fromisoformat(host['expires_at'])
    if expiry.tzinfo is None or expiry<=datetime.now(timezone.utc): raise Invalid('host approval expired')
    # Host owner must actually establish these boundaries before making this declaration.
    if host.get('isolation_verified') is not True: raise Invalid('host isolation not qualified')
    return host

def capture(binary: Path, workspace: Path, capture_dir: Path, prompt: bytes,
            metadata: dict, timeout: int) -> dict:
    """One process, no resume, no automatic retry. Receipts stay outside writer cwd."""
    if capture_dir.exists(): raise Invalid('capture exists; preserve attempts, do not overwrite')
    capture_dir.mkdir(parents=True);(capture_dir/'prompt.txt').write_bytes(prompt)
    save_new(capture_dir/'before.json',snapshot(workspace))
    argv=[str(binary),'exec','--json','--ephemeral','--ignore-user-config','--color','never',
          '--sandbox','workspace-write','--cd',str(workspace),'--skip-git-repo-check',
          '--model',metadata['requested_model'],'-c','approval_policy="never"',
          '-c','web_search="disabled"','-c','sandbox_workspace_write.network_access=false',
          '--output-last-message',str(capture_dir/'last-message.txt'),'-']
    env={k:v for k,v in os.environ.items() if k in ENV_KEYS}
    # No GitHub/API credentials forwarded; CLI may use pre-provisioned login on qualified host.
    # Do not use --ignore-rules or bypass managed sandbox/approval requirements.
    tempdir=workspace/'work/tmp';tempdir.mkdir(parents=True,exist_ok=True)
    env['TMPDIR']=str(tempdir);env['PYTHONDONTWRITEBYTECODE']='1'
    started_at=datetime.now(timezone.utc).isoformat()
    start=time.monotonic(); stop='completed'; exit_code=None; process=None
    try:
        with (capture_dir/'prompt.txt').open('rb') as stdin, (capture_dir/'events.jsonl').open('xb') as stdout, (capture_dir/'stderr.txt').open('xb') as stderr:
            process=subprocess.Popen(argv,cwd=workspace,env=env,stdin=stdin,stdout=stdout,stderr=stderr,start_new_session=True)
            while process.poll() is None:
                if time.monotonic()-start>timeout: stop='timeout';break
                if sum((capture_dir/n).stat().st_size for n in ('events.jsonl','stderr.txt'))>16*1024*1024:
                    stop='capture_budget_exceeded';break
                time.sleep(.03)
            if process.poll() is None:
                os.killpg(process.pid,signal.SIGTERM)
                try:process.wait(timeout=2)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=2)
            exit_code=process.returncode
    except BaseException as exc:
        stop='interrupted' if isinstance(exc,KeyboardInterrupt) else 'launch_error'
        if process is not None and process.poll() is None:
            os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=2)
        (capture_dir/'launch-error.txt').write_text(type(exc).__name__+': '+str(exc))
    if process is not None:
        try:os.killpg(process.pid,signal.SIGTERM)
        except ProcessLookupError:pass
    if not (capture_dir/'last-message.txt').exists():(capture_dir/'last-message.txt').write_bytes(b'')
    for name in ('events.jsonl','stderr.txt'):
        if not (capture_dir/name).exists():(capture_dir/name).write_bytes(b'')
    try:save_new(capture_dir/'after.json',snapshot(workspace))
    except (Invalid,OSError) as exc:
        stop='snapshot_failure';save_new(capture_dir/'after.json',{'capture_error':str(exc)})
    thread=None;capture_error=None
    if sum((capture_dir/n).stat().st_size for n in ('events.jsonl','stderr.txt'))>16*1024*1024:
        stop='capture_budget_exceeded';capture_error='capture budget exceeded; raw files retained'
    else:
        try:thread,_=parse_events(regular(capture_dir/'events.jsonl'))
        except (Invalid,ValueError,UnicodeError) as exc:capture_error=str(exc)
    files={n:sha(regular(capture_dir/n)) for n in ('events.jsonl','stderr.txt','last-message.txt','before.json','after.json','prompt.txt')}
    receipt={'schema_version':'writer-capture@1',**metadata,'argv':argv,'exit_code':exit_code,
             'stop_reason':stop,'elapsed_seconds':time.monotonic()-start,'thread_id':thread,'started_at':started_at,
             'files':files,'capture_error':capture_error,'controller_sha256':tool_hashes(),
             'observed_model':'UNKNOWN','effect_scope':'workspace snapshots plus delivered CLI events',
             'authenticity':'host-selected executable; no cryptographic attestation of model identity'}
    save_new(capture_dir/'run.json',receipt)
    return {'run_sha256':sha(regular(capture_dir/'run.json')),**receipt}

def execute(folder: Path, packet_sha: str, binary: str, approval: Path, approval_sha: str, phase: str) -> dict:
    packet=validate_packet(folder,packet_sha);report=doctor(binary)
    if report['status']!='EXECUTABLE_FOUND_NOT_QUALIFIED':return report
    host=validate_host(approval,approval_sha,packet_sha,report)
    if packet['execution_kind']!='host_codex_exec': raise Invalid('CLI never launches synthetic fixtures as real experiments')
    if phase=='comparison':
        pilot=folder/'pilot/capture'; pilot_sha=host.get('pilot_run_sha256')
        from evaluate_writer_run import inspect_capture
        if not isinstance(pilot_sha,str) or not host.get('capture_review_ref'):raise Invalid('qualified pilot and external capture review required')
        pilot_run,_=inspect_capture(pilot,pilot_sha)
        if pilot_run['phase']!='pilot' or pilot_run['packet_sha256']!=packet_sha or pilot_run['requested_model']!=host['model']:
            raise Invalid('pilot does not qualify this packet/model')
        if pilot_run.get('codex_sha256')!=report['codex_sha256']:raise Invalid('pilot used another executable')
    runs=folder/('pilot' if phase=='pilot' else 'runs')
    if runs.exists():raise Invalid('run area already exists; do not overwrite or resample')
    runs.mkdir()
    (runs/'host-approval.json').write_bytes(regular(approval))
    save_new(runs/'doctor.json',report)
    jobs=[{'id':'pilot','arm':'pilot'}] if phase=='pilot' else packet['jobs']
    save_new(runs/'scheduled.json',{'jobs':jobs,'phase':phase,'packet_sha256':packet_sha})
    results=[]; failed=False
    for job in jobs:
        base=runs if phase=='pilot' else runs/job['id'];base.mkdir(exist_ok=True)
        workspace=base/'workspace'
        if phase=='pilot':
            workspace.mkdir();(workspace/'work').mkdir();(workspace/'pilot.txt').write_text('Capture qualification only.\n')
            prompt=PILOT_PROMPT.encode()
        else:
            # Recheck all immutable controller-selected inputs between every launch.
            validate_packet(folder,packet_sha)
            shutil.copytree(folder/f"capsules/{job['arm']}",workspace);(workspace/'work').mkdir(exist_ok=True)
            prompt=regular(folder/'task.txt')
        validate_host(approval,approval_sha,packet_sha,report)
        metadata={'packet_sha256':packet_sha,'job_id':job['id'],'arm':job['arm'],'phase':phase,
                  'requested_model':host['model'],'execution_kind':'host_codex_exec',
                  'codex_sha256':report['codex_sha256'],'codex_version':report['version'],
                  'host_approval_sha256':approval_sha}
        result=capture(Path(report['codex']),workspace,base/'capture',prompt,metadata,packet['timeout_seconds'])
        results.append({'id':job['id'],'run_sha256':result['run_sha256'],'stop_reason':result['stop_reason']})
        if result['exit_code']!=0 or result['capture_error'] or result['stop_reason']!='completed':
            failed=True;break
    output={'status':'CAPTURED_NOT_GRADED' if len(results)==len(jobs) and not failed else 'INCOMPLETE',
            'phase':phase,'jobs':results,'behavior':None,'authorizes_landing':False}
    save_new(runs/'result.json',output);return output

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='cmd',required=True)
    q=s.add_parser('doctor');q.add_argument('--codex',default='codex')
    q=s.add_parser('prepare');q.add_argument('--spec',type=Path,required=True);q.add_argument('--baseline-root',type=Path,required=True)
    q.add_argument('--treatment-root',type=Path,required=True);q.add_argument('--common-root',type=Path,default=ROOT);q.add_argument('--out',type=Path,required=True)
    q=s.add_parser('run');q.add_argument('--packet',type=Path,required=True);q.add_argument('--packet-sha256',required=True)
    q.add_argument('--phase',choices=['pilot','comparison'],required=True);q.add_argument('--codex',default='codex')
    q.add_argument('--host-approval',type=Path,required=True);q.add_argument('--host-approval-sha256',required=True)
    a=p.parse_args()
    try:
        if a.cmd=='doctor':result=doctor(a.codex)
        elif a.cmd=='prepare':result=prepare(a.spec,{'baseline':a.baseline_root,'treatment':a.treatment_root,'common':a.common_root},a.out)
        else:result=execute(a.packet,a.packet_sha256,a.codex,a.host_approval,a.host_approval_sha256,a.phase)
    except (Invalid,ValueError,OSError,KeyError,TypeError) as exc:
        result={'status':'BLOCKED','error':str(exc),'writer_runs':'inspect retained run area' if a.cmd=='run' else 0,'behavior':None,'authorizes_landing':False}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 3 if result['status'] in {'BLOCKED','INCOMPLETE'} else 0

if __name__=='__main__':raise SystemExit(main())
