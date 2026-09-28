# FASTAPI Products Dashboard

This project contains a FastAPI backend and a Streamlit dashboard for managing products.

## Project structure

- `backend/main.py` - FastAPI API
- `streamlit_app.py` - Streamlit UI
- `data/products.json` - product storage
- `.env.example` - environment config

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the FastAPI backend:
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Start the Streamlit dashboard:
   ```bash
   streamlit run streamlit_app.py
   ```

## API endpoints

- `GET /` - API status
- `GET /products` - fetch products with optional search and pagination
- `GET /products/{id}` - fetch one product
- `POST /products` - add a new product
- `PUT /products/{id}` - update a product
- `DELETE /products/{id}` - delete a product

## Dashboard features

- View all products
- Search products by name or description
- Add new products from the UI
- Show product details like price, stock, and category
