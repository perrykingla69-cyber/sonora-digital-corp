"""Web search skill — search the web using DuckDuckGo (no API key required)."""

from __future__ import annotations

from typing import Any

from skills.base_skill import BaseSkill


class Skill(BaseSkill):
    name = "web_search"
    description = "Search the web via DuckDuckGo and fetch page content. No API key needed."

    def execute(self, action: str = "search", **kwargs: Any) -> Any:
        """
        Actions:
            search  — search DuckDuckGo (query, max_results=5)
            fetch   — fetch and extract text from a URL (url, timeout=10)
            news    — search recent news (query, max_results=5)
        """
        action = action.lower()

        if action == "search":
            return self._search(
                query=kwargs["query"],
                max_results=int(kwargs.get("max_results", 5)),
            )

        if action == "news":
            return self._news(
                query=kwargs["query"],
                max_results=int(kwargs.get("max_results", 5)),
            )

        if action == "fetch":
            return self._fetch(
                url=kwargs["url"],
                timeout=int(kwargs.get("timeout", 10)),
            )

        raise ValueError(f"Unknown action '{action}'. Valid: search, news, fetch")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _search(self, query: str, max_results: int = 5) -> list[dict]:
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            return results
        except ImportError:
            return self._fallback_search(query, max_results)

    def _news(self, query: str, max_results: int = 5) -> list[dict]:
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.news(query, max_results=max_results))
            return results
        except ImportError:
            return self._fallback_search(query, max_results)

    def _fetch(self, url: str, timeout: int = 10) -> dict:
        """Fetch URL and extract visible text."""
        import urllib.request
        import html.parser

        class _TextExtractor(html.parser.HTMLParser):
            SKIP_TAGS = {"script", "style", "head", "meta", "link"}

            def __init__(self):
                super().__init__()
                self._skip = False
                self._skip_tag = None
                self.parts: list[str] = []

            def handle_starttag(self, tag, attrs):
                if tag in self.SKIP_TAGS:
                    self._skip = True
                    self._skip_tag = tag

            def handle_endtag(self, tag):
                if tag == self._skip_tag:
                    self._skip = False
                    self._skip_tag = None

            def handle_data(self, data):
                if not self._skip:
                    text = data.strip()
                    if text:
                        self.parts.append(text)

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html_bytes = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
            html_str = html_bytes.decode(charset, errors="replace")

        parser = _TextExtractor()
        parser.feed(html_str)
        text = " ".join(parser.parts)
        # Truncate to 4000 chars to keep payloads reasonable
        return {"url": url, "text": text[:4000], "length": len(text)}

    def _fallback_search(self, query: str, max_results: int) -> list[dict]:
        """Minimal fallback using urllib when duckduckgo_search is not installed."""
        import urllib.request
        import urllib.parse
        import json

        encoded = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        results = []
        if data.get("AbstractText"):
            results.append({"title": data.get("Heading", query),
                             "body": data["AbstractText"],
                             "href": data.get("AbstractURL", "")})
        for item in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(item, dict) and item.get("Text"):
                results.append({"title": item.get("Text", "")[:80],
                                 "body": item.get("Text", ""),
                                 "href": item.get("FirstURL", "")})
        return results[:max_results]
