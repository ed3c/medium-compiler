import test from 'node:test'
import assert from 'node:assert/strict'
import {PROBLEMS,validateAttempt,encodeExport,decodeExport,progress} from './learning-domain.mjs'
const a={id:'attempt-001',problem_id:'python-sum',code:'def total(v): return sum(v)',
 timestamp:100,status:'passed',passed_cases:3,total_cases:3,oracle:'browser_untrusted'}
test('source-bound problem set never declares native acceptance',()=>{
 assert.equal(PROBLEMS.length,2)
 assert.equal(progress([a])[0].oracle,'browser_untrusted')
})
test('duplicate, false pass, forged oracle and unknown problem refuse',()=>{
 assert.throws(()=>validateAttempt({...a,passed_cases:2}),/FALSE_PASS/)
 assert.throws(()=>validateAttempt({...a,oracle:'native_agent'}),/INVALID_ORACLE/)
 assert.throws(()=>validateAttempt({...a,problem_id:'foreign'}),/INVALID_TARGET/)
 assert.throws(()=>decodeExport(JSON.stringify({schema_version:'medium-local-learning-v1',attempts:[a,a]})),/DUPLICATE/)
})
test('export round trip preserves exact attempt and browser-only claim',()=>{
 assert.deepEqual(decodeExport(encodeExport([a])),[a])
 assert.equal(progress([])[0].locally_passed,false)
})
