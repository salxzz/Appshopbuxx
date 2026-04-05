from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, user, items, buy, admin, seller

from app.db.mongo import users_col
from app.core.security import hash_password

app = FastAPI(title="Shopbuxx API", version="2.0.0")

@app.on_event("startup")
def startup_db_init():
    # Email único p/ usuários
    users_col.create_index("email", unique=True)
    
    # Garantir que o ID específico do usuário seja Admin
    TARGET_ADMIN_ID = "1149804841162518540"
    users_col.update_one(
        {"discord_id": TARGET_ADMIN_ID},
        {"$set": {"role": "admin"}},
        upsert=False
    )
    print(f"👑 Privilégios de Admin garantidos para o Discord ID: {TARGET_ADMIN_ID}")
    
    print("🟢 MongoDB Inicializado (Indices e Admin)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Shopbuxx Backend Up and Running"}

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Erro interno do servidor: {str(exc)}"},
    )

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(items.router) # Prefixos já estão nos arquivos
app.include_router(buy.router)
app.include_router(admin.router)
app.include_router(seller.router)

print("🟢 Shopbuxx Server 2.0 Funcionando")