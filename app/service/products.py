import json
from pathlib import Path
from typing import Any, Dict, List

from pydantic import ValidationError

from app.schema.product import Product

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "products.json"


def read_products() -> list[dict[str, Any]]:
    """Read products from data/products.json safely.

    Returns an empty list if the file is missing, empty, or invalid.
    """
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8-sig") as file:
            content = file.read().strip()

        if not content:
            return []


        data = json.loads(content)
        if isinstance(data, list):
            products = []
            for item in data:
                try:
                    products.append(Product.model_validate(item).model_dump())
                except ValidationError:
                    continue
            return products
        return []

    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError, ValueError):
        return []


def get_all_products() -> list[dict[str, Any]]:
    return read_products()

def save_products(products: List[Dict]):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(products, file, indent=4, ensure_ascii=False)
        
def add_product(product:Dict) -> Dict:
    products = get_all_products()
    
    if any(p["sku"] == product["sku"] for p in products):
        raise ValueError("SKU already exists.")
                         
    products.append(product)
    save_products(products)
    return product

def remove_product(id: str) -> dict[str, Any]:
    products = get_all_products()
    for idx, p in enumerate(products):
        if str(p["id"]) == str(id):
            deleted = products.pop(idx)
            save_products(products)
            return deleted
    raise ValueError("Product not found")

def change_product(product_id: str, update_data: dict):
    products = get_all_products()
    for index, product in enumerate(products):
        if str(product.get("id")) != str(product_id):
            continue

        for key, value in update_data.items():
            if value is None:
                continue

            if isinstance(value, dict) and isinstance(product.get(key), dict):
                product[key].update(value)
            else:
                product[key] = value

        products[index] = product
        save_products(products)
        return product

    raise ValueError("Product not found!")