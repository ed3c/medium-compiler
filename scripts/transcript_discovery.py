"""Public single-podcast discovery shared by the CLI and website; no credentials."""
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import re
from urllib.parse import urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

try:
    from .transcript import parse, source_url, video_url, digest
except ImportError:
    from transcript import parse, source_url, video_url, digest

# Public PodScripts catalog IDs, observed 2026-10-04. One selected show per search.
PODCASTS = {
    "a16z": (1750, "The a16z Show"),
    "a16z-podcast": (1074, "a16z Podcast"),
    "latent-space": (1772, "Latent Space: The AI Engineer Podcast"),
    "dwarkesh": (1220, "Dwarkesh Podcast"),
    "no-priors": (1075, "No Priors"),
    "lenny": (1744, "Lenny's Podcast"),
    "lex-fridman": (70, "Lex Fridman Podcast"),
}
ALIASES = (("每個人都", "agent"), ("代理", "agent"), ("智能體", "agent"),
           ("差異化", "differentiation"), ("上下文", "context"), ("記憶", "memory"),
           ("評估", "evaluation"), ("推理", "reasoning"), ("模型", "model"))
VIDEO = "https://www.youtube.com/watch?v=ekK8urKHPMQ"
EPISODE = "https://podscripts.co/podcasts/the-a16z-show/beyond-the-god-model-alex-atallah-amjad-masad"


