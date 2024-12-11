#base.py
from abc import abstractmethod,ABC
from typing import Dict,Any,Optional
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from transactions.exceptions import PaymentError,PaymentValidationError
from transactions.utils import validate_currency,validate_amount,calcule_commission

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


# main.py
from decimal import Decimal
from typing import Dict, Optional
from transactions.providers.paypal_provider import PayPalPaymentProvider
# from transactions.providers.flutterware_provider import FlutterwarePaymentProvider
from .base import PaymentResult, PaymentStatus

class PaymentService:
    PROVIDERS = {
        "stripe": StripePaymentProvider,
        "paypal": PayPalPaymentProvider,
        # "flutterwave": FlutterwarePaymentProvider
        
    }
    
    def __init__(self, provider_name: str, config: Dict[str, str]):
        self.provider = self._get_provider(provider_name, config)
    
    def _get_provider(self, provider_name: str, config: Dict[str, str]):
        provider_class = self.PROVIDERS.get(provider_name)
        if not provider_class:
            raise ValueError(f"Provider '{provider_name}' is not supported")
        return provider_class(**config)

    def create_payment_intent(self, amount: Decimal, currency: str, payment_method_data: Dict, metadata: Optional[Dict] = None) -> PaymentResult:
        return self.provider.create_payment_intent(amount, currency, payment_method_data, metadata)

    def confirm_payment(self, payment_intent_id: str, payment_method_data: Optional[Dict] = None) -> PaymentResult:
        return self.provider.confirm_payment(payment_intent_id, payment_method_data)

    def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None, reason: Optional[str] = None) -> PaymentResult:
        return self.provider.refund_payment(transaction_id, amount, reason)

    def get_payment_status(self, transaction_id: str) -> PaymentResult:
        return self.provider.get_payment_status(transaction_id)


# paypal_provider.py

import paypalrestsdk
from django.conf import settings
from typing import Dict, Any, Optional
from decimal import Decimal
import logging
from transactions.providers.base import PaymentProvider,PaymentResult,PaymentStatus


logger = logging.getLogger(__name__)

class PayPalPaymentProvider(PaymentProvider):
    """Implémentation du provider de paiement PayPal"""
    
    def __init__(self, client_id: str, client_secret: str, mode: str = 'sandbox'):
        self.api = paypalrestsdk.Api({
            'mode': mode,
            'client_id': client_id,
            'client_secret': client_secret
        })
    
    def _handle_paypal_error(self, error: Exception) -> PaymentResult:
        """Gère les erreurs PayPal de manière standardisée"""
        logger.error(f"PayPal error: {str(error)}", exc_info=True,
                    extra={'error_type': type(error).__name__})
        
        return PaymentResult(
            success=False,
            provider_transaction_id=None,
            status=PaymentStatus.FAILED,
            error_message=str(error)
        )
    
    def create_payment_intent(self,
                            amount: Decimal,
                            currency: str,
                            payment_method_data: Dict,
                            metadata: Optional[Dict] = None) -> PaymentResult:
        """Crée un paiement PayPal"""
        try:
            payment_data = {
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [{
                    "amount": {
                        "total": str(amount),
                        "currency": currency.upper()
                    },
                    "description": metadata.get('description') if metadata else None
                }],
                "redirect_urls": {
                    "return_url": payment_method_data.get('return_url'),
                    "cancel_url": payment_method_data.get('cancel_url')
                }
            }
            
            # Créer le paiement
            payment = paypalrestsdk.Payment(payment_data, api=self.api)
            
            if payment.create():
                # Trouver l'URL de redirection
                approval_url = next(
                    link.href for link in payment.links
                    if link.rel == "approval_url"
                )
                
                return PaymentResult(
                    success=True,
                    provider_transaction_id=payment.id,
                    status=PaymentStatus.PENDING,
                    payment_method_details={'approval_url': approval_url},
                    provider_response=payment
                )
            else:
                return PaymentResult(
                    success=False,
                    provider_transaction_id=None,
                    status=PaymentStatus.FAILED,
                    error_message=str(payment.error)
                )
                
        except Exception as e:
            return self._handle_paypal_error(e)
    
    def confirm_payment(self,
                       payment_intent_id: str,
                       payment_method_data: Optional[Dict] = None) -> PaymentResult:
        """Exécute un paiement PayPal après approbation"""
        try:
            payment = paypalrestsdk.Payment.find(payment_intent_id, api=self.api)
            
            if payment_method_data and 'payer_id' in payment_method_data:
                if payment.execute({'payer_id': payment_method_data['payer_id']}):
                    # Calculer les frais
                    transaction = payment.transactions[0]
                    fee_amount = Decimal('0')
                    if hasattr(transaction, 'related_resources'):
                        for resource in transaction.related_resources:
                            if hasattr(resource, 'sale') and hasattr(resource.sale, 'transaction_fee'):
                                fee_amount = Decimal(resource.sale.transaction_fee.value)
                    
                    return PaymentResult(
                        success=True,
                        provider_transaction_id=payment.id,
                        status=PaymentStatus.COMPLETED,
                        payment_method_details={'payer_id': payment_method_data['payer_id']},
                        provider_response=payment,
                        amount_processed=Decimal(transaction.amount.total),
                        fee_amount=fee_amount
                    )
                else:
                    return PaymentResult(
                        success=False,
                        provider_transaction_id=payment.id,
                        status=PaymentStatus.FAILED,
                        error_message=str(payment.error)
                    )
            
            return PaymentResult(
                success=False,
                provider_transaction_id=payment.id,
                status=PaymentStatus.FAILED,
                error_message="Missing payer_id"
            )
            
        except Exception as e:
            return self._handle_paypal_error(e)
    
    def refund_payment(self,
                      transaction_id: str,
                      amount: Optional[Decimal] = None,
                      reason: Optional[str] = None) -> PaymentResult:
        """Effectue un remboursement PayPal"""
        try:
            payment = paypalrestsdk.Payment.find(transaction_id, api=self.api)
            sale = payment.transactions[0].related_resources[0].sale
            
            refund_data = {}
            if amount:
                refund_data['amount'] = {
                    'total': str(amount),
                    'currency': sale.amount.currency
                }
            
            if reason:
                refund_data['description'] = reason
            
            refund = sale.refund(refund_data)
            
            if refund.success():
                return PaymentResult(
                    success=True,
                    provider_transaction_id=refund.id,
                    status=PaymentStatus.REFUNDED,
                    amount_processed=Decimal(refund.amount.total),
                    provider_response=refund
                )
            else:
                return PaymentResult(
                    success=False,
                    provider_transaction_id=None,
                    status=PaymentStatus.FAILED,
                    error_message=str(refund.error)
                )
                
        except Exception as e:
            return self._handle_paypal_error(e)

