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

# ---------- Order Service Functions ----------
def get_orders():
    res = requests.get(f"{BASE_URL}/orders")
    return res.json() if res.status_code == 200 else []

def create_order(customer_id, items):
    data = {
        "customer_id": customer_id,
        "items": items
    }
    res = requests.post(f"{BASE_URL}/orders", json=data)
    return res.status_code == 201

def update_order_status(order_id, status):
    data = {"status": status}
    res = requests.put(f"{BASE_URL}/orders/{order_id}", json=data)
    return res.status_code == 200

def delete_order(order_id):
    res = requests.delete(f"{BASE_URL}/orders/{order_id}")
    return res.status_code == 200

#-------Analytics Service Functions-----------

def get_sales_analytics():
    res = requests.get(f"{SERVICE_URLS['Analytics Service']}/analytics/sales")
    return res.json() if res.status_code == 200 else {}


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
    st.title("📑 Order Management")
    
    tab1, tab2 = st.tabs(["View Orders", "Create Order"])
    
    with tab1:
        st.subheader("📋 All Orders")
        orders = get_orders()
        for order in orders:
            with st.expander(f"Order #{order['id']} - {order['status']}"):
                st.write(f"Customer ID: {order['customer_id']}")
                st.write(f"Total Amount: ${order['total_amount']:.2f}")
                st.write("Items:")
                for item in order['items']:
                    st.write(f"- Product #{item['product_id']}: {item['quantity']} units at ${item['unit_price']} each")
                
                col1, col2 = st.columns(2)
                with col1:
                    new_status = st.selectbox(
                        "Update Status",
                        ["PENDING", "PROCESSING", "COMPLETED", "CANCELLED"],
                        key=f"status_{order['id']}"
                    )
                    if st.button("Update Status", key=f"update_{order['id']}"):
                        if update_order_status(order['id'], new_status):
                            st.success("Order status updated.")
                            st.rerun()
                with col2:
                    if st.button("Delete Order", key=f"delete_{order['id']}"):
                        if delete_order(order['id']):
                            st.success("Order deleted.")
                            st.rerun()
    
    with tab2:
        st.subheader("➕ Create New Order")
        customer_id = st.number_input("Customer ID", min_value=1, step=1)
        
        # Get available products
        products = get_products()
        
        items = []
        st.write("Add Items:")
        add_item = st.button("Add Item")
        if add_item:
            if 'order_items' not in st.session_state:
                st.session_state.order_items = []
            st.session_state.order_items.append({})
            st.rerun()
        
        if 'order_items' in st.session_state:
            for idx, _ in enumerate(st.session_state.order_items):
                col1, col2, col3 = st.columns(3)
                with col1:
                    product = st.selectbox(
                        "Product",
                        products,
                        format_func=lambda x: f"{x['name']} (${x['price']})",
                        key=f"product_{idx}"
                    )
                with col2:
                    quantity = st.number_input("Quantity", min_value=1, step=1, key=f"quantity_{idx}")
                with col3:
                    if st.button("Remove", key=f"remove_{idx}"):
                        st.session_state.order_items.pop(idx)
                        st.rerun()
                
                if product:
                    items.append({
                        "product_id": product['id'],
                        "quantity": quantity
                    })
        
        if st.button("Create Order") and items:
            if create_order(customer_id, items):
                st.success("Order created successfully!")
                st.session_state.order_items = []
                st.rerun()
            else:
                st.error("Failed to create order. Please try again.")

# ---------- Delivery Service Tab ----------
elif service == "Delivery Service":
    st.title("🚚 Delivery Service")
    st.info("This section will connect to Delivery Service endpoints.")

# ---------- Analytics Service Tab ----------
elif service == "Analytics Service":
    st.title("📊 Analytics Dashboard")

    st.subheader("🔍 Insight Options")

    # 1. Input filter dari user
    status = st.selectbox("Filter Order Status", ["", "PENDING", "PROCESSING", "COMPLETED", "CANCELLED"])
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start Date", value=None)
    end_date = col2.date_input("End Date", value=None)

    # 2. Kirim parameter ke backend
    params = {}
    if status:
        params["status"] = status
    if start_date:
        params["start_date"] = str(start_date)
    if end_date:
        params["end_date"] = str(end_date)

    res = requests.get(f"{SERVICE_URLS['Analytics Service']}/analytics/sales", params=params)

    if res.status_code == 200:
        data = res.json()
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Revenue", f"${data['total_revenue']:.2f}")
        col2.metric("🧾 Total Orders", data['total_orders'])
        col3.metric("📦 Avg. Order Value", f"${data['average_order']:.2f}")
    else:
        st.error("Failed to load analytics.")


# ---------- External API Tab ----------
elif service == "External API":
    st.title("🔗 External Bookstore API")
    st.info("This will connect to the other group project API.")
