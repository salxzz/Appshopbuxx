import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.core.config import settings

# Password Hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Fernet Encryption
try:
    fernet = Fernet(settings.MP_ENCRYPTION_KEY.encode())
except Exception:
    # Generate one if invalid for now, but should be in .env
    key = Fernet.generate_key()
    fernet = Fernet(key)
    print(f"⚠️ Warning: Invalid MP_ENCRYPTION_KEY. Use this for testing: {key.decode()}")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    return fernet.decrypt(encrypted_token.encode()).decode()