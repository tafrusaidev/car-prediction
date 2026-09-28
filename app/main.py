from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import Body, FastAPI, HTTPException, Path, Query, Request,Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schema.product import Product, ProductUpdate
from app.service.products import add_product, change_product, get_all_products, remove_product

load_dotenv("app/.env")
app = FastAPI()

@app.middleware("http")
async def lifecycle(request:Request,call_next):
    print("Brfore request")
    response = await call_next(request)
    response.headers["lifecycle"] = "was inside"
    print("After request")
    return response

def common_logic() :
    return "Hello There" 
    

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/",response_model=dict)
def root(dep=Depends(common_logic)):
    DB_PATH = os.getenv("BASE_URL")
    # return {"message": "Welcome to the FastAPI E-commerce App",dep:{"data_path":DB_PATH}}

    return JSONResponse(
        status_code=200,
        content={
            "message": "Welcome to the FastAPI E-commerce App",
            "dependency": dep,
            "data_path": DB_PATH,
        },
    )

@app.get("/products")
def list_products(
    name: Optional[str] = Query(
        default=None,
        max_length=50,
        min_length=1,
        description="Search products by name (case insensitive)",
    ),
    sort_by_price: bool = Query(
        default=False,
        description="Sort products by price",
    ),
    order: str = Query(
        default="asc",
        description="Sort order when sort_by_price=True (asc|desc)",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of items to return",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Pagination offset",
    ),
):
    products = get_all_products()

    if name is not None:
        needle = name.strip().lower()
        products = [
            product for product in products
            if needle in str(product.get("name", "")).lower()
        ]

        if not products:
            raise HTTPException(
                status_code=404,
                detail=f"No products found matching name={name}",
            )

    if sort_by_price:
        reverse = order == "desc"
        products = sorted(products, key=lambda p: p.get("price", 0), reverse=reverse)

    total = len(products)
    products = products[offset : offset + limit]
    return {"total": total, "limit": limit, "items": products}


@app.get("/products/{product_id}")
def get_product(
    product_id: int = Path(
        ...,
        description="ID of the product",
        examples=[1, 2, 3],
    )
):
    products = get_all_products()
    for product in products:
        if product.get("id") == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found!")


@app.post("/products", status_code=201)
def create_product(product: Product):
    product_dict = product.model_dump(mode="json")
    product_dict["id"] = str(uuid4())
    product_dict["created_at"] = datetime.utcnow().isoformat() + "Z"

    try:
        add_product(product_dict)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return product_dict



@app.delete("/products/{product_id}")
def delete_product(
    product_id: int = Path(
        ...,
        description="Product ID",
        examples=[1, 2, 3],
    )
):
    try:
        return remove_product(str(product_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/products/{product_id}")
def update_product(
    product_id: int = Path(
        ...,
        description="Product ID",
        examples=[1, 2, 3],
    ),
    payload: ProductUpdate = Body(...),
):
    try:
        return change_product(
            str(product_id),
            payload.model_dump(mode="json", exclude_unset=True),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
