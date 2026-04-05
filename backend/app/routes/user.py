from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.db.mongo import orders_col

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/me")
def me(user = Depends(get_current_user)):
    user.pop("hashed_password", None)
    user.pop("mercadopago_token_encrypted", None)
    return user

@router.get("/inventory")
def get_inventory(user = Depends(get_current_user)):
    # Retorna as ordens pagas deste usuário
    orders = []
    for o in orders_col.find({"user_id": user["id"], "status": "approved"}):
        o["id"] = str(o.pop("_id"))
        orders.append(o)
    return orders