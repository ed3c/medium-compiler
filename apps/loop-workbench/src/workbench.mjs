/** Pure, effect-free projection. No inferred handoff or reward. */
export function safeManifest(input, origin) {
  if (typeof input !== 'string' || input.length > 500) return null
  try {
    const target = new URL(input, origin)
    if (target.origin !== origin ||
        !/^\/assets\/loop-data\/[0-9a-f]{64}\/graph\.json$/.test(target.pathname) ||
        target.username || target.password || target.search || target.hash) return null
    return target.pathname
  } catch {
    return null
  }
}

const EMPTY = Object.freeze({ valid: false, reason: 'NO_REVIEWED_SNAPSHOT',
  runs: [], nodes: [], edges: [], findings: [], metrics: [], repositories: [] })

export function projectWorkbench(data) {
  if (!data || data.schema_version !== 2 || !Array.isArray(data.runs) ||
      !data.graph || !Array.isArray(data.graph.nodes) ||
      !Array.isArray(data.graph.edges) || !Array.isArray(data.graph.findings) ||
      !Array.isArray(data.graph.metrics) || !Array.isArray(data.graph.repositories)) return EMPTY
  const runs = data.runs.map(r => ({
    id: String(r.id), repository: String(r.repository),
    status: String(r.status || 'unknown'), mode: String(r.mode || 'unknown')
  }))
  const runIds = new Set(runs.map(r => r.id))
  const nodes = data.graph.nodes.filter(n => runIds.has(n.run_id)).map(n => ({
    id: String(n.id), run_id: String(n.run_id),
    kind: String(n.kind || 'unknown'), label: String(n.label || 'Unknown node'),
    execution: String(n.status?.execution || 'unknown'),
    transfer: String(n.status?.transfer || 'unknown'),
    acceptance: String(n.status?.acceptance || 'unknown'),
    identity: n.identity?.status === 'observed' ? 'observed' : 'unknown',
    inputs: Array.isArray(n.input_artifact_ids) ? n.input_artifact_ids : [],
    outputs: Array.isArray(n.output_artifact_ids) ? n.output_artifact_ids : [],
    evidence: Array.isArray(n.evidence_artifact_ids) ? n.evidence_artifact_ids : []
  }))
  const nodeIds = new Set(nodes.map(n => n.id))
  const edges = data.graph.edges.filter(e => runIds.has(e.run_id) &&
    nodeIds.has(e.from_node_id) && nodeIds.has(e.to_node_id)).map(e => ({
    id: String(e.id), run_id: String(e.run_id), from: String(e.from_node_id),
    to: String(e.to_node_id), status: String(e.status || 'unknown'),
    validity: String(e.current_validity || 'unknown'), kind: String(e.kind || 'unknown'),
    scope: String(e.scope || 'unknown'), label: String(e.label || 'Handoff')
  }))
  return {valid: true, reason: null, runs, nodes, edges,
    findings: data.graph.findings.filter(f => runIds.has(f.run_id)).map(f => ({
      id: String(f.id), run_id: String(f.run_id),
      status: String(f.status || 'unknown'), kind: String(f.kind || 'unknown'),
      message: String(f.message || 'Evidence unavailable')
    })),
    metrics: data.graph.metrics.filter(m => runIds.has(m.run_id)).map(m => ({
      id: String(m.id), run_id: String(m.run_id), name: String(m.name),
      status: String(m.status || 'unknown'), value: m.status === 'observed' ? m.value : null,
      unit: String(m.unit || '')
    })),
    repositories: data.graph.repositories.map(r => ({
      id: String(r.id), label: String(r.label), index: String(r.index_status || 'unknown'),
      gaps: Array.isArray(r.gaps) ? r.gaps : []
    }))
  }
}

export function selectRun(view, runId) {
  const match = view.runs.find(r => r.id === runId)
  return { run: match || null,
    nodes: view.nodes.filter(n => !match || n.run_id === match.id),
    edges: view.edges.filter(e => !match || e.run_id === match.id),
    findings: view.findings.filter(f => !match || f.run_id === match.id),
    metrics: view.metrics.filter(m => !match || m.run_id === match.id) }
}

export function nativeClaim(edge) {
  // Only the original evidence producer may claim observed or verified.
  if (edge.status === 'failed') return 'FAILED'
  if (edge.status === 'observed' && edge.kind === 'handoff' &&
      edge.validity === 'current') return 'OBSERVED_HANDOFF'
  return 'UNKNOWN'
}

export function rlExperimentProjection(episode) {
  if (!episode || episode.schema_version !== 0 ||
      !episode.task_ref || !episode.environment_ref) return {
        status: 'NOT_CONNECTED', reward: null, termination: 'unknown' }
  return {status: episode.verification?.status || 'UNKNOWN',
    reward: episode.reward?.status === 'observed' ? episode.reward.value : null,
    termination: episode.termination?.status || 'unknown'}
}
