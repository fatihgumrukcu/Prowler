import sys

from src.scraper import scrape_all
from src.scraper_istockina import scrape_istockina
from src.exporter import export_to_csv

SITE_CSV = {
    "kazimalic": "data/output/kazimalic_products.csv",
    "istockina":  "data/output/istockina_products.csv",
}


def main():
    site = "kazimalic"
    for arg in sys.argv[1:]:
        if arg.startswith("--site="):
            site = arg.split("=", 1)[1]

    if site == "istockina":
        products = scrape_istockina()
    else:
        products = scrape_all()

    output_path = SITE_CSV.get(site, SITE_CSV["kazimalic"])
    export_to_csv(products, output_path)
    print(f"Done. Total products collected: {len(products)}")


if __name__ == "__main__":
    main()
