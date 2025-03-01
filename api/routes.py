from flask import request, jsonify, Blueprint, current_app as app
from .models import ValidationError, Receipt
import uuid

bp = Blueprint("main", __name__)

@bp.route("/test")
def test():
    print("======= Database =======")
    print(app.db)
    print("======= Cache =======")
    print(app.cache)
    return jsonify({}), 200


@bp.route("/receipts/process", methods=["POST"])
def process_receipt():
    """
    Processes a receipt, generates an ID for it, and stores it in the database.
    """
    try:
        body = request.get_json()
        receipt = Receipt.from_json(body)
        receipt_id = str(uuid.uuid4())

        # Simulate storing receipt in database
        app.db[receipt_id] = receipt
        return jsonify({"id": receipt_id}), 200
    except ValidationError as e:
        return jsonify({"error": f"The receipt is invalid. {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}."}), 400


@bp.route('/receipts/<id>/points', methods=['GET'])
def get_points(id):
    """
    Get the points for a receipt by ID.
    Calculate points on-demand and cache the result.
    """
    if id not in app.db:
        return jsonify({"error": "No receipt found for that ID."}), 404
    try:
        # Check if points already calculated and cached
        if id not in app.cache:
            # Simulate retrieving receipt from DB
            receipt = app.db[id]
            # Calculate and cache points (e.g. Redis)
            app.cache[id] = Receipt.calculate_points(receipt)
        return jsonify({"points": app.cache[id]}), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}."}), 500


@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200