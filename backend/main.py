from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional, List
from uuid import uuid4
from datetime import date, datetime
import json

app = FastAPI()

# ---------------------------
# Models
# ---------------------------
class Customer(BaseModel):
    id: Optional[str] = None
    name: str
    address: str
    email: EmailStr
    most_ordered_item: str
    first_order_date: date
    last_order_date: date

class Order(BaseModel):
    id: Optional[str] = None
    customer_id: str
    item: str
    quantity: int
    order_date: date

class CustomerOrderRequest(BaseModel):
    customer: Customer
    order: Order

# ---------------------------
# Data Handling
# ---------------------------
def load_customers_from_file() -> List[Customer]:
    try:
        with open("customers.json", "r") as f:
            data = json.load(f)
            loaded_customers = []
            for c in data:
                try:
                    loaded_customers.append(Customer(**c))
                except ValidationError as ve:
                    print(f"Validation error for customer: {c}\n{ve}")
            print(f"✅ Loaded {len(loaded_customers)} customers from JSON")
            return loaded_customers
    except Exception as e:
        print(f"❌ Failed to load customers.json: {e}")
        return []

def load_orders_from_file() -> List[Order]:
    try:
        with open("orders.json", "r") as f:
            data = json.load(f)
            return [Order(**o) for o in data]
    except Exception as e:
        print(f"❌ Failed to load orders.json: {e}")
        return []

def save_customers_to_file():
    with open("customers.json", "w") as f:
        json.dump([c.model_dump() for c in customers], f, indent=2, default=str)

def save_orders_to_file():
    with open("orders.json", "w") as f:
        json.dump([o.model_dump() for o in orders], f, indent=2, default=str)

def update_most_ordered_item(customer_id: str):
    customer_orders = [o for o in orders if o.customer_id == customer_id]
    item_counts = {}

    for o in customer_orders:
        item_counts[o.item] = item_counts.get(o.item, 0) + o.quantity

    if item_counts:
        most_ordered = max(item_counts.items(), key=lambda x: x[1])[0]
        customer = next((c for c in customers if c.id == customer_id), None)
        if customer:
            customer.most_ordered_item = most_ordered

# ---------------------------
# Initial Load
# ---------------------------
customers: List[Customer] = load_customers_from_file()
orders: List[Order] = load_orders_from_file()

# ---------------------------
# Customer Routes
# ---------------------------
@app.get("/customers", response_model=List[Customer])
def get_customers():
    return customers

@app.post("/customers", response_model=Customer)
def create_customer(customer: Customer):
    customer.id = str(uuid4())
    customers.append(customer)
    save_customers_to_file()
    return customer

@app.get("/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: str):
    customer = next((c for c in customers if c.id == customer_id), None)
    if customer:
        return customer
    raise HTTPException(status_code=404, detail="Customer not found")

@app.get("/customers/{customer_id}/history")
def get_customer_history(customer_id: str):
    customer = next((c for c in customers if c.id == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    first = datetime.strptime(str(customer.first_order_date), "%Y-%m-%d")
    last = datetime.strptime(str(customer.last_order_date), "%Y-%m-%d")
    days_between = (last - first).days
    est_orders = max(1, days_between // 30)

    return {
        "customer_id": customer.id,
        "name": customer.name,
        "most_ordered_item": customer.most_ordered_item,
        "first_order_date": customer.first_order_date,
        "last_order_date": customer.last_order_date,
        "estimated_orders": est_orders
    }

@app.get("/customers/{customer_id}/orders", response_model=List[Order])
def get_orders_by_customer(customer_id: str):
    return [o for o in orders if o.customer_id == customer_id]

@app.get("/customers/{customer_id}/latest-order")
def get_customer_with_latest_order(customer_id: str):
    customer = next((c for c in customers if c.id == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer_orders = [o for o in orders if o.customer_id == customer_id]
    if not customer_orders:
        return {
            "customer": customer,
            "latest_order": None,
            "message": "No orders found for this customer"
        }

    latest_order = max(customer_orders, key=lambda o: o.order_date)
    return {
        "customer": customer,
        "latest_order": latest_order
    }

# ---------------------------
# Order Routes
# ---------------------------
@app.get("/orders", response_model=List[Order])
def get_all_orders():
    return orders

@app.post("/orders", response_model=Order)
def create_order(order: Order):
    customer = next((c for c in customers if c.id == order.customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    order.id = str(uuid4())
    orders.append(order)
    save_orders_to_file()

    customer.last_order_date = order.order_date
    update_most_ordered_item(customer.id)
    save_customers_to_file()

    return order

# ---------------------------
# Combo Route: Place Order + Create Customer if Needed
# ---------------------------
@app.post("/place-order", response_model=Order)
def place_order(data: CustomerOrderRequest):
    existing_customer = next((c for c in customers if c.email == data.customer.email), None)

    if existing_customer:
        customer_id = existing_customer.id
    else:
        data.customer.id = str(uuid4())
        customers.append(data.customer)
        save_customers_to_file()
        customer_id = data.customer.id

    data.order.id = str(uuid4())
    data.order.customer_id = customer_id
    orders.append(data.order)
    save_orders_to_file()

    customer = next((c for c in customers if c.id == customer_id), None)
    if customer:
        customer.last_order_date = data.order.order_date
        update_most_ordered_item(customer_id)
        save_customers_to_file()

    return data.order
