from app.services.payment import create_pix_payment
from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_current_user
from app.db.mongo import products_col, users_col
from app.core.security import decrypt_token
from bson import ObjectId

router = APIRouter(prefix="/buy", tags=["Purchase"])

@router.post("/{item_id}")
def buy_item(item_id: str, user = Depends(get_current_user)):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="ID de produto inválido")

    # 1. Buscar produto
    item = products_col.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if item.get("stock", 0) <= 0:
        raise HTTPException(status_code=400, detail="Este item está sem estoque")

    # 2. Buscar vendedor para pegar o token do Mercado Pago
    seller = users_col.find_one({"_id": item["seller_id"]})
    if not seller:
        raise HTTPException(status_code=404, detail="Vendedor não encontrado")

    # 3. Descriptografar token se existir
    encrypted_token = seller.get("mercadopago_token_encrypted")
    mp_token = None
    if encrypted_token:
        try:
            mp_token = decrypt_token(encrypted_token)
        except Exception:
            # Se falhar a descriptografia, pode ser erro de chave
            pass

    # 4. Criar pagamento PIX
    payment = create_pix_payment(item["name"], item["price"], mp_token)

    if "point_of_interaction" not in payment:
        return {
            "error": "Ocorreu um erro ao processar o pagamento com o Mercado Pago",
            "detail": payment.get("message") or str(payment)
        }

    return {
        "item_name": item["name"],
        "price": item["price"],
        "pix_qr": payment["point_of_interaction"]["transaction_data"]["qr_code"],
        "pix_code_base64": payment["point_of_interaction"]["transaction_data"]["qr_code_base64"]
    }