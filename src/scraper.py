import time
import requests
from bs4 import BeautifulSoup
from src.parser import parse_product

BASE_URL = "https://kazimalic.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
DELAY = 1


def get_category_urls():
    response = requests.get(BASE_URL, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    urls = set()
    for a in soup.select("nav a[href]"):
        href = a["href"]
        if "/urun-kategori/" in href:
            if href.startswith("http"):
                urls.add(href.rstrip("/"))
            else:
                urls.add(BASE_URL + href.rstrip("/"))
    return list(urls)


def scrape_category(category_url, category_name):
    products = []
    seen_urls = set()
    page = 1

    while True:
        url = f"{category_url}/page/{page}/" if page > 1 else category_url
        response = requests.get(url, headers=HEADERS)
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
            product = parse_product(el, category_name, BASE_URL)
            if product and product.get("product_url") not in seen_urls:
                seen_urls.add(product["product_url"])
                products.append(product)
                new_found = True

        if not new_found:
            break

        page += 1
        time.sleep(DELAY)

    return products


def scrape_all():
    all_products = []
    seen_global = set()
    category_urls = get_category_urls()
    print(f"Found {len(category_urls)} categories.")

    for cat_url in category_urls:
        category_name = cat_url.rstrip("/").split("/")[-1].replace("-", " ").title()
        print(f"Scraping: {category_name} ({cat_url})")
        products = scrape_category(cat_url, category_name)
        for p in products:
            if p["product_url"] not in seen_global:
                seen_global.add(p["product_url"])
                all_products.append(p)
        print(f"  → {len(products)} products")
        time.sleep(DELAY)

    return all_products
