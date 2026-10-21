#!/usr/bin/env node
/** Soodles code-intel method, extended locally to actual JS/TSX AST facts.
 * Soodles' original code_intel.py is Python-only. This does not call its MCP,
 * mutate its cache, infer a call graph, or authorize an Outer/Inner dispatch.
 */
import ts from 'typescript'
import {createHash} from 'node:crypto'
import {readFileSync,lstatSync} from 'node:fs'
import {resolve,relative,sep} from 'node:path'
import {fileURLToPath} from 'node:url'

const APP=resolve(fileURLToPath(new URL('..',import.meta.url)))
const ROOT=resolve(APP,'../..')
function sha(bytes,algorithm){return createHash(algorithm).update(bytes).digest('hex')}
export function gitBlobSha(bytes) {
 const payload=Buffer.isBuffer(bytes)?bytes:Buffer.from(bytes)
 return createHash('sha1').update(Buffer.from('blob '+payload.length+'\0')).update(payload).digest('hex')
}
export function astFacts(path,bytes) {
 const file=ts.createSourceFile(path,bytes.toString('utf8'),ts.ScriptTarget.Latest,true,
   path.endsWith('.tsx')?ts.ScriptKind.TSX:ts.ScriptKind.JS)
 if(file.parseDiagnostics.length){
  throw Error('AST_PARSE_REFUSED: '+ts.flattenDiagnosticMessageText(file.parseDiagnostics[0].messageText,' '))
 }
 const declarations=[],registrations=[],exports=[],calls=[]
 function visit(node){
  if(ts.isFunctionDeclaration(node)&&node.name){
   declarations.push({name:node.name.text,kind:'function',line:file.getLineAndCharacterOfPosition(node.getStart(file)).line+1})
  }else if(ts.isVariableDeclaration(node)&&ts.isIdentifier(node.name)&&node.initializer&&
    (ts.isFunctionExpression(node.initializer)||ts.isArrowFunction(node.initializer))){
   declarations.push({name:node.name.text,kind:'function-value',line:file.getLineAndCharacterOfPosition(node.getStart(file)).line+1})
  }
  if(ts.isCallExpression(node)){
   const callee=node.expression.getText(file)
   if(callee==='LF.register'&&node.arguments.length===1&&ts.isObjectLiteralExpression(node.arguments[0])){
    for(const entry of node.arguments[0].properties){
     if(ts.isPropertyAssignment(entry)){
      const n=entry.name
      if(ts.isStringLiteral(n)||ts.isIdentifier(n)) registrations.push(n.text)
     }
    }
   }
   if(['window.mountLessonFigures','window.AIFS_loadFigureProviders'].includes(callee))calls.push(callee)
  }
  if(ts.isBinaryExpression(node)&&node.operatorToken.kind===ts.SyntaxKind.EqualsToken&&
    ts.isPropertyAccessExpression(node.left)&&node.left.expression.getText(file)==='window'&&
    ['LF','mountLessonFigures','AIFSFigureRuntime'].includes(node.left.name.text)){
    exports.push('window.'+node.left.name.text)
  }
  ts.forEachChild(node,visit)
 }
 visit(file)
 return {declarations,registrations:registrations.sort(),exports:exports.sort(),calls}
}
function safeSource(relativeName){
 const path=resolve(ROOT,relativeName)
 if(!path.startsWith(ROOT+sep)||relative(ROOT,path).startsWith('..'))throw Error('PATH_OUTSIDE_REPOSITORY')
 let current=path
 while(current!==ROOT){
  if(lstatSync(current).isSymbolicLink())throw Error('SOURCE_SYMLINK_REFUSED')
  current=resolve(current,'..')
 }
 return readFileSync(path)
}
export function inspect(){
 const lock=JSON.parse(safeSource('references/aifs-figure-vendor.json'))
 if(lock.schema_version!=='aifs-figure-vendor@1'||lock.source_files.length!==4||
    lock.upstream!=='rohitg00/ai-engineering-from-scratch'||lock.license!=='MIT')
   throw Error('VENDOR_LOCK_REFUSED')
 const expected=['lesson-figures.js','figures-math.js','figures-demo.js','LICENSE']
 const records={}
 for(let i=0;i<expected.length;i++){
  const row=lock.source_files[i]
  if(row.vendor_path!=='apps/loop-workbench/public/aifs/'+expected[i])throw Error('SOURCE_PATH_DRIFT')
  const content=safeSource(row.vendor_path)
  if(row.git_blob_sha1!==gitBlobSha(content))throw Error('SOURCE_BYTES_DRIFT: '+expected[i])
  const facts=i===3?null:astFacts(expected[i],content)
  records[expected[i]]={git_blob_sha1:row.git_blob_sha1,sha256:sha(content,'sha256'),
    length:content.length,...(facts||{})}
 }
 const runtime=records['lesson-figures.js']
 if(!runtime.exports.includes('window.LF')||!runtime.exports.includes('window.mountLessonFigures'))
  throw Error('FIGURE_RUNTIME_API_DRIFT')
 if(!records['figures-math.js'].registrations.includes('vector-projection')||
    !records['figures-math.js'].registrations.includes('matrix-transform')||
    !records['figures-demo.js'].registrations.includes('demo-token-bucket'))
   throw Error('FIGURE_REGISTRATION_DRIFT')
 const host=astFacts('figures.tsx',safeSource('apps/loop-workbench/src/routes/figures.tsx'))
 if(!host.declarations.some(x=>x.name==='FigureLab'))throw Error('MISSING_REACT_CONSUMER')
 const html=safeSource('apps/loop-workbench/public/aifs/figure-lab.html').toString('utf8')
 for(const name of expected.slice(0,3)){
  if(!html.includes('src="./'+name+'"'))throw Error('MISSING_SCRIPT_ORDER: '+name)
 }
 if(!html.includes('window.mountLessonFigures(document)'))throw Error('MISSING_MOUNT_CONSUMER')
 return {status:'ready',owner:'medium-compiler.javascript-code-intel',method:'soodles.code-intel-source-bound',
  original_analyzer:'Soodles Python-only (not called)',revision:lock.revision,
  source:records,consumer:{tsx:host.declarations.map(x=>x.name),html:'figure-lab.html'},
  claims:['lexical AST facts and selected registrations only','no complete dynamic call graph','no native run, test PASS or effect authority'],
  effects:[],authorizes_landing:false}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 try{console.log(JSON.stringify(inspect()))}
 catch(e){console.error(JSON.stringify({status:'refused',reason:String(e)}));process.exitCode=1}
}
