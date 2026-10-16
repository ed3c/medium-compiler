// These controls run the bundled API in local workerd/HTMLRewriter.
// Provider fixtures are synthetic; deployed-provider/browser evidence is separate.
import {after, before, test} from "node:test";
import assert from "node:assert/strict";
import {execFileSync} from "node:child_process";
import {mkdtempSync, readFileSync, rmSync} from "node:fs";
import {tmpdir} from "node:os";
import {join} from "node:path";
import {createHash} from "node:crypto";
import {Miniflare, convertV4MiniflareOptions} from "miniflare";
const episode = "https://podscripts.co/podcasts/test-show/test-episode";
const results = `<h3><a href="/podcasts/test-show/test-episode?search_type=basic">Agent &amp; memory &copy;</a></h3>
<h3><a href="https://evil.test/podcasts/test-show/test-episode">Wrong host</a></h3>
<a href="/podcasts/test-show/another-episode">Navigation</a>
<h3><a href="/podcasts/test-show/test-episode">Duplicate</a></h3>`;
const transcript = `<title>Fixture episode - Transcript</title>
<span class="pod_timestamp_indicator">Starting point is 00:00:00</span>
<span class="transcript-text">This &amp; that is a synthetic transcript with enough words to exercise the public excerpt budget and ensure later words never leave the response.</span>
<span class="pod_timestamp_indicator">Starting point is 00:01:00</span>
<span class="transcript-text">PRIVATE FULL TEXT MARKER</span>`;
let runtime, temporary, calls = [], payload = results, responseStatus = 200, responseType = "text/html";
before(async () => {
  temporary = mkdtempSync(join(tmpdir(), "medium-site-worker-"));
  execFileSync(process.execPath, ["node_modules/wrangler/bin/wrangler.js", "deploy", "--dry-run", "--outdir", temporary], {stdio: "pipe"});
  runtime = new Miniflare(convertV4MiniflareOptions({workers: [{name: "site-test", modules: true, script: readFileSync(join(temporary, "index.js"), "utf8"), compatibilityDate: "2026-10-11",
    serviceBindings: {ASSETS: () => new Response("fixture asset")},
    outboundService: request => {
      calls.push(request.url);
      return new Response(payload, {status: responseStatus, headers: {"Content-Type": responseType}});
    }}]}));
  await runtime.ready;
});
after(async () => { if (runtime) await runtime.dispose(); if (temporary) rmSync(temporary, {recursive: true}); });
function reset(html = results) { calls = []; payload = html; responseStatus = 200; responseType = "text/html"; }
const get = path => runtime.dispatchFetch("https://site.test" + path);

test("search retains decoded titles, one-podcast scope and filtered candidate links", async () => {
  reset();
  const response = await get("/api/transcripts?q=" + encodeURIComponent("Agent 記憶") + "&podcast=latent-space");
  assert.equal(response.status, 200);
  const result = await response.json();
  assert.equal(result.search_terms, "Agent memory");
  assert.deepEqual(result.results, [{title: "Agent & memory ©", source_url: episode, status: "candidate_not_audio_verified"}]);
  assert.equal(new URL(calls[0]).searchParams.get("podSelectedId"), "1772");
});
test("inspect retains exact source digest and fixed bounded excerpt, not full transcript", async () => {
  reset(transcript);
  const response = await get("/api/transcripts?action=inspect&url=" + encodeURIComponent(episode));
  assert.equal(response.status, 200);
  const result = await response.json();
  assert.equal(result.source_sha256, createHash("sha256").update(transcript).digest("hex"));
  assert.equal(result.segment_count, 2);
  assert.equal(result.last_timestamp, "00:01:00");
  assert.equal(result.audio_verified, false);
  assert.ok(result.excerpt.startsWith("This & that"));
  assert.ok(result.excerpt.split(/\s+/).length <= 18);
  assert.ok(!JSON.stringify(result).includes("PRIVATE FULL TEXT MARKER"));
});
test("invalid inputs/duplicate parameters/SSRF are refused before upstream fetch", async () => {
  reset();
  for (const path of ["?q=x", "?q=xx&podcast=evil", "?q=xx&q=yy", "?action=other",
    "?action=inspect&url=http://localhost", "?q=https://example.com", "?q=" + "x".repeat(241)])
    assert.equal((await get("/api/transcripts" + path)).status, 400, path);
  assert.equal(calls.length, 0);
});
test("provider errors, redirects, wrong content and changed timestamp markup fail closed", async () => {
  for (const status of [302, 503]) {
    reset(); responseStatus = status;
    assert.equal((await get("/api/transcripts?q=agent")).status, 502);
  }
  reset(); responseType = "application/octet-stream";
  assert.equal((await get("/api/transcripts?q=agent")).status, 502);
  reset("<title>Blocked page</title>");
  assert.equal((await get("/api/transcripts?q=agent")).status, 502);
  for (const html of [transcript.replace("00:01:00", "00:00:00"), transcript.replace("Starting point is", "new markup")]) {
    reset(html);
    assert.equal((await get("/api/transcripts?action=inspect&url=" + encodeURIComponent(episode))).status, 502);
  }
});
test("real zero results retain the attempted query instead of inventing candidates", async () => {
  reset("Found <span>0</span> results");
  const result = await (await get("/api/transcripts?q=Agent%20memory")).json();
  assert.deepEqual(result.results, []);
  assert.deepEqual(result.attempted_terms, ["Agent memory", "memory"]);
  assert.equal(calls.length, 2);
});
test("known YouTube association remains a caller-supplied candidate, not audio proof", async () => {
  reset();
  const result = await (await get("/api/transcripts?q=" + encodeURIComponent("https://youtu.be/ekK8urKHPMQ"))).json();
  assert.equal(result.video_title, "Beyond the God Model");
  assert.equal(result.search_terms, "Beyond the God Model");
  assert.equal(result.video_association, "existing_caller_supplied_association_not_audio_verified");
  assert.equal(result.podcast_key, "a16z");
  assert.equal(calls.length, 1);
});
test("only the read-only transcript API is public; no checkout or load proxy", async () => {
  assert.equal((await get("/api/create")).status, 404);
  assert.equal((await runtime.dispatchFetch("https://site.test/api/transcripts", {method: "POST"})).status, 405);
  assert.equal(await (await get("/articles/")).text(), "fixture asset");
  const config = JSON.parse(readFileSync("wrangler.jsonc", "utf8"));
  assert.deepEqual(config.assets.run_worker_first, ["/api/*"]);
  assert.equal(config.queues, undefined);
  assert.equal(config.durable_objects, undefined);
});
