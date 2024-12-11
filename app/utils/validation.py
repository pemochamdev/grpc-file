from decimal import Decimal
import re

def validate_currency(currency: str) -> bool:
  return bool(re.match(r"^[A-Z]{3}$",currency))

def validate_amount(amount: str) -> bool:
  return amount > Decimal('0') and amount <= Decimal("999999.99")

def calcule_commission(amount: Decimal, rate: Decimal) -> Decimal:
  return (amount * rate / Decimal("100")).quantize(Decimal("0.01"))

