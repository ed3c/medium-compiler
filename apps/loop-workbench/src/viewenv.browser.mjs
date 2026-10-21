/** Bounded real Chromium smoke: preview only; no Run or Provider mutation. */
import { chromium } from 'playwright'
import { mkdir } from 'node:fs/promises'
import {createHash} from 'node:crypto'
const url=process.env.VIEWENV_TEST_URL || 'http://127.0.0.1:3107/viewenv'
const browser=await chromium.launch({headless:true})
try{
  await mkdir('test-artifacts',{recursive:true})
  const page=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce'})
  const errors=[]
  page.on('pageerror',e=>errors.push(e.message))
  const response=await page.goto(url,{waitUntil:'networkidle'})
  if(response?.status()!==200)throw new Error('ViewEnv did not serve HTTP 200')
  await page.getByText('A visible system.').waitFor()
  await page.getByText('NOT CONNECTED').first().waitFor()
  await page.getByRole('button',{name:/PROPOSED/}).count() // no source-labeled action is executed
  await page.getByRole('button',{name:/Harness hypothesis/}).click()
  await page.getByText('Proposed', {exact:true}).count()
  await page.screenshot({path:'test-artifacts/viewenv-desktop.png',fullPage:true})
  await page.setViewportSize({width:390,height:844})
  await page.screenshot({path:'test-artifacts/viewenv-mobile.png',fullPage:true})
  const badOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)
  if(badOverflow)throw new Error('mobile horizontal overflow')
  await page.keyboard.press('Tab')
  const focused=await page.evaluate(()=>Boolean(document.activeElement && document.activeElement!==document.body))
  if(!focused)throw new Error('no keyboard focus')

  // A source-only browser fixture tests the canonical adapter, not native
  // acceptance or any originally observed provider transfer.
  const fakeRun = 'local-browser-fixture'
  const originalRequest = JSON.stringify({goal:'Inspect a source-backed example'})
  const artifactBytes=Buffer.from(originalRequest)
  const artifactSha=createHash('sha256').update(artifactBytes).digest('hex')
  const graph = {
    objects:[{id:'loop-owner',namespace:'soodles.loop',label:'LoopManager',kind:'owner',scope:'shared',
      source_artifact_ids:[]}],
    ports:[],
    repositories:[{id:'fixture-repo',label:'Fixture only',root:'redacted',revision:null,
      index_status:'unknown',tracked_files:[],selected_files:[],gaps:[]}],
    artifacts:[{id:'request-original',repository_id:'fixture-repo',role:'loop_request',
      format:'application/json',authority:'source',knowledge_role:'unknown',scope:fakeRun,
      status:'available',public_sha256:artifactSha,public_bytes:artifactBytes.length,source:null}],
    nodes:[{id:'source-occurrence',run_id:fakeRun,repository_id:'fixture-repo',
      object_id:'loop-owner',kind:'cli',label:'Original Goal (fixture)',stage_id:null,
      identity:{status:'unknown',invocation_id:null,attempt_id:null,session_id:null,locator:null},
      status:{execution:'unknown',transfer:'unknown',acceptance:'unknown'},
      input_artifact_ids:[],output_artifact_ids:['request-original'],evidence_artifact_ids:[]}],
    edges:[],findings:[],metrics:[]
  }
  const snapshot={schema_version:2,snapshot_sha256:'a'.repeat(64),content_urls:{'request-original':'/assets/loop-data/'+'a'.repeat(64)+'/artifacts/'+artifactSha+'.txt'},runs:[{id:fakeRun,repository:'fixture/browser',
    mode:'outer-only',status:'unknown',stages:[],cards:[],notes:[],breakpoints:[],
    resources:[],next:null}],graph}
  const manifest='/assets/loop-data/'+'a'.repeat(64)+'/graph.json'
  await page.route('**/assets/loop-data/**',route=>route.fulfill({
    status:200,contentType:'application/json',body:route.request().url().endsWith('.txt') ? originalRequest : JSON.stringify(snapshot)
  }))
  const panoramaResponse=await page.goto('http://127.0.0.1:3107/panorama?manifest='+encodeURIComponent(manifest),
    {waitUntil:'networkidle'})
  if(panoramaResponse?.status()!==200)throw new Error('Canonical panorama HTTP error')
  await page.getByRole('heading',{name:/One machine/}).waitFor()
  await page.getByRole('combobox',{name:'立體視圖執行範圍'}).selectOption(fakeRun)
  await page.getByRole('button',{name:/Human Intent.*原來源/}).click()
  await page.getByText('原始 Carrier · loop_request').waitFor()
  const nativeEdges=await page.locator('.li-observed-wire, .li-observed').count()
  if(nativeEdges>0)throw new Error('fabricated native handoff in source-only fixture')
  await page.screenshot({path:'test-artifacts/canonical-panorama-source-only.png',fullPage:true})
  await page.setViewportSize({width:390,height:844})
  await page.screenshot({path:'test-artifacts/canonical-panorama-mobile.png',fullPage:true})

  if(errors.length)throw new Error('browser uncaught errors: '+errors.join(','))
  console.log('ViewEnv browser smoke PASS: desktop/mobile, reduced motion, layers, keyboard')
}finally{await browser.close()}
