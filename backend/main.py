import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "products.json"

app = FastAPI(title="FASTAPI Products Dashboard API")


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=5, max_length=500)
    category: str = Field(..., min_length=2, max_length=50)
    brand: str = Field(default="Generic", min_length=2, max_length=50)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    rating: float = Field(default=0.0, ge=0, le=5)
    is_active: bool = True
    image_url: Optional[str] = None


class ProductUpdate(ProductCreate):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, min_length=5, max_length=500)
    category: Optional[str] = Field(default=None, min_length=2, max_length=50)
    brand: Optional[str] = Field(default=None, min_length=2, max_length=50)
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    is_active: Optional[bool] = None
    image_url: Optional[str] = None


def load_products() -> list[dict]:
    if not DATA_FILE.exists():
        return []

    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass

    return []


def save_products(products: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(products, indent=2), encoding="utf-8")


def next_product_id(products: list[dict]) -> int:
    if not products:
        return 1
    return max(int(product.get("id", 0)) for product in products) + 1


@app.get("/")
def read_root():
    return {"message": "FASTAPI Products Dashboard API is running"}


@app.get("/products")
def get_products(
    name: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    products = load_products()

    if name:
        query = name.lower().strip()
        products = [
            product
            for product in products
            if query in str(product.get("name", "")).lower()
            or query in str(product.get("description", "")).lower()
        ]

    if category:
        category_query = category.lower().strip()
        products = [
            product
            for product in products
            if category_query in str(product.get("category", "")).lower()
        ]

    total = len(products)
    page = products[offset : offset + limit]

    return {
        "items": page,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/products/{product_id}")
def get_product(product_id: int):
    products = load_products()
    for product in products:
        if int(product.get("id")) == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    products = load_products()
    new_product = product.model_dump()
    new_product["id"] = next_product_id(products)
    new_product["created_at"] = datetime.now(timezone.utc).isoformat()
    products.append(new_product)
    save_products(products)
    return new_product


@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductUpdate):
    products = load_products()

    for index, current in enumerate(products):
        if int(current.get("id")) == product_id:
            updated = current.copy()
            payload = product.model_dump(exclude_unset=True)
            updated.update(payload)
            updated["updated_at"] = datetime.now(timezone.utc).isoformat()
            products[index] = updated
            save_products(products)
            return updated

    raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    products = load_products()
    for index, product in enumerate(products):
        if int(product.get("id")) == product_id:
            deleted = products.pop(index)
            save_products(products)
            return {"message": "Product deleted", "deleted_product": deleted}

    raise HTTPException(status_code=404, detail="Product not found")
