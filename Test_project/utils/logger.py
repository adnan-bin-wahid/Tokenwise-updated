import time
from config.settings import config

def log_info(message: str):
    """Log an info message with timestamp."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [INFO] {message}")

def log_error(message: str, exc: Exception = None):
    """Log an error message with optional exception details."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    err_str = f" - Exception: {exc}" if exc else ""
    print(f"[{timestamp}] [ERROR] {message}{err_str}")

def log_audit(user_id: str, action: str, status: str):
    """Log audit security actions if audit logging is enabled."""
    if config.ENABLE_AUDIT_LOGS:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [AUDIT] User={user_id} Action={action} Status={status}")
