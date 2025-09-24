

from django.core.exceptions import ValidationError
from PIL import Image


def validate_image_file(value):
    if not value:
        return
    valid_formats = ["JPEG", "JPG", "PNG"]
    max_size_mb = 5
    max_width = 4000
    max_height = 4000

    try:
        # Abre a imagem diretamente do arquivo
        img = Image.open(value)
        img.verify()  # verifica se é imagem válida
    except Exception:
        raise ValidationError("Arquivo inválido ou corrompido.")

    # Reabre para acessar propriedades
    value.seek(0)
    img = Image.open(value)

    # Verifica formato
    if img.format.upper() not in valid_formats:
        raise ValidationError("Formato inválido. Use JPG, JPEG, PNG.")

    # Verifica tamanho
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"O arquivo não pode ultrapassar {max_size_mb}MB.")

    # Verifica resolução
    width, height = img.size
    if width > max_width or height > max_height:
        raise ValidationError(
            f"A imagem não pode ultrapassar {max_width}x{max_height} pixels."
        )
    