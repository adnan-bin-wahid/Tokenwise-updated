import unittest
from checkout.coupons import CouponService
from checkout.inventory import Inventory
from checkout.models import Coupon, Item
from checkout.orders import OrderService
from checkout.pricing import calculate_total


class OrderTests(unittest.TestCase):
    def test_expired_coupon_does_not_discount_order(self):
        order = OrderService(CouponService({"WELCOME10": Coupon("WELCOME10", 10, 1000)}), Inventory({"BOOK": 2}))
        totals = order.checkout([Item("BOOK", 10000, 1)], "WELCOME10", 1000)
        self.assertEqual(totals, {"subtotal": 10000, "discount": 0, "tax": 1500, "shipping": 500, "total": 12000})

    def test_tax_rounds_half_up_in_integer_cents(self):
        self.assertEqual(calculate_total(10, 0)["tax"], 2)
        self.assertEqual(calculate_total(9, 0)["tax"], 1)

    def test_discount_uses_floor_cents(self):
        self.assertEqual(calculate_total(999, 10)["discount"], 99)

    def test_invalid_cart_does_not_reserve_stock(self):
        inventory = Inventory({"BOOK": 2})
        order = OrderService(CouponService({}), inventory)
        with self.assertRaises(ValueError):
            order.checkout([Item("BOOK", 100, 0)], "", 100)
        self.assertEqual(inventory.stock["BOOK"], 2)
