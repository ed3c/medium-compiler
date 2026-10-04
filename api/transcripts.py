"""Vercel Python HTTP function. No secrets, arbitrary URLs, storage or full-text proxy."""
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlsplit
from scripts.transcript_discovery import search, inspect_episode, ProviderError


def respond(path):
    if len(path) > 2000:
        return 400, {"error": "Request too long"}
    params = parse_qs(urlsplit(path).query)
    def one(key, default=""):
        values = params.get(key, [default])
        if len(values) != 1:
            raise ValueError("Duplicate parameter")
        return values[0]
    try:
        action = one("action", "search")
        if action == "search":
            result = search(one("q"), one("podcast", "a16z"), one("mode", "basic"))
        elif action == "inspect":
            result = inspect_episode(one("url"))
        else:
            raise ValueError("Unknown action")
        return 200, result
    except (ValueError, KeyError, TypeError):
        return 400, {"error": "請檢查查詢內容、節目選項或網址格式。"}
    except (ProviderError, OSError):
        return 502, {"error": "逐字稿來源暫時無法讀取。請稍後重試，或使用原站搜尋。"}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, result = respond(self.path)
        data = json.dumps(result, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "public, s-maxage=300" if status == 200 else "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)
