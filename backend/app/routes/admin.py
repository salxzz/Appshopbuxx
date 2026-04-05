from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import SellerCreate, UserResponse
from app.db.mongo import users_col
from app.core.security import hash_password
from app.core.deps import get_admin
from bson import ObjectId
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin", tags=["Admin"])

class PromoteSellerRequest(BaseModel):
    discord_id: str

@router.post("/sellers/promote", response_model=UserResponse)
def promote_seller_by_discord(data: PromoteSellerRequest, admin = Depends(get_admin)):
    # Buscar usuário pelo Discord ID
    user = users_col.find_one({"discord_id": data.discord_id})
    
    if not user:
        # Se não existe, criar um placeholder que será preenchido no primeiro login via Discord
        new_user = {
            "name": f"Pendente (Discord ID: {data.discord_id})",
            "discord_id": data.discord_id,
            "role": "seller",
            "mercadopago_token_encrypted": None
        }
        result = users_col.insert_one(new_user)
        return {
            "id": str(result.inserted_id),
            "name": new_user["name"],
            "email": "pendente@discord.com",
            "role": "seller"
        }

    # Se já existe, atualizar role para seller
    users_col.update_one(
        {"discord_id": data.discord_id},
        {"$set": {"role": "seller"}}
    )
    
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user.get("email") or "discord_user@email.com",
        "role": "seller"
    }

@router.post("/sellers", response_model=UserResponse)
def create_seller(seller_data: SellerCreate, admin = Depends(get_admin)):
    # Validar email único
    if users_col.find_one({"email": seller_data.email}):
        raise HTTPException(status_code=400, detail="Este e-mail já está cadastrado")

    new_user = {
        "name": seller_data.name,
        "email": seller_data.email,
        "hashed_password": hash_password(seller_data.password),
        "role": "seller",
        "mercadopago_token_encrypted": None
    }
    
    result = users_col.insert_one(new_user)
    
    return {
        "id": str(result.inserted_id),
        "name": new_user["name"],
        "email": new_user["email"],
        "role": new_user["role"]
    }
