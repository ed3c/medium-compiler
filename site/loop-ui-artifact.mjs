/** Pure read-only design artifact: original graph facts -> TanStack Start view props.
 * Preconditions: the existing public Loop importer has validated the snapshot and
 * its selected catalog digest. This does not validate owner authority or effects.
 */
const sha256 = /^[a-f0-9]{64}$/;
const refs = item => [
  ...(item?.source_artifact_ids || []),
  ...(item?.input_artifact_ids || []),
  ...(item?.output_artifact_ids || []),
  ...(item?.evidence_artifact_ids || []),
];
const stable = list => [...new Set(list)].sort();
const evidenceState = edge => edge.status === 'failed' ? 'failed'
  : edge.current_validity === 'stale' ? 'stale'
  : edge.status === 'observed' && edge.current_validity === 'current' ? 'observed'
  : edge.status === 'not_applicable' ? 'not_applicable' : 'unknown';

/** This projection does not synthesize edges, steps, invocations, reward or new IDs. */
export function compileLoopUIArtifact(snapshot, sourceDigest, {
  runId, primarySkill = 'impeccable', mode = 'operate', skillPins = [],
} = {}) {
  const allowedSkills = ['anatomy', 'impeccable', 'emil-design-eng',
    'design-taste-frontend', 'build-review-interface'];
  if (!sha256.test(sourceDigest) || snapshot?.schema_version !== 2
      || !snapshot.graph || !Array.isArray(snapshot.graph.nodes)
      || !Array.isArray(snapshot.graph.edges) || !Array.isArray(snapshot.graph.artifacts)
      || !Array.isArray(snapshot.runs)) {
    throw Error('Source must be an already-validated, digested Loop v2 public snapshot');
  }
  const run = snapshot.runs.find(r => r.id === runId);
  if (!run || !allowedSkills.includes(primarySkill)
      || !['read', 'operate', 'explain', 'present'].includes(mode)
      || !Array.isArray(skillPins) || skillPins.some(pin => typeof pin !== 'string')) {
    throw Error('Unknown run or unsupported design selection');
  }
  const graph = snapshot.graph;
  const edges = graph.edges.filter(e => e.run_id === runId);
  const nodes = graph.nodes.filter(n => n.run_id === runId);
  const artifacts = new Map(graph.artifacts.map(a => [a.id, a]));
  const related = stable([...edges.flatMap(refs), ...nodes.flatMap(refs)]);
  const states = stable([
    ...edges.map(evidenceState),
    ...related.filter(id => artifacts.get(id)?.status === 'not_public').map(() => 'not_public'),
    ...nodes.filter(n => n.identity?.status === 'unknown').map(() => 'unknown'),
  ]);
  if (states.length === 0) states.push('unknown');
  const contract = stable(graph.artifacts.filter(a => (
    a.scope === runId || a.scope === 'original_source'
  ) && ['loop_expectation', 'loop_comparison', 'mechanism_contract',
        'state_machine_contract'].includes(a.role)).map(a => a.id));
  const views = [
    { view_id: 'run-'+runId, source_artifact_ids: related, states },
    { view_id: 'contract-'+runId, source_artifact_ids: contract,
      states: contract.length ? ['unknown'] : ['not_run'] },
  ];
  return {
    schema_version: 1,
    source: { snapshot_ref: runId, source_sha256: sourceDigest,
      visibility: 'reviewed_public' },
    render_target: 'tanstack-start-react',
    design: { primary_skill: primarySkill, skill_pins: stable(skillPins), mode,
      rationale: 'Source-bound read-only renderer; creative geometry is non-authoritative.' },
    views,
    verification: { mechanical: 'UNKNOWN', browser: 'NOT_RUN',
      semantic: 'NOT_RUN', native_consumer: 'NOT_RUN' },
    permissions: { dispatch: false, review_effect: false, deployment: false, train: false },
  };
}
