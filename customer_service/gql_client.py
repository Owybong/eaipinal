import httpx

def fetch_products():
    try:
        response = httpx.get("http://localhost:5001/products")  # Updated product_service port
        return response.json()
    except Exception as e:
        print("Error fetching products:", e)
        return []

def get_customer(customer_id):
    # For now, we'll mock the customer data
    # In a real application, this would fetch from a database
    customers = {
        1: {"id": 1, "name": "John Doe", "email": "john@example.com"},
        2: {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
        3: {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
    }
    return customers.get(customer_id)

def fetch_warehouses():
    try:
        response = httpx.get("http://localhost:5003/warehouses")
        return response.json()
    except Exception as e:
        print("Error fetching warehouses:", e)
        return []

def fetch_inventory_by_product(product_id):
    try:
        response = httpx.get(f"http://localhost:5003/inventory/product/{product_id}")
        return response.json()
    except Exception as e:
        print(f"Error fetching inventory for product {product_id}:", e)
        return []

def fetch_inventory_by_warehouse(warehouse_id):
    try:
        response = httpx.get(f"http://localhost:5003/inventory/warehouse/{warehouse_id}")
        return response.json()
    except Exception as e:
        print(f"Error fetching inventory for warehouse {warehouse_id}:", e)
        return []