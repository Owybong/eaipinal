from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

# Dummy: Simulasi pengambilan data dari order_service
def fetch_orders():
    return [
        {"id": 1, "total_amount": 120.5},
        {"id": 2, "total_amount": 90.0},
        {"id": 3, "total_amount": 150.25},
    ]

@app.route("/analytics/sales", methods=["GET"])
def get_sales_kpi():
    orders = fetch_orders()
    df = pd.DataFrame(orders)
    total_revenue = df["total_amount"].sum()
    avg_order_value = df["total_amount"].mean()
    total_orders = len(orders)

    return jsonify({
        "total_revenue": total_revenue,
        "average_order_value": avg_order_value,
        "total_orders": total_orders
    })

from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

# Dummy fetch from other service (simulasikan dulu)
def fetch_orders():
    return [
        {"id": 1, "total_amount": 100, "status": "COMPLETED", "date": "2024-01-01"},
        {"id": 2, "total_amount": 200, "status": "PENDING", "date": "2024-02-10"},
        {"id": 3, "total_amount": 150, "status": "COMPLETED", "date": "2024-03-15"},
    ]

@app.route("/analytics/sales", methods=["GET"])
def analytics_sales():
    # Ambil parameter dari frontend
    status_filter = request.args.get("status")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    orders = fetch_orders()
    df = pd.DataFrame(orders)

    # Filter status
    if status_filter:
        df = df[df["status"] == status_filter]

    # Filter tanggal
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]

    total_revenue = df["total_amount"].sum()
    avg_order = df["total_amount"].mean()
    count = len(df)

    return jsonify({
        "total_revenue": total_revenue,
        "average_order": avg_order,
        "total_orders": count
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)