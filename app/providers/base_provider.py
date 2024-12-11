from abc import abstractmethod,ABC
from typing import Dict,Optional
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from utils.exceptions import PaymentError,PaymentValidationError
from utils.validation import validate_currency,validate_amount

class PaymentStatus(Enum):
  PENDING = 'pending' # en attente
  PROCESSING="processing" # en cours de traitement
  COMPLETED="completed" # terminé
  FAILED = "failed" # échoué
  REFUNDED="refunded" # remboursé
  PARTIALLY_REFUNDED = 'partially_refunded' # partiellement remboursé
  CANCELLED = 'cancelled' #  annulé


@dataclass(frozen=True)
class PaymentResult:

  success:bool
  provider_transaction_id: Optional[str]
  status:PaymentStatus
  error_message:Optional[str]=None
  payment_method_details: Optional[Dict] = None
  provider_response: Optional[Dict] = None
  amount_processed: Optional[Decimal] = None
  fee_amount: Optional[Decimal] = None
  risk_score: Optional[int] = None
  created_at: datetime = datetime.now()

  def __post_init__(self):
     if self.amount_processed is not None and not validate_amount(self.amount_processed):
        raise PaymentError("Invalid Amount Processed")


class PaymentProvider(ABC):
    """Classe de base abstraite pour les providers de paiement"""


    def validate_payment_data(self, amount: Decimal, currency: str)->None:
      if not validate_amount(amount):
        raise PaymentValidationError("Invalid Payment amount")
      if not validate_currency(currency):
         raise PaymentValidationError("Invalid Currency code")
    
    @abstractmethod
    def create_payment_intent(self, 
                          amount: Decimal,
                          currency: str,
                          payment_method_data: Dict,
                          metadata: Optional[Dict] = None) -> PaymentResult:
      self.validate_payment_data(amount,currency)
    
    @abstractmethod
    def confirm_payment(self,
                      payment_intent_id: str,
                      payment_method_data: Optional[Dict] = None) -> PaymentResult:
        pass
    
    @abstractmethod
    def refund_payment(self,
                      transaction_id: str,
                      amount: Optional[Decimal] = None,
                      reason: Optional[str] = None) -> PaymentResult:
      if amount is not None:
         self.validate_payment_data(amount,"")
    
    @abstractmethod
    def get_payment_status(self, transaction_id: str) -> PaymentResult:
        pass