import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup, Tag
from models import Check

# BCP 47 temel pattern: 2-3 harf dil kodu + isteğe bağlı bölge
_LANG_RE = re.compile(r"^[a-z]{2,3}(-[A-Za-z]{2,4})?$")


def _is_valid_lang(code: str) -> bool:
    if code.lower() == "x-default":
        return True
    return bool(_LANG_RE.match(code))


def _rel_contains(tag: Tag, keyword: str) -> bool:
    rel = tag.get("rel", [])
    if isinstance(rel, list):
        return keyword in rel
    return keyword == str(rel)


def _find_by_rel(soup: BeautifulSoup, keyword: str) -> Optional[Tag]:
    for tag in soup.find_all("link"):
        if _rel_contains(tag, keyword):
            return tag
    return None


def analyze_structural(soup: BeautifulSoup, page_url: str) -> List[Check]:
    checks = []

    # 1. hreflang
    hreflang_tags = [
        t for t in soup.find_all("link")
        if _rel_contains(t, "alternate") and t.get("hreflang")
    ]
    if hreflang_tags:
        langs = [t.get("hreflang", "") for t in hreflang_tags]
        invalid = [l for l in langs if not _is_valid_lang(l)]
        if invalid:
            checks.append(Check(
                id="structural_hreflang", category="Structure", label="Hreflang",
                status="warning",
                message=f"Geçersiz hreflang kodu tespit edildi: {', '.join(invalid[:5])}",
                value=", ".join(langs[:10]),
                recommendation="Hreflang kodları BCP 47 standardına uygun olmalı (örn: tr, en-US, x-default)",
            ))
        else:
            checks.append(Check(
                id="structural_hreflang", category="Structure", label="Hreflang",
                status="passed",
                message=f"{len(hreflang_tags)} hreflang tag mevcut: {', '.join(langs[:5])}",
                value=", ".join(langs[:10]),
            ))
    else:
        checks.append(Check(
            id="structural_hreflang", category="Structure", label="Hreflang",
            status="passed",
            message="Hreflang tag yok — çok dilli site değilse beklenen durum",
        ))

    # 2. Pagination (rel=next / rel=prev)
    next_link = _find_by_rel(soup, "next")
    prev_link = _find_by_rel(soup, "prev")
    if next_link or prev_link:
        parts = []
        if prev_link:
            parts.append(f"prev: {prev_link.get('href', '')[:80]}")
        if next_link:
            parts.append(f"next: {next_link.get('href', '')[:80]}")
        checks.append(Check(
            id="structural_pagination", category="Structure", label="Pagination (rel=next/prev)",
            status="passed",
            message="Sayfalama linkleri mevcut",
            value=" | ".join(parts),
        ))

    # 3. Favicon
    favicon = _find_by_rel(soup, "icon") or _find_by_rel(soup, "shortcut icon")
    if not favicon:
        # apple-touch-icon da kabul edilebilir ama gerçek favicon arayalım
        for tag in soup.find_all("link"):
            rel = tag.get("rel", [])
            rel_str = " ".join(rel).lower() if isinstance(rel, list) else str(rel).lower()
            if "icon" in rel_str:
                favicon = tag
                break

    if favicon:
        checks.append(Check(
            id="structural_favicon", category="Structure", label="Favicon",
            status="passed",
            message="Favicon tanımlı",
            value=(favicon.get("href") or "")[:200],
        ))
    else:
        checks.append(Check(
            id="structural_favicon", category="Structure", label="Favicon",
            status="warning",
            message="Favicon bulunamadı",
            recommendation="<link rel='icon' href='/favicon.ico'> ekleyin",
        ))

    # 4. RSS / Atom feed
    feed_link = (
        soup.find("link", type="application/rss+xml")
        or soup.find("link", type="application/atom+xml")
    )
    if feed_link:
        checks.append(Check(
            id="structural_rss", category="Structure", label="RSS / Atom Feed",
            status="passed",
            message="Feed linki mevcut",
            value=(feed_link.get("href") or "")[:200],
        ))

    # 5. Viewport (mobil uyumluluk)
    viewport = soup.find("meta", attrs={"name": "viewport"})
    if not viewport:
        checks.append(Check(
            id="structural_viewport", category="Structure", label="Viewport Meta",
            status="failed",
            message="Viewport meta tag eksik — mobil uyumluluk bozulabilir",
            recommendation="<meta name='viewport' content='width=device-width, initial-scale=1'> ekleyin",
        ))
    else:
        content = (viewport.get("content") or "").lower()
        if "width=device-width" not in content:
            checks.append(Check(
                id="structural_viewport", category="Structure", label="Viewport Meta",
                status="warning",
                message="Viewport mevcut ama 'width=device-width' eksik",
                value=viewport.get("content", ""),
                recommendation="content='width=device-width, initial-scale=1' olarak güncelleyin",
            ))
        else:
            checks.append(Check(
                id="structural_viewport", category="Structure", label="Viewport Meta",
                status="passed",
                message="Viewport doğru yapılandırılmış",
                value=viewport.get("content", ""),
            ))

    return checks


def get_structural_metadata(soup: BeautifulSoup) -> Dict:
    hreflang_tags = [
        t for t in soup.find_all("link")
        if _rel_contains(t, "alternate") and t.get("hreflang")
    ]
    langs = [t.get("hreflang", "") for t in hreflang_tags]

    favicon = None
    for tag in soup.find_all("link"):
        rel = tag.get("rel", [])
        rel_str = " ".join(rel).lower() if isinstance(rel, list) else str(rel).lower()
        if "icon" in rel_str:
            favicon = tag
            break

    feed = (
        soup.find("link", type="application/rss+xml")
        or soup.find("link", type="application/atom+xml")
    )
    viewport = soup.find("meta", attrs={"name": "viewport"})

    return {
        "hreflang_langs": langs,
        "has_favicon": favicon is not None,
        "has_rss": feed is not None,
        "has_viewport": viewport is not None,
    }
