from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

# Dummy fetch from other service (simulasi)
def fetch_orders():
    return [
        {"id": 1, "total_amount": 100, "status": "COMPLETED", "date": "2024-01-01"},
        {"id": 2, "total_amount": 200, "status": "PENDING", "date": "2024-02-10"},
        {"id": 3, "total_amount": 150, "status": "COMPLETED", "date": "2024-03-15"},
    ]

@app.route("/analytics/sales", methods=["GET"])
def analytics_sales():
    try:
        status_filter = request.args.get("status")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        orders = fetch_orders()
        df = pd.DataFrame(orders)

        if status_filter:
            df = df[df["status"] == status_filter]
        if start_date:
            df = df[df["date"] >= start_date]
        if end_date:
            df = df[df["date"] <= end_date]

        total_revenue = df["total_amount"].sum()
        avg_order = df["total_amount"].mean() or 0
        count = len(df)

        return jsonify({
            "total_revenue": total_revenue,
            "average_order": avg_order,
            "total_orders": count
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)
