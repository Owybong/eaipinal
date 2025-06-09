"""
Product Service
=============

This service manages the product catalog for the EAI Bookstore system.

Features:
- Product CRUD operations
- SKU management
- Price management
- Category management

Author: Dennis
Version: 1.0.0
Date: March 2024
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from database import db
from models import Product
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_DIR = os.path.abspath('instance')
DB_FILE = 'products.db'
DB_PATH = os.path.join(DB_DIR, DB_FILE)

# Ensure instance directory exists
os.makedirs(DB_DIR, exist_ok=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

def validate_product_data(data, check_required=True):
    """Validate product input data"""
    if check_required:
        required_fields = ['name', 'sku', 'category', 'price']
        for field in required_fields:
            if field not in data:
                return False, f'{field} is required'
            
    if 'price' in data and (not isinstance(data['price'], (int, float)) or data['price'] < 0):
        return False, 'price must be a non-negative number'
        
    if 'sku' in data and len(str(data['sku'])) > 50:
        return False, 'sku must be less than 50 characters'
        
    if 'name' in data and len(str(data['name'])) > 100:
        return False, 'name must be less than 100 characters'
        
    if 'category' in data and len(str(data['category'])) > 50:
        return False, 'category must be less than 50 characters'
        
    return True, None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Try a simple database query
        Product.query.limit(1).all()
        db_status = "UP"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "DOWN"

    health = {
        'status': 'UP' if db_status == "UP" else 'DOWN',
        'timestamp': datetime.utcnow().isoformat(),
        'database': db_status
    }
    
    return jsonify(health)

@app.route('/products', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        category = request.args.get('category')
        query = Product.query
        
        if category:
            query = query.filter_by(category=category)
            
        products = query.all()
        logger.info(f"Retrieved {len(products)} products")
        return jsonify([p.to_dict() for p in products])
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return jsonify({'error': 'Failed to fetch products'}), 500

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product"""
    try:
        product = Product.query.get_or_404(product_id)
        logger.info(f"Retrieved product {product_id}")
        return jsonify(product.to_dict())
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        return jsonify({'error': 'Product not found'}), 404

@app.route('/products', methods=['POST'])
def create_product():
    """Create a new product"""
    logger.info("Received request to create product")
    try:
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        # Validate input data
        is_valid, error = validate_product_data(data)
        if not is_valid:
            logger.error(f"Validation error: {error}")
            return jsonify({'error': error}), 400
            
        # Check if SKU already exists
        existing_product = Product.query.filter_by(sku=data['sku']).first()
        if existing_product:
            logger.error(f"SKU {data['sku']} already exists")
            return jsonify({'error': 'SKU already exists'}), 400
        
        new_product = Product(
            name=data['name'],
            sku=data['sku'],
            category=data['category'],
            price=float(data['price'])
        )
        logger.info(f"Created product object: {new_product.to_dict()}")
        
        db.session.add(new_product)
        db.session.commit()
        
        logger.info(f"Successfully created product with ID {new_product.id}")
        return jsonify(new_product.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Validate input data
        is_valid, error = validate_product_data(data, check_required=False)
        if not is_valid:
            return jsonify({'error': error}), 400
            
        # Check SKU uniqueness if it's being updated
        if 'sku' in data and data['sku'] != product.sku:
            if Product.query.filter_by(sku=data['sku']).first():
                return jsonify({'error': 'SKU already exists'}), 400
        
        product.name = data.get('name', product.name)
        product.sku = data.get('sku', product.sku)
        product.category = data.get('category', product.category)
        product.price = float(data.get('price', product.price))
        
        db.session.commit()
        
        logger.info(f"Updated product {product_id}")
        return jsonify(product.to_dict())
        
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        
        logger.info(f"Deleted product {product_id}")
        return jsonify({"message": "Product deleted"})
        
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

def init_sample_products():
    """Initialize sample products if none exist"""
    try:
        if Product.query.count() == 0:
            sample_products = [
                {
                    "name": "The Great Gatsby",
                    "sku": "BOOK-001",
                    "category": "Fiction",
                    "price": 9.99
                },
                {
                    "name": "To Kill a Mockingbird",
                    "sku": "BOOK-002",
                    "category": "Fiction",
                    "price": 12.99
                },
                {
                    "name": "Python Programming",
                    "sku": "BOOK-003",
                    "category": "Technology",
                    "price": 29.99
                },
                {
                    "name": "Data Structures",
                    "sku": "BOOK-004",
                    "category": "Technology",
                    "price": 24.99
                }
            ]
            
            for product_data in sample_products:
                product = Product(**product_data)
                db.session.add(product)
            
            db.session.commit()
            logger.info(f"Initialized {len(sample_products)} sample products")
    except Exception as e:
        logger.error(f"Error initializing sample products: {str(e)}")
        db.session.rollback()

# Create database and initialize sample data
with app.app_context():
    try:
        # Always create tables
        db.create_all()
        logger.info(f"Database initialized at {DB_PATH}")
        
        # Initialize sample products if none exist
        if Product.query.count() == 0:
            init_sample_products()
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
    
# SKU stands for Stock Keeping Unit.
# It's a unique code used to identify a product in your inventory system.




