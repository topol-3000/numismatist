from enum import Enum

class TransactionType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    GIFT = "gift"
    OTHER = "other"
