import requests
from decouple import config
from django.conf import settings

FRENET_API_URL = getattr(settings, "FRENET_API_URL", "https://api.frenet.com.br")
TOKEN_FRENET = config("FRENET_API_KEY")

def calcular_frete(origem_cep, destino_cep, peso, altura, largura, comprimento, valor, quantidade=1):
    headers = {
        "token": TOKEN_FRENET,
        "Content-Type": "application/json"
    }

    payload = {
        "SellerCEP": str(origem_cep),
        "RecipientCEP": str(destino_cep),
        "ShipmentInvoiceValue": float(valor),
        "ShippingItemArray": [
            {
                "Weight": float(peso),
                "Length": float(comprimento),
                "Height": float(altura),
                "Width": float(largura),
                "Quantity": int(quantidade)
            }
        ]
    }

    try:
        response = requests.post(f"{FRENET_API_URL.rstrip('/')}/shipping/quote", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e), "response": getattr(e.response, 'text', None)}
