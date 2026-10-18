import { createFileRoute } from '@tanstack/react-router'
import { useEffect, useMemo, useState } from 'react'
import { nativeClaim, projectWorkbench, safeManifest, selectRun } from '../workbench.mjs'

export const Route = createFileRoute('/')({
  validateSearch: (search: Record<string, unknown>) => ({
    manifest: typeof search.manifest === 'string' ? search.manifest : '',
  }),
  component: LoopWorkbench,
})

type Phase = 'all' | 'observed' | 'failed' | 'unknown'

function LoopWorkbench() {
  const { manifest } = Route.useSearch()
  const [raw, setRaw] = useState<unknown>(null)
  const [loadError, setLoadError] = useState('')
  const [runId, setRunId] = useState('')
  const [phase, setPhase] = useState<Phase>('all')
  const [focus, setFocus] = useState('')
  const [tab, setTab] = useState<'execution' | 'environment' | 'comparison'>('execution')
  useEffect(() => {
    if (!manifest) { setRaw(null); setLoadError(''); return }
    const safe = safeManifest(manifest, window.location.origin)
    if (!safe) { setRaw(null); setLoadError('REFUSED: 非同源、非版本化的公開 Snapshot'); return }
    const controller = new AbortController()
    setRaw(null); setLoadError('')
    fetch(safe, { credentials:'omit', redirect:'error', signal:controller.signal })
      .then(res => { if (!res.ok) throw new Error('Snapshot HTTP ' + res.status); return res.json() })
      .then(value => { if (!controller.signal.aborted) setRaw(value) })
      .catch(error => { if (!controller.signal.aborted) setLoadError(String(error)) })
    return () => controller.abort()
  }, [manifest])
  const view = useMemo(() => projectWorkbench(raw), [raw])
  const scope = useMemo(() => selectRun(view, runId), [view, runId])
  const currentNodes = scope.nodes.filter(node => phase === 'all' || (phase === 'observed' ?
    node.identity === 'observed' : phase === 'failed' ?
      scope.findings.some(f => f.status === 'failed' && f.run_id === node.run_id) :
      node.identity !== 'observed'))
  const selectedNode = scope.nodes.find(n => n.id === focus)
  const selectedEdge = scope.edges.find(e => e.id === focus)
  const currentRun = view.runs.find(r => r.id === runId)
  const failures = scope.findings.filter(f => f.status === 'failed')
  const known = scope.edges.filter(e => nativeClaim(e) === 'OBSERVED_HANDOFF')

  return <main className="shell">
    <header className="masthead">
      <div className="mark"><span className="mark-icon">L<span className="mark-node">●</span></span><span>LOOP / WORKBENCH</span></div>
      <div className="mast-actions"><span className="mode">READ ONLY · SOURCE BOUND</span><a href="https://github.com/ed3c/medium-compiler" rel="noreferrer">Source <span aria-hidden="true">↗</span></a></div>
    </header>
    <div className="intro"><div className="eyebrow">Agent systems / Evidence atlas · Preview architecture</div>
      <h1>Where a task becomes <em>observable.</em></h1>
      <p>From the original Goal to runtime handoffs, evidence gaps and replay eligibility. Geometry explains sources; it never authorizes execution.</p>
    </div>
    <div className="workspace">
      <aside className="sidebar">
        <h2>01 / Workspace</h2><p className="muted">Selected source, not an execution plan.</p>
        <button className={!runId ? 'selector active' : 'selector'} onClick={() => {setRunId('');setFocus('')}}>All published runs <span>{view.runs.length}</span></button>
        {view.runs.map(r => <button key={r.id} className={runId === r.id ? 'selector active' : 'selector'} onClick={() => {setRunId(r.id);setFocus('')}}>
          <strong>{r.repository}</strong><small>{r.mode} / {r.id.slice(0,10)}</small></button>)}
        <div className="side-note"><div className="eyebrow">Trust boundary</div>
          <p>Cloud content must be disclosure-reviewed, versioned and same-origin. No Host RPC or hidden replay on selection.</p></div>
      </aside>
      <section className="central" aria-label="Execution workspace">
        <div className="section-head"><div><span className="eyebrow">02 / Causal evidence</span><h2>{currentRun?.repository || 'Cross-repository topology'}</h2></div><span className="mini">Observed ≠ accepted</span></div>
        <div className="metrics">
          <div><strong>{scope.nodes.length}</strong><span>Original occurrences</span></div>
          <div><strong>{known.length}</strong><span>Current handoffs</span></div>
          <div><strong>{failures.length}</strong><span>Known failures</span></div>
          <div><strong>UNKNOWN</strong><span>Whole-goal acceptance</span></div>
        </div>
        <div className="tabs" role="tablist" aria-label="Workbench views">
          {(['execution','environment','comparison'] as const).map(value =>
            <button type="button" role="tab" aria-selected={tab===value} key={value} onClick={()=>setTab(value)}>
              {value==='execution'?'Execution DAG':value==='environment'?'Environment model':'Paired comparison'}
            </button>)}
        </div>
        {tab === 'execution' && <div className="scene">
          <div className="scene-toolbar"><span>ORIGINAL OCCURRENCES</span><label>Filter <select value={phase} onChange={e => setPhase(e.target.value as Phase)}>
            <option value="all">All</option><option value="observed">Observed identity</option>
            <option value="failed">Runs with failures</option><option value="unknown">Unknown identity</option>
          </select></label></div>
          {scope.nodes.length ? <div className="machine-grid">
            {currentNodes.map((n,index)=><button key={n.id} className={focus===n.id?'machine selected':'machine'} onClick={()=>setFocus(n.id)}>
              <span className="machine-top"><span>0{(index+1)%10}</span><span className={n.identity==='observed'?'light known':'light'}></span></span>
              <span className="machine-figure" aria-hidden="true"><span className="machine-top-plane"></span><span className="machine-cube"></span><span className="machine-plinth"></span></span>
              <strong>{n.label}</strong><small>{n.kind} · {n.execution}</small></button>)}
          </div> : <div className="empty"><div className="empty-symbol" aria-hidden="true">◇</div><strong>No original execution occurrences</strong>
            <p>{loadError || (manifest ? 'The inspected snapshot is missing or has no eligible nodes.' : 'Select a reviewed public snapshot via the manifest URL parameter. No sample execution is invented.')}</p></div>}
          <div className="handoffs"><h3>Recorded handoffs</h3>
            {scope.edges.length ? scope.edges.map(e=><button key={e.id} className="handoff" onClick={()=>setFocus(e.id)}>
              <span>{e.from} <span className="arrow">→</span> {e.to}</span>
              <span className={nativeClaim(e)==='FAILED'?'failure':nativeClaim(e)==='OBSERVED_HANDOFF'?'verified':'muted'}>{nativeClaim(e)}</span>
            </button>) : <p className="muted">No observed relation in the current source scope.</p>}</div>
        </div>}
        {tab === 'environment' && <div className="env-grid">
          {['Task / Dataset','Action Space','Observations','Execution Backend','State','Reward / Rubric','Termination','Replay / Hard Gates'].map((title,i)=>
            <div className="env-cell" key={title}><span className="eyebrow">{String(i+1).padStart(2,'0')}</span><strong>{title}</strong><span>NOT CONNECTED · NeoWeaver adapter pending</span></div>)}
          <p className="muted env-note">Inspired by FineEnvs environment components. These cards are unpopulated contracts—not completed rollouts or training evidence.</p>
        </div>}
        {tab === 'comparison' && <div className="comparison"><div><span className="eyebrow">BASELINE H0</span><h3>No admitted replay</h3><p>Immutable task, environment, seed policy and original oracle required.</p></div><span className="compare-mark">↔</span><div><span className="eyebrow">CANDIDATE H1</span><h3>NOT RUN</h3><p>No reward, regression result or harness improvement is claimed.</p></div></div>}
        {failures.length > 0 && <section className="failures"><h3>Confirmed failure history</h3>{failures.map(f=><p key={f.id}><strong>{f.kind}</strong> — {f.message}</p>)}</section>}
      </section>
      <aside className="inspector">
        <div className="section-head"><div><span className="eyebrow">03 / Inspect</span><h2>Original readback</h2></div></div>
        {selectedNode ? <><h3>{selectedNode.label}</h3><dl><dt>Occurrence</dt><dd>{selectedNode.id}</dd><dt>Execution</dt><dd>{selectedNode.execution}</dd><dt>Transfer</dt><dd>{selectedNode.transfer}</dd><dt>Acceptance</dt><dd>{selectedNode.acceptance}</dd><dt>Identity</dt><dd>{selectedNode.identity}</dd><dt>Inputs</dt><dd>{selectedNode.inputs.length} refs</dd><dt>Outputs</dt><dd>{selectedNode.outputs.length} refs</dd><dt>Evidence</dt><dd>{selectedNode.evidence.length} refs</dd></dl></>
          : selectedEdge ? <><h3>{selectedEdge.label}</h3><dl><dt>Status</dt><dd>{selectedEdge.status}</dd><dt>Validity</dt><dd>{selectedEdge.validity}</dd><dt>Kind</dt><dd>{selectedEdge.kind}</dd><dt>Scope</dt><dd>{selectedEdge.scope}</dd></dl></>
          : <div className="inspector-empty"><span aria-hidden="true">◎</span><p>Choose a machine or handoff to inspect its original status. Labels are inert and all absent source contents stay UNKNOWN.</p></div>}
        <div className="inspector-bottom"><h3>Evidence policy</h3><p>Current transfers, historical failures, scoped semantic review and whole-goal acceptance remain separate outcomes.</p></div>
      </aside>
    </div>
    <footer><span>LOOP WORKBENCH / TANSTACK START PREVIEW</span><span>Learning, execution, verification — separate planes</span></footer>
  </main>
}
