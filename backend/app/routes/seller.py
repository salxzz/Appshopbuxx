from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import ProductCreate, ProductUpdate, ProductResponse, StockUpdate, MPConfig
from app.db.mongo import products_col, users_col
from app.core.deps import get_seller
from app.core.security import encrypt_token
from bson import ObjectId
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/seller", tags=["Seller"])

@router.post("/products", response_model=ProductResponse)
def create_product(product_in: ProductCreate, user = Depends(get_seller)):
    new_product = product_in.model_dump()
    new_product.update({
        "seller_id": ObjectId(user["id"]),
        "stock": [], # Lista de contas
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    result = products_col.insert_one(new_product)
    new_product["id"] = str(result.inserted_id)
    new_product["seller_id"] = str(new_product["seller_id"])
    new_product["stock_count"] = 0
    new_product.pop("_id", None)
    return new_product

@router.get("/products", response_model=List[ProductResponse])
def get_my_products(user = Depends(get_seller)):
    # Admin vê tudo, seller só os seus
    query = {} if user["role"] == "admin" else {"seller_id": ObjectId(user["id"])}
    
    products = []
    for p in products_col.find(query):
        p["id"] = str(p.pop("_id"))
        p["seller_id"] = str(p["seller_id"])
        
        # Migração segura para estoque em lista
        stock_data = p.get("stock", [])
        p["stock_count"] = len(stock_data) if isinstance(stock_data, list) else int(stock_data)
        
        products.append(p)
    return products

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, product_in: ProductUpdate, user = Depends(get_seller)):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="ID de produto inválido")
    
    product = products_col.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Check permissão (Admin ou Dono)
    if str(product["seller_id"]) != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Você não tem permissão para editar este produto")

    update_data = {k: v for k, v in product_in.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    products_col.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_data}
    )
    
    updated_product = products_col.find_one({"_id": ObjectId(product_id)})
    updated_product["id"] = str(updated_product.pop("_id"))
    updated_product["seller_id"] = str(updated_product["seller_id"])
    return updated_product

@router.delete("/products/{product_id}")
def delete_product(product_id: str, user = Depends(get_seller)):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="ID de produto inválido")

    product = products_col.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if str(product["seller_id"]) != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Não autorizado")

    products_col.delete_one({"_id": ObjectId(product_id)})
    return {"message": "Produto deletado com sucesso"}

@router.patch("/products/{product_id}/stock")
def update_stock(product_id: str, stock_in: StockUpdate, user = Depends(get_seller)):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="ID de produto inválido")
        
    product = products_col.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Check permissão (Proprietário ou Admin)
    current_seller_id = str(product["seller_id"])
    if current_seller_id != user["id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Não autorizado")

    if stock_in.mode == "replace":
        new_stock = stock_in.accounts
    else: # add
        new_stock = product.get("stock", []) + stock_in.accounts

    products_col.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"stock": new_stock, "updated_at": datetime.utcnow()}}
    )
    return {"status": "ok", "count": len(new_stock)}

@router.post("/mercadopago/config")
def config_mp(config: MPConfig, user = Depends(get_seller)):
    if not config.access_token:
        raise HTTPException(status_code=400, detail="Token MP é obrigatório")
        
    encrypted = encrypt_token(config.access_token)
    
    users_col.update_one(
        {"_id": ObjectId(user["id"])},
        {"$set": {"mercadopago_token_encrypted": encrypted}}
    )
    return {"message": "Configuração do Mercado Pago salva com sucesso (Protegida)"}
