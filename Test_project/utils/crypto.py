import hashlib
import hmac
import base64
import json
import time
from config.settings import config

def hash_password(password: str, salt: str = "tokenwise_salt") -> str:
    """Hashes a raw password using SHA256 with salt."""
    salted = (password + salt).encode("utf-8")
    return hashlib.sha256(salted).hexdigest()

def generate_jwt_token(payload: dict) -> str:
    """Generates a simple mock JWT token."""
    header = {"alg": config.JWT_ALGORITHM, "typ": "JWT"}
    payload_copy = payload.copy()
    payload_copy["exp"] = int(time.time()) + (config.JWT_EXPIRATION_MINUTES * 60)
    
    header_b64 = base64.b64encode(json.dumps(header).encode()).decode()
    payload_b64 = base64.b64encode(json.dumps(payload_copy).encode()).decode()
    
    signature_raw = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(config.SECRET_KEY.encode(), signature_raw, hashlib.sha256).hexdigest()
    
    return f"{header_b64}.{payload_b64}.{signature}"

def verify_jwt_token(token: str) -> dict | None:
    """Verifies a JWT token signature and expiration."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature = parts
        
        expected_sig = hmac.new(
            config.SECRET_KEY.encode(), 
            f"{header_b64}.{payload_b64}".encode(), 
            hashlib.sha256
        ).hexdigest()
        
        if signature != expected_sig:
            return None
            
        payload = json.loads(base64.b64decode(payload_b64).decode())
        if payload.get("exp", 0) < time.time():
            return None
            
        return payload
    except Exception:
        return None
