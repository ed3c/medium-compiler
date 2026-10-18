/** Readonly, source-ref-preserving ViewEnv episode projection. No causal edge synthesis. */
export function reviewedEpisodePath(input, origin) {
  if (typeof input !== 'string' || input.length > 512) return null
  try {
    const parsed = new URL(input, origin)
    if (parsed.origin !== origin || parsed.username || parsed.password ||
      parsed.search || parsed.hash ||
      !/^\/assets\/viewenv\/episodes\/[a-f0-9]{64}\.json$/.test(parsed.pathname)) return null
    return parsed.pathname
  } catch { return null }
}
const EMPTY = Object.freeze({status:'NOT_CONNECTED', episode:null, harness:null,
  actions:[],observations:[],verification:null,reward:null,termination:null,
  message:'No original verified episode is present.'})
const validRef = x => typeof x === 'string' && x.length > 0 && x.length <= 512
export function projectViewEnv(record) {
  if (!record || record.schema_version !== 0 ||
      !['run_ref','episode_ref','task_ref','environment_ref','actor_ref'].every(k=>validRef(record[k])) ||
      !record.harness || !['propose','probe','compose','reflect','unknown'].includes(record.harness.phase) ||
      !Array.isArray(record.actions) || !Array.isArray(record.observations) ||
      record.actions.some(x=>!validRef(x)) || record.observations.some(x=>!validRef(x)) ||
      !record.reward || !record.verification || !record.termination) return EMPTY
  const v=record.verification,r=record.reward,t=record.termination
  if (!['PASS','FAIL','INCONCLUSIVE','NOT_RUN'].includes(v.status) ||
      !['observed','unknown','not_applicable'].includes(r.status) ||
      !['done','truncated','unknown'].includes(t.status) ||
      ((v.status==='PASS'||v.status==='FAIL')&&!validRef(v.verifier_ref)) ||
      (r.status !== 'observed' && r.value !== null) ||
      (r.status === 'observed' &&
        (typeof r.value!=='number'||!Number.isFinite(r.value)||!validRef(r.source_ref)||!validRef(v.verifier_ref)))) return EMPTY
  return {
    status:'SOURCE_BOUND',
    episode:{run_ref:record.run_ref,episode_ref:record.episode_ref,
      task_ref:record.task_ref,environment_ref:record.environment_ref,actor_ref:record.actor_ref},
    harness:{phase:record.harness.phase,baseline_ref:record.harness.baseline_ref||null,
      candidate_ref:record.harness.candidate_ref||null},
    actions:[...record.actions],observations:[...record.observations],
    verification:{status:v.status,verifier_ref:v.verifier_ref||null},
    reward:{status:r.status,value:r.status==='observed'?r.value:null,source_ref:r.source_ref||null},
    termination:{status:t.status,reason_ref:t.reason_ref||null},
    message:'Read-only projection of original producer references; no execution authority.'
  }
}
export function inspectLayer(scene,layer){
  if(!['actual','proposed','replay'].includes(layer))throw new Error('unknown_view_layer')
  if(scene.status!=='SOURCE_BOUND')return {layer,status:'NOT_CONNECTED',refs:[]}
  if(layer==='actual')return {layer,status:scene.verification.status,
    refs:[scene.episode.task_ref,scene.episode.environment_ref,scene.verification.verifier_ref].filter(Boolean)}
  if(layer==='proposed')return {layer,status:scene.harness.candidate_ref?'PROPOSED':'UNKNOWN',
    refs:[scene.harness.baseline_ref,scene.harness.candidate_ref].filter(Boolean)}
  return {layer,status:scene.termination.status==='unknown'?'UNKNOWN':'RECORDED',
    refs:[...scene.actions,...scene.observations]}
}
