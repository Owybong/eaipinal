import streamlit as st
import requests

# ---------- Streamlit UI ----------
st.set_page_config(page_title="📚 Bookstore Control Panel", layout="wide")

service = st.sidebar.selectbox(
    "📂 Select Service",
    ("Product Service", "Inventory Service", "Order Service", "Delivery Service", "Analytics Service", "External API")
)

# Base URLs for each service
SERVICE_URLS = {
    "Product Service": "http://localhost:5002",
    "Inventory Service": "http://localhost:5003",
    "Order Service": "http://localhost:5004",
    "Delivery Service": "http://localhost:5005",
    "Analytics Service": "http://localhost:5006",
    "External API": "http://localhost:5007"
}

BASE_URL = SERVICE_URLS[service]

# ---------- Product Service Functions ----------
def get_products():
    res = requests.get(f"{BASE_URL}/products")
    return res.json() if res.status_code == 200 else []

def create_product(name, sku, category, price):
    data = {"name": name, "sku": sku, "category": category, "price": price}
    res = requests.post(f"{BASE_URL}/products", json=data)
    return res.status_code == 201

def update_product(product_id, name, sku, category, price):
    data = {"name": name, "sku": sku, "category": category, "price": price}
    res = requests.put(f"{BASE_URL}/products/{product_id}", json=data)
    return res.status_code == 200

def delete_product(product_id):
    res = requests.delete(f"{BASE_URL}/products/{product_id}")
    return res.status_code == 200

# ---------- Product Service Tab ----------
if service == "Product Service":
    st.title("🛒 Product Management")

    st.subheader("📋 All Products")
    products = get_products()
    for p in products:
        with st.expander(f"{p['name']} - ${p['price']}"):
            st.write(f"SKU: {p['sku']}")
            st.write(f"Category: {p['category']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Edit", key=f"edit_{p['id']}"):
                    st.session_state.edit_id = p['id']
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{p['id']}"):
                    if delete_product(p['id']):
                        st.success("Product deleted.")
                        st.rerun()

    st.subheader("➕ Add / Edit Product")

    edit_id = st.session_state.get("edit_id")
    product_data = next((p for p in products if p['id'] == edit_id), {})

    name = st.text_input("Name", product_data.get("name", ""))
    sku = st.text_input("SKU", product_data.get("sku", ""))
    category = st.text_input("Category", product_data.get("category", ""))
    price = st.number_input("Price", min_value=0.0, step=0.01, value=float(product_data.get("price", 0.0)))

    if edit_id:
        if st.button("Update Product"):
            if update_product(edit_id, name, sku, category, price):
                st.success("Product updated.")
                st.session_state.edit_id = None
                st.rerun()
    else:
        if st.button("Add Product"):
            if create_product(name, sku, category, price):
                st.success("Product added.")
                st.rerun()

# ---------- Inventory Service Tab ----------
elif service == "Inventory Service":
    st.title("📦 Inventory Service")
    st.info("This section will connect to Inventory Service endpoints.")

# ---------- Order Service Tab ----------
elif service == "Order Service":
    st.title("📑 Order Service")
    st.info("This section will connect to Order Service endpoints.")

# ---------- Delivery Service Tab ----------
elif service == "Delivery Service":
    st.title("🚚 Delivery Service")
    st.info("This section will connect to Delivery Service endpoints.")

# ---------- Analytics Service Tab ----------
elif service == "Analytics Service":
    st.title("📊 Analytics Dashboard")
    st.info("This section will visualize analytics and KPIs.")

# ---------- External API Tab ----------
elif service == "External API":
    st.title("🔗 External Bookstore API")
    st.info("This will connect to the other group project API.")
