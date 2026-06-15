import re
from typing import List, Dict
from bs4 import BeautifulSoup
from models import Check

_SKIP_TAGS = {"script", "style", "noscript", "svg", "path", "head", "meta", "link", "template"}
_JS_ROOT_IDS = {"root", "app", "__next", "__nuxt", "react-root", "vue-app"}
_JS_MARKERS = ("data-reactroot", "data-react-helmet", "ng-version", "__nuxt", "__next", "data-v-app")


def _visible_text(soup: BeautifulSoup) -> str:
    parts = []
    for string in soup.strings:
        parent = string.parent
        if parent and parent.name in _SKIP_TAGS:
            continue
        t = string.strip()
        if t:
            parts.append(t)
    return " ".join(parts)


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def _jaccard(a: str, b: str) -> float:
    sa = set(_normalize(a).split())
    sb = set(_normalize(b).split())
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _is_js_render(soup: BeautifulSoup, word_count: int) -> bool:
    if word_count >= 100:
        return False
    for root_id in _JS_ROOT_IDS:
        if soup.find(id=root_id):
            return True
    snippet = str(soup)[:8000]
    if any(m in snippet for m in _JS_MARKERS):
        return True
    if word_count < 30 and len(soup.find_all("script")) >= 3:
        return True
    return False


def analyze_content(soup: BeautifulSoup, raw_html: str = "") -> List[Check]:
    checks = []
    visible = _visible_text(soup)
    word_count = len(visible.split()) if visible.strip() else 0

    title_tag = soup.find("title")
    h1_tag = soup.find("h1")
    desc_tag = soup.find("meta", attrs={"name": "description"})

    # 1. Kelime sayısı / thin content
    if word_count == 0:
        checks.append(Check(
            id="content_word_count", category="Content", label="Kelime Sayısı",
            status="failed",
            message="Sayfada görünür metin bulunamadı",
            value="0 kelime",
            recommendation="Sayfaya okunabilir içerik ekleyin",
        ))
    elif word_count < 100:
        checks.append(Check(
            id="content_word_count", category="Content", label="Kelime Sayısı",
            status="failed",
            message=f"İçerik kritik eşiğin altında: {word_count} kelime",
            value=f"{word_count} kelime",
            recommendation="En az 300 kelimelik kaliteli içerik ekleyin",
        ))
    elif word_count < 300:
        checks.append(Check(
            id="content_word_count", category="Content", label="Kelime Sayısı",
            status="warning",
            message=f"İnce içerik (thin content): {word_count} kelime — önerilen ≥300",
            value=f"{word_count} kelime",
            recommendation="Kapsamlı ve kullanıcıya değer katan içerik için en az 300 kelime hedefleyin",
        ))
    else:
        checks.append(Check(
            id="content_word_count", category="Content", label="Kelime Sayısı",
            status="passed",
            message=f"{word_count} kelime",
            value=f"{word_count} kelime",
        ))

    # 2. Metin / HTML oranı
    if raw_html:
        html_len = max(1, len(raw_html))
        ratio = round(len(visible) / html_len, 4)
        ratio_pct = round(ratio * 100, 1)
        if ratio < 0.05:
            checks.append(Check(
                id="content_text_html_ratio", category="Content", label="Metin/HTML Oranı",
                status="warning",
                message=f"Metin/HTML oranı çok düşük: %{ratio_pct} — HTML şişirilmiş ya da içerik az",
                value=f"%{ratio_pct}",
                recommendation="Gereksiz inline CSS/JS ve yorum satırlarını kaldırın; içerik ekleyin",
            ))
        else:
            checks.append(Check(
                id="content_text_html_ratio", category="Content", label="Metin/HTML Oranı",
                status="passed",
                message=f"Metin/HTML oranı: %{ratio_pct}",
                value=f"%{ratio_pct}",
            ))

    # 3. Title vs H1 örtüşmesi
    if title_tag and h1_tag:
        title_text = title_tag.get_text().strip()
        h1_text = h1_tag.get_text().strip()
        sim = _jaccard(title_text, h1_text)
        sim_pct = int(sim * 100)
        if sim >= 0.4:
            checks.append(Check(
                id="content_title_h1_match", category="Content", label="Title / H1 Örtüşmesi",
                status="passed",
                message=f"Title ve H1 yeterince örtüşüyor (benzerlik: %{sim_pct})",
                value=f"Title: \"{title_text[:60]}\" | H1: \"{h1_text[:60]}\"",
            ))
        else:
            checks.append(Check(
                id="content_title_h1_match", category="Content", label="Title / H1 Örtüşmesi",
                status="warning",
                message=f"Title ve H1 çok farklı (benzerlik: %{sim_pct})",
                value=f"Title: \"{title_text[:60]}\" | H1: \"{h1_text[:60]}\"",
                recommendation="Title ve H1 aynı konuyu yansıtmalı; birbirini tamamlayan ifadeler kullanın",
            ))

    # 4. Meta description, title'ı tekrarlıyor mu
    if title_tag and desc_tag:
        title_text = title_tag.get_text().strip()
        desc_text = (desc_tag.get("content") or "").strip()
        if desc_text:
            sim = _jaccard(title_text, desc_text)
            if sim > 0.8:
                checks.append(Check(
                    id="content_desc_title_dupe", category="Content", label="Description & Title Tekrarı",
                    status="warning",
                    message=f"Meta description title'ı neredeyse birebir tekrarlıyor (%{int(sim*100)} benzerlik)",
                    value=desc_text[:120],
                    recommendation="Meta description; title'dan farklı ek bilgi içermeli",
                ))
            else:
                checks.append(Check(
                    id="content_desc_title_dupe", category="Content", label="Description & Title Tekrarı",
                    status="passed",
                    message="Meta description ve title birbirinden farklı içeriğe sahip",
                ))

    # 5. JS-render tespiti
    if _is_js_render(soup, word_count):
        checks.append(Check(
            id="content_js_render", category="Content", label="JavaScript Render Tespiti",
            status="warning",
            message="Sayfa muhtemelen JS ile render ediliyor; ham HTML neredeyse boş",
            recommendation="Googlebot JS render kuyruğuna alır. SSR veya prerendering kullanın",
        ))

    return checks


def get_content_metadata(soup: BeautifulSoup, raw_html: str = "") -> Dict:
    visible = _visible_text(soup)
    word_count = len(visible.split()) if visible.strip() else 0
    ratio = round(len(visible) / max(1, len(raw_html)), 4) if raw_html else 0.0
    return {"word_count": word_count, "text_html_ratio": ratio}
