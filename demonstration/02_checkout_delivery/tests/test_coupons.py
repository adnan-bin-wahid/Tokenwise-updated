import unittest
from checkout.coupons import CouponService
from checkout.models import Coupon


class CouponTests(unittest.TestCase):
    def setUp(self):
        self.service = CouponService({"WELCOME10": Coupon("WELCOME10", 10, 1000, 5000)})

    def test_coupon_expiry_boundary(self):
        self.assertEqual(self.service.discount_percent("WELCOME10", 10000, 999), 10)
        self.assertEqual(self.service.discount_percent("WELCOME10", 10000, 1000), 0)

    def test_unknown_and_minimum_spend(self):
        self.assertEqual(self.service.discount_percent("UNKNOWN", 10000, 999), 0)
        self.assertEqual(self.service.discount_percent("WELCOME10", 4999, 999), 0)
