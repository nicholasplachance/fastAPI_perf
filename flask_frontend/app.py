from flask import Flask, render_template, request, redirect, url_for
import json
import os
from uuid import uuid4
from datetime import date

app = Flask(__name__)

# Adjust paths relative to root/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CUSTOMER_PATH = os.path.join(BASE_DIR, "backend", "customers.json")
ORDER_PATH = os.path.join(BASE_DIR, "backend", "orders.json")

def load_customers():
    with open(CUSTOMER_PATH) as f:
        return json.load(f)

def load_orders():
    with open(ORDER_PATH) as f:
        return json.load(f)

def save_customers(data):
    with open(CUSTOMER_PATH, "w") as f:
        json.dump(data, f, indent=2)

def save_orders(data):
    with open(ORDER_PATH, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def index():
    customers = load_customers()
    orders = load_orders()
    return render_template("index.html", customers=customers, orders=orders)

@app.route("/customer/<customer_id>")
def view_customer(customer_id):
    customers = load_customers()
    orders = load_orders()
    customer = next((c for c in customers if c["id"] == customer_id), None)
    customer_orders = [o for o in orders if o["customer_id"] == customer_id]
    return render_template("customer.html", customer=customer, orders=customer_orders)

@app.route("/create-order", methods=["GET", "POST"])
def create_order():
    if request.method == "POST":
        customers = load_customers()
        orders = load_orders()

        name = request.form["name"]
        address = request.form["address"]
        town = request.form["town"]
        multiverse = request.form["multiverse"]
        email = request.form["email"]
        item = request.form["item"]
        quantity = int(request.form["quantity"])
        order_date = str(date.today())

        existing = next((c for c in customers if c["email"] == email), None)

        if existing:
            customer_id = existing["id"]
        else:
            customer_id = str(uuid4())
            new_customer = {
                "id": customer_id,
                "name": name,
                "address": address,
                "email": email,
                "most_ordered_item": "",
                "first_order_date": order_date,
                "last_order_date": order_date,
                "town": town,
                "multiverse": multiverse
            }
            customers.append(new_customer)

        order = {
            "id": str(uuid4()),
            "customer_id": customer_id,
            "item": item,
            "quantity": quantity,
            "order_date": order_date
        }

        orders.append(order)
        save_customers(customers)
        save_orders(orders)

        return redirect(url_for("index"))

    return render_template("create_order.html")

if __name__ == "__main__":
    app.run(debug=True)
