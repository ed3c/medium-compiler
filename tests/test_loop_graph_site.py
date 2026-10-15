import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_loop_site import ROOT, fixture, site


def graph_fixture():
    value = fixture()
    value['schema_version'] = 2
    run = value['runs'][0]['id']
    graph = {key: [] for key in ('objects', 'ports', 'repositories', 'nodes', 'artifacts', 'edges', 'findings', 'metrics')}
    value['graph'] = graph
    for i in range(3):
        repo, artifact, owner, node = 'repo-' + str(i), 'a-' + str(i), 'o-' + str(i), 'n-' + str(i)
        raw = ('{"message": "<script>inert</script>", "step": ' + str(i) + '}').encode()
        graph['repositories'].append({'id': repo, 'label': 'example/repo-' + str(i), 'root': 'public:repo-' + str(i),
            'revision': 'a' * 40, 'index_status': 'not_public', 'tracked_files': [{'id': 'f-' + str(i), 'path': 'src/source.py',
            'git_blob': 'b' * 40, 'git_mode': '100644', 'bytes': len(raw), 'artifact_ids': [artifact], 'node_ids': [node]}],
            'selected_files': [], 'gaps': ['Only reviewed files are public; other files are not public.']})
        graph['artifacts'].append({'id': artifact, 'repository_id': repo, 'role': 'source' if i == 0 else 'representation',
            'format': 'application/json', 'authority': 'knowledge_data', 'knowledge_role': 'source', 'scope': run,
            'source': {'path': 'private:original-' + str(i), 'sha256': 'a' * 64, 'bytes': 123}, 'status': 'available',
            'public_content': raw.decode(), 'public_sha256': hashlib.sha256(raw).hexdigest(), 'public_bytes': len(raw)})
        graph['objects'].append({'id': owner, 'namespace': 'soodles.loop' if i == 1 else 'example.owner-' + str(i),
            'label': 'LoopManager' if i == 1 else 'Owner ' + str(i), 'kind': 'manager', 'scope': 'shared' if i == 1 else 'repository', 'source_artifact_ids': [artifact]})
        for direction in ('input', 'output'):
            graph['ports'].append({'id': owner + '-' + direction, 'object_id': owner, 'name': direction, 'direction': direction,
                'schema': 'application/json', 'effect_scope': 'display_only', 'source_artifact_ids': [artifact]})
        graph['nodes'].append({'id': node, 'run_id': run, 'repository_id': repo, 'object_id': owner, 'kind': 'cli', 'label': 'Fixture occurrence ' + str(i),
            'identity': {'status': 'observed', 'invocation_id': 'fixture-' + str(i), 'attempt_id': None, 'session_id': None, 'locator': 'fixture:invocation-' + str(i)},
            'status': {'execution': 'completed', 'transfer': 'observed', 'acceptance': 'unknown'},
            'input_artifact_ids': [artifact], 'output_artifact_ids': [artifact], 'evidence_artifact_ids': [artifact], 'stage_id': 'review'})
    for i in range(2):
        graph['edges'].append({'id': 'e-' + str(i), 'run_id': run, 'from_node_id': 'n-' + str(i), 'to_node_id': 'n-' + str(i + 1),
            'from_port_id': 'o-' + str(i) + '-output', 'to_port_id': 'o-' + str(i + 1) + '-input',
            'input_artifact_ids': ['a-' + str(i)], 'output_artifact_ids': ['a-' + str(i + 1)], 'evidence_artifact_ids': ['a-' + str(i)],
            'kind': 'handoff', 'status': 'observed', 'label': 'JSON → selected JSON', 'scope': 'cross_repository', 'current_validity': 'current'})
    graph['findings'].append({'id': 'gap', 'run_id': run, 'kind': 'evidence_gap', 'status': 'unknown', 'message': 'Original acceptance not observed',
        'node_ids': ['n-2'], 'edge_ids': [], 'artifact_ids': ['a-2'], 'requirement_refs': ['REQ-fixture'], 'original_next': {'required': 'original readback'}})
    graph['metrics'].append({'id': 'coverage', 'run_id': run, 'name': 'Handoff coverage', 'status': 'unknown', 'value': None, 'unit': 'ratio',
        'numerator': 2, 'denominator': None, 'source_artifact_ids': [], 'gaps': ['Required handoff set incomplete']})
    return value


