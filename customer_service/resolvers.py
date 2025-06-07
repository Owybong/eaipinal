from ariadne import QueryType
from gql_client import fetch_products

query = QueryType()

@query.field("getProducts")
def resolve_get_products(_, info):
    return fetch_products()

# @query.field("getOrders")
# def resolve_get_orders(_, info, userId):
#     return fetch_orders(userId)
