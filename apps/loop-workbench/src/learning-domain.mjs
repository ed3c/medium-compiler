/** Source-bound local learning state. Not a native Agent/evals oracle. */
export const PROBLEMS=Object.freeze([
 Object.freeze({id:'python-sum',title:'Accumulate integers',entry:'total',starter:'def total(values):\n    return 0',input:[[1,2,3],[],[-2,7,5]],expected:[6,0,10]}),
 Object.freeze({id:'python-count',title:'Count even numbers',entry:'count_even',starter:'def count_even(values):\n    return 0',input:[[1,2,4,5],[],[-2,0,3]],expected:[2,0,2]})
]);
export const EXPORT_SCHEMA='medium-local-learning-v1';
const allowed=['not_run','passed','failed','inconclusive'];
export function validateAttempt(x){
 if(!x || typeof x!=='object'||Array.isArray(x))throw Error('INVALID_ATTEMPT');
 if(typeof x.id!=='string'|| !/^[a-zA-Z0-9-]{8,80}$/.test(x.id))throw Error('INVALID_ID');
 if(!PROBLEMS.some(p=>p.id===x.problem_id)||!allowed.includes(x.status))throw Error('INVALID_TARGET');
 if(typeof x.code!=='string'||x.code.length>32768)throw Error('INVALID_CODE');
 if(!Number.isSafeInteger(x.timestamp)||x.timestamp<0)throw Error('INVALID_TIME');
 if(!Number.isInteger(x.passed_cases)||!Number.isInteger(x.total_cases)||x.total_cases<0||
 x.total_cases>100||x.passed_cases<0||x.passed_cases>x.total_cases)throw Error('INVALID_CASES');
 if(x.status==='passed' && (!x.total_cases||x.passed_cases!==x.total_cases))throw Error('FALSE_PASS');
 if(x.status==='not_run' && (x.passed_cases||x.total_cases))throw Error('FALSE_UNRUN');
 if(x.oracle!=='browser_untrusted'&&x.oracle!=='not_observed')throw Error('INVALID_ORACLE');
 if(x.oracle==='not_observed'&&x.status!=='not_run')throw Error('UNVERIFIED_CLAIM');
 return {id:x.id,problem_id:x.problem_id,code:x.code,timestamp:x.timestamp,
  status:x.status,passed_cases:x.passed_cases,total_cases:x.total_cases,oracle:x.oracle};
}
export function encodeExport(rows){
 if(!Array.isArray(rows)||rows.length>10000)throw Error('INVALID_SIZE');
 return JSON.stringify({schema_version:EXPORT_SCHEMA,owner:'local_browser_not_native',
  attempts:rows.map(validateAttempt)},null,2);
}
export function decodeExport(raw){
 if(typeof raw!=='string'||raw.length>12000000)throw Error('INVALID_SIZE');
 let parsed;try{parsed=JSON.parse(raw)}catch{throw Error('INVALID_JSON')}
 if(parsed?.schema_version!==EXPORT_SCHEMA||!Array.isArray(parsed.attempts)||
 parsed.attempts.length>10000)throw Error('INVALID_SCHEMA');
 const rows=parsed.attempts.map(validateAttempt),seen=new Set();
 for(const a of rows){if(seen.has(a.id))throw Error('DUPLICATE_ATTEMPT');seen.add(a.id)}
 return rows;
}
export function progress(rows){
 const checked=rows.map(validateAttempt);
 return PROBLEMS.map(p=>({id:p.id,attempts:checked.filter(a=>a.problem_id===p.id).length,
  locally_passed:checked.some(a=>a.problem_id===p.id && a.status==='passed'),
  oracle:'browser_untrusted'}));
}
