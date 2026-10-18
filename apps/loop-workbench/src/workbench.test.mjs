import { test } from 'node:test'
import assert from 'node:assert/strict'
import { safeManifest, projectWorkbench, selectRun, nativeClaim, rlExperimentProjection } from './workbench.mjs'

const graph = {
  schema_version: 2,
  runs: [{ id: 'r1', repository: 'NeoWeaver', status: 'unknown', mode: 'outer-inner' }],
  graph: {
    nodes: [
      { id:'a',run_id:'r1',label:'Original',kind:'session',status:{execution:'started'},identity:{status:'observed'} },
      { id:'b',run_id:'r1',label:'Consumer',kind:'cli',status:{execution:'unknown'},identity:{status:'unknown'} }
    ],
    edges: [
      {id:'e1',run_id:'r1',from_node_id:'a',to_node_id:'b',status:'unknown',kind:'handoff',current_validity:'unknown'},
      {id:'e2',run_id:'r1',from_node_id:'b',to_node_id:'a',status:'failed',kind:'diagnostic',current_validity:'current'}
    ],
    findings: [{id:'f',run_id:'r1',status:'failed',message:'Missing actual consumer readback'}],
    metrics: [{id:'m',run_id:'r1',name:'reward',status:'unknown',value:42}],
    repositories: [{id:'repo',label:'NeoWeaver',index_status:'unknown'}]
  }
}

test('public path cannot fetch remote, other origins, traversal or foreign static assets', () => {
  const origin = 'https://workbench.example'
  const correct = '/assets/loop-data/' + 'a'.repeat(64) + '/graph.json'
  assert.equal(safeManifest(correct, origin), correct)
  for (const input of ['https://evil.example'+correct, '/api/dispatch',
    '/assets/loop-data/../private/graph.json', correct+'?token=abc',
    'javascript:alert(1)', correct+'#ignore']) {
    assert.equal(safeManifest(input,origin), null)
  }
})

test('unknown and failure remain distinct with no invented cost/reward', () => {
  const result = projectWorkbench(graph)
  assert.equal(result.valid, true)
  assert.equal(result.nodes.length, 2)
  assert.equal(selectRun(result,'r1').edges.length, 2)
  assert.equal(nativeClaim(result.edges[0]), 'UNKNOWN')
  assert.equal(nativeClaim(result.edges[1]), 'FAILED')
  assert.equal(result.metrics[0].value, null)
  assert.equal(rlExperimentProjection({}).reward, null)
  assert.equal(rlExperimentProjection({schema_version:0,task_ref:'t',environment_ref:'e',
    reward:{status:'unknown',value:1}}).reward, null)
})

test('invalid graph refuses rather than inventing a run', () => {
  assert.equal(projectWorkbench({runs:[]}).valid, false)
  assert.equal(projectWorkbench(null).runs.length, 0)
})

test('native handoff must be explicitly current and observed', () => {
  assert.equal(nativeClaim({status:'observed',kind:'handoff',validity:'current'}), 'OBSERVED_HANDOFF')
  assert.equal(nativeClaim({status:'observed',kind:'diagnostic',validity:'current'}), 'UNKNOWN')
  assert.equal(nativeClaim({status:'observed',kind:'handoff',validity:'stale'}), 'UNKNOWN')
})
