from checkout.models import Item
from checkout.settings import FREE_SHIPPING_THRESHOLD, SHIPPING_CENTS, TAX_BASIS_POINTS


def subtotal(items: list[Item]) -> int:
    if not items or any(item.quantity <= 0 or item.price_cents < 0 for item in items):
        raise ValueError("Items need positive quantities and nonnegative prices")
    return sum(item.price_cents * item.quantity for item in items)


def calculate_total(subtotal_cents: int, discount_percent: int) -> dict[str, int]:
    if subtotal_cents < 0 or not 0 <= discount_percent <= 100:
        raise ValueError("Invalid pricing inputs")
    discount = subtotal_cents * discount_percent // 100
    net = subtotal_cents - discount
    tax = (net * TAX_BASIS_POINTS + 5000) // 10000
    shipping = 0 if net >= FREE_SHIPPING_THRESHOLD else SHIPPING_CENTS
    return {"subtotal": subtotal_cents, "discount": discount, "tax": tax,
            "shipping": shipping, "total": net + tax + shipping}
