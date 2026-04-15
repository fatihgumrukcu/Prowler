import os
import pandas as pd

DEFAULT_PATH = "data/output/kazimalic_products.csv"


def export_to_csv(products, output_path=DEFAULT_PATH):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame(products, columns=[
        "product_name",
        "price",
        "product_url",
        "image_url",
        "category_name",
    ])
    df.drop_duplicates(subset=["product_url"], inplace=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
