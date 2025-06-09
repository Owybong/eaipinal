import requests
import pandas as pd

def get_order_data():
    try:
        res = requests.get("http://order_service:5003/orders")
        return pd.DataFrame(res.json())
    except:
        return pd.DataFrame()

def get_inventory_data():
    try:
        res = requests.get("http://inventory_service:5002/inventory")
        return pd.DataFrame(res.json())
    except:
        return pd.DataFrame()
