"""
Sitemap discovery: collects page URLs from all sitemap sources.

Handles:
  - robots.txt  Sitemap: directives
  - /sitemap.xml and /sitemap_index.xml (auto-tried)
  - Nested sitemap indexes (recursive, depth-limited)
  - Deduplication and domain filtering
"""

import asyncio
from typing import List, Optional, Set
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

MAX_SITEMAP_DEPTH = 3   # max nesting levels for sitemap indexes
MAX_SITEMAP_URLS = 5_000  # hard cap on collected URLs


# ── Helpers ───────────────────────────────────────────────────────────────────

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


_SKIP_EXT = {
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico",
    ".css", ".js", ".zip", ".tar", ".gz", ".mp4", ".mp3",
    ".webp", ".woff", ".woff2", ".ttf", ".eot", ".json",
}


def _is_html_url(url: str) -> bool:
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        return False
    return not any(p.path.lower().endswith(ext) for ext in _SKIP_EXT)


async def _fetch(client: httpx.AsyncClient, url: str) -> Optional[str]:
    try:
        r = await client.get(url, timeout=10.0)
        return r.text if r.status_code == 200 else None
    except Exception:
        return None


# ── Sitemap parsing ───────────────────────────────────────────────────────────

def _is_index(text: str) -> bool:
    return "<sitemapindex" in text.lower()


def _child_sitemap_urls(text: str) -> List[str]:
    """From a sitemap index, extract child sitemap URLs."""
    soup = BeautifulSoup(text, "html.parser")
    urls = []
    for sitemap_tag in soup.find_all("sitemap"):
        loc = sitemap_tag.find("loc")
        if loc:
            urls.append(loc.get_text().strip())
    return urls


def _page_urls_from_sitemap(text: str) -> List[str]:
    """From a regular sitemap, extract page URLs."""
    soup = BeautifulSoup(text, "html.parser")
    # Standard: <url><loc>…</loc></url>
    url_tags = soup.find_all("url")
    if url_tags:
        urls = []
        for tag in url_tags:
            loc = tag.find("loc")
            if loc:
                urls.append(loc.get_text().strip())
        return urls
    # Fallback: bare <loc> tags
    return [loc.get_text().strip() for loc in soup.find_all("loc")]


# ── Recursive sitemap walker ──────────────────────────────────────────────────

async def _walk_sitemap(
    client: httpx.AsyncClient,
    url: str,
    collected: List[str],
    visited: Set[str],
    base_netloc: str,
    include_subdomains: bool,
    depth: int,
) -> None:
    """Recursively fetch a sitemap or sitemap index and collect page URLs."""
    if depth > MAX_SITEMAP_DEPTH or url in visited or len(collected) >= MAX_SITEMAP_URLS:
        return
    visited.add(url)

    text = await _fetch(client, url)
    if not text:
        return

    if _is_index(text):
        children = _child_sitemap_urls(text)
        await asyncio.gather(*[
            _walk_sitemap(client, child, collected, visited, base_netloc, include_subdomains, depth + 1)
            for child in children
        ])
    else:
        for page_url in _page_urls_from_sitemap(text):
            if len(collected) >= MAX_SITEMAP_URLS:
                break
            if not page_url or not _is_html_url(page_url):
                continue
            netloc = urlparse(page_url).netloc
            if _same_domain(netloc, base_netloc, include_subdomains):
                collected.append(page_url)


# ── Public entry point ────────────────────────────────────────────────────────

async def discover_sitemap_urls(
    client: httpx.AsyncClient,
    base_url: str,
    base_netloc: str,
    include_subdomains: bool = False,
) -> List[str]:
    """
    Discover all page URLs from sitemaps.

    Sources tried (in order, de-duplicated):
      1. Sitemap: directives from robots.txt
      2. {base_url}/sitemap.xml
      3. {base_url}/sitemap_index.xml

    Returns a deduplicated list of page URLs belonging to the target domain.
    """
    sitemap_roots: List[str] = []

    # 1. robots.txt Sitemap: directives
    robots_text = await _fetch(client, f"{base_url}/robots.txt")
    if robots_text:
        for line in robots_text.splitlines():
            line = line.strip()
            if line.lower().startswith("sitemap:"):
                sm = line.split(":", 1)[1].strip()
                if sm and sm not in sitemap_roots:
                    sitemap_roots.append(sm)

    # 2 & 3. Default locations
    for path in ("/sitemap.xml", "/sitemap_index.xml"):
        candidate = f"{base_url}{path}"
        if candidate not in sitemap_roots:
            sitemap_roots.append(candidate)

    collected: List[str] = []
    visited_sitemaps: Set[str] = set()

    await asyncio.gather(*[
        _walk_sitemap(client, root, collected, visited_sitemaps, base_netloc, include_subdomains, depth=0)
        for root in sitemap_roots
    ])

    # Deduplicate while preserving order
    seen: Set[str] = set()
    unique: List[str] = []
    for u in collected:
        if u not in seen:
            seen.add(u)
            unique.append(u)

    return unique
