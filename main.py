from fastapi import FastAPI, HTTPException, Body
from fastapi import HTTPException, Body, FastAPI, Depends, Response, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Product, Order, OrderItem, User
from typing import Optional
from langdetect import detect
from fastapi.middleware.cors import CORSMiddleware
from auth import hash_password, verify_password, create_access_token, get_current_user


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow all origins (simple)
    allow_credentials=True,
    allow_methods=["*"],      # allow all HTTP methods
    allow_headers=["*"],      # allow all headers (including custom ones)
)

# Dependency to get DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


###        Authentication           ###


@app.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(password)
    user = User(email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully", "user_id": user.id}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# To get all Products


@app.get("/products")
def get_products(min_price: Optional[float] = Query(None),
                 max_price: Optional[float] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Product)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    return query.all()


# To create a Product


@app.post("/products")
def create_product(name: str, price: float, response: Response, db: Session = Depends(get_db)):
    new_product = Product(name=name, price=price)

    lang = detect(name)
    response.headers["X-Payload-Language"] = lang

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# To get a paticular Product by ID


@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

# Update a Product


@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    name: Optional[str] = None,
    price: Optional[int] = None,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if name is not None:
        product.name = name

    if price is not None:
        product.price = price

    db.commit()
    db.refresh(product)
    return product


# Delete Product by ID


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}

###        Placing Order           ###


@app.post("/place-order")
def place_order(body=Body(...), current_user: User = Depends(get_current_user)):
    """
    Requires authentication. Example JSON:

    {
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 3, "quantity": 4}
        ]
    }
    """

    items = body.get("items")

    db = SessionLocal()

    total_cost = 0
    order_items_temp = []

    try:
        # 1. Validate all products and calculate total
        for item in items:
            pid = item.get("product_id")
            qty = item.get("quantity")

            # if not pid or not qty:
            #     raise HTTPException(
            #         status_code=400, detail="Each item needs product_id and quantity")

            product = db.query(Product).filter(Product.id == pid).first()
            # if not product:
            #     raise HTTPException(
            #         status_code=404, detail=f"Product {pid} not found")

            # if product.stock < qty:
            #     raise HTTPException(
            #         status_code=400,
            #         detail=f"Not enough stock for product ID {pid}"
            #     )

            cost = product.price * qty
            total_cost += cost

            order_items_temp.append({
                "product": product,
                "quantity": qty,
                "price": product.price
            })

        # 2. Create order
        order = Order(total_amount=total_cost)
        db.add(order)
        db.commit()
        db.refresh(order)

        # 3. Deduct stock & insert order items
        for item in order_items_temp:
            product = item["product"]
            qty = item["quantity"]

            # Deduct stock
            product.stock -= qty

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                price_at_purchase=product.price
            )
            db.add(order_item)

        db.commit()

        return {
            "message": "Order placed successfully",
            "order_id": order.id,
            "total_amount": total_cost,
            "total_items": len(items)
        }

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()


#        GET order by id
@app.get("/order/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):

    # 1. Fetch the order
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        return {"error": "Order not found"}

    # 2. Build response manually (no Pydantic)
    items_list = []
    for item in order.items:
        items_list.append({
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price": item.price
        })

    # 3. Return plain dict
    return {
        "order_id": order.id,
        "total_amount": order.total_amount,
        "items": items_list
    }


# GET all orders

@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):

    orders = db.query(Order).all()

    result = []

    for order in orders:
        items_list = []
        for item in order.items:
            items_list.append({
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price_at_purchase
            })

        result.append({
            "order_id": order.id,
            "total_amount": order.total_amount,
            "items": items_list
        })

    return result
