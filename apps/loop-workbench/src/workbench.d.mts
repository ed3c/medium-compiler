export interface Run {
  id: string; repository: string; status: string; mode: string
}
export interface Occurrence {
  id: string; run_id: string; kind: string; label: string; execution: string;
  transfer: string; acceptance: string; identity: string;
  inputs: string[]; outputs: string[]; evidence: string[]
}
export interface Handoff {
  id: string; run_id: string; from: string; to: string;
  status: string; validity: string; kind: string; scope: string; label: string
}
export interface Finding { id: string; run_id: string; status: string; kind: string; message: string }
export interface Metric {
  id: string; run_id: string; name: string; status: string; value: number | null; unit: string
}
export interface Repo { id: string; label: string; index: string; gaps: string[] }
export interface View {
  valid: boolean; reason: string | null; runs: Run[]; nodes: Occurrence[];
  edges: Handoff[]; findings: Finding[]; metrics: Metric[]; repositories: Repo[]
}
export function safeManifest(input: unknown, origin: string): string | null
export function projectWorkbench(data: unknown): View
export function selectRun(view: View, runId: string): {
  run: Run | null; nodes: Occurrence[]; edges: Handoff[]; findings: Finding[]; metrics: Metric[]
}
export function nativeClaim(edge: Handoff): 'FAILED' | 'OBSERVED_HANDOFF' | 'UNKNOWN'
export function rlExperimentProjection(episode: unknown): {
  status: string; reward: number | null; termination: string
}
