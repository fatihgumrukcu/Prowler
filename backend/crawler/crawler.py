"""
BFS site crawler.

URL discovery sources (merged, deduped):
  1. Sitemap URLs  (via crawler/sitemap_discovery.py)
  2. Internal links found while crawling pages

Respects robots.txt Disallow rules, max_pages / max_depth, HARD_CAP,
asyncio.Semaphore concurrency limit, and per-request rate-limit delay.
"""

import asyncio
from collections import deque
from typing import Deque, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urldefrag, urlparse

import httpx
from bs4 import BeautifulSoup

from analyzer import analyze_html
from analyzer.fetcher import USER_AGENT
from crawler.sitemap_discovery import discover_sitemap_urls
from models import PageResult, Summary

HARD_CAP = 1000
CONCURRENCY = 5
REQUEST_TIMEOUT = 12.0
CRAWL_DELAY = 0.25  # seconds between requests (per semaphore slot)

_SKIP_EXT = {
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico",
    ".css", ".js", ".zip", ".tar", ".gz", ".mp4", ".mp3",
    ".webp", ".woff", ".woff2", ".ttf", ".eot", ".json",
}


# ── URL helpers ───────────────────────────────────────────────────────────────

def _strip_www(netloc: str) -> str:
    return netloc[4:] if netloc.startswith("www.") else netloc


def _same_domain(netloc: str, base: str, include_subdomains: bool) -> bool:
    if netloc == base:
        return True
    if _strip_www(netloc) == _strip_www(base):
        return True
    if include_subdomains and _strip_www(netloc).endswith("." + _strip_www(base)):
        return True
    return False


def _is_html_url(url: str) -> bool:
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        return False
    return not any(p.path.lower().endswith(ext) for ext in _SKIP_EXT)


def _norm(url: str) -> str:
    """Strip fragment, normalise trailing slash."""
    url, _ = urldefrag(url)
    p = urlparse(url)
    path = p.path.rstrip("/") or "/"
    return p._replace(path=path, fragment="").geturl()


# ── robots.txt ────────────────────────────────────────────────────────────────

async def _fetch_text(client: httpx.AsyncClient, url: str) -> Optional[str]:
    try:
        r = await client.get(url, timeout=8.0)
        return r.text if r.status_code == 200 else None
    except Exception:
        return None


def _parse_disallowed(text: str) -> List[str]:
    """Return Disallow paths that apply to User-agent: *."""
    disallowed: List[str] = []
    applies = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        low = line.lower()
        if low.startswith("user-agent:"):
            applies = low.split(":", 1)[1].strip() == "*"
        elif applies and low.startswith("disallow:"):
            path = line.split(":", 1)[1].strip()
            if path:
                disallowed.append(path)
    return disallowed


def _is_disallowed(path: str, rules: List[str]) -> bool:
    return any(path.startswith(r) for r in rules)


# ── Main crawler ──────────────────────────────────────────────────────────────

