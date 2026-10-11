// Same public discovery contract as scripts/transcript_discovery.py.
// Native HTMLRewriter parses provider markup; entities preserves decoded text.
import {decodeHTML} from "entities";

export const PODCASTS = {
  "a16z": [1750, "The a16z Show"], "a16z-podcast": [1074, "a16z Podcast"],
  "latent-space": [1772, "Latent Space: The AI Engineer Podcast"],
  "dwarkesh": [1220, "Dwarkesh Podcast"], "no-priors": [1075, "No Priors"],
  "lenny": [1744, "Lenny's Podcast"], "lex-fridman": [70, "Lex Fridman Podcast"]
};
const aliases = [["每個人都", "agent"], ["代理", "agent"], ["智能體", "agent"],
  ["差異化", "differentiation"], ["上下文", "context"], ["記憶", "memory"],
  ["評估", "evaluation"], ["推理", "reasoning"], ["模型", "model"]];
const video = "https://www.youtube.com/watch?v=ekK8urKHPMQ";
const episode = "https://podscripts.co/podcasts/the-a16z-show/beyond-the-god-model-alex-atallah-amjad-masad";
const episodePath = /^\/podcasts\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+\/?$/;
const normalize = text => decodeHTML(text).replace(/\s+/gu, " ").trim();
export class ProviderError extends Error {}

