import os
import pandas as pd


def export_to_csv(products, output_path):
    if not output_path:
        raise ValueError("output_path is required")
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