async def crawl_site(
    start_url: str,
    max_pages: int,
    max_depth: int,
    include_subdomains: bool,
    job_id: str,
    job_store,
) -> Tuple[List[PageResult], int, int, int]:
    """
    BFS crawl from start_url seeded with sitemap URLs.

    Returns (page_results, pages_done, pages_failed, sitemap_urls_found).
    Continuously updates job_store with live progress.
    """
    max_pages = min(max_pages, HARD_CAP)

    p = urlparse(start_url)
    base_netloc = p.netloc
    base_url = f"{p.scheme}://{base_netloc}"

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    page_results: List[PageResult] = []
    visited: Set[str] = set()
    url_sources: Dict[str, str] = {}   # norm_url -> "start" | "sitemap" | "crawl"
    sem = asyncio.Semaphore(CONCURRENCY)

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=httpx.Timeout(REQUEST_TIMEOUT),
        headers=headers,
        verify=True,
    ) as client:
        # ── Phase 1: robots.txt ──────────────────────────────────────────────
        disallowed: List[str] = []
        robots_text = await _fetch_text(client, f"{base_url}/robots.txt")
        if robots_text:
            disallowed = _parse_disallowed(robots_text)

        # ── Phase 2: sitemap discovery ───────────────────────────────────────
        sitemap_page_urls = await discover_sitemap_urls(
            client, base_url, base_netloc, include_subdomains
        )
        sitemap_urls_found = len(sitemap_page_urls)

        # ── Phase 3: initialise frontier ─────────────────────────────────────
        start_norm = _norm(start_url)
        frontier: Deque[Tuple[str, int]] = deque([(start_norm, 0)])
        visited.add(start_norm)
        url_sources[start_norm] = "start"

        # Enqueue sitemap URLs (depth=1, respecting disallow + html filter)
        for su in sitemap_page_urls:
            if not _is_html_url(su):
                continue
            ap = urlparse(su)
            if _is_disallowed(ap.path, disallowed):
                continue
            n = _norm(su)
            if n not in visited:
                visited.add(n)
                frontier.append((n, 1))
                url_sources[n] = "sitemap"

        pages_done = 0
        pages_failed = 0

        # ── Phase 4: BFS ─────────────────────────────────────────────────────

        async def fetch_and_analyze(url: str, depth: int) -> Tuple[PageResult, List[str]]:
            async with sem:
                await asyncio.sleep(CRAWL_DELAY)
                new_links: List[str] = []
                source = url_sources.get(url, "crawl")
                try:
                    resp = await client.get(url)
                    final_url = str(resp.url)
                    status_code = resp.status_code
                    html = resp.text or ""

                    if status_code >= 400:
                        result = PageResult(
                            url=url,
                            final_url=final_url,
                            status_code=status_code,
                            score=0,
                            discovery_source=source,
                            error=f"HTTP {status_code}",
                        )
                        return result, []

                    if html:
                        soup = BeautifulSoup(html, "html.parser")

                        # Discover links for next BFS level
                        if depth < max_depth:
                            for a in soup.find_all("a", href=True):
                                href = (a.get("href") or "").strip()
                                if not href or href.startswith(
                                    ("javascript:", "mailto:", "tel:", "#")
                                ):
                                    continue
                                abs_url = urljoin(final_url, href)
                                ap = urlparse(abs_url)
                                if (
                                    _same_domain(ap.netloc, base_netloc, include_subdomains)
                                    and _is_html_url(abs_url)
                                    and not _is_disallowed(ap.path, disallowed)
                                ):
                                    new_links.append(_norm(abs_url))

                        checks, score, summary, _ = analyze_html(soup, final_url, raw_html=html)
                    else:
                        checks, score = [], 0
                        summary = Summary(passed=0, warnings=0, failed=0)

                    result = PageResult(
                        url=url,
                        final_url=final_url,
                        status_code=status_code,
                        score=score,
                        summary=summary,
                        checks=checks,
                        discovery_source=source,
                    )
                    return result, new_links

                except Exception as exc:
                    result = PageResult(
                        url=url,
                        final_url=url,
                        score=0,
                        discovery_source=source,
                        error=str(exc)[:300],
                    )
                    return result, []

        while frontier:
            total_processed = pages_done + pages_failed
            if total_processed >= max_pages:
                break

            remaining = max_pages - total_processed
            batch_size = min(CONCURRENCY, remaining, len(frontier))
            if batch_size <= 0:
                break

            batch = [frontier.popleft() for _ in range(batch_size)]

            results = await asyncio.gather(
                *[fetch_and_analyze(url, depth) for url, depth in batch]
            )

            for (url, depth), (page_result, new_links) in zip(batch, results):
                page_results.append(page_result)
                if page_result.error:
                    pages_failed += 1
                else:
                    pages_done += 1

                # Push URL to live feed
                job_store.add_completed_url(job_id, page_result.url)

                # Enqueue newly discovered crawl links
                if depth < max_depth:
                    for link in new_links:
                        if link not in visited:
                            visited.add(link)
                            url_sources[link] = "crawl"
                            frontier.append((link, depth + 1))

            job_store.update(
                job_id,
                pages_done=pages_done,
                pages_failed=pages_failed,
                pages_found=len(visited),
            )

    return page_results, pages_done, pages_failed, sitemap_urls_found
