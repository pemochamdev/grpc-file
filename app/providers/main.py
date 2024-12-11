from decimal import Decimal
from typing import Dict, Optional
import logging
from providers.paypal_provider import PayPalPaymentProvider
from .base_provider import PaymentResult
from utils.exceptions import ProviderNotSupportedError, InvalidProviderConfigError

class PaymentService:
    PROVIDERS = {
        "paypal": PayPalPaymentProvider
    }

    def __init__(self, provider_name: str, config: Dict[str, str]):
        self.provider = self._get_provider(provider_name, config)
        self.logger = logging.getLogger(__name__)

    def _get_provider(self, provider_name: str, config: Dict[str, str]):
        provider_class = self.PROVIDERS.get(provider_name)
        if not provider_class:
            raise ProviderNotSupportedError(f"Provider '{provider_name}' is not supported")
        # Validation des configurations
        required_keys = getattr(provider_class, "REQUIRED_CONFIG_KEYS", [])
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise InvalidProviderConfigError(f"Missing required config keys: {', '.join(missing_keys)}")
        return provider_class(**config)

    def create_payment_intent(self, amount: Decimal, currency: str, payment_method_data: Dict, metadata: Optional[Dict] = None) -> PaymentResult:
        self.logger.info(f"Creating payment intent with amount: {amount}, currency: {currency}")
        try:
            result = self.provider.create_payment_intent(amount, currency, payment_method_data, metadata)
            self.logger.info(f"Payment intent created successfully: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error creating payment intent: {e}")
            raise

    def confirm_payment(self, payment_intent_id: str, payment_method_data: Optional[Dict] = None) -> PaymentResult:
        self.logger.info(f"Confirming payment with intent ID: {payment_intent_id}")
        return self.provider.confirm_payment(payment_intent_id, payment_method_data)

    def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None, reason: Optional[str] = None) -> PaymentResult:
        self.logger.info(f"Refunding payment for transaction ID: {transaction_id}, amount: {amount}, reason: {reason}")
        return self.provider.refund_payment(transaction_id, amount, reason)

    def get_payment_status(self, transaction_id: str) -> PaymentResult:
        self.logger.info(f"Fetching payment status for transaction ID: {transaction_id}")
        return self.provider.get_payment_status(transaction_id)
