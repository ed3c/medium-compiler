import {test} from 'node:test'
import assert from 'node:assert/strict'
import {reviewedEpisodePath,projectViewEnv,inspectLayer} from './viewenv.mjs'

const base = {
  schema_version:0,run_ref:'run-a',episode_ref:'ep-a',task_ref:'task-1',
  environment_ref:'env-1',actor_ref:'native-owner',
  harness:{phase:'probe',baseline_ref:'H0',candidate_ref:'H1'},
  actions:['a1'],observations:['o1'],
  verification:{status:'INCONCLUSIVE',verifier_ref:null},
  reward:{status:'unknown',value:null,source_ref:null},
  termination:{status:'unknown',reason_ref:null}
}

test('only same-origin, content addressed public episode path is readable',()=>{
  const url='/assets/viewenv/episodes/'+'b'.repeat(64)+'.json'
  assert.equal(reviewedEpisodePath(url,'https://app.example'),url)
  for(const x of ['https://evil.example'+url,url+'?raw=1',url+'#foo',
    '/api/loop/dispatch','/assets/viewenv/episodes/../private.json',
    'javascript:alert(1)'])assert.equal(reviewedEpisodePath(x,'https://app.example'),null)
})
test('unverified reward stays unknown and layers preserve original references',()=>{
  const view=projectViewEnv(base)
  assert.equal(view.status,'SOURCE_BOUND')
  assert.equal(view.reward.value,null)
  assert.deepEqual(inspectLayer(view,'proposed').refs,['H0','H1'])
  assert.deepEqual(inspectLayer(view,'replay').refs,['a1','o1'])
  assert.equal(inspectLayer(view,'actual').status,'INCONCLUSIVE')
})
test('empty/malformed original record does not create an episode',()=>{
  assert.equal(projectViewEnv(null).status,'NOT_CONNECTED')
  assert.equal(projectViewEnv({...base,action:'guess'}).status,'SOURCE_BOUND')
  assert.equal(projectViewEnv({...base,reward:{status:'unknown',value:0}}).status,'NOT_CONNECTED')
  assert.equal(projectViewEnv({...base,verification:{status:'PASS',verifier_ref:null}}).status,'NOT_CONNECTED')
  assert.equal(projectViewEnv({...base,reward:{status:'observed',value:1,source_ref:null}}).status,'NOT_CONNECTED')
})
test('an independently referenced failed/verdict keeps separate reward and termination',()=>{
  const view=projectViewEnv({...base,verification:{status:'FAIL',verifier_ref:'oracle-original'},
    reward:{status:'observed',value:-1,source_ref:'reward-original'},
    termination:{status:'done',reason_ref:'native-terminal'}})
  assert.equal(view.verification.status,'FAIL')
  assert.equal(view.reward.value,-1)
  assert.equal(view.termination.status,'done')
  assert.equal(inspectLayer(view,'replay').status,'RECORDED')
})
