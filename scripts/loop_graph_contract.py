"""Portable, effect-free validation of the original Loop display v2 contract."""
import hashlib
import math
import re

ID = re.compile(r"[A-Za-z0-9_-]+\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
ARRAYS = ('objects', 'ports', 'repositories', 'nodes', 'artifacts', 'edges', 'findings', 'metrics')
FIELDS = {
    'objects': 'id namespace label kind scope source_artifact_ids',
    'ports': 'id object_id name direction schema effect_scope source_artifact_ids',
    'repositories': 'id label root revision index_status tracked_files selected_files gaps',
    'nodes': 'id run_id repository_id object_id kind label identity status input_artifact_ids output_artifact_ids evidence_artifact_ids stage_id',
    'artifacts': 'id repository_id role format authority knowledge_role scope source status',
    'edges': 'id run_id from_node_id to_node_id from_port_id to_port_id input_artifact_ids output_artifact_ids evidence_artifact_ids kind status label scope current_validity',
    'findings': 'id run_id kind status message node_ids edge_ids artifact_ids requirement_refs original_next',
    'metrics': 'id run_id name status value unit numerator denominator source_artifact_ids gaps',
}
OPTIONAL = {'artifacts': {'content', 'content_encoding', 'public_content', 'public_sha256', 'public_bytes'},
            'metrics': {'observation_scope'}, 'repositories': {'observation'}}


def check(condition, message):
    if not condition:
        raise ValueError('loop.graph: ' + message)


def record(value, fields, label, optional=()):
    check(isinstance(value, dict), label + ' must be an object')
    required = set(fields.split())
    check(required <= value.keys() <= required | set(optional), label + ' fields differ')


def strings(value, label):
    check(isinstance(value, list) and all(isinstance(x, str) for x in value), label + ' must be strings')


def validate(view):
    """Validate display references, evidence claims and DAG; never inspect files."""
    check(isinstance(view, dict) and type(view.get('schema_version')) is int, 'version missing')
    check(view['schema_version'] in (1, 2) and isinstance(view.get('runs'), list), 'version/runs invalid')
    if view['schema_version'] == 1:
        check('graph' not in view, 'v1 cannot contain graph')
        return view
    graph = view.get('graph')
    record(graph, ' '.join(ARRAYS), 'graph')
    for run in view['runs']:
        check(isinstance(run, dict) and isinstance(run.get('id'), str) and ID.fullmatch(run['id']), 'run identity')
        check(isinstance(run.get('stages'), list) and all(isinstance(s, dict) and isinstance(s.get('id'), str) for s in run['stages']), 'run stages')
    runs = {r['id']: r for r in view['runs']}
    check(len(runs) == len(view['runs']), 'duplicate run')
    tables = {}
    for kind in ARRAYS:
        check(isinstance(graph[kind], list), kind + ' must be array')
        table = tables[kind] = {}
        for row in graph[kind]:
            record(row, FIELDS[kind], kind, OPTIONAL.get(kind, ()))
            identity = row['id']
            check(isinstance(identity, str) and ID.fullmatch(identity), kind + ' invalid identity')
            check(identity not in table, kind + ' duplicate identity')
            table[identity] = row
            for key in ('namespace', 'label', 'kind', 'scope', 'name', 'schema', 'effect_scope', 'root', 'role', 'format', 'authority', 'knowledge_role', 'message', 'unit'):
                if key in row:
                    check(isinstance(row[key], str), kind + ' ' + key + ' must be string')
    def ref(value, kind, nullable=False):
        check((value is None and nullable) or isinstance(value, str) and value in tables[kind], 'missing ' + kind + ' reference')
    def refs(values, kind):
        strings(values, kind + ' references')
        check(len(set(values)) == len(values), 'duplicate ' + kind + ' reference')
        for value in values:
            ref(value, kind)
    for kind, table in tables.items():
        for row in table.values():
            if 'run_id' in row:
                check(row['run_id'] in runs, 'missing run')
            if 'repository_id' in row:
                ref(row['repository_id'], 'repositories', nullable=kind == 'artifacts')
            for key, value in row.items():
                if key.endswith('_artifact_ids') or key == 'artifact_ids':
                    refs(value, 'artifacts')
    namespaces = [obj['namespace'] for obj in tables['objects'].values()]
    check(len(set(namespaces)) == len(namespaces), 'duplicate owner namespace')
    for obj in tables['objects'].values():
        check(obj['scope'] in ('shared', 'repository'), 'object scope')
    for port in tables['ports'].values():
        ref(port['object_id'], 'objects')
        check(port['direction'] in ('input', 'output'), 'port direction')
    for repo in tables['repositories'].values():
        check(repo['index_status'] in ('complete', 'unknown', 'not_public'), 'index status')
        strings(repo['gaps'], 'repository gaps')
        check(repo['index_status'] != 'complete' or isinstance(repo['revision'], str) and repo['revision'], 'complete index revision missing')
        if 'observation' in repo:
            obs = repo['observation']
            record(obs, 'status scope observed_at repository_id worktree_id snapshot_id branch detached dirty revision gap', 'repository observation')
            check(obs['status'] in ('observed', 'unknown') and obs['scope'] == 'display_readback', 'observation scope/status')
            check(isinstance(obs['observed_at'], str) and obs['observed_at'], 'observation time')
            check(obs['revision'] == repo['revision'], 'observation revision differs')
            for field in ('repository_id', 'worktree_id', 'snapshot_id'):
                check(obs[field] is None or isinstance(obs[field], str) and ID.fullmatch(obs[field]), 'observation identity')
            check(obs['branch'] is None or isinstance(obs['branch'], str) and obs['branch'], 'observation branch')
            check(obs['gap'] is None or isinstance(obs['gap'], str), 'observation gap')
            for field in ('dirty', 'detached'):
                check(obs[field] is None or type(obs[field]) is bool, 'observation boolean')
            if obs['status'] == 'observed':
                check(all(obs[k] is not None for k in ('repository_id', 'worktree_id', 'snapshot_id', 'dirty', 'detached')), 'observed Git identity missing')
                check((obs['branch'] is None) == obs['detached'] and obs['gap'] is None, 'observed branch state')
            else:
                check(all(obs[k] is None for k in ('repository_id', 'worktree_id', 'snapshot_id', 'branch', 'dirty', 'detached')) and bool(obs['gap']), 'unknown Git observation claims state')
        for key in ('tracked_files', 'selected_files'):
            check(isinstance(repo[key], list), 'files must be array')
            seen = set()
            for item in repo[key]:
                record(item, 'id path git_blob git_mode bytes artifact_ids node_ids', 'index entry')
                check(isinstance(item['id'], str) and ID.fullmatch(item['id']) and item['id'] not in seen, 'duplicate/invalid index entry')
                seen.add(item['id'])
                check(isinstance(item['path'], str) and item['path'] and not item['path'].startswith('/') and '..' not in item['path'].split('/'), 'index traversal')
                refs(item['artifact_ids'], 'artifacts'); refs(item['node_ids'], 'nodes')
                check(item['bytes'] is None or type(item['bytes']) is int and item['bytes'] >= 0, 'index bytes')
    for artifact in tables['artifacts'].values():
        check(artifact['status'] in ('available', 'unknown', 'stale', 'not_public'), 'artifact status')
        source = artifact['source']
        if source is not None:
            record(source, 'path sha256 bytes', 'artifact source')
            check(isinstance(source['path'], str) and source['path'], 'artifact path')
            check(source['sha256'] is None or isinstance(source['sha256'], str) and SHA.fullmatch(source['sha256']), 'artifact digest')
            check(source['bytes'] is None or type(source['bytes']) is int and source['bytes'] >= 0, 'artifact size')
        if artifact['status'] == 'available':
            check(source is not None and source['sha256'] is not None and source['bytes'] is not None, 'available source incomplete')
        if 'content' in artifact:
            check(artifact.get('content_encoding') == 'utf-8' and isinstance(artifact['content'], str), 'content encoding')
            raw = artifact['content'].encode('utf-8')
            check(source is not None and hashlib.sha256(raw).hexdigest() == source['sha256'] and len(raw) == source['bytes'], 'original content mismatch')
        if 'public_content' in artifact:
            check(isinstance(artifact['public_content'], str), 'public content text')
            raw = artifact['public_content'].encode('utf-8')
            check(hashlib.sha256(raw).hexdigest() == artifact.get('public_sha256') and len(raw) == artifact.get('public_bytes'), 'public representation mismatch')
        else:
            check('public_sha256' not in artifact and 'public_bytes' not in artifact, 'public representation missing')
    for node in tables['nodes'].values():
        ref(node['object_id'], 'objects')
        check(node['kind'] in ('session', 'pclass', 'cli', 'observation'), 'node kind')
        record(node['status'], 'execution transfer acceptance', 'node status')
        check(all(isinstance(x, str) and x for x in node['status'].values()), 'node status value')
        record(node['identity'], 'status invocation_id attempt_id session_id locator', 'node identity')
        identity = node['identity']
        check(all(identity[k] is None or isinstance(identity[k], str) for k in ('invocation_id', 'attempt_id', 'session_id', 'locator')), 'identity field type')
        check(identity['status'] in ('observed', 'unknown'), 'identity status')
        if identity['status'] == 'observed':
            check(identity['locator'] and any(identity[k] for k in ('invocation_id', 'attempt_id', 'session_id')), 'observed invocation locator missing')
        stage = node['stage_id']
        check(stage is None or stage in {s['id'] for s in runs[node['run_id']]['stages']}, 'stage reference')
    adjacency = {identity: set() for identity in tables['nodes']}
    for edge in tables['edges'].values():
        for key in ('from_node_id', 'to_node_id'):
            ref(edge[key], 'nodes')
        for key in ('from_port_id', 'to_port_id'):
            ref(edge[key], 'ports')
        source, target = (tables['nodes'][edge[k]] for k in ('from_node_id', 'to_node_id'))
        outport, inport = (tables['ports'][edge[k]] for k in ('from_port_id', 'to_port_id'))
        check(outport['object_id'] == source['object_id'] and inport['object_id'] == target['object_id'], 'edge port owner mismatch')
        check(outport['direction'] == 'output' and inport['direction'] == 'input', 'edge port direction')
        check(edge['kind'] in ('handoff', 'diagnostic') and edge['status'] in ('observed', 'unknown', 'failed', 'not_applicable'), 'edge kind/status')
        check(edge['current_validity'] in ('current', 'stale', 'unknown'), 'edge validity')
        crossing = source['repository_id'] != target['repository_id']
        check(edge['scope'] == ('cross_repository' if crossing else 'within_repository'), 'edge repository scope')
        if edge['kind'] == 'handoff':
            adjacency[source['id']].add(target['id'])
        if edge['status'] == 'observed':
            check(edge['kind'] == 'handoff', 'diagnostic cannot claim successful handoff')
            check(source['identity']['status'] == target['identity']['status'] == 'observed', 'handoff invocation unknown')
            check(all(edge[k] for k in ('input_artifact_ids', 'output_artifact_ids', 'evidence_artifact_ids')), 'handoff evidence missing')
            check(set(edge['input_artifact_ids']) <= set(source['input_artifact_ids'] + source['output_artifact_ids']), 'producer input mismatch')
            check(set(edge['output_artifact_ids']) <= set(target['input_artifact_ids'] + target['output_artifact_ids']), 'consumer output mismatch')
            check(all(tables['artifacts'][i]['status'] in ('available', 'not_public', 'stale') for i in edge['evidence_artifact_ids']), 'handoff evidence unavailable')
            if crossing:
                check(any(tables['objects'][n['object_id']]['namespace'] == 'soodles.loop' for n in (source, target)), 'cross repository lacks LoopManager occurrence')
    indegree = {key: 0 for key in adjacency}
    for children in adjacency.values():
        for child in children:
            indegree[child] += 1
    ready = [key for key, degree in indegree.items() if degree == 0]
    visited = 0
    while ready:
        key = ready.pop(); visited += 1
        for child in adjacency[key]:
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
    check(visited == len(adjacency), 'causal cycle')
    for finding in tables['findings'].values():
        refs(finding['node_ids'], 'nodes'); refs(finding['edge_ids'], 'edges')
        check(finding['kind'] in ('mechanical', 'semantic', 'acceptance', 'evidence_gap'), 'finding kind')
        check(finding['status'] in ('failed', 'unknown', 'not_applicable', 'resolved'), 'finding status')
        strings(finding['requirement_refs'], 'requirements')
    for metric in tables['metrics'].values():
        check(metric['status'] in ('observed', 'unknown', 'not_applicable'), 'metric status')
        strings(metric['gaps'], 'metric gaps')
        if 'observation_scope' in metric:
            scope = metric['observation_scope']
            record(scope, 'kind host_version host_pid started_at finished_at run_ids formula limitations', 'observation scope')
            check(scope['kind'] == 'historical_measurement', 'observation kind')
            check(isinstance(scope['host_version'], str) and isinstance(scope['formula'], str), 'observation description')
            check(scope['host_pid'] is None or type(scope['host_pid']) is int and scope['host_pid'] > 0, 'observation PID')
            check(all(scope[k] is None or isinstance(scope[k], str) for k in ('started_at', 'finished_at')), 'observation interval')
            strings(scope['run_ids'], 'observation run ids'); strings(scope['limitations'], 'observation limitations')
        for key in ('value', 'numerator', 'denominator'):
            check(metric[key] is None or type(metric[key]) in (int, float) and math.isfinite(metric[key]) and (key == 'value' or metric[key] >= 0), 'metric value')
        if metric['unit'] in ('ratio', 'percent') and metric['status'] == 'observed':
            check(metric['numerator'] is not None and metric['denominator'] is not None and metric['denominator'] > 0, 'observed ratio denominator incomplete')
            expected = metric['numerator'] / metric['denominator'] * (100 if metric['unit'] == 'percent' else 1)
            check(metric['value'] is not None and math.isclose(metric['value'], expected), 'ratio formula mismatch')
        if metric['denominator'] == 0:
            check(metric['status'] == 'not_applicable' and metric['value'] is None, 'zero denominator')
        if metric['status'] == 'unknown':
            check(metric['value'] is None, 'unknown metric value')
        if metric['numerator'] is not None and metric['denominator'] is not None:
            check(metric['numerator'] <= metric['denominator'], 'metric numerator outside denominator')
    return view
