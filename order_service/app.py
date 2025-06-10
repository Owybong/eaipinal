"""
Order Service Module
==================

This module implements a RESTful order management service for the EAI Bookstore system.

Author: Dennis
Version: 1.0.0
Date: March 2024

Dependencies:
------------
- Flask
- SQLAlchemy
- PyMySQL
- Requests

Main Components:
--------------
1. Order Management API
   - Create, read, update, delete orders
   - Manage order items
   - Track order status

2. Storage Systems
   - Primary: MySQL database
   - Fallback: JSON file storage

3. External Service Integration
   - Customer Service (port 5000) - Customer validation
   - Product Service (port 5002) - Product and price validation

API Endpoints:
------------
GET    /orders          - Retrieve all orders
GET    /orders/{id}     - Retrieve specific order
POST   /orders          - Create new order
PUT    /orders/{id}     - Update order status
DELETE /orders/{id}     - Delete order
GET    /health         - Health check endpoint

Environment Variables:
-------------------
MYSQL_HOST      - MySQL host (default: localhost)
MYSQL_PORT      - MySQL port (default: 3308)
MYSQL_USER      - MySQL user (default: root)
MYSQL_PASSWORD  - MySQL password (default: empty)
MYSQL_DATABASE  - MySQL database (default: order_db)

Usage:
-----
Run directly:
    python app.py

Run with Docker:
    docker-compose up
"""

from flask import Flask, request, jsonify
from database import db
from models import Order, OrderItem
import requests
import os
import json
import logging
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Service URLs from environment variables
CUSTOMER_SERVICE_URL = os.getenv('CUSTOMER_SERVICE_URL', 'http://host.docker.internal:5000')
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://host.docker.internal:5002')

# MySQL configuration from environment variables
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3308')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'order_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure retry strategy for external service calls
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)

# JSON storage configuration
JSON_STORAGE_FILE = 'data/orders.json'
os.makedirs(os.path.dirname(JSON_STORAGE_FILE), exist_ok=True)

def init_json_storage():
    if not os.path.exists(JSON_STORAGE_FILE):
        with open(JSON_STORAGE_FILE, 'w') as f:
            json.dump({
                "orders": [],
                "next_order_id": 1,
                "next_item_id": 1
            }, f)

# Try to initialize database, fallback to JSON if fails
try:
    db.init_app(app)
    with app.app_context():
        db.create_all()
    USE_JSON_STORAGE = False
    logger.info("Successfully connected to MySQL database")
except Exception as e:
    logger.error(f"Failed to connect to MySQL, falling back to JSON storage: {e}")
    init_json_storage()
    USE_JSON_STORAGE = True

def load_json_data():
    try:
        with open(JSON_STORAGE_FILE, 'r') as f:
            return json.load(f)
    except:
        init_json_storage()
        with open(JSON_STORAGE_FILE, 'r') as f:
            return json.load(f)

