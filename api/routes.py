from flask import request, jsonify, Blueprint
from models import Receipt, ReceiptItem

bp = Blueprint("main", __name__)

@bp.route("/test")
def test():
    return jsonify({"hi": 1})


@bp.route("/receipts/process", method=["POST"])
def process_receipt():
    try:
        body = request.get_data()
        receipt = Receipt.from_json()

        print(receipt)
    except Exception as e:
        pass