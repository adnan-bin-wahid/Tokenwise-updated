from checkout.coupons import CouponService
from checkout.inventory import Inventory
from checkout.models import Item
from checkout.pricing import calculate_total, subtotal


class OrderService:
    def __init__(self, coupons: CouponService, inventory: Inventory):
        self.coupons = coupons
        self.inventory = inventory

    def checkout(self, items: list[Item], code: str, now: int) -> dict[str, int]:
        amount = subtotal(items)
        percent = self.coupons.discount_percent(code, amount, now)
        totals = calculate_total(amount, percent)
        self.inventory.reserve(items)
        return totals
