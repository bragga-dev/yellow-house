
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import logging
from django.utils.text import slugify
from vitrine.services.frenet import calcular_frete
from brazilcep import get_address_from_cep, WebService
from brazilcep.exceptions import BrazilCEPException
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP



logger = logging.getLogger(__name__)
# Ensure default media files are present in storage
def ensure_default_media():
    base_path = os.path.join(os.path.dirname(__file__), "default_media")

    for filename in os.listdir(base_path):
        local_path = os.path.join(base_path, filename)
        key = f"default/{filename}"
        logger.info(f"Uploading {key}")

        if not default_storage.exists(key):
            with open(local_path, "rb") as f:
                default_storage.save(key, ContentFile(f.read()))



# Slug generation utility
def generate_unique_slug(instance, *args):
    field_value = "-".join(str(arg) for arg in args if arg)
    base_slug = slugify(field_value)
    
    unique_slug = base_slug
    num = 1
    Klass = instance.__class__
    
    while Klass.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{base_slug}-{num}"
        num += 1

    return unique_slug



# Calculate fretes 
def calcular_frete_item(origem_cep, destino_cep, package, valor_unitario, quantidade=1):
    """
    Calcula o frete de um item levando em conta a quantidade e validação de dados.
    Retorna apenas os fretes válidos (sem erros).
    """

    # 1️⃣ Validação de entrada
    if not origem_cep or not destino_cep or not package:
        return {"error": "CEP de origem, destino ou pacote ausente."}

    try:
        quantidade = int(quantidade)
        if quantidade < 1:
            raise ValueError
    except ValueError:
        return {"error": "Quantidade inválida."}

    try:
        valor_unitario = float(valor_unitario)
    except (TypeError, ValueError):
        return {"error": "Valor unitário inválido."}

    # 2️⃣ Cálculo total considerando quantidade
    peso_total = round(package.package_weight * quantidade, 3)
    valor_total = round(valor_unitario * quantidade, 2)

    # 3️⃣ Chamada à função de cálculo principal
    resultado = calcular_frete(
        origem_cep=origem_cep,
        destino_cep=destino_cep,
        peso=peso_total,
        altura=package.package_height,
        largura=package.package_width,
        comprimento=package.package_length,
        valor=valor_total,
        quantidade=quantidade
    )

    # 4️⃣ Tratamento de erros na resposta
    if not resultado or "error" in resultado:
        return {"error": resultado.get("error", "Erro desconhecido ao calcular o frete.")}

    servicos = resultado.get("ShippingSevicesArray", [])

    # 5️⃣ Filtrar apenas fretes válidos (sem erro)
    fretes_validos = [
        s for s in servicos
        if not s.get("Error") and s.get("ShippingPrice") and float(s.get("ShippingPrice", 0)) > 0
    ]

    # 6️⃣ Normalização de saída
    for s in fretes_validos:
        s["ShippingPrice"] = Decimal(str(s["ShippingPrice"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        s["DeliveryTime"] = int(s.get("DeliveryTime", 0))

    return {"fretes": fretes_validos}



# Validação de cep

def validar_cep(value):
    cep = value.replace('-', '').strip()
    if len(cep) != 8 or not cep.isdigit():
        raise ValidationError('CEP inválido: formato incorreto.')

    try:
        get_address_from_cep(cep, webservice=WebService.VIACEP)
    except BrazilCEPException:
        raise ValidationError('CEP inválido ou não encontrado.')
