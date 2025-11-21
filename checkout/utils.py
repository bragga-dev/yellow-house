
import uuid
from django.core.exceptions import ValidationError




def  generate_order_code():
    return uuid.uuid4().hex[:10].upper()


def value_greater_than_zero(value):
    if value <= 0:
        raise ValidationError("O valor deve ser maior que zero.")