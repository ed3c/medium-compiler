import test from 'node:test';
import assert from 'node:assert/strict';
import { layoutGraph } from '../site/loop-graph-layout.mjs';
import { edgeClass, sourceRelations, compareText, mount } from '../site/loop-graph.mjs';

test('shared layout is stable for multi-parent occurrences without merging repeated owner calls', () => {
  const nodes = [{ id: 'call-1', repository_id: 'repo-a' }, { id: 'call-2', repository_id: 'repo-a' }, { id: 'consumer', repository_id: 'repo-b' }];
  const edges = [{ from: 'call-1', to: 'consumer' }, { from: 'call-2', to: 'consumer' }];
  const layout = layoutGraph({ nodes, edges });
  assert.deepEqual(layout, layoutGraph({ nodes: [...nodes].reverse(), edges: [...edges].reverse() }));
  assert.equal(layout.nodes.length, 3);
  assert.equal(new Set(layout.nodes.map(n => n.id)).size, 3);
  assert.ok(layout.nodes.find(n => n.id === 'consumer').rank > layout.nodes.find(n => n.id === 'call-1').rank);
  assert.throws(() => layoutGraph({ nodes, edges: [...edges, { from: 'consumer', to: 'call-1' }] }));
  assert.throws(() => layoutGraph({ nodes, edges: [{ from: 'missing', to: 'consumer' }] }));
});
test('unknown and historical edges do not become current success or proven red X', () => {
  assert.equal(edgeClass({ status: 'unknown', kind: 'handoff' }), 'unknown');
  assert.equal(edgeClass({ status: 'failed', kind: 'diagnostic' }), 'failed');
  assert.equal(edgeClass({ status: 'observed', kind: 'handoff', current_validity: 'unknown' }), 'unknown');
  assert.equal(edgeClass({ status: 'observed', kind: 'handoff', current_validity: 'stale' }), 'stale');
});
test('source links come only from explicit refs, including reverse owner relations', () => {
  const graph = { objects: [{ id: 'owner', source_artifact_ids: ['a'] }], nodes: [{ id: 'n', object_id: 'owner', input_artifact_ids: ['a'], output_artifact_ids: [] }, { id: 'same-name', object_id: 'owner', input_artifact_ids: [], output_artifact_ids: [] }], edges: [{ id: 'e', from_node_id: 'n', to_node_id: 'same-name', input_artifact_ids: ['a'], output_artifact_ids: [] }] };
  const related = sourceRelations(graph, ['a']);
  assert.deepEqual([...related.nodes], ['n']);
  assert.deepEqual([...related.edges], ['e']);
  assert.deepEqual([...sourceRelations(graph, ['unrecorded']).nodes], []);
});
test('comparison preserves Unicode and JSON field absence without semantic PASS', () => {
  assert.equal(compareText('😀', '😀x').leftPoints, 1);
  const comparison = compareText('{"a":null}', '{"b":false}');
  assert.equal(comparison.equal, false);
  assert.deepEqual(comparison.fields.map(f => f.path), ['$["a"]', '$["b"]']);
  assert.deepEqual(compareText('prefix\nold\nsuffix', 'prefix\nnew\nsuffix').removed, ['old']);
});
test('protected snapshot reads use same-origin login and refuse external sources before fetch', async t => {
  const oldLocation = Object.getOwnPropertyDescriptor(globalThis, 'location');
  Object.defineProperty(globalThis, 'location', { configurable: true, value: new URL('https://preview.example/loops/run/') });
  t.after(() => oldLocation ? Object.defineProperty(globalThis, 'location', oldLocation) : delete globalThis.location);
  const calls = [];
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    calls.push({ url: String(url), options });
    return { ok: false, status: 503 };
  });
  await assert.rejects(mount({ dataset: { manifest: '/assets/loop-data/digest/graph.json' } }), /503/);
  assert.deepEqual(calls, [{ url: 'https://preview.example/assets/loop-data/digest/graph.json', options: { credentials: 'same-origin', redirect: 'error' } }]);
  for (const manifest of ['https://other.example/assets/loop-data/graph.json', '/private/data.json']) {
    await assert.rejects(mount({ dataset: { manifest } }), /非此快照/);
  }
  assert.equal(calls.length, 1);
});
