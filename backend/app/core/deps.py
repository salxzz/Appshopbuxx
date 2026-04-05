import jwt
from fastapi import Header, HTTPException, Depends
from app.core.config import settings
from app.db.mongo import users_col
from bson import ObjectId

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autorização inválido ou ausente")

    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Payload do token inválido")
        
        # Buscar no banco para ter info atualizado (Nome, Avatar, Role)
        user = users_col.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
            
        user["id"] = str(user.pop("_id"))
        return user 
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

def get_admin(user = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito para administradores")
    return user

def get_seller(user = Depends(get_current_user)):
    if user.get("role") not in ["seller", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso restrito para vendedores")
    return user