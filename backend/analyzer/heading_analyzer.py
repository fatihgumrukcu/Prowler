from typing import List, Dict
from bs4 import BeautifulSoup
from models import Check


def analyze_headings(soup: BeautifulSoup) -> List[Check]:
    checks = []

    h1_tags = soup.find_all("h1")
    h1_count = len(h1_tags)
    h2_count = len(soup.find_all("h2"))

    # H1 varlığı ve sayısı
    if h1_count == 0:
        checks.append(Check(
            id="heading_h1", category="Headings", label="H1 Tag",
            status="failed",
            message="Sayfada H1 etiketi yok",
            recommendation="Sayfanın ana konusunu açıklayan tek bir H1 ekleyin",
        ))
    elif h1_count == 1:
        text = h1_tags[0].get_text().strip()
        checks.append(Check(
            id="heading_h1", category="Headings", label="H1 Tag",
            status="passed",
            message="Tek H1 etiketi var",
            value=text[:200],
        ))
    else:
        texts = ", ".join(h.get_text().strip()[:80] for h in h1_tags[:5])
        checks.append(Check(
            id="heading_h1", category="Headings", label="H1 Tag",
            status="warning",
            message=f"Birden fazla H1 var ({h1_count} adet)",
            value=texts,
            recommendation="Sayfa başına tek H1 kullanın; net içerik hiyerarşisi için önemli",
        ))

    # H2 varlığı
    if h2_count == 0:
        checks.append(Check(
            id="heading_h2", category="Headings", label="H2 Tags",
            status="warning",
            message="Sayfada H2 etiketi yok",
            value="0",
            recommendation="İçeriği bölümlere ayırmak için H2 etiketleri kullanın",
        ))
    else:
        checks.append(Check(
            id="heading_h2", category="Headings", label="H2 Tags",
            status="passed",
            message=f"{h2_count} H2 etiketi var",
            value=str(h2_count),
        ))

    # Başlık hiyerarşisi (seviye atlama kontrolü)
    all_headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    if len(all_headings) > 1:
        prev_level = 0
        skipped: List[str] = []
        for h in all_headings:
            level = int(h.name[1])
            if prev_level > 0 and level > prev_level + 1:
                skipped.append(f"H{prev_level}→H{level}")
            prev_level = level

        if skipped:
            checks.append(Check(
                id="heading_hierarchy", category="Headings", label="Başlık Hiyerarşisi",
                status="warning",
                message=f"Başlık sırası atlanıyor: {', '.join(skipped[:5])}",
                value=", ".join(skipped[:5]),
                recommendation="Başlıkları H1→H2→H3 sırasıyla kullanın; seviye atlamamaya dikkat edin",
            ))
        else:
            checks.append(Check(
                id="heading_hierarchy", category="Headings", label="Başlık Hiyerarşisi",
                status="passed",
                message="Başlık hiyerarşisi doğru sırada",
            ))

    # Başlık dağılımı (bilgi amaçlı)
    counts = []
    for i in range(1, 7):
        n = len(soup.find_all(f"h{i}"))
        if n > 0:
            counts.append(f"H{i}:{n}")
    if counts:
        checks.append(Check(
            id="heading_breakdown", category="Headings", label="Başlık Dağılımı",
            status="passed",
            message=f"Sayfadaki başlık dağılımı: {', '.join(counts)}",
            value=", ".join(counts),
        ))

    return checks


def get_heading_metadata(soup: BeautifulSoup) -> Dict:
    h1_tags = soup.find_all("h1")
    h1_texts = [h.get_text().strip() for h in h1_tags]
    h2_count = len(soup.find_all("h2"))
    return {"h1": h1_texts, "h2_count": h2_count}
