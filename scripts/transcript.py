#!/usr/bin/env python3
"""Acquire PodScripts source bytes separately from Medium prose (stdlib only)."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import parse_qs, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

VERSION = "podscripts-html@1"
MAX_BYTES = 8 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def source_url(value):
    p = urlsplit(value)
    if (p.scheme != "https" or p.netloc != "podscripts.co" or p.query or p.fragment
            or not re.fullmatch(r"/podcasts/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/?", p.path)):
        raise ValueError("Expected a public https://podscripts.co/podcasts/show/episode URL")
    return value


def video_url(value):
    p = urlsplit(value)
    if p.scheme != "https" or p.username or p.password or p.port:
        raise ValueError("Expected an HTTPS YouTube video URL")
    if p.netloc == "youtu.be":
        key = p.path.lstrip("/")
    elif p.netloc in ("youtube.com", "www.youtube.com") and p.path == "/watch":
        key = parse_qs(p.query).get("v", [""])[0]
    else:
        key = ""
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", key):
        raise ValueError("Expected a YouTube URL with an 11-character video ID")
    return "https://www.youtube.com/watch?v=" + key


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        source_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class PodScriptsParser(HTMLParser):
    """Read provider timestamp/text spans, excluding menus, ads and scripts."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.capture = None
        self.depth = 0
        self.buffer = []
        self.title = ""
        self.segments = []

    def handle_starttag(self, tag, attrs):
        if self.capture:
            if tag == self.capture[1]:
                self.depth += 1
            if tag == "br":
                self.buffer.append(" ")
            return
        classes = set(dict(attrs).get("class", "").split())
        kind = ("time" if "pod_timestamp_indicator" in classes else
                "text" if "transcript-text" in classes else
                "title" if tag == "title" else None)
        if kind:
            self.capture = (kind, tag)
            self.depth = 1
            self.buffer = []

    def handle_data(self, data):
        if self.capture:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if not self.capture or tag != self.capture[1]:
            return
        self.depth -= 1
        if self.depth:
            return
        text = " ".join("".join(self.buffer).split())
        kind = self.capture[0]
        self.capture = None
        if kind == "title":
            self.title = text
        elif kind == "time":
            match = re.fullmatch(r"Starting point is (\d{2}:\d{2}:\d{2})", text)
            if not match:
                raise ValueError("Unrecognized provider timestamp")
            stamp = match[1]
            h, m, s = map(int, stamp.split(":"))
            seconds = h * 3600 + m * 60 + s
            if m >= 60 or s >= 60 or (self.segments and seconds <= self.segments[-1]["start_seconds"]):
                raise ValueError("Invalid or non-increasing provider timestamp")
            self.segments.append({"timestamp": stamp, "start_seconds": seconds, "text": ""})
        elif kind == "text":
            if not self.segments:
                raise ValueError("Transcript text appeared before its timestamp")
            segment = self.segments[-1]
            segment["text"] += (" " if segment["text"] else "") + text


def parse(raw):
    parser = PodScriptsParser()
    parser.feed(raw.decode("utf-8-sig"))
    parser.close()
    if parser.capture or not parser.title or not parser.segments or any(not s["text"] for s in parser.segments):
        raise ValueError("No usable timestamped transcript; page may be blocked or provider markup changed")
    return {"schema_version": "medium-transcript@1", "parser": VERSION,
            "title": parser.title, "segments": parser.segments}


def markdown(transcript):
    return ("# " + transcript["title"] + "\n\n" + "\n\n".join(
        "## " + s["timestamp"] + "\n\n" + s["text"] for s in transcript["segments"]) + "\n").encode("utf-8")


