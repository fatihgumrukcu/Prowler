from typing import List, Dict
from models import Check


def analyze_http_tech(
    headers: Dict[str, str],
    response_time_ms: int,
    page_url: str,
) -> List[Check]:
    checks = []
    h = {k.lower(): v for k, v in headers.items()}

    # 1. X-Robots-Tag
    x_robots = h.get("x-robots-tag", "")
    if x_robots:
        xl = x_robots.lower()
        if "noindex" in xl:
            checks.append(Check(
                id="http_x_robots_noindex", category="HTTP", label="X-Robots-Tag: noindex",
                status="warning",
                message="Sunucu X-Robots-Tag: noindex gönderiyor — sayfa indekslenmeyecek",
                value=x_robots,
                recommendation="Sayfanın indekslenmesini istiyorsanız bu header'ı kaldırın",
            ))
        elif "nofollow" in xl:
            checks.append(Check(
                id="http_x_robots_nofollow", category="HTTP", label="X-Robots-Tag: nofollow",
                status="warning",
                message="Sunucu X-Robots-Tag: nofollow gönderiyor — linkler takip edilmeyecek",
                value=x_robots,
                recommendation="Link equity aktarmak istiyorsanız bu direktifi kaldırın",
            ))
        else:
            checks.append(Check(
                id="http_x_robots_tag", category="HTTP", label="X-Robots-Tag",
                status="passed",
                message=f"X-Robots-Tag zararsız: {x_robots}",
                value=x_robots,
            ))

    # 2. Content-Type + charset
    content_type = h.get("content-type", "")
    if not content_type:
        checks.append(Check(
            id="http_content_type", category="HTTP", label="Content-Type",
            status="warning",
            message="Content-Type header eksik",
            recommendation="Sunucunun 'Content-Type: text/html; charset=utf-8' göndermesi gerekiyor",
        ))
    elif "text/html" not in content_type:
        checks.append(Check(
            id="http_content_type", category="HTTP", label="Content-Type",
            status="warning",
            message=f"Beklenmeyen Content-Type: {content_type}",
            value=content_type,
            recommendation="HTML sayfalar için 'text/html; charset=utf-8' kullanın",
        ))
    elif "utf-8" not in content_type.lower() and "charset" not in content_type.lower():
        checks.append(Check(
            id="http_content_type", category="HTTP", label="Content-Type",
            status="warning",
            message="Content-Type'ta charset belirtilmemiş",
            value=content_type,
            recommendation="'Content-Type: text/html; charset=utf-8' olarak güncelleyin",
        ))
    else:
        checks.append(Check(
            id="http_content_type", category="HTTP", label="Content-Type",
            status="passed",
            message="Content-Type doğru",
            value=content_type,
        ))

    # 3. Sıkıştırma (gzip / brotli)
    encoding = h.get("content-encoding", "").lower()
    if encoding in ("gzip", "br", "brotli", "zstd", "deflate"):
        label_map = {"br": "Brotli", "brotli": "Brotli", "gzip": "Gzip",
                     "zstd": "Zstandard", "deflate": "Deflate"}
        label = label_map.get(encoding, encoding.upper())
        checks.append(Check(
            id="http_compression", category="HTTP", label="HTTP Sıkıştırma",
            status="passed",
            message=f"Sıkıştırma aktif: {label}",
            value=encoding,
        ))
    else:
        checks.append(Check(
            id="http_compression", category="HTTP", label="HTTP Sıkıştırma",
            status="warning",
            message="HTTP sıkıştırma (gzip / brotli) kullanılmıyor",
            value=encoding or "yok",
            recommendation="Sunucuda gzip veya brotli etkinleştirin; sayfa boyutunu %60-80 azaltır",
        ))

    # 4. Yanıt süresi
    if response_time_ms > 0:
        if response_time_ms > 3000:
            checks.append(Check(
                id="http_response_time", category="HTTP", label="Sunucu Yanıt Süresi",
                status="failed",
                message=f"Sunucu çok yavaş yanıt veriyor: {response_time_ms}ms (kritik eşik: 3000ms)",
                value=f"{response_time_ms}ms",
                recommendation="Sunucu taraflı önbellek, CDN ve veritabanı optimizasyonu uygulayın",
            ))
        elif response_time_ms > 1500:
            checks.append(Check(
                id="http_response_time", category="HTTP", label="Sunucu Yanıt Süresi",
                status="warning",
                message=f"Sunucu yanıt süresi yavaş: {response_time_ms}ms (önerilen: <1500ms)",
                value=f"{response_time_ms}ms",
                recommendation="TTFB iyileştirmesi için sunucu önbelleği veya CDN kullanın",
            ))
        else:
            checks.append(Check(
                id="http_response_time", category="HTTP", label="Sunucu Yanıt Süresi",
                status="passed",
                message=f"Sunucu yanıt süresi iyi: {response_time_ms}ms",
                value=f"{response_time_ms}ms",
            ))

    # 5. Önbellekleme (Cache-Control / ETag / Last-Modified)
    cache_control = h.get("cache-control", "")
    etag = h.get("etag", "")
    last_modified = h.get("last-modified", "")
    if cache_control or etag or last_modified:
        parts = []
        if cache_control:
            parts.append(f"Cache-Control: {cache_control}")
        if etag:
            parts.append("ETag: var")
        if last_modified:
            parts.append(f"Last-Modified: {last_modified}")
        checks.append(Check(
            id="http_caching", category="HTTP", label="HTTP Önbellekleme",
            status="passed",
            message="Önbellekleme header'ları mevcut",
            value=" | ".join(parts),
        ))
    else:
        checks.append(Check(
            id="http_caching", category="HTTP", label="HTTP Önbellekleme",
            status="warning",
            message="Cache-Control, ETag ve Last-Modified header'larının tümü eksik",
            recommendation="Cache-Control ve ETag ekleyin; tekrar ziyaretlerde sayfa daha hızlı yüklenir",
        ))

    # 6. HSTS (sadece HTTPS sayfalar için anlamlı)
    if page_url.startswith("https://"):
        hsts = h.get("strict-transport-security", "")
        if hsts:
            checks.append(Check(
                id="http_hsts", category="HTTP", label="HSTS",
                status="passed",
                message="Strict-Transport-Security header mevcut",
                value=hsts[:200],
            ))
        else:
            checks.append(Check(
                id="http_hsts", category="HTTP", label="HSTS",
                status="warning",
                message="HTTPS kullanılıyor ama HSTS header eksik",
                recommendation="Strict-Transport-Security: max-age=31536000; includeSubDomains ekleyin",
            ))

    return checks


def get_http_metadata(headers: Dict[str, str], response_time_ms: int) -> Dict:
    h = {k.lower(): v for k, v in headers.items()}
    encoding = h.get("content-encoding", "").lower()
    if "br" in encoding or "brotli" in encoding:
        compression = "brotli"
    elif "gzip" in encoding:
        compression = "gzip"
    elif "deflate" in encoding:
        compression = "deflate"
    elif encoding:
        compression = encoding
    else:
        compression = None
    return {"response_time_ms": response_time_ms, "compression": compression}
