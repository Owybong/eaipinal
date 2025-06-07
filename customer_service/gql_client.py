import httpx

def fetch_products():
    try:
        response = httpx.get("http://localhost:5002/products")  # your product_service port
        return response.json()
    except Exception as e:
        print("Error fetching products:", e)
        return []