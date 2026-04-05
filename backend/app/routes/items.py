from fastapi import APIRouter, Depends, HTTPException
from app.db.mongo import products_col
from app.core.deps import get_current_user
from app.models.schemas import ProductResponse
from bson import ObjectId

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/")
def get_items():
    # Retorna produtos públicos que tenham estoque
    products = []
    for p in products_col.find():
        p["id"] = str(p.pop("_id"))
        p["seller_id"] = str(p["seller_id"])
        
        # Lidar com estoque v1 (int) ou v2 (list)
        stock_data = p.get("stock", [])
        p["stock_count"] = len(stock_data) if isinstance(stock_data, list) else int(stock_data)
        
        products.append(p)
    return products

@router.get("/{item_id}", response_model=ProductResponse)
def get_item(item_id: str):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="ID de item inválido")

    item = products_col.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    item["id"] = str(item.pop("_id"))
    item["seller_id"] = str(item["seller_id"])
    
    stock_data = item.get("stock", [])
    item["stock_count"] = len(stock_data) if isinstance(stock_data, list) else int(stock_data)
    
    return item