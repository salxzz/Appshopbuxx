from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class SellerCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str

class ProductBase(BaseModel):
    name: str
    description: str
    image_url: Optional[str] = None
    price: float

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[float] = None

class ProductResponse(ProductBase):
    id: str
    stock: List[str] = []  # Lista de contas/chaves (Sempre [] para o público)
    stock_count: int = 0
    seller_id: str
    created_at: datetime
    updated_at: datetime

class StockUpdate(BaseModel):
    accounts: List[str]  # Novas contas para adicionar
    mode: str = "add"    # "add" ou "replace"

class MPConfig(BaseModel):
    access_token: str
