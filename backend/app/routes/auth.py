from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
import httpx
import os
import urllib.parse
from app.core.security import create_access_token, verify_password
from app.db.mongo import users_col
from pydantic import BaseModel, EmailStr

from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# 🔗 LOGIN DISCORD (Para Clientes)
@router.get("/login")
def login_discord():
    encoded_redirect = urllib.parse.quote(REDIRECT_URI)
    url = (
        "https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={encoded_redirect}"
        "&response_type=code"
        "&scope=identify%20email"
    )
    return RedirectResponse(url)

@router.get("/callback")
async def callback(code: str):
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://discord.com/api/oauth2/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token_data = token_res.json()
        access_token = token_data.get("access_token")

        user_res = await client.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        discord_user = user_res.json()

        # Sicronizar com MongoDB (Priorizando Discord ID)
        user = users_col.find_one({"discord_id": discord_user["id"]})
        
        if not user:
            # Tentar por email caso ele já tenha sido criado via Admin/Email
            user = users_col.find_one({"email": discord_user.get("email")})

        if not user:
            new_user = {
                "name": discord_user["username"],
                "email": discord_user.get("email"),
                "role": "user",
                "discord_id": discord_user["id"],
                "avatar": discord_user.get("avatar")
            }
            res = users_col.insert_one(new_user)
            user_id = str(res.inserted_id)
            role = "user"
        else:
            # Atualizar dados do Discord (Nome, avatar) mas MANTER a role (ex: seller)
            users_col.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "discord_id": discord_user["id"],
                    "name": discord_user["username"],
                    "email": discord_user.get("email"),
                    "avatar": discord_user.get("avatar")
                }}
            )
            user_id = str(user["_id"])
            role = user["role"]

        token = create_access_token({"id": user_id, "username": discord_user["username"], "role": role})

    return RedirectResponse(f"http://localhost:5500/src/homepage.html?token={token}")

# 🔑 LOGIN PASSWORD (Para Admin e Sellers)
@router.post("/login/password")
def login_password(data: LoginRequest):
    user = users_col.find_one({"email": data.email})
    if not user or not verify_password(data.password, user.get("hashed_password", "")):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    
    token = create_access_token({
        "id": str(user["_id"]), 
        "username": user["name"], 
        "role": user["role"]
    })
    
    return {"token": token, "role": user["role"]}