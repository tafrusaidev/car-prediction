import os
import sys
from typing import Any

import requests
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@st.cache_data(ttl=30)
def fetch_products() -> list[dict[str, Any]]:
    response = requests.get(f"{API_BASE_URL}/products", timeout=10)
    response.raise_for_status()
    payload = response.json()
    return payload.get("items", [])


def add_product(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{API_BASE_URL}/products", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> None:
    st.set_page_config(page_title="FASTAPI Products Dashboard", layout="wide")
    st.title("FASTAPI Products Dashboard")

    search_query = st.text_input("Search products", placeholder="Search by name or description")
    category_filter = st.text_input("Filter by category", placeholder="e.g. Electronics")

    try:
        products = fetch_products()
    except Exception as exc:
        st.error(f"Could not load products from backend: {exc}")
        st.info("Make sure the FastAPI server is running at http://localhost:8000")
        return

    if search_query:
        query = search_query.lower().strip()
        products = [
            product
            for product in products
            if query in str(product.get("name", "")).lower()
            or query in str(product.get("description", "")).lower()
        ]

    if category_filter:
        category_query = category_filter.lower().strip()
        products = [
            product
            for product in products
            if category_query in str(product.get("category", "")).lower()
        ]

    st.subheader(f"Products ({len(products)})")

    if not products:
        st.warning("No products found for the current filter.")

    cols = st.columns(3)
    for index, product in enumerate(products):
        with cols[index % 3]:
            st.markdown(f"### {product.get('name', 'Unnamed Product')}")
            st.write(product.get("description", "No description available."))
            st.write(f"Category: {product.get('category', 'N/A')}")
            st.write(f"Brand: {product.get('brand', 'N/A')}")
            st.write(f"Price: ${product.get('price', 0):,.2f}")
            st.write(f"Stock: {product.get('stock', 0)}")
            st.write(f"Rating: {product.get('rating', 0)} / 5")
            if product.get("image_url"):
                st.image(product["image_url"], width=220)
            st.divider()

    st.subheader("Add New Product")
    with st.form("add_product_form"):
        name = st.text_input("Name")
        description = st.text_area("Description")
        category = st.text_input("Category")
        brand = st.text_input("Brand", value="Generic")
        price = st.number_input("Price", min_value=0.01, step=0.01)
        stock = st.number_input("Stock", min_value=0, step=1)
        rating = st.number_input("Rating", min_value=0.0, max_value=5.0, step=0.1, value=0.0)
        is_active = st.checkbox("Active", value=True)
        image_url = st.text_input("Image URL", placeholder="https://example.com/image.jpg")

        submitted = st.form_submit_button("Add Product")

        if submitted:
            payload = {
                "name": name,
                "description": description,
                "category": category,
                "brand": brand,
                "price": float(price),
                "stock": int(stock),
                "rating": float(rating),
                "is_active": bool(is_active),
                "image_url": image_url or None,
            }

            try:
                created = add_product(payload)
                st.success(f"Product added successfully: {created.get('name')}")
                st.rerun()
            except Exception as exc:
                st.error(f"Failed to add product: {exc}")


if __name__ == "__main__":
    main()