export function sourceURL(value) {
  if (!/^https:\/\/podscripts\.co\/podcasts\/[A-Za-z0-9_-]+\/[A-Za-z0-9_-]+\/?$/.test(value)) throw Error("Invalid source URL");
  const url = new URL(value);
  if (url.protocol !== "https:" || url.host !== "podscripts.co" || url.username || url.password ||
      url.search || url.hash || !episodePath.test(url.pathname)) throw Error("Invalid source URL");
  return url.href;
}
export function videoURL(value) {
  if (/^https:\/\/[^/]*:\d+/.test(value)) throw Error("Explicit port refused");
  const url = new URL(value);
  if (url.protocol !== "https:" || url.username || url.password || url.port) throw Error("Invalid video URL");
  const key = url.hostname === "youtu.be" ? url.pathname.slice(1) :
    ["youtube.com", "www.youtube.com"].includes(url.hostname) && url.pathname === "/watch" ? url.searchParams.get("v") : "";
  if (!/^[A-Za-z0-9_-]{11}$/.test(key || "")) throw Error("Invalid video ID");
  return "https://www.youtube.com/watch?v=" + key;
}
export function termsFor(query) {
  const words = query.match(/[A-Za-z0-9][A-Za-z0-9'-]*/g) || [];
  for (const [term, word] of aliases) if (query.includes(term)) words.push(word);
  const stop = new Set(["i", "want", "podcast", "about", "the", "a", "an", "and", "with", "of", "to", "why", "how"]);
  return [...new Set(words.filter(word => !stop.has(word.toLowerCase())))].join(" ").slice(0, 160) || query;
}
export async function readPublic(value, kind = "text/html", limit = 8 * 1024 * 1024, fetcher = fetch) {
  const url = new URL(value);
  const allowed = url.host === "podscripts.co" && (url.pathname === "/podkeywordsearch/" || episodePath.test(url.pathname)) ||
    url.host === "www.youtube.com" && url.pathname === "/oembed";
  if (url.protocol !== "https:" || url.username || url.password || url.hash || !allowed) throw Error("Unsupported provider");
  try {
    const response = await fetcher(url.href, {redirect: "manual", signal: AbortSignal.timeout(15000),
      headers: {"User-Agent": "medium-compiler/1.1 public-transcript-discovery", Accept: kind, "Accept-Encoding": "identity"}});
    if (!response.ok || response.headers.get("Content-Type")?.split(";")[0].trim() !== kind)
      throw new ProviderError("Provider status or type changed");
    const reader = response.body.getReader(), chunks = [];
    let length = 0;
    try {
      while (true) {
        const {done, value: chunk} = await reader.read();
        if (done) break;
        length += chunk.byteLength;
        if (length > limit) throw new ProviderError("Provider response too large");
        chunks.push(chunk);
      }
    } finally { await reader.cancel(); }
    const raw = new Uint8Array(length);
    let offset = 0;
    for (const chunk of chunks) { raw.set(chunk, offset); offset += chunk.length; }
    return raw;
  } catch (error) {
    throw error instanceof ProviderError ? error : new ProviderError("Provider unavailable", {cause: error});
  }
}
export async function parseResults(raw) {
  const results = [], seen = new Set();
  let current;
  const parser = new HTMLRewriter().on("h3 a", {
    element(element) {
      current = null;
      try {
        const url = new URL(element.getAttribute("href") || "", "https://podscripts.co");
        url.search = ""; url.hash = "";
        const source_url = sourceURL(url.href);
        const item = {source_url, parts: []}; current = item;
        element.onEndTag(() => {
          const title = normalize(item.parts.join("")).slice(0, 300);
          if (title && !seen.has(source_url)) { seen.add(source_url); results.push({title, source_url, status: "candidate_not_audio_verified"}); }
          current = null;
        });
      } catch { /* Other-host/navigation links are not candidates. */ }
    },
    text(chunk) { if (current) current.parts.push(chunk.text); }
  });
  try { await parser.transform(new Response(raw)).arrayBuffer(); }
  catch (error) { throw new ProviderError("Provider search parse failed", {cause: error}); }
  return results;
}
export async function parseTranscript(raw) {
  let title = "", last = null, first = null, preferred = null, count = 0;
  function capture(selector, accept) {
    return {selector, handler: {
      element(element) {
        const parts = [];
        this.parts = parts;
        element.onEndTag(() => accept(normalize(parts.join(""))));
      },
      text(chunk) { this.parts.push(chunk.text); }
    }};
  }
  const handlers = [capture("title", text => { title = text; }),
    capture(".pod_timestamp_indicator", text => {
      if (last && !last.text) throw new ProviderError("Empty transcript segment");
      const match = /^Starting point is (\d{2}):(\d{2}):(\d{2})$/.exec(text);
      if (!match) throw new ProviderError("Unrecognized timestamp");
      const [, h, m, s] = match, seconds = Number(h) * 3600 + Number(m) * 60 + Number(s);
      if (+m >= 60 || +s >= 60 || last && seconds <= last.start_seconds) throw new ProviderError("Invalid timestamp order");
      last = {timestamp: `${h}:${m}:${s}`, start_seconds: seconds, text: ""}; count++;
      if (!first) first = last;
      if (seconds === 845) preferred = last;
    }),
    capture(".transcript-text", text => {
      if (!last) throw new ProviderError("Text before timestamp");
      // Count/validate every segment, retaining only the fixed excerpt candidates.
      if (last === first || last === preferred) last.text += (last.text ? " " : "") + text;
      else if (text) last.text = "present";
    })];
  let parser = new HTMLRewriter();
  for (const {selector, handler} of handlers) parser = parser.on(selector, handler);
  try { await parser.transform(new Response(raw)).arrayBuffer(); }
  catch (error) { throw new ProviderError("Provider transcript parse failed", {cause: error}); }
  if (!title || !first || !last.text) throw new ProviderError("No usable transcript");
  return {title, count, first, last, preferred};
}
export async function search(query, podcast = "a16z", mode = "basic", reader = readPublic) {
  query = query.trim();
  if (query.length < 2 || query.length > 240 || /[\x00-\x1f]/.test(query) ||
      !Object.hasOwn(PODCASTS, podcast) || !["basic", "episode"].includes(mode)) throw Error("Invalid query");
  let terms = termsFor(query), video_url = null, video_title = null, association = null;
  if (/^https?:\/\//.test(query)) {
    video_url = videoURL(query);
    if (video_url === video) {
      video_title = "Beyond the God Model"; terms = video_title; podcast = "a16z"; mode = "episode";
      association = "existing_caller_supplied_association_not_audio_verified";
    }
    else {
      const params = new URLSearchParams({url: video_url, format: "json"});
      let data;
      try { data = JSON.parse(new TextDecoder().decode(await reader("https://www.youtube.com/oembed?" + params, "application/json", 65536))); }
      catch (error) { throw new ProviderError("Invalid video metadata", {cause: error}); }
      video_title = String(data.title || "").trim().slice(0, 240);
      if (!video_title) throw new ProviderError("Missing video title");
      terms = video_title; mode = "episode"; association = "video_title_search_only_not_verified";
    }
  }
  const [podSelectedId, name] = PODCASTS[podcast], attempts = [];
  let results = [], provider_search_url;
  for (let attempt = 0; attempt < 2; attempt++) {
    attempts.push(terms);
    provider_search_url = "https://podscripts.co/podkeywordsearch/?" + new URLSearchParams({
      search_type: mode, keywordsToSearch: terms, exact_match: "false", slv: "single", podSelectedId: String(podSelectedId)});
    const raw = await reader(provider_search_url);
    results = await parseResults(raw);
    if (!results.length && !/Found\s*<span[^>]*>\s*0|couldn.t find any|No results/i.test(new TextDecoder().decode(raw)))
      throw new ProviderError("Search markup changed");
    const words = termsFor(terms).split(/\s+/);
    if (results.length || attempt || words.length <= 1) break;
    terms = words.sort((a, b) => b.length - a.length)[0];
  }
  results = results.slice(0, 5);
  if (video_url === video) results.sort((a, b) => Number(b.source_url === episode) - Number(a.source_url === episode));
  return {query, search_terms: terms, attempted_terms: attempts, podcast: name, podcast_key: podcast, mode,
    video_url, video_title, video_association: association, provider_search_url, checked_at: new Date().toISOString(),
    scope: "one_public_podcast_first_page_max_5", results};
}
export async function inspect(value, reader = readPublic) {
  const url = sourceURL(value), raw = await reader(url), parsed = await parseTranscript(raw);
  const title = parsed.title.split(" - Transcript")[0];
  const budget = Math.max(0, Math.min(18, 25 - title.split(/\s+/).length));
  const selected = url === episode ? parsed.preferred || parsed.first : parsed.first;
  const hash = await crypto.subtle.digest("SHA-256", raw);
  return {source_url: url, title, provider: "PodScripts", checked_at: new Date().toISOString(),
    source_sha256: [...new Uint8Array(hash)].map(byte => byte.toString(16).padStart(2, "0")).join(""),
    segment_count: parsed.count, first_timestamp: parsed.first.timestamp, last_timestamp: parsed.last.timestamp,
    excerpt: selected.text.split(/\s+/).slice(0, budget).join(" "), excerpt_timestamp: selected.timestamp,
    status: "timestamped_transcript_found", audio_verified: false, publication: "metadata_and_fixed_short_excerpt_only",
    completeness: "provider_page_only_episode_coverage_unknown"};
}
export async function transcripts(url, reader = readPublic) {
  let status = 200, result;
  try {
    if (url.pathname.length + url.search.length > 2000) throw Error("Request too long");
    const one = (key, fallback = "") => {
      const values = url.searchParams.getAll(key);
      if (values.length > 1) throw Error("Duplicate parameter");
      return values[0] ?? fallback;
    };
    const action = one("action", "search");
    if (action === "search") result = await search(one("q"), one("podcast", "a16z"), one("mode", "basic"), reader);
    else if (action === "inspect") result = await inspect(one("url"), reader);
    else throw Error("Unknown action");
  } catch (error) {
    status = error instanceof ProviderError ? 502 : 400;
    result = {error: status === 502 ? "逐字稿來源暫時無法讀取。請稍後重試，或使用原站搜尋。" : "請檢查查詢內容、節目選項或網址格式。"};
    if (status === 502) console.warn(JSON.stringify({phase: "transcript-provider", error: error.message}));
  }
  return Response.json(result, {status, headers: {"Cache-Control": status === 200 ? "public, max-age=300" : "no-store",
    "X-Content-Type-Options": "nosniff"}});
}
