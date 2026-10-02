import os

class AppConfig:
    """Application configuration settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-12345")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_MINUTES = 60
    
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_NAME = "enterprise_db"
    
    PAYMENT_GATEWAY_URL = "https://api.stripe-mock.internal/v1/charge"
    PAYMENT_TIMEOUT_SECONDS = 5
    MAX_PAYMENT_RETRIES = 3
    
    ENABLE_AUDIT_LOGS = True
    LOG_LEVEL = "INFO"

config = AppConfig()
