/** Bounded real Chromium smoke: preview only; no Run or Provider mutation. */
import { chromium } from 'playwright'
import { mkdir } from 'node:fs/promises'
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
  if(errors.length)throw new Error('browser uncaught errors: '+errors.join(','))
  console.log('ViewEnv browser smoke PASS: desktop/mobile, reduced motion, layers, keyboard')
}finally{await browser.close()}
