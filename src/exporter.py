import os
import pandas as pd

OUTPUT_PATH = "data/output/products.csv"


def export_to_csv(products):
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df = pd.DataFrame(products, columns=[
        "product_name",
        "price",
        "product_url",
        "image_url",
        "category_name",
    ])
    df.drop_duplicates(subset=["product_url"], inplace=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
