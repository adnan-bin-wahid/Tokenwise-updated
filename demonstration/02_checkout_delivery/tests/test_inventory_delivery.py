import unittest
from checkout.inventory import Inventory
from checkout.models import Item
from delivery import delivery_days, tracking_summary


class InventoryDeliveryTests(unittest.TestCase):
    def test_duplicate_sku_reservation_is_atomic(self):
        inventory = Inventory({"BOOK": 3})
        with self.assertRaises(ValueError):
            inventory.reserve([Item("BOOK", 100, 2), Item("BOOK", 100, 2)])
        self.assertEqual(inventory.stock["BOOK"], 3)

    def test_delivery_and_tracking(self):
        self.assertEqual(delivery_days("regional", express=True), 1)
        self.assertEqual(tracking_summary(["packed", "dispatched"]), "dispatched")
        with self.assertRaises(ValueError):
            delivery_days("unknown")
