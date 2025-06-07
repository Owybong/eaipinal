from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from database import db
from models import Product

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(
        name=data['name'],
        sku=data['sku'],
        category=data['category'],
        price=data['price']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201
  
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    product.name = data.get('name', product.name)
    product.sku = data.get('sku', product.sku)
    product.category = data.get('category', product.category)
    product.price = data.get('price', product.price)
    db.session.commit()
    return jsonify(product.to_dict())


@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})

if __name__ == '__main__':
    app.run(port=5002, debug=True)
    
# SKU stands for Stock Keeping Unit.
# It’s a unique code used to identify a product in your inventory system.




