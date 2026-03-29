from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from time import perf_counter
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


def normalize_target(target: str) -> str:
    parsed = urlparse(target)
    if not parsed.scheme:
        target = f"https://{target.lstrip('/')}"
    return target if target.endswith("/") else f"{target}/"


@dataclass(slots=True)
class FetchResult:
    requested_url: str
    final_url: str
    status_code: int
    headers: dict[str, str]
    body: str
    elapsed_ms: float
    body_bytes: int
    truncated: bool
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.error and 200 <= self.status_code < 400


@dataclass(slots=True)
class PageSignals:
    title: str
    meta_description: str
    canonical: str
    robots: str
    h1_count: int
    html_lang: str
    has_viewport: bool


class _SignalsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._capture_tag = ""
        self._buffer: list[str] = []
        self.title = ""
        self.meta_description = ""
        self.canonical = ""
        self.robots = ""
        self.h1_count = 0
        self.html_lang = ""
        self.has_viewport = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key.lower(): value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = attr_map.get("lang", self.html_lang)
        if tag == "title":
            self._capture_tag = "title"
            self._buffer = []
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta":
            name = attr_map.get("name", "").lower()
            content = attr_map.get("content", "")
            if name == "description" and not self.meta_description:
                self.meta_description = content.strip()
            if name == "robots" and not self.robots:
                self.robots = content.strip()
            if name == "viewport":
                self.has_viewport = True
        if tag == "link":
            rel = " ".join(part.lower() for part in attr_map.get("rel", "").split())
            if "canonical" in rel and not self.canonical:
                self.canonical = attr_map.get("href", "").strip()

    def handle_endtag(self, tag: str) -> None:
        if tag == self._capture_tag == "title":
            self.title = "".join(self._buffer).strip()
        if tag == self._capture_tag:
            self._capture_tag = ""
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._capture_tag:
            self._buffer.append(data)


def extract_page_signals(html: str) -> PageSignals:
    parser = _SignalsParser()
    parser.feed(html)
    return PageSignals(
        title=parser.title,
        meta_description=parser.meta_description,
        canonical=parser.canonical,
        robots=parser.robots,
        h1_count=parser.h1_count,
        html_lang=parser.html_lang,
        has_viewport=parser.has_viewport,
    )


class HttpProbe:
    def __init__(self, user_agent: str, timeout_seconds: int, max_response_bytes: int) -> None:
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.max_response_bytes = max_response_bytes
        self._cache: dict[str, FetchResult] = {}

    def fetch(self, url: str) -> FetchResult:
        if url in self._cache:
            return self._cache[url]

        request = Request(url, headers={"User-Agent": self.user_agent})
        started = perf_counter()
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = response.read(self.max_response_bytes + 1)
                elapsed_ms = (perf_counter() - started) * 1000
                charset = response.headers.get_content_charset() or "utf-8"
                truncated = len(payload) > self.max_response_bytes
                body_bytes = min(len(payload), self.max_response_bytes)
                body = payload[: self.max_response_bytes].decode(charset, errors="replace")
                result = FetchResult(
                    requested_url=url,
                    final_url=response.geturl(),
                    status_code=getattr(response, "status", 200),
                    headers=dict(response.headers.items()),
                    body=body,
                    elapsed_ms=elapsed_ms,
                    body_bytes=body_bytes,
                    truncated=truncated,
                )
        except HTTPError as error:
            result = FetchResult(
                requested_url=url,
                final_url=error.geturl(),
                status_code=error.code,
                headers=dict(error.headers.items()) if error.headers else {},
                body="",
                elapsed_ms=(perf_counter() - started) * 1000,
                body_bytes=0,
                truncated=False,
                error=str(error),
            )
        except URLError as error:
            result = FetchResult(
                requested_url=url,
                final_url=url,
                status_code=0,
                headers={},
                body="",
                elapsed_ms=(perf_counter() - started) * 1000,
                body_bytes=0,
                truncated=False,
                error=str(error.reason),
            )
        self._cache[url] = result
        return result

    def homepage(self, target: str) -> FetchResult:
        return self.fetch(normalize_target(target))

    def sitemap(self, target: str) -> FetchResult:
        return self.fetch(urljoin(normalize_target(target), "sitemap.xml"))
