def parse_product(element, category_name, base_url):
    try:
        name_el = element.select_one(".woocommerce-loop-product__title, .etheme-product-grid-title, h2, h3")
        product_name = name_el.get_text(strip=True) if name_el else ""

        price_el = element.select_one("span.price .woocommerce-Price-amount, span.price .amount, span.price")
        price = price_el.get_text(strip=True) if price_el else ""

        link_el = element.select_one(".etheme-product-grid-image a[href], h2 a[href], a[href]")
        if link_el:
            href = link_el["href"]
            product_url = href if href.startswith("http") else base_url + href
        else:
            product_url = ""

        img_el = element.select_one(".etheme-product-grid-image img, img")
        if img_el:
            src = img_el.get("src") or img_el.get("data-src", "")
            image_url = src if src.startswith("http") else base_url + src
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
