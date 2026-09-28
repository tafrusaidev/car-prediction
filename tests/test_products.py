import pytest
from pydantic import ValidationError

from app.schema.product import DimensionsCMUpdate, ProductUpdate, SellerUpdate
from app.service.products import get_all_products, remove_product


def test_product_update_models_allow_partial_updates_and_keep_validations():
    data = {
        "name": "Updated product",
        "price": 99.99,
        "dimensions_cm": {"length": 10.5, "width": 7.5},
        "seller": {"name": "New Seller", "email": "seller@gmail.com", "website": "https://example.com"},
    }

    model = ProductUpdate.model_validate(data)
    assert model.name == "Updated product"
    assert model.price == 99.99
    assert model.dimensions_cm is not None
    assert model.seller is not None

    with pytest.raises(ValidationError):
        ProductUpdate.model_validate({"price": 0})

    with pytest.raises(ValidationError):
        DimensionsCMUpdate.model_validate({"length": 0})

    with pytest.raises(ValidationError):
        SellerUpdate.model_validate({"name": "A"})


def test_get_all_products_reads_existing_json():
    products = get_all_products()
    assert len(products) > 0
    assert products[0]["id"] == 1


def test_remove_product_deletes_existing_product():
    deleted = remove_product("3")
    assert deleted["id"] == 3
    assert "3" not in [str(p["id"]) for p in get_all_products()]
