"""
Order Service Models
==================

This module defines the database models for the order service.

Models:
------
- Order: Represents an order in the system
- OrderItem: Represents individual items within an order

Author: Dennis
Version: 1.0.0
Date: March 2024
"""

from database import db
from datetime import datetime

class Order(db.Model):
    """
    Order Model
    
    Represents a customer order in the system. Each order can contain multiple
    OrderItems and tracks the total amount and status of the order.

    Attributes:
        id (int): Primary key
        customer_id (int): ID of the customer who placed the order
        created_at (datetime): Timestamp when order was created
        updated_at (datetime): Timestamp when order was last updated
        status (str): Current status of the order (PENDING/PROCESSING/COMPLETED/CANCELLED)
        total_amount (float): Total cost of all items in the order
        items (relationship): Relationship to OrderItem model
    """
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='PENDING')
    total_amount = db.Column(db.Float, default=0.0)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """
        Convert the order to a dictionary representation.
        
        Returns:
            dict: Dictionary containing order data
        """
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status,
            'total_amount': self.total_amount,
            'items': [item.to_dict() for item in self.items]
        }

class OrderItem(db.Model):
    """
    OrderItem Model
    
    Represents an individual item within an order. Each item is associated with
    a product and includes quantity and price information.

    Attributes:
        id (int): Primary key
        order_id (int): Foreign key to Order
        product_id (int): ID of the product
        quantity (int): Number of items ordered
        unit_price (float): Price per unit at time of order
    """
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        """
        Convert the order item to a dictionary representation.
        
        Returns:
            dict: Dictionary containing order item data
        """
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total': self.quantity * self.unit_price
        }