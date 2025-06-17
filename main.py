from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional, List
from uuid import uuid4
from datetime import date
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

customers: List[Customer] = load_customers_from_file()

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