def save_json_data(data):
    with open(JSON_STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def validate_order_data(data):
    """Validate order input data"""
    if not data.get('customer_id'):
        return False, 'customer_id is required'
    if not data.get('items'):
        return False, 'items are required'
    for item in data.get('items', []):
        if not item.get('product_id'):
            return False, 'product_id is required for each item'
        if not item.get('quantity') or item['quantity'] < 1:
            return False, 'valid quantity is required for each item'
    return True, None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    health = {
        'status': 'UP',
        'mysql': 'UP' if not USE_JSON_STORAGE else 'DOWN',
        'timestamp': datetime.utcnow().isoformat(),
        'dependencies': {
            'customer_service': 'UNKNOWN',
            'product_service': 'UNKNOWN'
        }
    }
    
    # Check customer service
    try:
        customer_response = http.get(f'{CUSTOMER_SERVICE_URL}/health', timeout=2)
        health['dependencies']['customer_service'] = 'UP' if customer_response.ok else 'DOWN'
    except:
        health['dependencies']['customer_service'] = 'DOWN'
    
    # Check product service
    try:
        product_response = http.get(f'{PRODUCT_SERVICE_URL}/health', timeout=2)
        health['dependencies']['product_service'] = 'UP' if product_response.ok else 'DOWN'
    except:
        health['dependencies']['product_service'] = 'DOWN'
    
    return jsonify(health)

@app.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    logger.info("Fetching all orders")
    if not USE_JSON_STORAGE:
        try:
            orders = Order.query.all()
            return jsonify([order.to_dict() for order in orders])
        except Exception as e:
            logger.error(f"Error fetching orders from database: {e}")
            return jsonify({'error': 'Failed to fetch orders'}), 500
    else:
        try:
            data = load_json_data()
            return jsonify(data['orders'])
        except Exception as e:
            logger.error(f"Error fetching orders from JSON: {e}")
            return jsonify({'error': 'Failed to fetch orders'}), 500

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get specific order"""
    logger.info(f"Fetching order {order_id}")
    if not USE_JSON_STORAGE:
        try:
            order = Order.query.get_or_404(order_id)
            return jsonify(order.to_dict())
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            return jsonify({'error': 'Order not found'}), 404
    else:
        try:
            data = load_json_data()
            order = next((o for o in data['orders'] if o['id'] == order_id), None)
            if order is None:
                return jsonify({'error': 'Order not found'}), 404
            return jsonify(order)
        except Exception as e:
            logger.error(f"Error fetching order from JSON: {e}")
            return jsonify({'error': 'Failed to fetch order'}), 500

@app.route('/orders', methods=['POST'])
def create_order():
    """Create new order"""
    logger.info("Creating new order")
    data = request.get_json()
    
    # Validate input data
    is_valid, error = validate_order_data(data)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    # Validate customer_id
    customer_id = data.get('customer_id')
    
    # Verify customer exists
    try:
        customer_response = http.post(f'{CUSTOMER_SERVICE_URL}/graphql', json={
            'query': '''
                query GetCustomer($id: Int!) {
                    getCustomer(id: $id) {
                        id
                        name
                        email
                    }
                }
            ''',
            'variables': {'id': int(customer_id)}
        }, timeout=5)
        
        if customer_response.status_code != 200:
            logger.error(f"Customer service returned status {customer_response.status_code}")
            return jsonify({'error': 'Error communicating with Customer Service'}), 503
            
        result = customer_response.json()
        if not result.get('data', {}).get('getCustomer'):
            return jsonify({'error': f'Customer {customer_id} not found'}), 400
    except requests.RequestException as e:
        logger.error(f"Error communicating with Customer Service: {e}")
        return jsonify({'error': f'Error communicating with Customer Service: {str(e)}'}), 503
    
    if not USE_JSON_STORAGE:
        # MySQL storage
        try:
            order = Order(
                customer_id=customer_id,
                status='PENDING',
                total_amount=0.0
            )
            db.session.add(order)
            db.session.flush()  # This gets the order ID
            
            total_amount = 0.0
            
            # Add order items
            for item_data in data.get('items', []):
                try:
                    # Verify product exists and get price
                    product_response = http.get(f'{PRODUCT_SERVICE_URL}/products/{item_data["product_id"]}', timeout=5)
                    if product_response.status_code == 200:
                        product = product_response.json()
                        unit_price = float(product.get('price', 0))
                        
                        order_item = OrderItem(
                            order_id=order.id,
                            product_id=item_data['product_id'],
                            quantity=item_data['quantity'],
                            unit_price=unit_price
                        )
                        db.session.add(order_item)
                        
                        # Calculate total
                        total_amount += unit_price * item_data['quantity']
                    else:
                        db.session.rollback()
                        return jsonify({'error': f'Product {item_data["product_id"]} not found'}), 400
                    
                except requests.RequestException as e:
                    logger.error(f"Error communicating with Product Service: {e}")
                    db.session.rollback()
                    return jsonify({'error': f'Error communicating with Product Service: {str(e)}'}), 503
            
            # Update order total
            order.total_amount = total_amount
            
            db.session.commit()
            logger.info(f"Successfully created order {order.id}")
            return jsonify(order.to_dict()), 201
        except Exception as e:
            logger.error(f"Error creating order in database: {e}")
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        # JSON storage
        try:
            json_data = load_json_data()
            
            # Create new order
            order = {
                'id': json_data['next_order_id'],
                'customer_id': customer_id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'status': 'PENDING',
                'total_amount': 0.0,
                'items': []
            }
            
            total_amount = 0.0
            item_id = json_data['next_item_id']
            
            # Add order items
            for item_data in data.get('items', []):
                try:
                    # Verify product exists and get price
                    product_response = http.get(f'{PRODUCT_SERVICE_URL}/products/{item_data["product_id"]}', timeout=5)
                    if product_response.status_code == 200:
                        product = product_response.json()
                        unit_price = float(product.get('price', 0))
                        
                        order_item = {
                            'id': item_id,
                            'product_id': item_data['product_id'],
                            'quantity': item_data['quantity'],
                            'unit_price': unit_price
                        }
                        order['items'].append(order_item)
                        item_id += 1
                        
                        # Calculate total
                        total_amount += unit_price * item_data['quantity']
                    else:
                        return jsonify({'error': f'Product {item_data["product_id"]} not found'}), 400
                    
                except requests.RequestException as e:
                    logger.error(f"Error communicating with Product Service: {e}")
                    return jsonify({'error': f'Error communicating with Product Service: {str(e)}'}), 503
            
            # Update order total
            order['total_amount'] = total_amount
            
            # Save to JSON file
            json_data['orders'].append(order)
            json_data['next_order_id'] = order['id'] + 1
            json_data['next_item_id'] = item_id
            
            save_json_data(json_data)
            logger.info(f"Successfully created order {order['id']} in JSON storage")
            return jsonify(order), 201
        except Exception as e:
            logger.error(f"Error creating order in JSON storage: {e}")
            return jsonify({'error': str(e)}), 400

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """Update order status"""
    logger.info(f"Updating order {order_id}")
    data = request.get_json()
    
    if not data.get('status'):
        return jsonify({'error': 'status is required'}), 400
        
    if data['status'] not in ['PENDING', 'PROCESSING', 'COMPLETED', 'CANCELLED']:
        return jsonify({'error': 'Invalid status value'}), 400
    
    if not USE_JSON_STORAGE:
        try:
            order = Order.query.get_or_404(order_id)
            order.status = data['status']
            order.updated_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Successfully updated order {order_id} status to {data['status']}")
            return jsonify(order.to_dict())
        except Exception as e:
            logger.error(f"Error updating order in database: {e}")
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        try:
            json_data = load_json_data()
            order = next((o for o in json_data['orders'] if o['id'] == order_id), None)
            if order is None:
                return jsonify({'error': 'Order not found'}), 404
                
            order['status'] = data['status']
            order['updated_at'] = datetime.utcnow().isoformat()
                
            save_json_data(json_data)
            logger.info(f"Successfully updated order {order_id} status to {data['status']} in JSON storage")
            return jsonify(order)
        except Exception as e:
            logger.error(f"Error updating order in JSON storage: {e}")
            return jsonify({'error': str(e)}), 400

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete order"""
    logger.info(f"Deleting order {order_id}")
    if not USE_JSON_STORAGE:
        try:
            order = Order.query.get_or_404(order_id)
            db.session.delete(order)
            db.session.commit()
            logger.info(f"Successfully deleted order {order_id}")
            return jsonify({'message': 'Order deleted successfully'})
        except Exception as e:
            logger.error(f"Error deleting order from database: {e}")
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        try:
            json_data = load_json_data()
            order_index = next((i for i, o in enumerate(json_data['orders']) if o['id'] == order_id), -1)
            
            if order_index == -1:
                return jsonify({'error': 'Order not found'}), 404
                
            json_data['orders'].pop(order_index)
            
            save_json_data(json_data)
            logger.info(f"Successfully deleted order {order_id} from JSON storage")
            return jsonify({'message': 'Order deleted successfully'})
        except Exception as e:
            logger.error(f"Error deleting order from JSON storage: {e}")
            return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True) 