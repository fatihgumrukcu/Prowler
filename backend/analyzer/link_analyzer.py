from typing import List, Dict, Tuple
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from models import Check


def _classify_links(soup: BeautifulSoup, page_url: str) -> Tuple[int, int, int, int]:
    base_netloc = urlparse(page_url).netloc
    internal = external = empty_href = non_navigable = 0

    for a in soup.find_all("a"):
        href = (a.get("href") or "").strip()

        if not href:
            empty_href += 1
            continue

        if href.startswith("javascript:") or href == "#" or (href.startswith("#") and len(href) > 1):
            non_navigable += 1
            continue

        try:
            abs_url = urljoin(page_url, href)
            netloc = urlparse(abs_url).netloc
            if netloc == base_netloc:
                internal += 1
            else:
                external += 1
        except Exception:
            non_navigable += 1

    return internal, external, empty_href, non_navigable


def analyze_links(soup: BeautifulSoup, page_url: str) -> List[Check]:
    checks = []
    internal, external, empty_href, non_navigable = _classify_links(soup, page_url)

    if internal > 0:
        checks.append(Check(id="links_internal", category="Links", label="Internal Links",
            status="passed", message=f"{internal} internal link(s) found", value=str(internal)))
    else:
        checks.append(Check(id="links_internal", category="Links", label="Internal Links",
            status="warning", message="No internal links found", value="0",
            recommendation="Add internal links to improve crawlability and PageRank distribution"))

    checks.append(Check(id="links_external", category="Links", label="External Links",
        status="passed", message=f"{external} external link(s) found", value=str(external)))

    total_bad = empty_href + non_navigable
    if total_bad > 0:
        checks.append(Check(id="links_invalid", category="Links", label="Invalid/Empty Links",
            status="warning",
            message=f"{empty_href} empty href and {non_navigable} non-navigable link(s) found",
            value=f"{empty_href} empty, {non_navigable} non-navigable",
            recommendation="Remove or fix empty href and javascript: links"))
    else:
        checks.append(Check(id="links_invalid", category="Links", label="Invalid/Empty Links",
            status="passed", message="No empty or invalid links found"))

    return checks


def get_link_metadata(soup: BeautifulSoup, page_url: str) -> Dict:
    internal, external, _, _ = _classify_links(soup, page_url)
    return {"internal_links": internal, "external_links": external}