def acquire(url, video, out, local_html=None):
    source_url(url)
    video = video_url(video)
    if out.exists():
        raise ValueError("Output already exists; verify it or choose a new snapshot directory")
    if local_html:
        with local_html.open("rb") as handle:
            raw = handle.read(MAX_BYTES + 1)
        final_url, retrieved_at = None, None
        mode = "imported_html"
    else:
        req = Request(url, headers={"User-Agent": "medium-compiler/1.0 transcript-reader",
                                    "Accept": "text/html", "Accept-Encoding": "identity"})
        with build_opener(SafeRedirect()).open(req, timeout=30) as response:
            final_url = source_url(response.url)
            if response.headers.get_content_type() != "text/html":
                raise ValueError("Provider response is not HTML")
            raw = response.read(MAX_BYTES + 1)
        retrieved_at = datetime.now(timezone.utc).isoformat()
        mode = "https_fetch"
    if len(raw) > MAX_BYTES:
        raise ValueError("Source exceeds 8 MiB limit")
    transcript = parse(raw)
    files = {"source.html": raw, "transcript.json": json_bytes(transcript),
             "transcript.md": markdown(transcript)}
    manifest = {"schema_version": "medium-transcript-snapshot@1", "provider": "PodScripts",
                "parser": VERSION, "source_url": url, "final_url": final_url,
                "video_url": video, "video_association": "caller_supplied_not_verified",
                "acquisition": mode, "retrieved_at": retrieved_at,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "title": transcript["title"], "segment_count": len(transcript["segments"]),
                "first_timestamp": transcript["segments"][0]["timestamp"],
                "last_timestamp": transcript["segments"][-1]["timestamp"],
                "audio_verified": False, "speaker_attribution": "not_inferred",
                "completeness": "provider_page_only_episode_coverage_unknown",
                "normalization": "HTML entities decoded; whitespace collapsed; no corrections or deduplication",
                "files": {name: digest(data) for name, data in files.items()}}
    out.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".transcript-", dir=out.parent))
    try:
        for name, data in files.items():
            (temp / name).write_bytes(data)
        (temp / "manifest.json").write_bytes(json_bytes(manifest))
        # Refuse existing output, including an empty directory created by another writer.
        out.mkdir()
        try:
            for file in temp.iterdir():
                file.rename(out / file.name)
        except BaseException:
            shutil.rmtree(out)
            raise
    finally:
        shutil.rmtree(temp)
    return manifest


def verify(snapshot):
    manifest = json.loads((snapshot / "manifest.json").read_bytes())
    if manifest.get("schema_version") != "medium-transcript-snapshot@1" or manifest.get("parser") != VERSION:
        raise ValueError("Unsupported snapshot schema or parser")
    if set(manifest.get("files", {})) != {"source.html", "transcript.json", "transcript.md"}:
        raise ValueError("Unexpected snapshot file inventory")
    source_url(manifest["source_url"])
    video_url(manifest["video_url"])
    if manifest["acquisition"] not in ("https_fetch", "imported_html") or manifest["audio_verified"] is not False:
        raise ValueError("Unsupported acquisition or audio verification claim")
    for name, expected in manifest["files"].items():
        if digest((snapshot / name).read_bytes()) != expected:
            raise ValueError("Source bytes changed: " + name)
    transcript = parse((snapshot / "source.html").read_bytes())
    if ((snapshot / "transcript.json").read_bytes() != json_bytes(transcript)
            or (snapshot / "transcript.md").read_bytes() != markdown(transcript)
            or manifest["title"] != transcript["title"]
            or manifest["segment_count"] != len(transcript["segments"])
            or manifest["first_timestamp"] != transcript["segments"][0]["timestamp"]
            or manifest["last_timestamp"] != transcript["segments"][-1]["timestamp"]):
        raise ValueError("Extracted text or metadata no longer matches the source HTML")
    return manifest


def receipt(snapshot, out):
    manifest = verify(snapshot)
    result = dict(manifest, schema_version="medium-transcript-source@1",
                  snapshot_manifest_sha256=digest((snapshot / "manifest.json").read_bytes()),
                  publication="metadata_only_no_transcript_republication")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("xb") as file:
        file.write(json_bytes(result))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("search", help="Find public transcript candidates without an episode URL")
    a.add_argument("--query", required=True)
    a.add_argument("--podcast", default="a16z")
    a.add_argument("--mode", choices=("basic", "episode"), default="basic")
    a = sub.add_parser("inspect", help="Read timestamp metadata and a fixed short excerpt")
    a.add_argument("--url", required=True)
    for cmd in ("fetch", "import-html"):
        a = sub.add_parser(cmd)
        a.add_argument("--url", required=True, help="Explicit PodScripts episode URL, not a search query")
        a.add_argument("--video-url", required=True, help="Caller-supplied episode association, not automatically verified")
        a.add_argument("--out", required=True, type=Path)
        if cmd == "import-html":
            a.add_argument("--html", required=True, type=Path)
    a = sub.add_parser("verify"); a.add_argument("--snapshot", required=True, type=Path)
    a = sub.add_parser("receipt"); a.add_argument("--snapshot", required=True, type=Path)
    a.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    from transcript_discovery import search, inspect_episode, ProviderError
    try:
        if args.command == "search":
            result = search(args.query, args.podcast, args.mode)
        elif args.command == "inspect":
            result = inspect_episode(args.url)
        elif args.command in ("fetch", "import-html"):
            result = acquire(args.url, args.video_url, args.out, getattr(args, "html", None))
        elif args.command == "verify":
            result = verify(args.snapshot)
        else:
            result = receipt(args.snapshot, args.out)
        print(json.dumps({"status": "OK", "result": result}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, ProviderError) as error:
        print(json.dumps({"status": "REFUSED", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
