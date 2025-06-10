from ariadne import QueryType
from gql_client import fetch_products, get_customer, fetch_warehouses, fetch_inventory_by_product, fetch_inventory_by_warehouse

query = QueryType()

@query.field("getProducts")
def resolve_get_products(_, info):
    return fetch_products()

@query.field("getCustomer")
def resolve_get_customer(_, info, id):
    return get_customer(id)

@query.field("getWarehouses")
def resolve_get_warehouses(_, info):
    return fetch_warehouses()

@query.field("getInventoryByProduct")
def resolve_get_inventory_by_product(_, info, productId):
    return fetch_inventory_by_product(productId)

@query.field("getInventoryByWarehouse")
def resolve_get_inventory_by_warehouse(_, info, warehouseId):
    return fetch_inventory_by_warehouse(warehouseId)

# @query.field("getOrders")
# def resolve_get_orders(_, info, userId):
#     return fetch_orders(userId)
