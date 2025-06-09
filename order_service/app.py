from flask import Flask, request, jsonify
from database import db
from models import Order, OrderItem
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)

# MySQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3308/order_db'  # Change the database name or the port to be inline with your xampp
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JSON storage configuration
JSON_STORAGE_FILE = 'order_service/data/orders.json'
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
except Exception as e:
    print(f"Failed to connect to MySQL, falling back to JSON storage: {e}")
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

@app.route('/orders', methods=['GET'])
def get_orders():
    if not USE_JSON_STORAGE:
        orders = Order.query.all()
        return jsonify([order.to_dict() for order in orders])
    else:
        data = load_json_data()
        return jsonify(data['orders'])

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    if not USE_JSON_STORAGE:
        order = Order.query.get_or_404(order_id)
        return jsonify(order.to_dict())
    else:
        data = load_json_data()
        order = next((o for o in data['orders'] if o['id'] == order_id), None)
        if order is None:
            return jsonify({'error': 'Order not found'}), 404
        return jsonify(order)

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    
    # Validate customer_id
    customer_id = data.get('customer_id')
    if not customer_id:
        return jsonify({'error': 'customer_id is required'}), 400
    
    # Verify customer exists
    try:
        customer_response = requests.get(f'http://localhost:5000/graphql', json={
            'query': '''
                query($id: Int!) {
                    getCustomer(id: $id) {
                        id
                    }
                }
            ''',
            'variables': {'id': customer_id}
        })
        if customer_response.status_code != 200 or not customer_response.json().get('data', {}).get('getCustomer'):
            return jsonify({'error': f'Customer {customer_id} not found'}), 400
    except requests.RequestException as e:
        return jsonify({'error': f'Error communicating with Customer Service: {str(e)}'}), 503
    
    if not USE_JSON_STORAGE:
        # MySQL storage
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
                product_response = requests.get(f'http://localhost:5002/products/{item_data["product_id"]}')
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
                db.session.rollback()
                return jsonify({'error': f'Error communicating with Product Service: {str(e)}'}), 503
        
        # Update order total
        order.total_amount = total_amount
        
        try:
            db.session.commit()
            return jsonify(order.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        # JSON storage
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
                product_response = requests.get(f'http://localhost:5002/products/{item_data["product_id"]}')
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
                return jsonify({'error': f'Error communicating with Product Service: {str(e)}'}), 503
        
        # Update order total
        order['total_amount'] = total_amount
        
        # Save to JSON file
        json_data['orders'].append(order)
        json_data['next_order_id'] = order['id'] + 1
        json_data['next_item_id'] = item_id
        
        try:
            save_json_data(json_data)
            return jsonify(order), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.get_json()
    
    if not USE_JSON_STORAGE:
        order = Order.query.get_or_404(order_id)
        if 'status' in data:
            order.status = data['status']
            order.updated_at = datetime.utcnow()
        try:
            db.session.commit()
            return jsonify(order.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        json_data = load_json_data()
        order = next((o for o in json_data['orders'] if o['id'] == order_id), None)
        if order is None:
            return jsonify({'error': 'Order not found'}), 404
            
        if 'status' in data:
            order['status'] = data['status']
            order['updated_at'] = datetime.utcnow().isoformat()
            
        try:
            save_json_data(json_data)
            return jsonify(order)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    if not USE_JSON_STORAGE:
        order = Order.query.get_or_404(order_id)
        try:
            db.session.delete(order)
            db.session.commit()
            return jsonify({'message': 'Order deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    else:
        json_data = load_json_data()
        order_index = next((i for i, o in enumerate(json_data['orders']) if o['id'] == order_id), -1)
        
        if order_index == -1:
            return jsonify({'error': 'Order not found'}), 404
            
        json_data['orders'].pop(order_index)
        
        try:
            save_json_data(json_data)
            return jsonify({'message': 'Order deleted successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5004, debug=True) 