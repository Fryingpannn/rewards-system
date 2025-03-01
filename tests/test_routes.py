import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
import json
from api.main import app

class TestReceiptProcessor(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Clear the database and cache before each test
        app.db = {}
        app.cache = {}

    # =================== Happy Paths ==============================

    def test_target_receipt(self):
        # Test case for the Target receipt example from README
        with open('examples/grocery.json', 'r') as f:
            receipt_data = json.load(f)
        
        # Process receipt
        response = self.app.post('/receipts/process',
                               json=receipt_data,
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Get the receipt ID
        receipt_id = response.json['id']
        
        # Get points
        response = self.app.get(f'/receipts/{receipt_id}/points')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['points'], 28)  # Expected points from README

    def test_simple_target_receipt(self):
        # Test case for simple Target receipt
        with open('examples/simple-receipt.json', 'r') as f:
            receipt_data = json.load(f)
        
        # Process receipt
        response = self.app.post('/receipts/process',
                               json=receipt_data,
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Get the receipt ID
        receipt_id = response.json['id']
        
        # Get points
        response = self.app.get(f'/receipts/{receipt_id}/points')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['points'], 31)  # Expected points: 31
    
    def test_walgreens_morning_receipt(self):
        # Test case for Walgreens morning receipt
        with open('examples/morning-receipt.json', 'r') as f:
            receipt_data = json.load(f)
        
        # Process receipt
        response = self.app.post('/receipts/process',
                               json=receipt_data,
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Get the receipt ID
        receipt_id = response.json['id']
        
        # Get points
        response = self.app.get(f'/receipts/{receipt_id}/points')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['points'], 15) 

    def test_corner_market_receipt(self):
        # Test case for M&M Corner Market receipt example from README
        with open('examples/corner-market.json', 'r') as f:
            receipt_data = json.load(f)
        
        response = self.app.post('/receipts/process',
                               json=receipt_data,
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        receipt_id = response.json['id']
        
        response = self.app.get(f'/receipts/{receipt_id}/points')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['points'], 109)
    

    # =================== Invalid Paths =============================


    def test_invalid_receipt(self):
        # Test invalid receipt data
        invalid_receipt = {
            "retailer": "",  # Invalid: empty retailer
            "purchaseDate": "2022-03-20",
            "purchaseTime": "14:33",
            "items": [],  # Invalid: empty items
            "total": "9.00"
        }
        
        response = self.app.post('/receipts/process',
                               json=invalid_receipt,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_nonexistent_receipt(self):
        # Test getting points for non-existent receipt
        response = self.app.get('/receipts/nonexistent-id/points')
        self.assertEqual(response.status_code, 404)

    def test_invalid_date_format(self):
        # Test invalid date format
        invalid_receipt = {
            "retailer": "Target",
            "purchaseDate": "03-20-2022",  # Invalid: wrong format
            "purchaseTime": "14:33",
            "items": [{"shortDescription": "Item 1", "price": "5.00"}],
            "total": "5.00"
        }
        response = self.app.post('/receipts/process',
                               json=invalid_receipt,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_time_format(self):
        # Test invalid time format
        invalid_receipt = {
            "retailer": "Target",
            "purchaseDate": "2022-03-20",
            "purchaseTime": "2:33 PM",  # Invalid: should be 24hr format
            "items": [{"shortDescription": "Item 1", "price": "5.00"}],
            "total": "5.00"
        }
        response = self.app.post('/receipts/process',
                               json=invalid_receipt,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_price_format(self):
        # Test invalid price format
        invalid_receipt = {
            "retailer": "Target",
            "purchaseDate": "2022-03-20",
            "purchaseTime": "14:33",
            "items": [{"shortDescription": "Item 1", "price": "5.0"}],  # Invalid: needs 2 decimal places
            "total": "5.00"
        }
        response = self.app.post('/receipts/process',
                               json=invalid_receipt,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_total_format(self):
        # Test invalid total format
        invalid_receipt = {
            "retailer": "Target",
            "purchaseDate": "2022-03-20",
            "purchaseTime": "14:33",
            "items": [{"shortDescription": "Item 1", "price": "5.00"}],
            "total": "5"  # Invalid: needs decimal places
        }
        response = self.app.post('/receipts/process',
                               json=invalid_receipt,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_missing_required_fields(self):
        # Test missing required fields
        invalid_receipt = {
            "retailer": "Target",
            "purchaseDate": "2022-03-20",
            # Missing purchaseTime
            "items": [{"shortDescription": "Item 1", "price": "5.00"}],
            "total": "5.00"
        }
        response = self.app.post('/receipts/process',
                               json=invalid_receipt,
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_malformed_json(self):
        # Test malformed JSON
        response = self.app.post('/receipts/process',
                               data="not a json",
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()