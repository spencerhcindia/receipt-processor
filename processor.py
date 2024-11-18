from flask import Flask, request, jsonify
import uuid
import math
from datetime import datetime

app = Flask(__name__)

receipts_data = {}

# let's calculate the points!
def point_calc(receipt):
    points = 0

    # 1 point for every char in retailer name
    points += sum(char.isalnum() for char in receipt.get("retailer", ""))


    # 50 points if total is round dollar amount
    total = float(receipt.get("total", 0))
    if total.is_integer():
        points += 50

    # 25 points if total is multiple of 0.25
    if total % 0.25 == 0:
        points += 25

    # 5 points for every two items on receipt (// divide no remainder)
    items = receipt.get("items", [])
    points += (len(items) // 2) * 5

    # if trimmed length of item desc is multiple of 3, multiply price by 0.2 and round up
    for item in items:

        price = float(item.get("price", 0))
        description = item.get("shortDescription", "").strip()

        if description and len(description) % 3 == 0:

            price = float(item.get("price", 0))
            points += math.ceil(price * 0.2)


    # 6 points if purchase date is odd
    purchase_date = receipt.get("purchaseDate", "")

    if purchase_date:
        day = int(datetime.strptime(purchase_date, "%Y-%m-%d").day)
        if day % 2 != 0:
            points += 6

    # 10 points if time of purchase is between 2pm and 4pm
    purchase_time = receipt.get("purchaseTime", "")

    if purchase_time:
        time = datetime.strptime(purchase_time, "%H:%M").time()
        if time.hour == 14 or (time.hour == 15 and time.minute < 60):
            points += 10

    return points

# endpoint to post the receipt and assign uuid
@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    try:
        receipt = request.json
        if not receipt:
            return jsonify({"error": "Invalid JSON payload"}), 400

        receipt_id = str(uuid.uuid4())

        points = point_calc(receipt)

        receipts_data[receipt_id] = points

        return jsonify({"id": receipt_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# endpoint to get receipt point by id
@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_points(receipt_id):
    try:
        if receipt_id not in receipts_data:
            return jsonify({"error": "Receipt not found"}), 404

        points = receipts_data[receipt_id]
        return jsonify({"points": points})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
