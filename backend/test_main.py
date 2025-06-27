import json
from fastapi.testclient import TestClient
from main import app, customers, orders

client = TestClient(app)

def test_customer_multiverse_fields_exist():
    """Ensure the new multiverse and town fields are present and valid."""
    sample = customers[0]
    assert "multiverse" in sample.__fields__, "Missing 'multiverse' in Customer model"
    assert "town" in sample.__fields__, "Missing 'town' in Customer model"

def test_customer_orders_endpoint_matches_count():
    """Ensure that /customers/{id}/orders returns correct order count."""
    customer_id = customers[0].id
    expected = len([o for o in orders if o.customer_id == customer_id])

    resp = client.get(f"/customers/{customer_id}/orders")
    assert resp.status_code == 200
    assert len(resp.json()) == expected

def test_most_ordered_item_is_consistent():
    """Verify that most_ordered_item reflects reality in orders."""
    for customer in customers:
        customer_orders = [o for o in orders if o.customer_id == customer.id]
        if not customer_orders:
            continue
        item_counts = {}
        for o in customer_orders:
            item_counts[o.item] = item_counts.get(o.item, 0) + o.quantity
        most_ordered = max(item_counts.items(), key=lambda x: x[1])[0]
        assert customer.most_ordered_item == most_ordered

def test_customer_history_is_accurate():
    """Check that history endpoint returns correct structure."""
    customer_id = customers[0].id
    resp = client.get(f"/customers/{customer_id}/history")
    assert resp.status_code == 200
    data = resp.json()
    assert data["customer_id"] == customer_id
    assert "estimated_orders" in data
    assert isinstance(data["estimated_orders"], int)
