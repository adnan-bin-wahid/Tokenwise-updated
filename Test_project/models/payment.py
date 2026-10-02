from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

@dataclass
class PaymentTransaction:
    transaction_id: str
    user_id: str
    amount_cents: int
    currency: str = "USD"
    status: PaymentStatus = PaymentStatus.PENDING
    gateway_reference: str = ""
    error_message: str = ""
    retry_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
