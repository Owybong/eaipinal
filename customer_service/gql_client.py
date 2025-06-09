import httpx

def fetch_products():
    try:
        response = httpx.get("http://localhost:5002/products")  # your product_service port
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