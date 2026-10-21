import test from 'node:test'
import assert from 'node:assert/strict'
import {inspect,astFacts,gitBlobSha} from './aifs-code-intel.mjs'

test('real JS and TSX AST: pinned original LF exports, registrations and consumer',()=>{
 const result=inspect()
 assert.equal(result.status,'ready')
 assert.equal(result.source['figures-math.js'].registrations.includes('vector-projection'),true)
 assert.equal(result.source['figures-demo.js'].registrations.includes('demo-token-bucket'),true)
 assert.ok(result.source['lesson-figures.js'].exports.includes('window.mountLessonFigures'))
 assert.ok(result.consumer.tsx.includes('FigureLab'))
 assert.equal(result.authorizes_landing,false)
 assert.deepEqual(result.effects,[])
})
test('AST refuses malformed syntax; no regex-only guessed success',()=>{
 assert.throws(()=>astFacts('wrong.js',Buffer.from('function () {')),/AST_PARSE_REFUSED/)
})
test('source blob binding changes when actual bytes change',()=>{
 const before=Buffer.from('function test() {}')
 assert.notEqual(gitBlobSha(before),gitBlobSha(Buffer.concat([before,Buffer.from('x')])))
})
test('lexical registration never claims runtime acceptance',()=>{
 const facts=astFacts('figure.js',Buffer.from("LF.register({'demo': function(host){}});"))
 assert.deepEqual(facts.registrations,['demo'])
 assert.deepEqual(facts.exports,[])
})
