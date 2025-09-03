# Import all schemas
from .collection import (
    CollectionAddItem,
    CollectionBase,
    CollectionCreate,
    CollectionRead,
    CollectionRemoveItem,
    CollectionUpdate,
    CollectionWithItems,
    SharedCollectionRead,
)
from .grading_company import (
    GradingCompanyBase,
    GradingCompanyCreate,
    GradingCompanyRead,
    GradingCompanyUpdate,
)
from .grading_info import (
    GradingInfoBase,
    GradingInfoCreate,
    GradingInfoRead,
    GradingInfoUpdate,
)
from .item import (
    ItemBase,
    ItemCreate,
    ItemRead,
    ItemReadWithPriceHistory,
    ItemReadWithPurchasePrice,
    ItemUpdate,
)
from .item_price_history import (
    ItemPriceHistoryBase,
    ItemPriceHistoryCreate,
    ItemPriceHistoryRead,
    ItemPriceHistoryUpdate,
)
from .user import UserCreate, UserRead, UserRegisteredNotification, UserUpdate

# Define what should be exported when using 'from schemas import *'
__all__ = [
    # User schemas
    "UserRead",
    "UserCreate",
    "UserUpdate",
    "UserRegisteredNotification",
    # Item schemas
    "ItemBase",
    "ItemCreate",
    "ItemUpdate",
    "ItemRead",
    "ItemReadWithPurchasePrice",
    "ItemReadWithPriceHistory",
    # Item price history schemas
    "ItemPriceHistoryBase",
    "ItemPriceHistoryCreate",
    "ItemPriceHistoryRead",
    "ItemPriceHistoryUpdate",
    # Grading company schemas
    "GradingCompanyBase",
    "GradingCompanyCreate",
    "GradingCompanyRead",
    "GradingCompanyUpdate",
    # Grading info schemas
    "GradingInfoBase",
    "GradingInfoCreate",
    "GradingInfoRead",
    "GradingInfoUpdate",
    # Collection schemas
    "CollectionBase",
    "CollectionCreate",
    "CollectionUpdate",
    "CollectionRead",
    "CollectionWithItems",
    "CollectionAddItem",
    "CollectionRemoveItem",
    "SharedCollectionRead",
]
