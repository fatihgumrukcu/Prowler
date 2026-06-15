from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from models import Check


def analyze_indexability(soup: BeautifulSoup, page_url: str) -> List[Check]:
    checks = []

    robots_tag = soup.find("meta", attrs={"name": "robots"})
    robots = robots_tag.get("content", "").lower() if robots_tag else ""

    if "noindex" in robots:
        checks.append(Check(id="indexability_noindex", category="Indexability",
            label="Noindex Directive", status="warning",
            message="Page has noindex — search engines will not index this page",
            value=robots, recommendation="Remove noindex if this page should be indexed"))
    else:
        checks.append(Check(id="indexability_noindex", category="Indexability",
            label="Noindex Directive", status="passed", message="Page is indexable",
            value=robots or "index (default)"))

    if "nofollow" in robots:
        checks.append(Check(id="indexability_nofollow", category="Indexability",
            label="Nofollow Directive", status="warning",
            message="Page has nofollow — links will not pass PageRank",
            value=robots, recommendation="Remove nofollow if you want links to pass equity"))
    else:
        checks.append(Check(id="indexability_nofollow", category="Indexability",
            label="Nofollow Directive", status="passed", message="Links are followable",
            value=robots or "follow (default)"))

    canonical_tag = soup.find("link", rel="canonical")
    canonical = canonical_tag.get("href", "").strip() if canonical_tag else None

    if not canonical:
        checks.append(Check(id="indexability_canonical", category="Indexability",
            label="Canonical URL", status="warning", message="No canonical tag found",
            recommendation="Add a canonical tag to prevent duplicate content issues"))
    elif canonical.rstrip("/") != page_url.rstrip("/"):
        checks.append(Check(id="indexability_canonical", category="Indexability",
            label="Canonical URL", status="warning",
            message="Canonical URL differs from page URL",
            value=canonical, recommendation=f"Verify this is intentional. Page URL: {page_url}"))
    else:
        checks.append(Check(id="indexability_canonical", category="Indexability",
            label="Canonical URL", status="passed",
            message="Canonical matches page URL", value=canonical))

    html_tag = soup.find("html")
    lang = html_tag.get("lang", "").strip() if html_tag else ""

    if not lang:
        checks.append(Check(id="indexability_lang", category="Indexability",
            label="HTML Lang Attribute", status="warning",
            message="HTML lang attribute is missing",
            recommendation="Add lang attribute to <html> (e.g. lang='en')"))
    else:
        checks.append(Check(id="indexability_lang", category="Indexability",
            label="HTML Lang Attribute", status="passed",
            message="HTML lang attribute is present", value=lang))

    return checks


def get_indexability_metadata(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    robots_tag = soup.find("meta", attrs={"name": "robots"})
    robots = robots_tag.get("content", "").strip() if robots_tag else None

    canonical_tag = soup.find("link", rel="canonical")
    canonical = canonical_tag.get("href", "").strip() if canonical_tag else None

    html_tag = soup.find("html")
    lang = html_tag.get("lang", "").strip() if html_tag else None

    return {"robots": robots or None, "canonical": canonical or None, "lang": lang or None}
