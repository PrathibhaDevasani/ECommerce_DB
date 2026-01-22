# ECommerce API

A FastAPI-based REST API for managing products and orders.

## Prerequisites

- Python 3.9+
- PostgreSQL

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/PrathibhaDevasani/ECommerce_DB.git
   cd ECommerce_DB
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   ```sql
   CREATE DATABASE ecommerce_db;
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and update with your database credentials:
   ```
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/ecommerce_db
   ```

6. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at http://127.0.0.1:8000

## API Documentation

Once running, visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | List all products (supports `min_price`, `max_price` filters) |
| POST | `/products` | Create a product |
| GET | `/products/{id}` | Get product by ID |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Delete product |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/place-order` | Place a new order |
| GET | `/orders` | List all orders |
| GET | `/order/{id}` | Get order by ID |

## Example Usage

**Create a product:**
```bash
curl -X POST "http://127.0.0.1:8000/products?name=Laptop&price=999.99"
```

**Place an order:**
```bash
curl -X POST http://127.0.0.1:8000/place-order \
  -H "Content-Type: application/json" \
  -d '{"items": [{"product_id": 1, "quantity": 2}]}'
```
