from datetime import datetime
from typing import Annotated, Literal, Optional
from uuid import UUID, uuid4

from pydantic import AnyUrl, BaseModel, EmailStr, Field, computed_field, field_validator, model_validator

# Create Pydantic


class DimensionsCM(BaseModel):
    length: Annotated[
        float,
        Field(gt=0, title="Length in cm", examples=[10.5]),
    ]
    width: Annotated[
        float,
        Field(gt=0, title="Width in cm", examples=[5.2]),
    ]
    height: Annotated[
        float,
        Field(gt=0, title="Height in cm", examples=[2.8]),
    ]


class Seller(BaseModel):
    id: UUID
    name: Annotated[
        str,
        Field(
            min_length=2,
            max_length=60,
            title="Seller Name",
            description="Name of the seller (2-60 characters)",
            examples=["Mi Store", "Apple Store India"],
        ),
    ]
    email: EmailStr
    website: AnyUrl


class Product(BaseModel):
    id: int | UUID = Field(default_factory=lambda: uuid4())
    name: Annotated[
        str,
        Field(min_length=3, max_length=100, title="Product name"),
    ]
    description: Annotated[
        str,
        Field(min_length=10, max_length=500, title="Product description"),
    ]
    category: Annotated[
        Literal["Electronics", "Wearables", "Home Appliances", "Computers"],
        Field(title="Product category"),
    ]
    brand: Annotated[
        str,
        Field(min_length=2, max_length=50, title="Product brand"),
    ]
    price: Annotated[
        float,
        Field(gt=0, title="Product price", examples=[249.99]),
    ]
    stock: Annotated[
        int,
        Field(ge=0, title="Available stock"),
    ]
    rating: Annotated[
        float,
        Field(ge=0, le=5, title="Customer rating"),
    ]
    is_active: Annotated[
        bool,
        Field(title="Whether the product is active"),
    ]
    tags: Annotated[
        list[str],
        Field(min_length=1, title="Search tags"),
    ]
    image_urls: Annotated[
        Optional[list[AnyUrl]],
        Field(default=None, description="Optional product image URLs"),
    ]
    dimensions_cm: Annotated[
        Optional[DimensionsCM],
        Field(default=None, title="Dimensions in cm"),
    ]
    seller: Optional[Seller] = None
    discount_percent: Annotated[
        float,
        Field(default=0, ge=0, le=100, title="Discount percent"),
    ]
    sku: Annotated[
        Optional[str],
        Field(default=None, examples=["ABC-234"]),
    ]
    created_at: Optional[datetime] = None

    @field_validator("sku", mode="after")
    @classmethod
    def validate_sku_format(cls, value: Optional[str]):
        if value is None:
            return value
        if "-" not in value:
            raise ValueError("SKU must have '-' ")
        last = value.split("-")[-1]
        if not (len(last) == 3 and last.isdigit()):
            raise ValueError("SKU must end with 3-digit sequence like -234")
        return value

    @model_validator(mode="after")
    def validate_business_rules(self):
        if self.stock == 0 and self.is_active is True:
            raise ValueError("If stock is 0, is_active must be False")
        if self.discount_percent > 0 and self.rating == 0:
            raise ValueError("Discounted product must have a rating (rating != 0)")
        return self

    @computed_field
    @property
    def final_price(self) -> float:
        return round(self.price * (1 - self.discount_percent / 100), 2)


# Update Pydantic


class DimensionsCMUpdate(BaseModel):
    length: Optional[float] = Field(default=None, gt=0, title="Length in cm", examples=[10.5])
    width: Optional[float] = Field(default=None, gt=0, title="Width in cm", examples=[5.2])
    height: Optional[float] = Field(default=None, gt=0, title="Height in cm", examples=[2.8])


class SellerUpdate(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=60,
        title="Seller Name",
        description="Name of the seller (2-60 characters)",
        examples=["Mi Store", "Apple Store India"],
    )
    email: Optional[EmailStr] = None
    website: Optional[AnyUrl] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=100, title="Product name")
    description: Optional[str] = Field(default=None, min_length=10, max_length=500, title="Product description")
    category: Optional[Literal["Electronics", "Wearables", "Home Appliances", "Computers"]] = Field(
        default=None,
        title="Product category",
    )
    brand: Optional[str] = Field(default=None, min_length=2, max_length=50, title="Product brand")
    price: Optional[float] = Field(default=None, gt=0, title="Product price", examples=[249.99])
    stock: Optional[int] = Field(default=None, ge=0, title="Available stock")
    rating: Optional[float] = Field(default=None, ge=0, le=5, title="Customer rating")
    is_active: Optional[bool] = Field(default=None, title="Whether the product is active")
    tags: Optional[list[str]] = Field(default=None, min_length=1, title="Search tags")
    image_urls: Optional[list[AnyUrl]] = Field(default=None, description="Optional product image URLs")
    dimensions_cm: Optional[DimensionsCMUpdate] = None
    seller: Optional[SellerUpdate] = None
    discount_percent: Optional[float] = Field(default=None, ge=0, le=100, title="Discount percent")
    sku: Optional[str] = Field(default=None, examples=["ABC-234"])
    created_at: Optional[datetime] = None

    @field_validator("sku", mode="after")
    @classmethod
    def validate_sku_format(cls, value: Optional[str]):
        if value is None:
            return value
        if "-" not in value:
            raise ValueError("SKU must have '-' ")
        last = value.split("-")[-1]
        if not (len(last) == 3 and last.isdigit()):
            raise ValueError("SKU must end with 3-digit sequence like -234")
        return value

