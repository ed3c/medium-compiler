import test from 'node:test';
import assert from 'node:assert/strict';
import { compileLoopUIArtifact } from '../site/loop-ui-artifact.mjs';

const digest = 'a'.repeat(64);
const fixture = {
  schema_version: 2, runs: [{ id: 'runA', repository: 'repo', mode: 'outer-only' }],
  graph: {
    nodes: [{ id:'nodeA', run_id:'runA', identity:{status:'observed'},
      input_artifact_ids:['sourceA'], output_artifact_ids:[], evidence_artifact_ids:[] }],
    edges: [{id:'edgeA', run_id:'runA', status:'failed', current_validity:'current',
      input_artifact_ids:['sourceA'], output_artifact_ids:[], evidence_artifact_ids:['proofA']}],
    artifacts: [
      {id:'sourceA', role:'instruction', scope:'runA', status:'available'},
      {id:'proofA', role:'receipt', scope:'runA', status:'not_public'},
    ],
  },
};
test('a real observed failure remains a failure; withheld evidence is not silently public', () => {
  const view = compileLoopUIArtifact(fixture, digest, { runId:'runA' });
  assert.deepEqual(view.views[0].source_artifact_ids, ['proofA','sourceA']);
  assert.deepEqual(view.views[0].states, ['failed','not_public']);
  assert.deepEqual(view.permissions, {dispatch:false,review_effect:false,deployment:false,train:false});
  assert.equal(view.verification.browser, 'NOT_RUN');
});
test('no occurrence is never proof of success', () => {
  const view = compileLoopUIArtifact({...fixture,graph:{...fixture.graph,nodes:[],edges:[]}},
    digest, {runId:'runA',primarySkill:'anatomy',mode:'explain'});
  assert.deepEqual(view.views[0].states,['unknown']);
  assert.equal(view.verification.mechanical,'UNKNOWN');
});
test('unknown run and unpinned source refuse', () => {
  assert.throws(()=>compileLoopUIArtifact(fixture,digest,{runId:'foreign'}));
  assert.throws(()=>compileLoopUIArtifact(fixture,'not-a-digest',{runId:'runA'}));
});
