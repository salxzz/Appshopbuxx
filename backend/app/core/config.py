import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MONGO_URI = os.getenv("DB_URL", "mongodb://localhost:27017")
    DB_NAME = "shopbuxx"
    JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
    
    # Fernet for MP Token
    MP_ENCRYPTION_KEY = os.getenv("MP_ENCRYPTION_KEY", "uO-8L-E6l_8h8JpY9v6c_X8XW9J-B2K5y8JpY9v6c_Y=") # Use a real one in .env

settings = Settings()
