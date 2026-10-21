/** Actual isolated SeeCode HTML browser smoke: static fixture only. */
import {chromium} from 'playwright'
import {readFile,mkdir} from 'node:fs/promises'
import {pathToFileURL} from 'node:url'
import {resolve} from 'node:path'
const html=resolve(process.argv[2]||'')
const input=await readFile(html,'utf8')
if(!input.includes('<html')&&!input.includes('<!doctype'))throw Error('SEECODE_HTML_NOT_GENERATED')
const browser=await chromium.launch({headless:true})
try {
 const page=await browser.newPage({viewport:{width:1280,height:800},reducedMotion:'reduce'})
 const errors=[]
 const outbound=[]
 page.on('pageerror',e=>errors.push(String(e)))
 page.on('request',req=>{if(/^https?:/.test(req.url()))outbound.push(req.url())})
 await page.route(/^https?:\/\//,request=>request.abort())
 await page.goto(pathToFileURL(html).href,{waitUntil:'domcontentloaded'})
 await page.getByText('Source to reviewed figure',{exact:false}).first().waitFor({timeout:12000})
 const text=await page.locator('body').innerText()
 for(const word of ['Source','Diagram Spec','Review','Preview']){
  if(!text.includes(word))throw Error('DIAGRAM_CONTENT_MISSING: '+word)
 }
 const next=page.locator('[data-sc-action="next"]')
 if(await next.count()){
  await next.click()
  const stepping=await page.locator('svg[data-sc-motion]').first().evaluate(el=>el.classList.contains('sc-stepping'))
  if(!stepping)throw Error('STEPS_NOT_INTERACTIVE')
 }
 const firstNode=page.locator('[data-sc-node]').first()
 if(await firstNode.count()){
  await firstNode.click()
  await page.getByText('Node passport',{exact:false}).first().waitFor({timeout:5000})
 }
 await page.keyboard.press('Tab')
 const focus=await page.evaluate(()=>document.activeElement?.tagName||'UNKNOWN')
 await mkdir('test-artifacts',{recursive:true})
 await page.screenshot({path:'test-artifacts/seecode-editorial-desktop.png',fullPage:true})
 await page.setViewportSize({width:390,height:844})
 await page.screenshot({path:'test-artifacts/seecode-editorial-mobile.png',fullPage:true})
 if(outbound.length)throw Error('EXTERNAL_NETWORK_REQUEST_REFUSED: '+outbound.join(' | '))
 if(errors.length)throw Error('DIAGRAM_PAGE_ERROR: '+errors.join(' | '))
 console.log(JSON.stringify({status:'SEECODE_ACTUAL_CHROMIUM_SMOKE',content:true,focus,
  source:'fixture only',native_agent_acceptance:'NOT_RUN',production:'NOT_DEPLOYED'}))
}finally{await browser.close()}
