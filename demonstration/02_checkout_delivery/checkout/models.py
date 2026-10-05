from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    sku: str
    price_cents: int
    quantity: int


@dataclass(frozen=True)
class Coupon:
    code: str
    percent: int
    expires_at: int
    minimum_cents: int = 0
