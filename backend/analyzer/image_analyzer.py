import os
from typing import List, Dict
from urllib.parse import urlparse as _urlparse
from bs4 import BeautifulSoup
from models import Check

_MODERN_EXTS = {".webp", ".avif", ".svg"}
_LEGACY_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}


def _src_ext(src: str) -> str:
    """Return lowercase extension from image src, ignoring query strings."""
    path = _urlparse(src).path.lower()
    _, ext = os.path.splitext(path)
    return ext


def analyze_images(soup: BeautifulSoup) -> List[Check]:
    checks = []
    images = soup.find_all("img")
    total = len(images)

    # Alt attribute
    missing_alt = sum(1 for img in images if not (img.get("alt") or "").strip())

    if total == 0:
        checks.append(Check(
            id="image_alt", category="Images", label="Görsel Alt Attribute",
            status="passed",
            message="Sayfada görsel yok",
            value="0",
        ))
        return checks

    if missing_alt == 0:
        checks.append(Check(
            id="image_alt", category="Images", label="Görsel Alt Attribute",
            status="passed",
            message=f"Tüm {total} görselde alt attribute var",
            value=f"{total} görsel, 0 eksik",
        ))
    else:
        pct = int(missing_alt / total * 100)
        checks.append(Check(
            id="image_alt", category="Images", label="Görsel Alt Attribute",
            status="warning",
            message=f"{missing_alt}/{total} görselde alt attribute eksik (%{pct})",
            value=f"{missing_alt}/{total} eksik",
            recommendation="Tüm görsellere açıklayıcı alt text ekleyin — erişilebilirlik ve SEO için gerekli",
        ))

    # width/height eksikliği (CLS)
    no_dims = [img for img in images if not (img.get("width") and img.get("height"))]
    if no_dims:
        pct = int(len(no_dims) / total * 100)
        status = "failed" if pct > 50 else "warning"
        checks.append(Check(
            id="image_dimensions", category="Images", label="Görsel Boyutları (CLS)",
            status=status,
            message=f"{len(no_dims)}/{total} görselde width/height eksik (%{pct}) — CLS bozulabilir",
            value=f"{len(no_dims)}/{total}",
            recommendation="Tüm <img> etiketlerine width ve height attribute ekleyin; layout shift engellenir",
        ))
    else:
        checks.append(Check(
            id="image_dimensions", category="Images", label="Görsel Boyutları (CLS)",
            status="passed",
            message=f"Tüm {total} görselde width/height mevcut",
        ))

    # Modern format (WebP/AVIF)
    legacy_imgs = [
        img for img in images
        if _src_ext(img.get("src") or "") in _LEGACY_EXTS
    ]
    if legacy_imgs:
        pct = int(len(legacy_imgs) / total * 100)
        checks.append(Check(
            id="image_modern_format", category="Images", label="Modern Görsel Formatı",
            status="warning",
            message=f"{len(legacy_imgs)}/{total} görsel eski format (JPG/PNG/GIF) kullanıyor (%{pct})",
            value=f"{len(legacy_imgs)}/{total} eski format",
            recommendation="WebP veya AVIF formatına geçin; dosya boyutunu %25-50 azaltır",
        ))
    else:
        non_ext = sum(1 for img in images if not _src_ext(img.get("src") or ""))
        if non_ext == total:
            # Tüm src'ler data-url veya dinamik — değerlendirilemez
            checks.append(Check(
                id="image_modern_format", category="Images", label="Modern Görsel Formatı",
                status="passed",
                message="Görsel kaynak uzantısı tespit edilemedi (dinamik/data-url)",
            ))
        else:
            checks.append(Check(
                id="image_modern_format", category="Images", label="Modern Görsel Formatı",
                status="passed",
                message="Görseller modern format (WebP/AVIF/SVG) kullanıyor",
            ))

    # İlk 3 görselde loading=lazy (LCP'yi bozar)
    first_imgs = images[:3]
    lazy_on_early = [img for img in first_imgs if (img.get("loading") or "").lower() == "lazy"]
    if lazy_on_early:
        checks.append(Check(
            id="image_lazy_above_fold", category="Images", label="Lazy Load / LCP",
            status="warning",
            message=f"İlk {len(first_imgs)} görselden {len(lazy_on_early)} tanesi loading=lazy — LCP skoru düşebilir",
            recommendation="Sayfanın üstündeki (above-the-fold) görsellerde loading='lazy' kullanmayın",
        ))
    else:
        checks.append(Check(
            id="image_lazy_above_fold", category="Images", label="Lazy Load / LCP",
            status="passed",
            message="İlk görsellerde lazy load yok — LCP etkilenmez",
        ))

    # Uzun dosya adı
    long_names = []
    for img in images:
        src = img.get("src") or ""
        if src and not src.startswith("data:"):
            filename = os.path.basename(_urlparse(src).path)
            if len(filename) > 50:
                long_names.append(filename[:70])

    if long_names:
        checks.append(Check(
            id="image_filename_length", category="Images", label="Görsel Dosya Adı",
            status="warning",
            message=f"{len(long_names)} görselin dosya adı 50 karakterden uzun",
            value=long_names[0],
            recommendation="Kısa, açıklayıcı ve tire (-) ile ayrılmış dosya adları kullanın",
        ))
    else:
        checks.append(Check(
            id="image_filename_length", category="Images", label="Görsel Dosya Adı",
            status="passed",
            message="Görsel dosya adları uygun uzunlukta",
        ))

    return checks


def get_image_metadata(soup: BeautifulSoup) -> Dict:
    images = soup.find_all("img")
    total = len(images)
    missing_alt = sum(1 for img in images if not (img.get("alt") or "").strip())
    return {"images_total": total, "images_missing_alt": missing_alt}
