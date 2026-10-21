import {renderMermaidSVG} from 'beautiful-mermaid'
import {readFile,writeFile,mkdir} from 'node:fs/promises'
import {createHash} from 'node:crypto'
import {fileURLToPath} from 'node:url'
import {resolve,join} from 'node:path'
const root=fileURLToPath(new URL('../../',import.meta.url))
const [sourcePath,which,alt]=process.argv.slice(2)
if(!/^articles\/[a-zA-Z0-9/_-]+\.md$/.test(sourcePath||'') || !/^(0|[1-9]\d*)$/.test(which||'') || !alt?.trim())
  throw new Error('Usage: render.mjs articles/file.md ordinal alt')
const raw=await readFile(resolve(root,sourcePath),'utf8')
const lines=raw.split('\n'),blocks=[]
let fence=null,body=[]
for(const untrimmed of lines){
  const line=untrimmed.trimEnd()
  if(line.startsWith(String.fromCharCode(96).repeat(3))||line.startsWith('~~~')){
    if(fence!==null){if(fence==='mermaid')blocks.push(body.join('\n'));fence=null;body=[]}
    else fence=line.slice(3).trim().toLowerCase()
  }else if(fence!==null)body.push(line)
}
if(fence!==null)throw new Error('INCOMPLETE_FENCE')
const index=Number(which),mermaid=blocks[index]
if(!mermaid)throw new Error('MERMAID_BLOCK_NOT_FOUND')
const svg=renderMermaidSVG(mermaid)
if(typeof svg!=='string'||!svg.includes('<svg'))throw new Error('RENDER_FAILED')
const digest=x=>createHash('sha256').update(x).digest('hex')
const hash=digest(svg),dir=join(root,'site/article-diagrams')
await mkdir(dir,{recursive:true})
await writeFile(join(dir,hash+'.svg'),svg)
const path=join(root,'references/article-diagrams.json')
const registry=JSON.parse(await readFile(path,'utf8'))
if(registry.schema_version!=='article-diagram-registry@1')throw new Error('REGISTRY_VERSION')
const old=registry.items.find(r=>r.source===sourcePath&&r.ordinal===index)
const item={source:sourcePath,ordinal:index,mermaid_sha256:digest(mermaid),svg_sha256:hash,
  alt:alt.trim(),reviewed:Boolean(old?.reviewed&&old.mermaid_sha256===digest(mermaid)&&old.svg_sha256===hash&&old.alt===alt.trim())}
registry.items=registry.items.filter(r=>r.source!==sourcePath||r.ordinal!==index)
registry.items.push(item)
registry.items.sort((a,b)=>a.source.localeCompare(b.source)||a.ordinal-b.ordinal)
await writeFile(path,JSON.stringify(registry,null,2)+'\n')
console.log(JSON.stringify({source:sourcePath,ordinal:index,sha256:hash,reviewed:item.reviewed}))