# models.py
Base = declarative_base()

class Environment(enum.Enum):
    TEST = "test"
    PRODUCTION = "production"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(enum.Enum):
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CREDIT_CARD = "credit_card"

# Nouvelle table pour les documents KYC
class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey('merchants.id'))
    type = Column(String(50))  # ID, PASSPORT, BUSINESS_LICENSE
    file_url = Column(String(500))
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    merchant = relationship("Merchant", back_populates="documents")

class Merchant(Base):
    __tablename__ = 'merchants'
    
    id = Column(String(36), primary_key=True)
    business_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    website = Column(String(255))
    business_type = Column(String(100))
    tax_id = Column(String(100))
    status = Column(String(50), default="pending")
    phone_number = Column(String(50))
    legal_entity_type = Column(String(100))
    registration_number = Column(String(100))
    representative_name = Column(String(255))
    representative_id_number = Column(String(100))
    
    # Adresse
    street_line1 = Column(String(255))
    street_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relations
    credentials = relationship("MerchantCredential", back_populates="merchant")
    transactions = relationship("Transaction", back_populates="merchant")
    documents = relationship("Document", back_populates="merchant")
    balances = relationship("MerchantBalance", back_populates="merchant")

class MerchantBalance(Base):
    __tablename__ = 'merchant_balances'
    
    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey('merchants.id'))
    currency = Column(String(3))
    available = Column(Float, default=0.0)
    pending = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    merchant = relationship("Merchant", back_populates="balances")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey('merchants.id'))
    payment_method = Column(Enum(PaymentMethod))
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    provider_transaction_id = Column(String(255))
    order_id = Column(String(255))
    
    # Information client enrichie
    customer_id = Column(String(255))
    customer_email = Column(String(255))
    customer_phone = Column(String(50))
    customer_name = Column(String(255))
    
    # Information de facturation
    billing_address = Column(JSON)
    card_holder_name = Column(String(255))
    
    receipt_url = Column(String(500))
    return_url = Column(String(500))
    webhook_url = Column(String(500))
    idempotency_key = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    merchant = relationship("Merchant", back_populates="transactions")
    refunds = relationship("Refund", back_populates="transaction")

class MerchantCredential(Base):
    __tablename__ = 'merchant_credentials'
    
    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey('merchants.id'))
    api_key = Column(String(255), unique=True)
    api_secret = Column(String(255))
    environment = Column(Enum(Environment))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    merchant = relationship("Merchant", back_populates="credentials")

class Refund(Base):
    __tablename__ = 'refunds'
    
    id = Column(String(36), primary_key=True)
    transaction_id = Column(String(36), ForeignKey('transactions.id'))
    amount = Column(Float, nullable=False)
    reason = Column(String(500))
    status = Column(String(50))
    provider_refund_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    transaction = relationship("Transaction", back_populates="refunds")


