import { test } from 'node:test';
import assert from 'node:assert/strict';
import {createHash, webcrypto} from 'node:crypto';
import {reviewedArtifactRef, readReviewedArtifact} from './public-artifact.mjs';

const origin='https://example.test', digest='a'.repeat(64);
const manifest='/assets/loop-data/'+digest+'/graph.json';
const content='Source-approved evidence ✓';
const bytes=new TextEncoder().encode(content);
const sha=createHash('sha256').update(bytes).digest('hex');
const path='/assets/loop-data/'+digest+'/artifacts/'+sha+'.txt';
function snapshot() {
  return {schema_version:2,snapshot_sha256:digest,content_urls:{a:path},
    graph:{artifacts:[{id:'a',status:'available',public_sha256:sha,public_bytes:bytes.length}]}};
}
const fakeFetch=async () => new Response(bytes,{status:200});

test('readback accepts only digest-bound reviewed static bytes',async()=>{
  const s=snapshot();
  assert.equal(reviewedArtifactRef(s,manifest,'a',origin).pathname,path);
  assert.equal(await readReviewedArtifact(s,manifest,'a',origin,fakeFetch,webcrypto),content);
});
test('unreviewed source, unsafe URLs and mismatched identity are refused',()=>{
  const s=snapshot();
  for (const url of ['https://elsewhere.test'+manifest,manifest+'?redirect=/','/assets/x','/assets/loop-data/'+'b'.repeat(64)+'/graph.json'])
    assert.throws(()=>reviewedArtifactRef(s,url,'a',origin),/SOURCE_UNBOUND/);
  s.content_urls.a='https://elsewhere.test/secret';
  assert.throws(()=>reviewedArtifactRef(s,manifest,'a',origin),/ARTIFACT_URL_UNBOUND/);
  s.content_urls.a=path;s.graph.artifacts[0].content='private Host trace';
  assert.throws(()=>reviewedArtifactRef(s,manifest,'a',origin),/RAW_ARTIFACT_REFUSED/);
});
test('nonpublic, duplicate, too large and missing bytes are refused',()=>{
  const s=snapshot();s.graph.artifacts[0].status='not_public';
  assert.throws(()=>reviewedArtifactRef(s,manifest,'a',origin),/NOT_PUBLIC/);
  s.graph.artifacts[0].status='available';s.graph.artifacts[0].public_bytes=2097153;
  assert.throws(()=>reviewedArtifactRef(s,manifest,'a',origin),/NOT_PUBLIC/);
  s.graph.artifacts[0].public_bytes=bytes.length;
  s.graph.artifacts.push({...s.graph.artifacts[0]});
  assert.throws(()=>reviewedArtifactRef(s,manifest,'a',origin),/ARTIFACT_IDENTITY_UNKNOWN/);
});
test('content drift and unavailable source never become verified text',async()=>{
  const s=snapshot();
  await assert.rejects(readReviewedArtifact(s,manifest,'a',origin,
    async()=>new Response('tampered',{status:200}),webcrypto),/ARTIFACT_BYTES_DRIFT/);
  const wrong='X'.repeat(bytes.length);
  await assert.rejects(readReviewedArtifact(s,manifest,'a',origin,
    async()=>new Response(wrong,{status:200}),webcrypto),/ARTIFACT_DIGEST_DRIFT/);
  await assert.rejects(readReviewedArtifact(s,manifest,'a',origin,
    async()=>new Response('missing',{status:404}),webcrypto),/ARTIFACT_UNAVAILABLE/);
});
