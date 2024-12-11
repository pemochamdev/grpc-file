import paypalrestsdk
from typing import Dict, Optional
from decimal import Decimal
import logging
from providers.base_provider import PaymentProvider,PaymentResult,PaymentStatus


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
        