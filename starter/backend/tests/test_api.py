import pytest
from backend.app import app, in_memory_storage

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    in_memory_storage.clear()
    with app.test_client() as client:
        yield client

@pytest.mark.parametrize("status", [None, "shipped"])
def test_add_order_api_success(client, status):
    order_data = {
        "order_id": "API001", "item_name": "API Laptop", "quantity": 1, "customer_id": "APICUST001"
    }
    if status is not None:
        order_data["status"] = status

    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 201
    expected_order = {**order_data, "status": status or "pending"}
    assert response.json == expected_order
    assert in_memory_storage.get_order("API001") == expected_order

def test_get_order_api_success(client):
    order_data = {
        "order_id": "GET001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    }
    client.post('/api/orders', json=order_data)
    response = client.get('/api/orders/GET001')
    assert response.status_code == 200
    assert response.json == {**order_data, "status": "pending"}

def test_get_order_api_not_found(client):
    response = client.get('/api/orders/NONEXISTENT')
    assert response.status_code == 404
    assert response.json == {"error": "Order with ID 'NONEXISTENT' not found."}

def test_update_order_status_api_success(client):
    order_data = {
        "order_id": "UPDATE001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    }
    client.post('/api/orders', json=order_data)
    response = client.put('/api/orders/UPDATE001/status', json={"new_status": "shipped"})
    assert response.status_code == 200
    expected_order = {**order_data, "status": "shipped"}
    assert response.json == expected_order
    assert in_memory_storage.get_order("UPDATE001") == expected_order

def test_update_order_status_api_not_found(client):
    response = client.put('/api/orders/NONEXISTENT/status', json={"new_status": "shipped"})

    assert response.status_code == 404
    assert response.json == {"error": "Order with ID 'NONEXISTENT' not found."}
    assert in_memory_storage.get_all_orders() == {}

def test_list_all_orders_api_with_data(client):
    client.post('/api/orders', json={"order_id": "LST001", "item_name": "Item A", "quantity": 1, "customer_id": "C1"})
    client.post('/api/orders', json={"order_id": "LST002", "item_name": "Item B", "quantity": 2, "customer_id": "C2"})
    response = client.get('/api/orders')
    assert response.status_code == 200
    assert response.json == [
        {"order_id": "LST001", "item_name": "Item A", "quantity": 1, "customer_id": "C1", "status": "pending"},
        {"order_id": "LST002", "item_name": "Item B", "quantity": 2, "customer_id": "C2", "status": "pending"},
    ]

@pytest.mark.parametrize("query", ["", "?status=", "?status=pending"])
def test_list_orders_api_empty_storage(client, query):
    response = client.get(f'/api/orders{query}')

    assert response.status_code == 200
    assert response.json == []

def test_list_orders_api_empty_status_returns_all_orders(client):
    order_data = {"order_id": "S001", "item_name": "A", "quantity": 1, "customer_id": "C1"}
    client.post('/api/orders', json=order_data)

    response = client.get('/api/orders?status=')

    assert response.status_code == 200
    assert response.json == [{**order_data, "status": "pending"}]

def test_list_orders_by_status_api_matching(client):
    client.post('/api/orders', json={"order_id": "S001", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"})
    client.post('/api/orders', json={"order_id": "S002", "item_name": "B", "quantity": 2, "customer_id": "C2", "status": "shipped"})
    response = client.get('/api/orders?status=pending')
    assert response.status_code == 200
    assert response.json == [
        {"order_id": "S001", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"},
    ]

def test_list_orders_by_status_api_no_match(client):
    client.post('/api/orders', json={
        "order_id": "S001", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"
    })

    response = client.get('/api/orders?status=shipped')

    assert response.status_code == 200
    assert response.json == []
