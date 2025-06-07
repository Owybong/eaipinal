import streamlit as st
import requests

st.title("📚 Product Catalog")

# GraphQL query
query = """
query {
  getProducts {
    id
    name
    sku
    category
    price
  }
}
"""

# Send request to your customer_service GraphQL
response = requests.post(
    "http://127.0.0.1:5000/graphql",
    json={"query": query}
)

if response.status_code == 200:
    data = response.json()["data"]["getProducts"]
    for product in data:
        st.subheader(f"{product['name']} (ID: {product['id']})")
        st.write(f"Category: {product['category']}")
        st.write(f"SKU: {product['sku']}")
        st.write(f"Price: ${product['price']}")
        st.markdown("---")
else:
    st.error("Failed to fetch products")
