/** Isolated Rust tsrs WASM smoke. TS7.1-dev, deliberately NOT TS7.0 parity. */
import test from 'node:test'
import assert from 'node:assert/strict'
import {tsc} from '@tsrs/wasm'
test('tsrs 7.1-dev WASM reports a real TS2322 diagnostic on an in-memory fixture',async()=>{
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

test('tsrs 7.1-dev is explicitly not the TypeScript 7.0.2 native parity oracle',async()=>{
 const {readFileSync}=await import('node:fs')
 const pkg=JSON.parse(readFileSync(new URL('../package.json',import.meta.url),'utf8'))
 assert.equal(pkg.devDependencies['@typescript/native'],'npm:typescript@7.0.2')
 assert.match(pkg.devDependencies['@tsrs/wasm'],/ts7\.1\.0-dev\./)
 assert.notEqual(pkg.devDependencies['@tsrs/wasm'],pkg.devDependencies['@typescript/native'])
})
