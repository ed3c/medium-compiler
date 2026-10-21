/** Real DuckDB-Wasm OPFS store. Does not run Agent Mode CLI or Python. */
import * as duckdb from '@duckdb/duckdb-wasm'
import mvpWasm from '@duckdb/duckdb-wasm/dist/duckdb-mvp.wasm?url'
import mvpWorker from '@duckdb/duckdb-wasm/dist/duckdb-browser-mvp.worker.js?url'
import ehWasm from '@duckdb/duckdb-wasm/dist/duckdb-eh.wasm?url'
import ehWorker from '@duckdb/duckdb-wasm/dist/duckdb-browser-eh.worker.js?url'
import {validateAttempt,decodeExport,encodeExport} from './learning-domain.mjs'

const FILE='medium_learning_v1.duckdb'
const BUNDLES:duckdb.DuckDBBundles={
 mvp:{mainModule:mvpWasm,mainWorker:mvpWorker},
 eh:{mainModule:ehWasm,mainWorker:ehWorker}
}
type Attempt={id:string;problem_id:string;code:string;timestamp:number;status:string;
 passed_cases:number;total_cases:number;oracle:string}
type RecordRow=Record<string,unknown>
const TABLE='CREATE TABLE IF NOT EXISTS learning_attempts ('+
 'id VARCHAR PRIMARY KEY, problem_id VARCHAR NOT NULL, code VARCHAR NOT NULL, '+
 'timestamp_ms BIGINT NOT NULL, status VARCHAR NOT NULL, passed_cases INTEGER NOT NULL, '+
 'total_cases INTEGER NOT NULL, oracle VARCHAR NOT NULL)'
function rowsFrom(table:any):Attempt[]{
 return table.toArray().map((row:RecordRow)=>validateAttempt({
  id:String(row.id),problem_id:String(row.problem_id),code:String(row.code),
  timestamp:Number(row.timestamp_ms),status:String(row.status),
  passed_cases:Number(row.passed_cases),total_cases:Number(row.total_cases),
  oracle:String(row.oracle)
 })) as Attempt[]
}
// One local DuckDB writer per module. In Vite/React dev mode, lifecycle effects
// can overlap; serialize open/close instead of racing an OPFS Access Handle.
let writerLease:Promise<void>=Promise.resolve()
export async function openLearningStore(){
 if(typeof navigator==='undefined'||!navigator.storage?.getDirectory)
  throw Error('OPFS_UNSUPPORTED_NO_VOLATILE_FALLBACK')
 const previous=writerLease
 let releaseWriter!:()=>void
 writerLease=new Promise<void>(resolve=>{releaseWriter=resolve})
 await previous
 try{
 const bundle=await duckdb.selectBundle(BUNDLES)
 if(!bundle.mainWorker)throw Error('DUCKDB_WORKER_UNAVAILABLE')
 const worker=new Worker(bundle.mainWorker)
 const db=new duckdb.AsyncDuckDB(new duckdb.ConsoleLogger(),worker)
 let conn:duckdb.AsyncDuckDBConnection|undefined
 try{
  await db.instantiate(bundle.mainModule,bundle.pthreadWorker)
  await db.open({path:'opfs://'+FILE,accessMode:duckdb.DuckDBAccessMode.READ_WRITE})
  conn=await db.connect()
  await conn.query(TABLE)
  await conn.query('CHECKPOINT')
 }catch(error){
  if(conn)await conn.close().catch(()=>{})
  await db.terminate().catch(()=>{})
  worker.terminate()
  throw error
 }
 const connection=conn
 async function list():Promise<Attempt[]>{
  const r=await connection.query('SELECT id, problem_id, code, timestamp_ms, status, passed_cases, total_cases, oracle FROM learning_attempts ORDER BY timestamp_ms, id LIMIT 10001')
  const records=rowsFrom(r)
  if(records.length>10000)throw Error('EXPORT_TOO_LARGE')
  return records
 }
 async function add(record:Attempt){
  const data=validateAttempt(record)
  const stmt=await connection.prepare('INSERT INTO learning_attempts VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
  try{
   await stmt.query(data.id,data.problem_id,data.code,data.timestamp,data.status,data.passed_cases,data.total_cases,data.oracle)
  }finally{await stmt.close()}
  await connection.query('CHECKPOINT')
 }
 async function importJson(raw:string){
  const incoming=decodeExport(raw) as Attempt[]
  const prior=new Set((await list()).map(x=>x.id))
  if(incoming.some(x=>prior.has(x.id)))throw Error('EXISTING_ATTEMPT_REFUSED')
  await connection.query('BEGIN TRANSACTION')
  try{
   for(const item of incoming){
    const s=await connection.prepare('INSERT INTO learning_attempts VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
    try{await s.query(item.id,item.problem_id,item.code,item.timestamp,item.status,item.passed_cases,item.total_cases,item.oracle)}
    finally{await s.close()}
   }
   await connection.query('COMMIT')
  }catch(e){await connection.query('ROLLBACK');throw e}
  await connection.query('CHECKPOINT')
 }
 async function exportDbFile():Promise<File>{
  await connection.query('CHECKPOINT')
  const root=await navigator.storage.getDirectory()
  const handle=await root.getFileHandle(FILE,{create:false})
  return handle.getFile()
 }
 async function close(){
  try{
   await connection.query('CHECKPOINT')
   await connection.close()
   await db.terminate()
  }finally{
   worker.terminate()
   releaseWriter()
  }
 }
 return {list,add,importJson,exportJson:async()=>encodeExport(await list()),
  exportDbFile,close}
 }catch(error){releaseWriter();throw error}
}
