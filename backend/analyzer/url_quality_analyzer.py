from typing import List
from urllib.parse import urlparse, parse_qs, unquote
from models import Check

_TR_CHARS = set("ğüşıöçĞÜŞİÖÇ")


def analyze_url_quality(page_url: str) -> List[Check]:
    checks = []
    try:
        parsed = urlparse(page_url)
    except Exception:
        return checks

    path = parsed.path
    decoded_url = unquote(page_url)

    # 1. Türkçe karakter
    tr_found = [c for c in decoded_url if c in _TR_CHARS]
    if tr_found:
        unique = "".join(dict.fromkeys(tr_found))
        checks.append(Check(
            id="url_tr_chars", category="URL", label="URL Türkçe Karakter",
            status="warning",
            message=f"URL'de Türkçe karakter var: {unique}",
            value=decoded_url[:200],
            recommendation="URL'lerde Türkçe karakter yerine ASCII karşılığını kullanın (ş→s, ğ→g, ı→i vb.)",
        ))
    else:
        checks.append(Check(
            id="url_tr_chars", category="URL", label="URL Türkçe Karakter",
            status="passed",
            message="URL'de Türkçe karakter yok",
        ))

    # 2. Boşluk (%20)
    if "%20" in page_url:
        checks.append(Check(
            id="url_spaces", category="URL", label="URL Boşluk",
            status="warning",
            message="URL'de boşluk (encode edilmiş %20) var",
            value=page_url[:200],
            recommendation="URL'lerde boşluk yerine tire (-) kullanın",
        ))
    else:
        checks.append(Check(
            id="url_spaces", category="URL", label="URL Boşluk",
            status="passed",
            message="URL'de boşluk yok",
        ))

    # 3. Büyük harf (path kısmında)
    if any(c.isupper() for c in path):
        checks.append(Check(
            id="url_uppercase", category="URL", label="URL Büyük Harf",
            status="warning",
            message="URL path'inde büyük harf var",
            value=path[:200],
            recommendation="URL'leri tamamen küçük harfle yazın; büyük/küçük versiyonlar için 301 yönlendirmesi ekleyin",
        ))
    else:
        checks.append(Check(
            id="url_uppercase", category="URL", label="URL Büyük Harf",
            status="passed",
            message="URL tamamen küçük harf",
        ))

    # 4. URL uzunluğu
    url_len = len(page_url)
    if url_len > 115:
        checks.append(Check(
            id="url_length", category="URL", label="URL Uzunluğu",
            status="warning",
            message=f"URL çok uzun: {url_len} karakter (önerilen: ≤115)",
            value=f"{url_len} karakter",
            recommendation="Gereksiz parametreleri ve derin klasör yapısını kaldırarak URL'yi kısaltın",
        ))
    else:
        checks.append(Check(
            id="url_length", category="URL", label="URL Uzunluğu",
            status="passed",
            message=f"URL uzunluğu uygun: {url_len} karakter",
            value=f"{url_len} karakter",
        ))

    # 5. Fazla query parametresi
    if parsed.query:
        param_count = len(parse_qs(parsed.query))
        if param_count > 3:
            checks.append(Check(
                id="url_query_params", category="URL", label="Query Parametre Sayısı",
                status="warning",
                message=f"Çok fazla query parametresi: {param_count} (önerilen: ≤3)",
                value=f"{param_count} parametre",
                recommendation="Parametre sayısını azaltın; SEO dostu URL yapısı kullanın",
            ))
        else:
            checks.append(Check(
                id="url_query_params", category="URL", label="Query Parametre Sayısı",
                status="passed",
                message=f"Query parametre sayısı uygun: {param_count}",
                value=f"{param_count} parametre",
            ))

    # 6. Alt çizgi (tire önerilir)
    if "_" in path:
        checks.append(Check(
            id="url_underscore", category="URL", label="URL Alt Çizgi",
            status="warning",
            message="URL path'inde alt çizgi (_) var; tire (-) tercih edilmeli",
            value=path[:200],
            recommendation="Alt çizgi yerine tire kullanın (örn: /blog_yazisi → /blog-yazisi)",
        ))
    else:
        checks.append(Check(
            id="url_underscore", category="URL", label="URL Alt Çizgi",
            status="passed",
            message="URL'de alt çizgi yok",
        ))

    return checks
