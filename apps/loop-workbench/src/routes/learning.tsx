import {createFileRoute} from '@tanstack/react-router'
import {useEffect,useState} from 'react'
import {PROBLEMS,progress} from '../learning-domain.mjs'
import type {openLearningStore} from '../learning-store'
import '../learning.css'
type Store=Awaited<ReturnType<typeof openLearningStore>>
type Attempt={id:string;problem_id:string;code:string;timestamp:number;status:string;
 passed_cases:number;total_cases:number;oracle:string}
export const Route=createFileRoute('/learning')({component:Learning})
function download(name:string,blob:Blob){
 const url=URL.createObjectURL(blob)
 const link=document.createElement('a');link.href=url;link.download=name
 link.click();setTimeout(()=>URL.revokeObjectURL(url),1000)
}
function Learning(){
 const [status,setStatus]=useState('INITIALIZING OPFS')
 const [store,setStore]=useState<Store|null>(null)
 const [attempts,setAttempts]=useState<Attempt[]>([])
 const [selected,setSelected]=useState(PROBLEMS[0].id)
 const [code,setCode]=useState(PROBLEMS[0].starter)
 const [busy,setBusy]=useState(false)
 const [error,setError]=useState('')
 const [last,setLast]=useState('')
 useEffect(()=>{
  let disposed=false;let opened:Store|null=null
  import('../learning-store').then(m=>m.openLearningStore()).then(async db=>{
   opened=db;if(disposed){await db.close();return}
   setStore(db);setAttempts(await db.list());setStatus('PERSISTENT · OPFS')
  }).catch(e=>{if(!disposed){setStatus('BLOCKED · OPFS NOT VERIFIED');setError(String(e))}})
  return ()=>{disposed=true;if(opened)void opened.close()}
 },[])
 const choices=PROBLEMS.map(p=>({p,attempts:attempts.filter(a=>a.problem_id===p.id)}))
 const current=PROBLEMS.find(x=>x.id===selected)??PROBLEMS[0]
 async function save(){
  if(!store)return
  setBusy(true);setError('')
  try{
   await store.add({id:crypto.randomUUID(),problem_id:current.id,code,
    timestamp:Date.now(),status:'not_run',passed_cases:0,total_cases:0,oracle:'not_observed'})
   setAttempts(await store.list());setLast('Draft saved to DuckDB OPFS. No Python test executed.')
  }catch(e){setError(String(e))}finally{setBusy(false)}
 }
 async function exportFile(kind:'json'|'duckdb'){
  if(!store)return
  try{
   if(kind==='json')download('learning-progress.json',new Blob([await store.exportJson()],{type:'application/json'}))
   else download('medium_learning_v1.duckdb',await store.exportDbFile())
  }catch(e){setError(String(e))}
 }
 async function importFile(file:File|undefined){
  if(!file||!store)return
  setBusy(true);setError('')
  try{await store.importJson(await file.text());setAttempts(await store.list());setLast('Imported verified-shape local records (browser-untrusted).')}
  catch(e){setError(String(e))}finally{setBusy(false)}
 }
 const totals=progress(attempts)
 return <main className="learn-shell">
  <header className="learn-top"><a href="/">← LOOP WORKBENCH</a><span>MEDIUM / EXPLORABLE LEARNING</span><a href="/panorama">EVIDENCE VIEW ↗</a></header>
  <section className="learn-intro"><span className="learn-overline">RESEARCH NOTEBOOK · LOCAL FIRST</span>
   <h1>Learn the mechanism.<br/><em>Keep the evidence.</em></h1>
   <p>Small source-authored Python challenges, DuckDB-Wasm storage and exported local records. No account, cloud synchronization or fabricated Agent success.</p>
   <div className="learn-state"><b>{status}</b><span>{totals.filter(x=>x.locally_passed).length} browser-untrusted passes · {attempts.length} drafts/attempts</span></div>
  </section>
  <section className="learn-workspace">
   <aside className="learn-menu"><h2>01 / Problemset</h2>
    {choices.map(({p,attempts:seen})=><button key={p.id} aria-current={selected===p.id?'page':undefined} onClick={()=>{setSelected(p.id);setCode(p.starter);setLast('')}}>
      <b>{p.title}</b><small>{seen.length} local records</small></button>)}
    <p>Learning progress is intentionally not a trusted grading receipt.</p>
   </aside>
   <article className="learn-editor"><span className="learn-overline">02 / Python laboratory</span>
     <h2>{current.title}</h2><p>Implement <code>{current.entry}</code>. Edit and save a draft locally.</p>
     <label htmlFor="learn-code">Python source</label>
     <textarea id="learn-code" spellCheck={false} value={code} onChange={e=>setCode(e.target.value)} rows={11} maxLength={32768}/>
     <div className="learn-actions"><button type="button" onClick={save} disabled={!store||busy}>Save unverified draft</button>
       <button type="button" disabled title="Requires separately verified no-network Python sandbox">Run Python — gated</button></div>
     <p role="status">{last}</p>{error&&<p role="alert">{error}</p>}
     <p className="learn-warning">Pyodide execution and Browser Grader remain gated pending independently tested network-isolated sandbox. Saving a draft is not passing an exercise.</p>
   </article>
   <aside className="learn-export"><h2>03 / Your data</h2><p>DuckDB-Wasm persists attempts in this origin’s OPFS. Browser eviction or clearing site data can delete them.</p>
     <button onClick={()=>exportFile('json')} disabled={!store}>Export JSON</button>
     <button onClick={()=>exportFile('duckdb')} disabled={!store}>Export DuckDB for Agent CLI</button>
     <label htmlFor="learn-import">Import local JSON records</label>
     <input id="learn-import" type="file" accept="application/json,.json" disabled={!store||busy} onChange={e=>{void importFile(e.target.files?.[0]);e.target.value=''}}/>
     <p>CLI Agent Mode reads only an explicit exported file. It does not have browser OPFS access.</p>
   </aside>
  </section>
  <footer className="learn-footer">SOURCE-BOUND PRACTICE · NO NATIVE AGENT RECEIPT · NO PRODUCTION DEPLOYMENT</footer>
 </main>
}
