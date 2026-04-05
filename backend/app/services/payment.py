import mercadopago
import os
from dotenv import load_dotenv

load_dotenv()

def create_pix_payment(name, price, mp_access_token=None):
    # Se não houver token, tenta o global ou mocka
    token = mp_access_token or os.getenv("MP_ACCESS_TOKEN", "dummy_mp_token")

    if token == "dummy_mp_token":
        # Mock payment for testing
        return {
            "point_of_interaction": {
                "transaction_data": {
                    "qr_code": "00020101021226830014br.gov.bcb.pix0161mock-pix-copy-paste-for-testing-1234567890",
                    "qr_code_base64": "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEAAQMAAABmvDolAAAABlBMVEUAAAD///+l2Z/dSAAAAC5JREFUeNpjYBgFo2AUjIJRMApGwSgYBaNgFIyCUfBfC0TCKAiEYBSMglEwCvAAABmQACX/eK9/AAAAAElFTkSuQmCC"
                }
            }
        }

    sdk = mercadopago.SDK(token)

    payment_data = {
        "transaction_amount": float(price),
        "description": name,
        "payment_method_id": "pix",
        "payer": {
            "email": "comprador@email.com"
        }
    }

    try:
        payment_res = sdk.payment().create(payment_data)
        return payment_res["response"]
    except Exception as e:
        return {"error": f"Erro na API do Mercado Pago: {str(e)}"}