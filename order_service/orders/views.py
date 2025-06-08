from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
import requests
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        # Validate product availability with Product Service
        for item in request.data.get('items', []):
            product_id = item.get('product_id')
            quantity = item.get('quantity')
            
            try:
                # Replace with actual Product Service URL
                response = requests.get(f'http://product-service:5002/products/{product_id}')
                if response.status_code != 200:
                    return Response(
                        {'error': f'Product {product_id} not found'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Get product price from response
                product_data = response.json()
                item['unit_price'] = product_data.get('price', 0)
                
            except requests.RequestException as e:
                return Response(
                    {'error': f'Error communicating with Product Service: {str(e)}'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

        # Calculate total amount
        total_amount = sum(
            item.get('quantity', 0) * item.get('unit_price', 0)
            for item in request.data.get('items', [])
        )
        request.data['total_amount'] = total_amount

        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Enrich response with product details
        response_data = serializer.data
        for item in response_data['items']:
            try:
                # Replace with actual Product Service URL
                product_response = requests.get(f'http://product-service:5002/products/{item["product_id"]}')
                if product_response.status_code == 200:
                    product_data = product_response.json()
                    item['product_details'] = product_data
            except requests.RequestException:
                item['product_details'] = {'error': 'Product details unavailable'}
        
        return Response(response_data)
