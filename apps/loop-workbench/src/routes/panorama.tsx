import { createFileRoute } from '@tanstack/react-router'
import { useEffect, useRef, useState } from 'react'
import { safeManifest } from '../workbench.mjs'
import { mountPanorama } from '../../vendor/noodle/loop-panorama.mjs'
import '../../vendor/noodle/loop-panorama.css'

type Scope = { goal: string; runIds: string[] | null }
type Snapshot = { schema_version: number; runs: Array<{ id: string; repository: string; mode: string }>; graph: {
  nodes: unknown[]; edges: unknown[]; findings: unknown[]; metrics: unknown[];
  objects: unknown[]; ports: unknown[]; artifacts: unknown[]; repositories: unknown[]
}}
const isSnapshot = (x: unknown): x is Snapshot => {
  if (!x || typeof x !== 'object') return false
  const v = x as Record<string, unknown>
  const g = v.graph && typeof v.graph === 'object' ? v.graph as Record<string, unknown> : null
  return v.schema_version === 2 && Array.isArray(v.runs) && !!g &&
    ['nodes','edges','findings','metrics','objects','ports','artifacts','repositories']
      .every(key => Array.isArray(g[key]))
}

export const Route = createFileRoute('/panorama')({
  validateSearch: (search: Record<string, unknown>) => ({
    manifest: typeof search.manifest === 'string' ? search.manifest : '',
  }),
  component: CanonicalPanorama,
})

function CanonicalPanorama() {
  const { manifest } = Route.useSearch()
  const element = useRef<HTMLDivElement>(null)
  const [source, setSource] = useState<unknown>(null)
  const [error, setError] = useState('')
  const [scope, setScope] = useState<Scope>({ goal: '', runIds: null })
  useEffect(() => {
    setSource(null); setError(''); setScope({ goal: '', runIds: null })
    if (!manifest) return
    const safe = safeManifest(manifest, window.location.origin)
    if (!safe) { setError('REFUSED: unreviewed or cross-origin source'); return }
    const controller = new AbortController()
    fetch(safe, { credentials: 'omit', redirect: 'error', signal: controller.signal })
      .then(response => {
        if (!response.ok) throw new Error('Snapshot unavailable: ' + response.status)
        return response.json()
      })
      .then(value => { if (!controller.signal.aborted) setSource(value) })
      .catch(cause => { if (!controller.signal.aborted) setError(String(cause)) })
    return () => controller.abort()
  }, [manifest])

  useEffect(() => {
    const root = element.current
    if (!root) return
    root.replaceChildren()
    if (!isSnapshot(source)) return
    const graph = source.graph
    try {
      mountPanorama(root, {
        graph, runs: source.runs, runIds: scope.runIds, goal: scope.goal,
        onScope: (next: Scope) => setScope(next),
        onSelect: () => {}, onFocus: () => {}, onReset: () => {},
        // Only bytes already reviewed and included in this same-origin public
        // snapshot. Never resolve host paths, private capture, or invoke ports.
        readArtifact: async (id: string) => {
          const original = graph.artifacts.find((row: unknown) => {
            return !!row && typeof row === 'object' && (row as {id?: unknown}).id === id
          }) as { status?: string; public_content?: string; content?: string } | undefined
          if (!original) throw new Error('Unregistered original artifact')
          if (typeof original.public_content === 'string') return original.public_content
          if (original.status === 'available' && typeof original.content === 'string') {
            return original.content
          }
          throw new Error('NOT_PUBLIC or source bytes unavailable')
        },
      })
    } catch (cause) {
      root.replaceChildren()
      setError(String(cause))
    }
  }, [source, scope])

  return <main className="shell">
    <header className="masthead"><div className="mark"><span className="mark-icon">L</span>
      <span>VIEWENV / CANONICAL LOOP PANORAMA</span></div>
      <nav className="mast-actions"><a href="/">Workbench</a><a href="/viewenv">Environment Lab</a>
        <span className="mode">READ ONLY · NO HOST CONNECTION</span></nav>
    </header>
    <section className="intro"><div className="eyebrow">Noodle canonical renderer · source-bound comparison</div>
      <h1>One machine.<em> Three evidence layers.</em></h1>
      <p>Green = observed handoff, yellow = applicable contract, dashed yellow = source-grounded hypothesis. A recorded green transfer is not whole-goal acceptance.</p>
    </section>
    {error && <p role="alert">{error}</p>}
    {!source && !error && <section className="empty"><strong>No reviewed public snapshot selected</strong>
      <p>Open a versioned same-origin manifest through the <code>manifest</code> URL parameter. No native execution or source is invented.</p></section>}
    {source && !isSnapshot(source) && <p role="alert">REFUSED: invalid source-bound Graph v2 shape</p>}
    <div ref={element} aria-label="Canonical LoopManager panorama" />
    <footer><span>HUMAN INTENT → SESSION → P-CLASS → CLI / TOOL CALL</span>
      <span>Source rail ≠ execution · Whole Goal UNKNOWN without Owner acceptance</span></footer>
  </main>
}
