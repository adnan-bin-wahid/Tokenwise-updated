from services.auth_service import AuthService
from services.payment_service import PaymentService, PaymentProcessingError
from utils.logger import log_info, log_error

def main():
    log_info("Starting TokenWise Demo Application...")
    
    auth_service = AuthService()
    payment_service = PaymentService()
    
    # 1. Authenticate user
    token = auth_service.authenticate_user("admin", "adminSecret123")
    if not token:
        log_error("Authentication failed!")
        return

    payload = auth_service.validate_session(token)
    log_info(f"Session validated for user: {payload.get('username')}")

    # 2. Process payment
    try:
        tx = payment_service.process_payment(payload["user_id"], 4999, "4111111111111111")
        log_info(f"Payment completed successfully: {tx.transaction_id}")
    except PaymentProcessingError as err:
        log_error(f"Payment processing error: {err}")

if __name__ == "__main__":
    main()
