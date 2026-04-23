import hashlib
import jwt
import os
from datetime import datetime, timedelta

SECRET = os.environ.get("JWT_SECRET", "sttg-super-secret-key-2025")
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed

def create_token(user_id: int, role: str, name: str, admin_id: int = None, department_id: int = None) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "name": name,
        "admin_id": admin_id if admin_id else user_id,  # admins are their own admin_id
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    if department_id is not None:
        payload["department_id"] = department_id
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
