from enum import StrEnum


class Material(StrEnum):
    GOLD = "gold"
    SILVER = "silver"
    COPPER = "copper"
    BRONZE = "bronze"
    NICKEL = "nickel"
    ALUMINUM = "aluminum"
    BRASS = "brass"
    PLATINUM = "platinum"
    STEEL = "steel"
    ZINC = "zinc"
    TIN = "tin"
    LEAD = "lead"


class PriceType(StrEnum):
    """Price type for item price history tracking."""

    PURCHASE = "purchase"
    CURRENT = "current"
    SALE = "sale"
    COLLECTION_PURCHASE = "collection_purchase"
    COLLECTION_SALE = "collection_sale"


class CounterpartyRole(StrEnum):
    """Role of counterparty in transactions."""

    SELLER = "seller"
    BUYER = "buyer"
    BOTH = "dealer"


class Currency(StrEnum):
    """Currency types for transactions."""

    USD = "usd"
    EUR = "eur"


class TransactionStatus(StrEnum):
    """Status of transaction."""

    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TransactionType(StrEnum):
    """Type of transaction."""

    PURCHASE = "purchase"
    SALE = "sale"
    LOSS = "loss"
    GIFT = "gift"
    DAMAGE = "damage"
    THEFT = "theft"


class ImageType(StrEnum):
    """Image type for item images."""

    FRONT = "front"
    BACK = "back"
    ADDITIONAL = "additional"

    def is_unique(self) -> bool:
        """Return True if this image type should be unique per item."""
        return self in {self.FRONT, self.BACK}

    @classmethod
    def get_unique_types(cls) -> list["ImageType"]:
        """Get all image types that should be unique per item."""
        return [image_type for image_type in cls if image_type.is_unique()]

    @classmethod
    def get_non_unique_types(cls) -> list["ImageType"]:
        """Get all image types that can have multiple instances per item."""
        return [image_type for image_type in cls if not image_type.is_unique()]


class ErrorCode(StrEnum):
    UNKNOWN_ERROR = "000001"

    UNHANDLED_SERVER_ERROR = "100001"
    UNHANDLED_DATABASE_ERROR = "100002"
    INTERNAL_DATABASE_ERROR = "100003"
    DUPLICATE_RECORD_ERROR = "100004"
    NOT_FOUND_RECORD_ERROR = "100005"
