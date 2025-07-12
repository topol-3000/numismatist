from enum import StrEnum


class Material(StrEnum):
    GOLD = 'gold'
    SILVER = 'silver'
    COPPER = 'copper'
    BRONZE = 'bronze'
    NICKEL = 'nickel'
    ALUMINUM = 'aluminum'
    BRASS = 'brass'
    PLATINUM = 'platinum'
    STEEL = 'steel'
    ZINC = 'zinc'
    TIN = 'tin'
    LEAD = 'lead'


class PriceType(StrEnum):
    """Price type for item price history tracking."""
    PURCHASE = 'i'  # purchase price
    SOLD = 's'      # sold price
    CURRENT = 'c'   # current market price


class ErrorCode(StrEnum):
    UNKNOWN_ERROR = '000001'

    UNHANDLED_SERVER_ERROR = '100001'
    UNHANDLED_DATABASE_ERROR = '100002'
    INTERNAL_DATABASE_ERROR = '100003'
    DUPLICATE_RECORD_ERROR = '100004'
    NOT_FOUND_RECORD_ERROR = '100005'
