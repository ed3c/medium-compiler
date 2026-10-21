/** Genuine Chromium browser checks against immutable upstream LF runtime in a sandbox iframe. */
import {chromium} from 'playwright'
import {mkdir} from 'node:fs/promises'
const browser=await chromium.launch({headless:true})
try {
 const context=await browser.newContext({viewport:{width:1300,height:900},reducedMotion:'reduce'})
 const page=await context.newPage()
 const errors=[],requests=[]
 page.on('pageerror',e=>errors.push(String(e)))
 page.on('request',r=>{
  const u=new URL(r.url())
  if(u.protocol==='http:'||u.protocol==='https:'){
   if(u.origin!=='http://127.0.0.1:3107')requests.push(u.href)
  }
 })
 await page.goto('http://127.0.0.1:3107/figures',{waitUntil:'domcontentloaded'})
 const f=page.frameLocator('iframe[title="AIFS source-preserved interactive figures"]')
 for(const name of ['vector-projection','matrix-transform','demo-token-bucket']){
  await f.locator('.lesson-figure[data-figure="'+name+'"][data-lf-mounted="1"] svg').waitFor({timeout:18000})
 }
 const vector=f.locator('.lesson-figure[data-figure="vector-projection"]')
 const oldText=await vector.locator('.lf-meta').first().innerText()
 const slider=vector.locator('input[type=range]').first()
 await slider.evaluate(el=>{
  const v=Number(el.value),lo=Number(el.min),hi=Number(el.max),step=Number(el.step||1)
  el.value=String(v+step<=hi?v+step:Math.max(lo,v-step))
  el.dispatchEvent(new Event('input',{bubbles:true}))
 })
 await vector.locator('.lf-meta').first().waitFor({state:'visible'})
 const newText=await vector.locator('.lf-meta').first().innerText()
 if(oldText===newText)throw Error('SOURCE_MATH_INPUT_DID_NOT_RECOMPUTE')
 const frame=await page.locator('iframe').getAttribute('sandbox')
 if(frame!=='allow-scripts')throw Error('IFRAME_AUTHORITY_ESCALATION')
 await mkdir('test-artifacts',{recursive:true})
 await page.screenshot({path:'test-artifacts/aifs-figure-lab-desktop.png',fullPage:true})
 await page.setViewportSize({width:390,height:844})
 await page.screenshot({path:'test-artifacts/aifs-figure-lab-mobile.png',fullPage:true})
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('MOBILE_OVERFLOW')
 if(requests.length)throw Error('EXTERNAL_NETWORK: '+requests.join(' | '))
 if(errors.length)throw Error('BROWSER_JS_ERRORS: '+errors.join(' | '))
 console.log(JSON.stringify({status:'AIFS_SOURCE_PRESERVED_BROWSER_OK',modules:3,interactions:1,
   original_computation:true,source_only:true,native_agent:'NOT_RUN',production:'NOT_DEPLOYED'}))
}finally{await browser.close()}
