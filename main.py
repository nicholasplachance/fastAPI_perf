from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional, List
from uuid import uuid4
from datetime import date
from datetime import datetime
from fastapi import FastAPI, HTTPException
from uuid import uuid4
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


# ---------------------------
# Data Load
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
        print(f"Failed to load orders: {e}")
        return []


customers: List[Customer] = load_customers_from_file()
orders: List[Order] = load_orders_from_file()


# ---------------------------
# API Routes
# ---------------------------
@app.get("/customers", response_model=List[Customer])
def get_customers():
    return customers

@app.post("/customers", response_model=Customer)
def create_customer(customer: Customer):
    customer.id = str(uuid4())
    customers.append(customer)
    return customer

@app.get("/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: str):
    for c in customers:
        if c.id == customer_id:
            return c
    raise HTTPException(status_code=404, detail="Customer not found")

@app.get("/customers/{customer_id}/history")
def get_customer_history(customer_id: str):
    for c in customers:
        if c.id == customer_id:
            first = datetime.strptime(str(c.first_order_date), "%Y-%m-%d")
            last = datetime.strptime(str(c.last_order_date), "%Y-%m-%d")
            days_between = (last - first).days
            est_orders = max(1, days_between // 30)  # rough estimate: 1 order/month

            return {
                "customer_id": c.id,
                "name": c.name,
                "most_ordered_item": c.most_ordered_item,
                "first_order_date": c.first_order_date,
                "last_order_date": c.last_order_date,
                "estimated_orders": est_orders
            }

    raise HTTPException(status_code=404, detail="Customer not found")

@app.post("/orders", response_model=Order)
def create_order(order: Order):
    # Check if customer exists
    if not any(c.id == order.customer_id for c in customers):
        raise HTTPException(status_code=404, detail="Customer not found")

    order.id = str(uuid4())
    orders.append(order)

    # ✅ This block must be indented correctly
    with open("orders.json", "w") as f:
        json.dump([o.model_dump() for o in orders], f, indent=2, default=str)

    return order

@app.get("/orders", response_model=List[Order])
def get_all_orders():
    return orders

@app.get("/customers/{customer_id}/orders", response_model=List[Order])
def get_orders_by_customer(customer_id: str):
    customer_orders = [o for o in orders if o.customer_id == customer_id]
    return customer_orders

