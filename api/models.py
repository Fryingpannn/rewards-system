import math
from typing import List
from dataclasses import dataclass
from datetime import datetime
import re


def is_match(regex, s):
    return bool(re.match(regex, s))


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


@dataclass
class ReceiptItem:
    """
    Class representing an item on a receipt with validation.
    """
    shortDescription: str
    price: str

    def __post_init__(self):
        """Validation"""
        if not self.shortDescription:
            raise ValidationError("shortDescription is required.")
        if not is_match("^\\d+\\.\\d{2}$", self.price):
            raise ValidationError(f"ReceiptItem '{self.shortDescription}''s price is invalid.")
    
    @property
    def trimmed_desc(self) -> str:
        return self.shortDescription.strip()
    
    @property
    def price_value(self) -> float:
        return float(self.price)


@dataclass
class Receipt:
    retailer: str
    purchaseDate: str
    purchaseTime: str
    items: List["ReceiptItem"]
    total: str

    # If anything is invalid and error is shown, on user side probably show to manually input.
    def __post_init__(self):
        """Validation"""
        # We do not check the explicit regex pattern for retailer name because it forbids '&',
        # which is used in the example of M&M Corner Market given in the GitHub ReadMe.
        # So we assume that this is allowed.
        if not self.retailer:
            raise ValidationError(f"Retailer name is required.")
        
        if not self.purchaseDate:
            raise ValidationError("purchaseDate is required.")
        try:
            datetime.strptime(self.purchaseDate, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("purchaseDate must be in format 'YYYY-MM-DD'.")
        
        if not self.total:
            raise ValidationError("total is required.")
        if not re.match('^\\d+\\.\\d{2}$', self.total):
            raise ValidationError("total must be in format 'X.XX'.")

        if not self.purchaseTime:
            raise ValidationError("purchaseTime is required.")
        try:
            # TODO: Accept am/pm format as well
            datetime.strptime(self.purchaseTime, "%H:%M")
        except ValueError:
            raise ValidationError("purchaseTime must be in format 'HH:MM' (24-hour).")
        
        try:
            if not self.items: 
                raise Exception("No items in receipt.")
            # Create receipt items. Same items and prices can also be stored as frequency instead to save space.
            self.items = list(map(lambda item: ReceiptItem(**item), self.items))
        except Exception as e:
            raise ValidationError(f"Invalid item data: {str(e)}")
    
    @classmethod
    def from_json(cls, json_data):
        """Create a Receipt instance from JSON data"""
        if not isinstance(json_data, dict):
            raise ValidationError("Invalid receipt data.")

        return cls(**json_data)
    
    @property
    def total_value(self) -> float:
        """Return the total as a float"""
        return float(self.total)
    
    @property
    def purchase_date_obj(self) -> datetime:
        """Return the purchase date as a datetime object"""
        return datetime.strptime(self.purchaseDate, "%Y-%m-%d")
    
    @property
    def purchase_time_obj(self) -> datetime:
        """Return the purchase time as a datetime object"""
        return datetime.strptime(self.purchaseTime, "%H:%M")
    
    @classmethod
    def calculate_points(cls, receipt) -> int:
        """
        Calculate points based on the rules specified in the requirements.
        """
        points = 0
        
        # Rule 1: One point for every alphanumeric character in the retailer name
        points += sum(1 for char in receipt.retailer if char.isalnum())
        
        # Rule 2: 50 points if the total is a round dollar amount with no cents
        if receipt.total.endswith(".00"):
            points += 50
        
        # Rule 3: 25 points if the total is a multiple of 0.25
        if receipt.total_value % 0.25 == 0:
            points += 25
        
        # Rule 4: 5 points for every two items on the receipt
        points += (len(receipt.items) // 2) * 5
        
        # Rule 5: If the trimmed length of the item description is a multiple of 3,
        # multiply the price by 0.2 and round up to the nearest integer
        for item in receipt.items:
            if len(item.trimmed_desc) % 3 == 0:
                item_points = math.ceil(item.price_value * 0.2)
                points += item_points
        
        # Rule 6: 6 points if the day in the purchase date is odd
        if receipt.purchase_date_obj.day % 2 == 1:  # odd day
            points += 6
        
        # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm
        purchase_time = receipt.purchase_time_obj.time()
        if datetime.strptime("14:00", "%H:%M").time() < purchase_time < datetime.strptime("16:00", "%H:%M").time():
            points += 10
        
        return points
    