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
    short_description: str
    price: str

    def __post_init__(self):
        """Validation"""
        if not self.short_description:
            raise ValidationError("shortDescription is required.")
        if not re.match("^\\d+\\.\\d{2}$"):
            raise ValidationError(f"ReceiptItem '{self.short_description}''s price is invalid.")
    
    @property
    def trimmed_desc(self) -> str:
        return self.short_description.trim()
    
    @property
    def price_val(self) -> float:
        return float(self.price)


@dataclass
class Receipt:
    retailer: str
    purchaseDate: str
    purchaseTime: str
    items: List["ReceiptItem"]
    total: str

    def __post_init__(self):
        """Validation"""
        if not self.retailer or not is_match("^[\\w\\s\\-]+$", self.retailer):
            raise ValidationError(f"Receipt '{self.retailer}' has an invalid retailer name.")
        
        if not self.purchaseDate:
            raise ValidationError("purchaseDate is required.")
        try:
            datetime.strptime(self.purchaseDate, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("purchaseDate must be in format 'YYYY-MM-DD'. Please verify input.")
        
        if not self.total:
            raise ValidationError("total is required.")
        if not re.match('^\\d+\\.\\d{2}$', self.total):
            raise ValidationError("total must be in format 'X.XX'. Please verify input.")

        if not self.purchaseTime:
            raise ValidationError("purchaseTime is required.")
        try:
            # TODO: Accept am/pm format as well
            datetime.strptime(self.purchaseTime, "%H:%M")
        except ValueError:
            raise ValidationError("purchaseTime must be in format 'HH:MM' (24-hour). Please verify input.")
        
        try:
            if not self.items: 
                raise Exception("No items in receipt.")
            # Create receipt items
            self.items = map(lambda item: ReceiptItem(**item), self.items)
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
    