from flask import Flask, request, jsonify
from database import db
from models import Order, OrderItem
import requests
import os
from datetime import datetime

app = Flask(__name__)

# MySQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3308/order_db'  # Change the database name or the port to be inline with your xampp
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    
    # Create new order
    order = Order(
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

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    
    if 'status' in data:
        order.status = data['status']
        order.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify(order.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    try:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Order deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5003, debug=True) 