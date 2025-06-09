import graphene

class SalesData(graphene.ObjectType):
    product_id = graphene.ID()
    total_orders = graphene.Int()
    total_quantity = graphene.Int()

class Query(graphene.ObjectType):
    sales = graphene.List(SalesData)

    def resolve_sales(self, info):
        # Contoh dummy data
        return [
            SalesData(product_id="101", total_orders=10, total_quantity=25),
            SalesData(product_id="102", total_orders=5, total_quantity=9)
        ]

schema = graphene.Schema(query=Query)