class LoopGraphSiteTests(unittest.TestCase):
    def prepare(self, root, value):
        folder = root / 'reports/loops'
        folder.mkdir(parents=True)
        raw = json.dumps(value, ensure_ascii=False).encode()
        (folder / 'public.json').write_bytes(raw)
        entry = {'path': 'reports/loops/public.json', 'sha256': hashlib.sha256(raw).hexdigest()}
        (folder / 'catalog.json').write_text(json.dumps({'schema_version': 1, 'snapshots': [entry]}))
        return entry

    def test_v2_build_keeps_original_identity_and_fetches_only_reviewed_static_content(self):
        value = graph_fixture()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            entry = self.prepare(root, value)
            out = root / 'out'; out.mkdir()
            site.render_loops(root, out, lambda title, body, active: body)
            folder = out / 'assets/loop-data' / entry['sha256']
            public = json.loads((folder / 'graph.json').read_bytes())
            rendered = (out / 'loops/test-only-run/index.html').read_text()
            self.assertIn('/assets/loop-graph.mjs', rendered)
            self.assertNotIn('<script>inert', rendered)
            self.assertNotIn('public_content', (folder / 'graph.json').read_text())
            self.assertNotIn('stages', public['runs'][0])
            for original, artifact in zip(value['graph']['artifacts'], public['graph']['artifacts']):
                self.assertEqual(original['source'], artifact['source'])
                url = public['content_urls'][artifact['id']]
                self.assertEqual((out / url.lstrip('/')).read_text(), original['public_content'])
                self.assertNotEqual(artifact['source']['sha256'], artifact['public_sha256'])
            self.assertEqual(public['graph']['metrics'][0]['denominator'], None)
            self.assertTrue((out / 'assets/loop-graph-layout.mjs').is_file())

    def test_nonpublic_and_unknown_artifacts_keep_named_gaps_without_content_urls(self):
        value = graph_fixture()
        artifact = value['graph']['artifacts'][0]
        for key in ('public_content', 'public_bytes', 'public_sha256'):
            artifact.pop(key)
        artifact['status'] = 'not_public'
        site.validate_snapshot(value)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td); (out / 'loops').mkdir()
            site.graph_site().build_graph_package(value, 'a' * 64, out / 'loops')
            public = json.loads((out / 'assets/loop-data' / ('a' * 64) / 'graph.json').read_text())
            self.assertNotIn(artifact['id'], public['content_urls'])
            self.assertEqual(public['graph']['artifacts'][0]['status'], 'not_public')
            self.assertEqual(public['graph']['edges'][0]['status'], 'observed')

    def test_canonical_invalid_edges_cycle_identity_and_metric_denominator_refuse(self):
        mutations = [lambda g: g['nodes'].append(copy.deepcopy(g['nodes'][0])),
                     lambda g: g['edges'][0].update(to_node_id='missing'),
                     lambda g: g['edges'][0].update(from_port_id='o-2-output'),
                     lambda g: g['nodes'][0]['identity'].update(status='unknown'),
                     lambda g: g['metrics'][0].update(status='observed', value=100, denominator=None)]
        for mutate in mutations:
            value = graph_fixture(); mutate(value['graph'])
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                site.validate_snapshot(value)
        value = graph_fixture()
        edge = copy.deepcopy(value['graph']['edges'][0]); edge.update(id='cycle', from_node_id='n-1', to_node_id='n-0', from_port_id='o-1-output', to_port_id='o-0-input', input_artifact_ids=['a-1'], output_artifact_ids=['a-0'])
        value['graph']['edges'].append(edge)
        with self.assertRaises(ValueError): site.validate_snapshot(value)

    def test_private_original_content_public_digest_and_oversized_payload_refuse(self):
        for change in ({'content': 'original', 'content_encoding': 'utf-8'}, {'public_sha256': 'f' * 64}, {'public_content': '/Users/person/private'}, {'status': 'not_public'}):
            value = graph_fixture(); value['graph']['artifacts'][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError): site.validate_snapshot(value)
        value = graph_fixture(); artifact = value['graph']['artifacts'][0]
        raw = b'x' * (2 * 1024 * 1024 + 1)
        artifact.update(public_content=raw.decode(), public_bytes=len(raw), public_sha256=hashlib.sha256(raw).hexdigest())
        with self.assertRaisesRegex(ValueError, 'size limit'): site.validate_snapshot(value)
        value = graph_fixture(); value['graph']['repositories'][0]['tracked_files'][0]['path'] = '../private'
        with self.assertRaisesRegex(ValueError, 'traversal'): site.validate_snapshot(value)

    def test_public_v2_import_preserves_bytes_noop_and_rejects_symlink_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); self.prepare(root, {'schema_version': 1, 'runs': []})
            source = root / 'reviewed.json'; raw = json.dumps(graph_fixture()).encode(); source.write_bytes(raw)
            command = [sys.executable, str(ROOT / 'scripts/import_loop_snapshot.py'), '--snapshot', str(source), '--id', 'graph', '--root', str(root)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root / 'reports/loops/graph.json').read_bytes(), raw)
            self.assertEqual(json.loads(subprocess.run(command, capture_output=True, text=True).stdout)['status'], 'NOOP')
            link = root / 'link.json'; link.symlink_to(source); command[3] = str(link)
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('symlink', result.stderr)


if __name__ == '__main__': unittest.main()
