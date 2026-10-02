import unittest
from services.payment_service import PaymentService, PaymentProcessingError
from models.payment import PaymentStatus

class TestPaymentService(unittest.TestCase):
    def setUp(self):
        self.payment_service = PaymentService()

    def test_successful_payment(self):
        tx = self.payment_service.process_payment("usr_123", 2500, "4111111111111111")
        self.assertEqual(tx.status, PaymentStatus.SUCCESS)
        self.assertTrue(tx.gateway_reference.startswith("gw_ref_"))

    def test_invalid_card_number(self):
        tx = self.payment_service.process_payment("usr_123", 1000, "123")
        self.assertEqual(tx.status, PaymentStatus.FAILED)
        self.assertIn("Invalid card number", tx.error_message)

    def test_gateway_timeout_retry_exhaustion(self):
        with self.assertRaises(PaymentProcessingError):
            self.payment_service.process_payment("usr_123", 5000, "4111111111110000")

if __name__ == "__main__":
    unittest.main()
