from src.scraper import scrape_all
from src.exporter import export_to_csv


def main():
    products = scrape_all()
    export_to_csv(products)
    print(f"Done. Total products collected: {len(products)}")


if __name__ == "__main__":
    main()
