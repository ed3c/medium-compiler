import {test} from 'node:test'
import assert from 'node:assert/strict'
import {renderMermaidSVG} from 'beautiful-mermaid'
test('pinned Mermaid renderer outputs a real SVG candidate',()=>{
 const sample='flowchart LR\n  A[Goal] --> B{Verify}\n  B -->|yes| C[Readback]'
 const start=performance.now()
 const svg=renderMermaidSVG(sample)
 const ms=performance.now()-start
 assert.equal(typeof svg,'string')
 assert.match(svg,/<svg[\s>]/)
 assert.ok(svg.length>100)
 assert.doesNotMatch(svg,/<script|<foreignObject|javascript:/i)
 console.log(JSON.stringify({bytes:Buffer.byteLength(svg),elapsed_ms:Math.round(ms*100)/100,scope:'one CI fixture, not P95'}))
})
