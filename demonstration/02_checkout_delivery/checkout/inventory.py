from collections import Counter
from checkout.models import Item


class Inventory:
    def __init__(self, stock: dict[str, int]):
        self.stock = dict(stock)

    def reserve(self, items: list[Item]) -> None:
        requested = Counter()
        for item in items:
            if item.quantity <= 0:
                raise ValueError("Quantity must be positive")
            requested[item.sku] += item.quantity
        if any(self.stock.get(sku, 0) < amount for sku, amount in requested.items()):
            raise ValueError("Insufficient stock")
        for sku, amount in requested.items():
            self.stock[sku] -= amount
