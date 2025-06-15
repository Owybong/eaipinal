import streamlit as st
import requests

# ---------- Streamlit UI ----------
st.set_page_config(page_title="📚 Bookstore Control Panel", layout="wide")

service = st.sidebar.selectbox(
    "📂 Select Service",
    ("Product Service", "Inventory Service", "Customer Service", "Order Service", "Delivery Service", "Analytics Service", "External API")
)

# Base URLs for each service
SERVICE_URLS = {
    "Product Service": "http://product_service:5001",
    "Inventory Service": "http://inventory_service:5003",
    "Customer Service": "http://customer_service:5002",
    "Order Service": "http://order_service:5004",
    "Delivery Service": "http://delivery_service:5005",
    "Analytics Service": "http://analytics_service:5006",
    "External API": "http://external_api:5007"
}

BASE_URL = SERVICE_URLS[service]

# ---------- Product Service Functions ----------
def get_products(service_url=None):
    url = service_url if service_url else SERVICE_URLS["Product Service"]
    res = requests.get(f"{url}/products")
    return res.json() if res.status_code == 200 else []

def create_product(name, sku, category, price):
    data = {"name": name, "sku": sku, "category": category, "price": price}
    res = requests.post(f"{SERVICE_URLS['Product Service']}/products", json=data)
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

# ---------- Inventory Service Functions ----------
def get_warehouses():
    res = requests.get(f"{BASE_URL}/warehouses")
    return res.json() if res.status_code == 200 else []

def get_inventory_by_product(product_id):
    res = requests.get(f"{BASE_URL}/inventory/product/{product_id}")
    return res.json() if res.status_code == 200 else []

def get_inventory_by_warehouse(warehouse_id):
    res = requests.get(f"{BASE_URL}/inventory/warehouse/{warehouse_id}")
    return res.json() if res.status_code == 200 else []

def update_inventory_stock(product_id, warehouse_id, quantity_change):
    data = {
        "productId": product_id,
        "warehouseId": warehouse_id,
        "quantityChange": quantity_change
    }
    res = requests.post(f"{BASE_URL}/inventory/update", json=data)
    return res.json() if res.status_code == 200 else None

def create_warehouse(warehouse_id, name, location):
    data = {
        "id": warehouse_id,
        "name": name,
        "location": location
    }
    res = requests.post(f"{BASE_URL}/warehouses", json=data)
    return res.status_code == 201

# ---------- Customer Service Functions ----------
def get_customer(customer_id):
    query = """
    query GetCustomer($id: Int!) {
        getCustomer(id: $id) {
            id
            name
            email
        }
    }
    """
    variables = {"id": customer_id}
    res = requests.post(f"{BASE_URL}/graphql", json={"query": query, "variables": variables})
    if res.status_code == 200:
        data = res.json()
        if "errors" not in data and "data" in data and data["data"]["getCustomer"]:
            return data["data"]["getCustomer"]
    return None

def get_customer_inventory(product_id):
    query = """
    query GetInventoryByProduct($productId: String!) {
        getInventoryByProduct(productId: $productId) {
            productId
            warehouseId
            stock
            updatedAt
            warehouse {
                id
                name
                location
            }
        }
    }
    """
    variables = {"productId": product_id}
    res = requests.post(f"{BASE_URL}/graphql", json={"query": query, "variables": variables})
    if res.status_code == 200:
        data = res.json()
        if "errors" not in data and "data" in data:
            return data["data"]["getInventoryByProduct"]
    return []

def get_all_warehouses():
    query = """
    query GetAllWarehouses {
        getWarehouses {
            id
            name
            location
        }
    }
    """
    res = requests.post(f"{BASE_URL}/graphql", json={"query": query})
    if res.status_code == 200:
        data = res.json()
        if "errors" not in data and "data" in data:
            return data["data"]["getWarehouses"]
    return []

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
    st.title("📦 Inventory Management")
    
    tab1, tab2, tab3 = st.tabs(["Warehouses", "Inventory", "Update Stock"])
    
    with tab1:
        st.subheader("📍 Warehouses")
        warehouses = get_warehouses()
        
        for w in warehouses:
            with st.expander(f"{w['name']} - {w['location']}"):
                st.write(f"ID: {w['id']}")
                if st.button("View Inventory", key=f"view_{w['id']}"):
                    st.session_state.selected_warehouse = w['id']
                    st.rerun()
        
        st.subheader("➕ Add New Warehouse")
        with st.form("add_warehouse_form"):
            warehouse_id = st.text_input("Warehouse ID")
            warehouse_name = st.text_input("Name")
            warehouse_location = st.text_input("Location")
            
            submit_button = st.form_submit_button("Add Warehouse")
            if submit_button and warehouse_id and warehouse_name:
                if create_warehouse(warehouse_id, warehouse_name, warehouse_location):
                    st.success("Warehouse added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add warehouse. Please try again.")
    
    with tab2:
        st.subheader("🔍 Inventory Search")
        search_by = st.radio("Search by:", ["Product ID", "Warehouse ID"])
        
        if search_by == "Product ID":
            product_id = st.text_input("Enter Product ID")
            if product_id and st.button("Search"):
                inventory_items = get_inventory_by_product(product_id)
                if inventory_items:
                    for item in inventory_items:
                        st.write(f"Warehouse: {item.get('warehouse', {}).get('name', 'Unknown')} ({item['warehouseId']})")
                        st.write(f"Stock: {item['stock']} units")
                        st.write(f"Last Updated: {item['updatedAt']}")
                        st.divider()
                else:
                    st.info("No inventory found for this product.")
        
        elif search_by == "Warehouse ID":
            warehouse_id = st.text_input("Enter Warehouse ID")
            if warehouse_id and st.button("Search"):
                inventory_items = get_inventory_by_warehouse(warehouse_id)
                if inventory_items:
                    for item in inventory_items:
                        st.write(f"Product ID: {item['productId']}")
                        st.write(f"Stock: {item['stock']} units")
                        st.write(f"Last Updated: {item['updatedAt']}")
                        st.divider()
                else:
                    st.info("No inventory found for this warehouse.")
    
    with tab3:
        st.subheader("🔄 Update Inventory Stock")
        with st.form("update_stock_form"):
            product_id = st.text_input("Product ID")
            warehouse_id = st.text_input("Warehouse ID")
            quantity_change = st.number_input("Quantity Change", value=0, step=1, 
                                             help="Positive for stock addition, negative for reduction")
            
            submit_button = st.form_submit_button("Update Stock")
            if submit_button and product_id and warehouse_id:
                result = update_inventory_stock(product_id, warehouse_id, quantity_change)
                if result:
                    st.success(f"Stock updated successfully! New stock level: {result['stock']}")
                else:
                    st.error("Failed to update stock. Please check the product and warehouse IDs.")

