import os
import sys

import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.service.products import get_all_products


def main():
    st.set_page_config(page_title="E-commerce Catalog", page_icon="🛍️")
    st.title("FAStAPI Products Dashboard")

    products = get_all_products()

    if not products:
        st.info("No products available right now.")
        return

    for product in products:
        with st.container():
            st.subheader(product.get("name", "Unnamed product"))
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(product.get("description", "No description provided."))
                st.caption(
                    f"Category: {product.get('category', 'N/A')} • "
                    f"Brand: {product.get('brand', 'N/A')}"
                )

            with col2:
                st.metric("Price", f"${product.get('price', 0):,.2f}")
                st.write(f"Stock: {product.get('stock', 0)}")

            st.write("---")


if __name__ == "__main__":
    main()
