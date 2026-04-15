import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://istockina.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}
DELAY = 1


def get_category_urls():
    response = requests.get(BASE_URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    urls = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/urun-kategori/" in href:
            url = href if href.startswith("http") else BASE_URL + href
            urls.add(url.rstrip("/"))
    return list(urls)


def _parse_product(element, category_name):
    try:
        # Title
        name_el = element.select_one(
            "h2.woocommerce-loop-product__title, .etheme-product-grid-title"
        )
        product_name = name_el.get_text(strip=True) if name_el else ""

        # Price — prefer non-sale amount, fall back to any amount
        price_el = element.select_one(
            "span.price ins .woocommerce-Price-amount, "
            "span.price .woocommerce-Price-amount"
        )
        price = price_el.get_text(strip=True) if price_el else ""

        # Link — anchor inside image wrapper is most reliable
        link_el = element.select_one(".etheme-product-grid-image a[href]")
        if not link_el:
            link_el = element.select_one("a[href]")
        if link_el:
            href = link_el["href"]
            product_url = href if href.startswith("http") else BASE_URL + href
        else:
            product_url = ""

        # Image
        img_el = element.select_one(".etheme-product-grid-image img")
        if not img_el:
            img_el = element.select_one("img")
        if img_el:
            src = (
                img_el.get("src")
                or img_el.get("data-src")
                or img_el.get("data-lazy-src", "")
            )
            image_url = src if (src and src.startswith("http")) else (BASE_URL + src if src else "")
        else:
            image_url = ""

        if not product_name and not product_url:
            return None

        return {
            "product_name": product_name,
            "price": price,
            "product_url": product_url,
            "image_url": image_url,
            "category_name": category_name,
        }
    except Exception:
        return None


def scrape_category(category_url, category_name):
    products = []
    seen_urls = set()
    page = 1

    while True:
        url = f"{category_url}/page/{page}/" if page > 1 else f"{category_url}/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 404:
            break
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        product_elements = soup.select(".etheme-product-grid-item")

        if not product_elements:
            break

        new_found = False
        for el in product_elements:
            product = _parse_product(el, category_name)
            if product and product.get("product_url") not in seen_urls:
                seen_urls.add(product["product_url"])
                products.append(product)
                new_found = True

        if not new_found:
            break

        page += 1
        time.sleep(DELAY)

    return products


def scrape_istockina():
    all_products = []
    seen_global = set()
    category_urls = get_category_urls()
    print(f"[istockina] Found {len(category_urls)} categories.")

    for cat_url in category_urls:
        category_name = cat_url.rstrip("/").split("/")[-1].replace("-", " ").title()
        print(f"[istockina] Scraping: {category_name} ({cat_url})")
        products = scrape_category(cat_url, category_name)
        for p in products:
            if p["product_url"] not in seen_global:
                seen_global.add(p["product_url"])
                all_products.append(p)
        print(f"  -> {len(products)} products")
        time.sleep(DELAY)

    return all_products
