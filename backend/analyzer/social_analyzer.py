from typing import List, Optional
from bs4 import BeautifulSoup
from models import Check


def _og(soup: BeautifulSoup, prop: str) -> Optional[str]:
    tag = soup.find("meta", property=f"og:{prop}")
    if tag:
        return tag.get("content", "").strip() or None
    return None


def _twitter(soup: BeautifulSoup, name: str) -> Optional[str]:
    tag = soup.find("meta", attrs={"name": f"twitter:{name}"})
    if not tag:
        tag = soup.find("meta", property=f"twitter:{name}")
    if tag:
        return tag.get("content", "").strip() or None
    return None


def analyze_social(soup: BeautifulSoup) -> List[Check]:
    checks = []

    og_title = _og(soup, "title")
    og_description = _og(soup, "description")
    og_image = _og(soup, "image")

    missing = [f"og:{k}" for k, v in [("title", og_title), ("description", og_description), ("image", og_image)] if not v]
    status_line = (
        f"og:title={'✓' if og_title else '✗'}, "
        f"og:description={'✓' if og_description else '✗'}, "
        f"og:image={'✓' if og_image else '✗'}"
    )

    if missing:
        checks.append(Check(id="social_og", category="Social", label="Open Graph Tags",
            status="warning",
            message=f"Missing Open Graph tags: {', '.join(missing)}",
            value=status_line,
            recommendation="Add missing OG tags to improve appearance when shared on social media"))
    else:
        checks.append(Check(id="social_og", category="Social", label="Open Graph Tags",
            status="passed", message="All essential Open Graph tags present", value=status_line))

    twitter_card = _twitter(soup, "card")

    if not twitter_card:
        checks.append(Check(id="social_twitter", category="Social", label="Twitter Card",
            status="warning", message="twitter:card meta tag is missing",
            recommendation="Add twitter:card tag (e.g. 'summary_large_image') for rich previews"))
    else:
        checks.append(Check(id="social_twitter", category="Social", label="Twitter Card",
            status="passed", message="Twitter card tag is present", value=twitter_card))

    return checks
