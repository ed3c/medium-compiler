/** Isolated Rust tsrs WASM smoke. TS7.1-dev, deliberately NOT TS7.0 parity. */
import test from 'node:test'
import assert from 'node:assert/strict'
import {tsc} from '@tsrs/wasm'
test('tsrs WASM computes real stable diagnostic semantics on a small in-memory fixture',async()=>{
 const files={'/src/code.ts':'export const count: number = "wrong";'}
 const result=await tsc(['/src/code.ts','--noEmit','--strict'],{cwd:'/src',files,diagnostics:'json'})
 assert.notEqual(result.exitCode,0)
 assert.ok(Array.isArray(result.diagnostics)&&result.diagnostics.some(d=>d.code===2322),
  JSON.stringify({exitCode:result.exitCode,diagnostics:result.diagnostics?.slice(0,5),stderr:result.stderr}))
 assert.equal(typeof result.memoryBytes,'number')
})
test('tsrs WASM accepts a legitimate neighboring valid program',async()=>{
 const files={'/src/okay.ts':'export const count: number = 42;'}
 const result=await tsc(['/src/okay.ts','--noEmit','--strict'],{cwd:'/src',files,diagnostics:'json'})
 assert.equal(result.exitCode,0,JSON.stringify({diagnostics:result.diagnostics,stderr:result.stderr}))
})
