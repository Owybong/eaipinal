from flask import Flask, jsonify, request
import pandas as pd
import requests
import os
import json
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# Configure logging based on environment
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

# Add file handler
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'analytics.log'),
    maxBytes=1024 * 1024,  # 1MB
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
logging.getLogger().addHandler(file_handler)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Service URLs from environment variables
ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://order-service:5004')

# Data directory for caching
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)
CACHE_FILE = os.path.join(DATA_DIR, 'analytics_cache.json')

def save_to_cache(data):
    """Save analytics data to cache"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Error saving to cache: {e}")

def load_from_cache():
    """Load analytics data from cache"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading from cache: {e}")
    return None

def fetch_orders():
    """Fetch orders from the Order Service"""
    try:
        response = requests.get(f"{ORDER_SERVICE_URL}/orders", timeout=5)
        if response.status_code == 200:
            orders = response.json()
            # Cache the successful response
            save_to_cache(orders)
            return orders
        else:
            logger.error(f"Failed to fetch orders. Status code: {response.status_code}")
            # Try to load from cache if request fails
            cached_data = load_from_cache()
            if cached_data:
                logger.info("Using cached data")
                return cached_data
            return []
    except requests.RequestException as e:
        logger.error(f"Error fetching orders: {e}")
        # Try to load from cache if request fails
        cached_data = load_from_cache()
        if cached_data:
            logger.info("Using cached data")
            return cached_data
        return []

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    try:
        # Try to fetch orders to check connectivity
        orders = fetch_orders()
        order_service_status = "UP" if isinstance(orders, list) else "DOWN"
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        order_service_status = "DOWN"

    health = {
        'status': 'UP' if order_service_status == "UP" else 'DOWN',
        'timestamp': datetime.utcnow().isoformat(),
        'dependencies': {
            'order_service': order_service_status
        },
        'environment': os.getenv('FLASK_ENV', 'production')
    }
    
    return jsonify(health)

@app.route("/analytics/sales", methods=["GET"])
def analytics_sales():
    try:
        status_filter = request.args.get("status")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        logger.info(f"Fetching analytics with filters - status: {status_filter}, start_date: {start_date}, end_date: {end_date}")

        orders = fetch_orders()
        if not orders:
            return jsonify({
                "total_revenue": 0,
                "average_order": 0,
                "total_orders": 0
            })

        df = pd.DataFrame(orders)
        
        # Convert created_at to datetime if it exists
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Apply filters
        if status_filter:
            df = df[df["status"] == status_filter]
            logger.info(f"Filtered by status: {status_filter}, remaining orders: {len(df)}")
        if start_date:
            df = df[df["created_at"] >= start_date]
            logger.info(f"Filtered by start date: {start_date}, remaining orders: {len(df)}")
        if end_date:
            df = df[df["created_at"] <= end_date]
            logger.info(f"Filtered by end date: {end_date}, remaining orders: {len(df)}")

        total_revenue = df["total_amount"].sum()
        avg_order = df["total_amount"].mean() if not df.empty else 0
        count = len(df)

        result = {
            "total_revenue": float(total_revenue),
            "average_order": float(avg_order),
            "total_orders": count
        }

        logger.info(f"Analytics calculated: {result}")
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in analytics: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)
