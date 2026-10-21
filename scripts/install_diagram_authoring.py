#!/usr/bin/env python3
"""Install bounded pinned SeeCode/OMM skill trees, never execute them."""
import argparse
import importlib.util
import json
from pathlib import Path, PurePosixPath
import tempfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('base_installer',ROOT/'scripts/install_loop_visual_skills.py')
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

def select(source,files):
    output={}
    for path,data in files.items():
        for subtree in source['subtrees']:
            parts=PurePosixPath(subtree).parts
            if path.parts[:len(parts)]==parts and len(path.parts)>len(parts):
                group=parts[-1]
                relative=PurePosixPath(*path.parts[len(parts):])
                output.setdefault(group,{})[relative]=data
    license_file=files.get(PurePosixPath('LICENSE'))
    if not license_file or not license_file.startswith(b'MIT License'):
        raise ValueError('UNVERIFIED_UPSTREAM_LICENSE')
    if set(output)!=set(source['targets']):
        raise ValueError('INCOMPLETE_PINNED_SKILL')
    for name,members in output.items():
        if PurePosixPath('SKILL.md') not in members:
            raise ValueError('MISSING_SKILL_ENTRY')
        members[PurePosixPath('UPSTREAM-LICENSE')]=license_file
        members[PurePosixPath('.upstream-provenance.json')]=(
            json.dumps({k:source[k] for k in ('repo','sha','license')},sort_keys=True)+'\n'
        ).encode()
    return output

def install(root,lock,dry_run=False):
    if lock.get('schema_version')!=1:raise ValueError('BAD_LOCK')
    dest=root/'.agents/skills'
    if dest.is_symlink():raise ValueError('SKILLS_SYMLINK')
    expected={}
    for source in lock['sources']:
        if not isinstance(source['sha'],str) or len(source['sha'])!=40:
            raise ValueError('NOT_PINNED')
        files=base.extracted_files(base.read_archive(source),source)
        for name,members in select(source,files).items():
            if name in expected:raise ValueError('DUPLICATED_SKILL')
            expected[name]=members
    for name,members in expected.items():
        path=dest/name
        if path.is_symlink():raise ValueError('SKILL_SYMLINK')
        if path.exists():
            if not path.is_dir() or any(p.is_symlink() for p in path.rglob('*')):
                raise ValueError('BAD_INSTALLED_SKILL')
            prior={PurePosixPath(*p.relative_to(path).parts):p.read_bytes()
                   for p in path.rglob('*') if p.is_file()}
            if prior!=members:raise ValueError('INSTALLED_BYTES_DIFFER: '+name)
    if not dry_run:
        dest.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=dest,prefix='.diagram-skills-') as td:
            stage=Path(td)
            for name,members in expected.items():
                for relative,content in members.items():
                    target=stage/name/Path(*relative.parts)
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(content)
            for name in expected:
                if not (dest/name).exists():(stage/name).rename(dest/name)
    return {'status':'DRY_RUN' if dry_run else 'INSTALLED_OR_VERIFIED',
            'skills':sorted(expected)}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    lock=json.loads((ROOT/'design/diagram-authoring.lock.json').read_text())
    print(json.dumps(install(ROOT,lock,args.dry_run),sort_keys=True))
if __name__=='__main__':main()
