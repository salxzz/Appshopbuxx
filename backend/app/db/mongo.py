import pymongo
from app.core.config import settings

# Conexão MongoDB Síncrona (Pymongo)
client = pymongo.MongoClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

def get_db():
    return db

# Collections shorthands
users_col = db["users"]
products_col = db["products"]
orders_col = db["orders"]

def init_db():
    pass

# init_db()