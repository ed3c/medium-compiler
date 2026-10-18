import {createFileRoute} from '@tanstack/react-router'
import {useEffect,useMemo,useState} from 'react'
import {inspectLayer,projectViewEnv,readReviewedEpisode} from '../viewenv.mjs'
import '../viewenv.css'

export const Route=createFileRoute('/viewenv')({
  validateSearch:(raw:Record<string,unknown>)=>({
    episode:typeof raw.episode==='string'?raw.episode:''
  }),
  component:ViewEnv
})
type Layer='actual'|'proposed'|'replay'

function ViewEnv(){
  const {episode}=Route.useSearch()
  const [raw,setRaw]=useState<unknown>(null)
  const [error,setError]=useState('')
  const [layer,setLayer]=useState<Layer>('actual')
  const [focus,setFocus]=useState('')
  useEffect(()=>{
    setRaw(null);setLayer('actual');setFocus('');setError('')
    if(!episode)return
    const controller=new AbortController()
    readReviewedEpisode(episode,window.location.origin,{signal:controller.signal})
      .then(v=>{if(!controller.signal.aborted)setRaw(v)})
      .catch(e=>{if(!controller.signal.aborted)setError(String(e))})
    return()=>controller.abort()
  },[episode])
  const scene=useMemo(()=>projectViewEnv(raw),[raw])
  const inspected=inspectLayer(scene,layer)
  const laneRefs=inspected.refs
  const cards=[
    ['Task / Dataset',scene.episode?.task_ref],
    ['Harness candidate',scene.harness?.candidate_ref],
    ['Environment',scene.episode?.environment_ref],
    ['Execution / Actions',scene.actions.length?scene.actions.length+' original refs':null],
    ['Observation',scene.observations.length?scene.observations.length+' original refs':null],
    ['Verification',scene.verification?.verifier_ref],
    ['Reward',scene.reward?.status==='observed'?String(scene.reward.value):null],
    ['Termination',scene.termination?.status==='unknown'?null:scene.termination?.status]
  ]
  return <main className="shell ve-shell">
    <header className="masthead">
      <div className="mark"><span className="mark-icon">V</span><span>VIEWENV / LAB</span></div>
      <nav className="mast-actions"><a href="/">← Loop Workbench</a><span className="mode">DESIGN-TIME / READ-ONLY</span></nav>
    </header>
    <div className="intro ve-intro"><div className="eyebrow">NeoWeaver / Environment compiler / Harness²</div>
      <h1>A visible system.<br/><em>A verifiable action.</em></h1>
      <p>One environment domain. Three independent evidence layers. Every node and reward must trace to its original Owner.</p>
    </div>
    <section className="ve-statusline" aria-label="Source status">
      <span>EPISODE <strong>{scene.episode?.episode_ref||'NOT CONNECTED'}</strong></span>
      <span>VERIFIER <strong>{scene.verification?.status||'NOT RUN'}</strong></span>
      <span>REWARD <strong>{scene.reward?.status||'UNKNOWN'}</strong></span>
      <span>AUTHORITY <strong>NONE / DISPLAY ONLY</strong></span>
    </section>
    <section className="ve-main" aria-label="ViewEnv layers">
      <aside className="ve-workflow">
        <div className="eyebrow">01 / Execution planes</div>
        <h2>Evidence, not illusion.</h2>
        <p>Choose a layer. No selection creates an original action, a missing observation, or reward.</p>
        {(['actual','proposed','replay'] as Layer[]).map((name,i)=><button key={name}
          className={'ve-choice '+(layer===name?'selected':'')}
          onClick={()=>{setLayer(name);setFocus('')}}
          aria-pressed={layer===name}>
          <span>0{i+1} / {name.toUpperCase()}</span>
          <strong>{name==='actual'?'Native truth':name==='proposed'?'Harness hypothesis':'Recorded episode'}</strong>
          <small>{name==='actual'?'Original Owner and Verifier':
            name==='proposed'?'Propose → Probe → Compose':'Action / Observation history'}</small>
        </button>)}
        <div className="ve-border-note">OpenEnv + Verifiers interface first. ORS / NeMo Gym are reserved adapters; Training has a separate Owner.</div>
      </aside>
      <section className="ve-scene" aria-label="Source-bound environment model">
        <div className="ve-scene-head"><span className="eyebrow">02 / Interactive environment topology</span>
          <span className="ve-scene-pill">{inspected.status}</span></div>
        <div className="ve-stage"><div className="ve-stage-grid" aria-hidden="true"></div>
          {cards.map(([title,content],i)=><button key={title} className={'ve-unit '+(focus===title?'active':'')} onClick={()=>setFocus(String(title))} aria-pressed={focus===title}>
            <span className="ve-iso" aria-hidden="true"><span></span></span>
            <span className="ve-unit-type">0{i+1} / {content?'SOURCE REF':'UNOBSERVED'}</span>
            <strong>{title}</strong><small>{content||'UNKNOWN'}</small></button>)}
        </div>
        <div className="ve-footnote">Geometric proximity is illustrative only. There are no inferred causal edges; original DAG and episode receipts remain authoritative.</div>
      </section>
      <aside className="ve-readback" aria-label="Original references">
        <div className="eyebrow">03 / Inspection</div><h2>{focus||layer.toUpperCase()}</h2>
        {error&&<p role="alert">{error}</p>}
        <p className="ve-copy">{scene.message}</p>
        <dl><dt>Source status</dt><dd>{scene.status}</dd>
          <dt>Layer</dt><dd>{layer}</dd><dt>Verification</dt><dd>{scene.verification?.status||'NOT RUN'}</dd>
          <dt>Reward</dt><dd>{scene.reward?.value??'UNKNOWN'}</dd>
          <dt>Termination</dt><dd>{scene.termination?.status||'UNKNOWN'}</dd></dl>
        <div className="ve-refs"><h3>Original references · {laneRefs.length}</h3>
          {laneRefs.length?laneRefs.map((ref,i)=><code key={i}>{ref}</code>):
            <p>There is no original evidence for this layer.</p>}</div>
        <p className="ve-copy">Import disclosure-reviewed data under the pinned same-origin Episode asset path; this page never requests local/private Host material.</p>
      </aside>
    </section>
    <footer><span>VIEWENV / SOURCE → ACTION → OBSERVATION → VERIFICATION</span>
      <span>Actual ≠ Proposed ≠ Replay</span></footer>
  </main>
}
