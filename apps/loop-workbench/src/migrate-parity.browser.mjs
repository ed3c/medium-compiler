/** Two distinct source/consumer Chromium observations for AIFS and SeeCode.
 * Compares a direct original renderer with its sandboxed target adapter.
 * Source/Browser parity for selected fixtures only; NOT a fresh native eval.
 */
import {chromium} from 'playwright'
import {readFile} from 'node:fs/promises'
import assert from 'node:assert/strict'
const base='http://127.0.0.1:3107'
const seeCodeFile=process.argv[2]
if(!seeCodeFile)throw Error('EXPECTED_PINNED_SEECODE_HTML')
const seecodeHtml=await readFile(seeCodeFile,'utf8')
if(!seecodeHtml.toLowerCase().includes('<html'))throw Error('SEECODE_INPUT_NOT_HTML')
const browser=await chromium.launch({headless:true})
const env={viewport:{width:980,height:850},reducedMotion:'reduce'}
function sorted(arr){return arr.sort((a,b)=>a.localeCompare(b))}
async function readFigure(host,name) {
 const target=host.locator('.lesson-figure[data-figure="'+name+'"]')
 await target.locator('svg').waitFor({timeout:15000})
 const metadata=target.locator('.lf-meta').first()
 const before=(await metadata.innerText()).trim()
 const ctl=target.locator('input[type=range]').first()
 if(!await ctl.count())throw Error('NO_INTERACTIVE_INPUT:'+name)
 await ctl.evaluate(node=>{
  const low=Number(node.min),high=Number(node.max),step=Number(node.step||1),val=Number(node.value)
  node.value=String(val+step<=high?val+step:Math.max(low,val-step))
  node.dispatchEvent(new Event('input',{bubbles:true}))
  node.dispatchEvent(new Event('change',{bubbles:true}))
 })
 const after=(await metadata.innerText()).trim()
 if(before===after)throw Error('NOT_RECOMPUTED:'+name)
 return {before,after}
}
async function observeSeeCode(host) {
 const nodeIds=sorted(await host.locator('[data-sc-node]').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('data-sc-node')||'')))
 const edgeIds=sorted(await host.locator('[data-sc-edge]').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('data-sc-edge')||'')))
 const stepCount=await host.locator('[data-sc-steps]').first().getAttribute('data-sc-steps')
 if(nodeIds.length!==4||edgeIds.length!==3)throw Error('SEECODE_FIXTURE_SHAPE_DRIFT')
 const next=host.locator('[data-sc-action="next"]')
 await next.click()
 const active=await host.locator('svg.sc-stepping').count()
 if(!active)throw Error('SEECODE_STEP_BROKEN')
 return {nodeIds,edgeIds,stepCount,stepping:active>0}
}
async function installFixture(page) {
 await page.route('**/__migration_seecode_baseline__.html',route=>route.fulfill({
  status:200,contentType:'text/html;charset=utf-8',body:seecodeHtml}))
}
const independentErrors=[]
try{
 const original=await browser.newContext(env)
 const migrated=await browser.newContext(env)
 const originalA=await original.newPage(),migratedA=await migrated.newPage()
 for(const pg of [originalA,migratedA])pg.on('pageerror',e=>independentErrors.push(e.message))
 await originalA.goto(base+'/aifs/figure-lab.html',{waitUntil:'domcontentloaded'})
 await migratedA.goto(base+'/figures',{waitUntil:'domcontentloaded'})
 const app=migratedA.frameLocator('iframe[title="AIFS source-preserved interactive figures"]')
 const names=['vector-projection','matrix-transform','demo-token-bucket']
 const aifsControl=[],aifsTreatment=[]
 for(const name of names){
  aifsControl.push(await readFigure(originalA,name))
  aifsTreatment.push(await readFigure(app,name))
 }
 assert.deepEqual(aifsTreatment,aifsControl,'AIFS Consumer behavior drift (DOM+sliders)')
 assert.equal(await migratedA.locator('iframe').first().getAttribute('sandbox'),'allow-scripts')
 const originalS=await original.newPage(),migratedS=await migrated.newPage()
 for(const p of [originalS,migratedS]){
  p.on('pageerror',e=>independentErrors.push(e.message))
  await installFixture(p)
 }
 await originalS.goto(base+'/__migration_seecode_baseline__.html',{waitUntil:'domcontentloaded'})
 await migratedS.goto(base+'/figures',{waitUntil:'domcontentloaded'})
 await migratedS.evaluate(()=>{
  const f=document.createElement('iframe')
  f.setAttribute('data-migration-seecode','1')
  f.setAttribute('sandbox','allow-scripts')
  f.setAttribute('src','/__migration_seecode_baseline__.html')
  f.style.width='900px'
  f.style.height='800px'
  document.body.appendChild(f)
 })
 const control=await observeSeeCode(originalS)
 const wrapped=await observeSeeCode(migratedS.frameLocator('iframe[data-migration-seecode]'))
 assert.deepEqual(wrapped,control,'SeeCode sandboxed Consumer parity drift')
 assert.notDeepEqual({...wrapped,edgeIds:wrapped.edgeIds.slice(1)},control,
   'Planted removed-edge control was not detected')
 if(independentErrors.length)throw Error('PARITY_BROWSER_ERRORS: '+independentErrors.join('|'))
 console.log(JSON.stringify({status:'SOURCE_BROWSER_DIFFERENTIAL_PASS',source_count:2,
  aifs_figures:3,seecode_nodes:4,seecode_edges:3,planted_removed_edge:'REJECTED',
  native_agent:'NOT_RUN',environment:'Chromium',production:'NOT_DEPLOYED'}))
}finally{await browser.close()}