class ProviderError(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Public canonical routes are requested directly. A login/host redirect is not a result.
        raise ProviderError("來源重新導向；請使用原站搜尋。")


def read_public(url, kind="text/html", limit=8 * 1024 * 1024):
    p = urlsplit(url)
    allowed = (p.netloc == "podscripts.co" and
               (p.path == "/podkeywordsearch/" or
                re.fullmatch(r"/podcasts/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/?", p.path)))
    allowed = allowed or (p.netloc == "www.youtube.com" and p.path == "/oembed")
    if p.scheme != "https" or not allowed or p.fragment:
        raise ValueError("Unsupported public provider URL")
    try:
        req = Request(url, headers={"User-Agent": "medium-compiler/1.1 public-transcript-discovery",
                                    "Accept": kind, "Accept-Encoding": "identity"})
        with build_opener(NoRedirect()).open(req, timeout=15) as response:
            if response.headers.get_content_type() != kind:
                raise ProviderError("來源回應格式改變，尚未取得逐字稿。")
            data = response.read(limit + 1)
        if len(data) > limit:
            raise ProviderError("來源超過大小限制。")
        return data
    except (OSError, ValueError) as error:
        raise ProviderError("來源目前無法讀取；可稍後重試或開啟原站。") from error


class ResultsParser(HTMLParser):
    """Read only episode-title anchors in public search results, never paywalled data."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_heading = False
        self.url = None
        self.words = []
        self.results = []

    def handle_starttag(self, tag, attrs):
        if tag == "h3":
            self.in_heading = True
        if tag == "a" and self.in_heading:
            p = urlsplit(urljoin("https://podscripts.co", dict(attrs).get("href", "")))
            try:
                self.url = source_url(urlunsplit((p.scheme, p.netloc, p.path, "", "")))
                self.words = []
            except ValueError:
                self.url = None

    def handle_data(self, data):
        if self.url:
            self.words.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.url:
            title = " ".join("".join(self.words).split())[:300]
            if title and self.url not in {r["source_url"] for r in self.results}:
                self.results.append({"title": title, "source_url": self.url,
                                     "status": "candidate_not_audio_verified"})
            self.url = None
        if tag == "h3":
            self.in_heading = False


def terms_for(query):
    """Transparent keyword extraction, not an LLM or a semantic match claim."""
    english = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", query)
    stop = {"i", "want", "podcast", "about", "the", "a", "an", "and", "with", "of", "to", "why", "how"}
    terms = [w for w in english if w.lower() not in stop]
    terms.extend(english for chinese, english in ALIASES if chinese in query)
    return " ".join(dict.fromkeys(terms))[:160] or query


def search(query, podcast="a16z", mode="basic", reader=read_public):
    query = query.strip()
    if not 2 <= len(query) <= 240 or any(ord(c) < 32 for c in query):
        raise ValueError("請輸入 2–240 個字元的主題、來賓或 YouTube 連結。")
    if podcast not in PODCASTS or mode not in ("basic", "episode"):
        raise ValueError("Unsupported podcast or search mode")
    video = None
    association = None
    known = False
    title = None
    if re.match(r"https?://", query):
        video = video_url(query)
        if video == VIDEO:
            # Existing receipt records a caller-supplied association, not audio verification.
            title, podcast, mode, known = "Beyond the God Model", "a16z", "episode", True
            association = "existing_caller_supplied_association_not_audio_verified"
        else:
            metadata = json.loads(reader("https://www.youtube.com/oembed?" +
                                         urlencode({"url": video, "format": "json"}),
                                         "application/json", 65536))
            title = str(metadata.get("title", "")).strip()[:240]
            if not title:
                raise ProviderError("無法取得影片標題；請改用來賓或節目名稱搜尋。")
            mode = "episode"
            association = "video_title_search_only_not_verified"
    terms = title or terms_for(query)
    pod_id, name = PODCASTS[podcast]
    attempted = []
    for attempt in range(2):
        attempted.append(terms)
        url = "https://podscripts.co/podkeywordsearch/?" + urlencode({
            "search_type": mode, "keywordsToSearch": terms, "exact_match": "false",
            "slv": "single", "podSelectedId": pod_id})
        raw = reader(url)
        parser = ResultsParser()
        parser.feed(raw.decode("utf-8"))
        if not parser.results and not re.search(rb'(?:Found\s*<span[^>]*>\s*0|couldn.t find any|No results)', raw, re.I):
            raise ProviderError("無法辨識搜尋結果；原站可能暫時受限或已更換版型。")
        words = terms_for(terms).split()
        if parser.results or len(words) < 2 or attempt == 1:
            break
        # One bounded, visible broader retry; never claim semantic equivalence.
        terms = max(words, key=len)
    candidates = parser.results[:5]
    if known:
        candidates.sort(key=lambda r: r["source_url"] != EPISODE)
    return {"query": query, "search_terms": terms, "attempted_terms": attempted,
            "podcast": name, "podcast_key": podcast,
            "mode": mode, "video_url": video, "video_title": title,
            "video_association": association, "provider_search_url": url,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "scope": "one_public_podcast_first_page_max_5", "results": candidates}


def inspect_episode(url, reader=read_public):
    source_url(url)
    raw = reader(url)
    try:
        transcript = parse(raw)
    except ValueError as error:
        raise ProviderError("來源頁面沒有可辨識的時間戳逐字稿。") from error
    segments = transcript["segments"]
    # Fixed preview per episode: repeated requests never expose successive chunks of a transcript.
    # Count title plus excerpt within a conservative 25-word public quotation budget.
    title = transcript["title"].split(" - Transcript")[0]
    budget = max(0, min(18, 25 - len(title.split())))
    segment = next((s for s in segments if s["start_seconds"] == 845), segments[0]) if url == EPISODE else segments[0]
    return {"title": title, "source_url": url, "provider": "PodScripts",
            "status": "timestamped_transcript_found", "audio_verified": False,
            "checked_at": datetime.now(timezone.utc).isoformat(), "source_sha256": digest(raw),
            "segment_count": len(segments), "first_timestamp": segments[0]["timestamp"],
            "last_timestamp": segments[-1]["timestamp"],
            "excerpt": " ".join(segment["text"].split()[:budget]),
            "excerpt_timestamp": segment["timestamp"],
            "publication": "metadata_and_fixed_short_excerpt_only",
            "completeness": "provider_page_only_episode_coverage_unknown"}
