"""
Database Configuration Module
==========================

This module handles the database configuration and initialization for the Order Service.
It supports both MySQL and JSON file-based storage, with automatic fallback to JSON
if MySQL connection fails.

Configuration:
------------
The database connection is configured through environment variables:
- MYSQL_HOST: Database host (default: localhost)
- MYSQL_PORT: Database port (default: 3308)
- MYSQL_USER: Database user (default: root)
- MYSQL_PASSWORD: Database password
- MYSQL_DATABASE: Database name (default: order_db)

Fallback:
--------
If MySQL connection fails, the service automatically falls back to JSON file storage
in the data/orders.json file.

Author: Dennis
Version: 1.0.0
Date: March 2024
"""

from flask_sqlalchemy import SQLAlchemy
import os

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """
    Initialize the database connection.
    
    Args:
        app: Flask application instance
    
    Returns:
        bool: True if MySQL connection successful, False if using JSON fallback
    """
    # ... existing code ...