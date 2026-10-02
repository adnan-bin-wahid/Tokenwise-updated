import time
import uuid

from config.settings import config
from models.payment import PaymentStatus, PaymentTransaction
from utils.logger import log_audit, log_error, log_info


class PaymentProcessingError(Exception):
    """Raised after retryable payment-gateway failures are exhausted."""


class PaymentService:
    """Handles payment transactions and gateway retries."""

    def __init__(self):
        self._transactions: dict[str, PaymentTransaction] = {}

    def process_payment(
        self, user_id: str, amount_cents: int, card_number: str
    ) -> PaymentTransaction:
        tx_id = f'tx_{uuid.uuid4().hex[:8]}'
        transaction = PaymentTransaction(
            transaction_id=tx_id,
            user_id=user_id,
            amount_cents=amount_cents,
        )
        self._transactions[tx_id] = transaction

        for attempt in range(1, config.MAX_PAYMENT_RETRIES + 1):
            transaction.retry_count = attempt
            try:
                log_info(
                    f'Attempting payment {tx_id} '
                    f'(Attempt {attempt}/{config.MAX_PAYMENT_RETRIES})...'
                )
                reference = self._call_payment_gateway_api(card_number, amount_cents)
                transaction.status = PaymentStatus.SUCCESS
                transaction.gateway_reference = reference
                log_audit(user_id, 'payment_charge', f'SUCCESS_{amount_cents}_CENTS')
                return transaction
            except TimeoutError as exc:
                transaction.error_message = f'Timeout error on attempt {attempt}: {exc}'
                log_error(f'Gateway timeout on payment {tx_id}', exc)
                if attempt == config.MAX_PAYMENT_RETRIES:
                    transaction.status = PaymentStatus.FAILED
                    log_audit(user_id, 'payment_charge', 'FAILED_TIMEOUT')
                    raise PaymentProcessingError(
                        f'Payment failed after {config.MAX_PAYMENT_RETRIES} attempts due to gateway timeout.'
                    ) from exc
                time.sleep(0.05)
            except ValueError as exc:
                transaction.status = PaymentStatus.FAILED
                transaction.error_message = str(exc)
                log_error(f'Validation failure for payment {tx_id}', exc)
                log_audit(user_id, 'payment_charge', 'FAILED_INVALID_INPUT')
                return transaction

        return transaction

    @staticmethod
    def _call_payment_gateway_api(card_number: str, amount_cents: int) -> str:
        if amount_cents <= 0:
            raise ValueError('Payment amount must be positive')
        if not card_number or len(card_number) < 13:
            raise ValueError('Invalid card number format')
        if card_number.endswith('0000'):
            raise TimeoutError('Connection timed out reaching payment gateway endpoint')
        return f'gw_ref_{uuid.uuid4().hex[:12]}'
