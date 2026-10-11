import {validPayment} from "../../../site/reliability/logic.mjs";

export function validRunId(runId){
  if(typeof runId!=="string"||!/^[A-Za-z0-9-]{1,40}$/.test(runId))throw Error("Run ID: 1-40 letters, digits or hyphens");
  return runId;
}
export function readScope(input){
  if(!input||typeof input!=="object"||Array.isArray(input))throw Error("Readback scope required");
  const choices=[input.key!==undefined,input.runId!==undefined,input.full===true];
  if(choices.filter(Boolean).length!==1)throw Error("Select exactly one Payment Key, Run ID or explicit full readback");
  if(input.key!==undefined){validPayment(input.key,1);return {type:"key",key:input.key};}
  if(input.runId!==undefined){
    return {type:"run",runId:validRunId(input.runId)};
  }
  return {type:"full"};
}
export function scopeQuery(scope,outbox=false){
  // Revalidate at the DO boundary; never silently fall back to an entire table.
  const selected=readScope(scope.type==="key"?{key:scope.key}:scope.type==="run"?{runId:scope.runId}:scope.type==="full"?{full:true}:{});
  if(selected.type==="key")return {where:" WHERE key=?",bindings:[selected.key]};
  if(selected.type==="run")return {where:outbox?" WHERE key IN (SELECT key FROM orders WHERE run_id=?)":" WHERE run_id=?",bindings:[selected.runId]};
  return {where:"",bindings:[]};
}
export function readRows(sql,query,bindings){
  const cursor=sql.exec(query,...bindings),rows=cursor.toArray();
  // Consume synchronously before measuring. Null means adapter unavailable,
  // never an invented count from returned rows. This excludes other SQL work.
  return {rows,rowsRead:typeof cursor.rowsRead==="number"?cursor.rowsRead:null};
}