# ---------- Customer Service Tab ----------
elif service == "Customer Service":
    st.title("👤 Customer Management")
    
    tab1, tab2 = st.tabs(["Customer Details", "Inventory Access"])
    
    with tab1:
        st.subheader("🔍 Customer Lookup")
        customer_id = st.number_input("Enter Customer ID", min_value=1, step=1)
        if st.button("Search Customer"):
            customer = get_customer(customer_id)
            if customer:
                st.write(f"**Name:** {customer['name']}")
                st.write(f"**Email:** {customer['email']}")
                st.session_state.current_customer = customer
            else:
                st.error("Customer not found.")
    
    with tab2:
        st.subheader("🔄 Customer Inventory Access")
        
        if "current_customer" in st.session_state:
            st.write(f"Customer: {st.session_state.current_customer['name']}")
            
            search_type = st.radio("Search Inventory By:", ["Product ID", "Warehouse"])
            
            if search_type == "Product ID":
                product_id = st.text_input("Enter Product ID")
                if product_id and st.button("Check Inventory"):
                    inventory_items = get_customer_inventory(product_id)
                    if inventory_items:
                        for item in inventory_items:
                            st.write(f"Warehouse: {item.get('warehouse', {}).get('name', 'Unknown')} ({item['warehouseId']})")
                            st.write(f"Stock: {item['stock']} units")
                            st.write(f"Last Updated: {item['updatedAt']}")
                            st.divider()
                    else:
                        st.info("No inventory found for this product.")
            
            elif search_type == "Warehouse":
                warehouses = get_all_warehouses()
                if warehouses:
                    warehouse_id = st.selectbox(
                        "Select Warehouse",
                        options=[w["id"] for w in warehouses],
                        format_func=lambda x: next((w["name"] for w in warehouses if w["id"] == x), x)
                    )
                    
                    if warehouse_id and st.button("View Warehouse Inventory"):
                        inventory_items = get_inventory_by_warehouse(warehouse_id)
                        if inventory_items:
                            for item in inventory_items:
                                st.write(f"Product ID: {item['productId']}")
                                st.write(f"Stock: {item['stock']} units")
                                st.write(f"Last Updated: {item['updatedAt']}")
                                st.divider()
                        else:
                            st.info("No inventory found in this warehouse.")
                else:
                    st.info("No warehouses found.")
        else:
            st.info("Please search for a customer first in the Customer Details tab.")

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
        
        # Get available products from Product Service
        products = get_products(SERVICE_URLS["Product Service"])
        
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

    # 1. Input filter
    status = st.selectbox("Filter Order Status", ["", "PENDING", "PROCESSING", "COMPLETED", "CANCELLED"])
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start Date")
    end_date = col2.date_input("End Date")

    # 2. Parameter untuk request
    params = {}
    if status:
        params["status"] = status
    if start_date:
        params["start_date"] = str(start_date)
    if end_date:
        params["end_date"] = str(end_date)

    try:
        res = requests.get(f"{SERVICE_URLS['Analytics Service']}/analytics/sales", params=params)
        data = res.json()

        if "error" in data:
            st.error("Gagal memuat data analytics: " + data["error"])
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total Revenue", f"${data['total_revenue']:.2f}")
            col2.metric("🧾 Total Orders", data['total_orders'])
            col3.metric("📦 Avg. Order Value", f"${data['average_order']:.2f}")

    except Exception as e:
        st.error("Terjadi kesalahan saat mengambil data: " + str(e))


# ---------- External API Tab ----------
elif service == "External API":
    st.title("🔗 External Bookstore API")
    st.info("This will connect to the other group project API.")
