import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

def test_add_order_successfully(order_tracker, mock_storage):
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    mock_storage.save_order.assert_called_once_with("ORD001", {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    })


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="^Order with ID 'ORD_EXISTING' already exists\\.$"):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

    mock_storage.get_order.assert_called_once_with("ORD_EXISTING")
    mock_storage.save_order.assert_not_called()


def test_get_order_by_id_returns_existing_order(order_tracker, mock_storage):
    order = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    mock_storage.get_order.return_value = order

    assert order_tracker.get_order_by_id("ORD001") == order
    mock_storage.get_order.assert_called_once_with("ORD001")


def test_get_order_by_id_returns_none_if_not_found(order_tracker, mock_storage):
    assert order_tracker.get_order_by_id("MISSING") is None
    mock_storage.get_order.assert_called_once_with("MISSING")


def test_update_order_status_successfully(order_tracker, mock_storage):
    mock_storage.get_order.return_value = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }

    order_tracker.update_order_status("ORD001", "shipped")

    mock_storage.get_order.assert_called_once_with("ORD001")
    mock_storage.save_order.assert_called_once_with("ORD001", {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "shipped",
    })


def test_update_order_status_raises_error_if_not_found(order_tracker, mock_storage):
    with pytest.raises(ValueError, match="^Order with ID 'MISSING' not found\\.$"):
        order_tracker.update_order_status("MISSING", "shipped")

    mock_storage.get_order.assert_called_once_with("MISSING")
    mock_storage.save_order.assert_not_called()


def test_list_all_orders_returns_stored_orders(order_tracker, mock_storage):
    first_order = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    second_order = {
        "order_id": "ORD002",
        "item_name": "Mouse",
        "quantity": 2,
        "customer_id": "CUST002",
        "status": "shipped",
    }
    mock_storage.get_all_orders.return_value = {
        "ORD001": first_order,
        "ORD002": second_order,
    }

    assert order_tracker.list_all_orders() == [first_order, second_order]
    mock_storage.get_all_orders.assert_called_once_with()


def test_list_all_orders_returns_empty_list_if_no_orders(order_tracker, mock_storage):
    assert order_tracker.list_all_orders() == []
    mock_storage.get_all_orders.assert_called_once_with()
