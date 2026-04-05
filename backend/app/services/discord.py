from fastapi import Request, APIRouter
import httpx
import dotenv
import os

router = APIRouter()
dotenv.load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

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
            headers={"Content-Type": "application/x-www-form-urlencoded"},
         
        )

        token_json = token_res.json()
        access_token = token_json["access_token"]

        user_res = await client.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        user = user_res.json()

    return user