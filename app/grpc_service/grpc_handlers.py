import grpc
from protos.payment_service_pb2 import (
    PaymentResponse,
    ValidationResponse,
    RefundResponse,
    TransactionStatusResponse,
    MerchantBalanceResponse,
    PaymentAmount
)
from protos.payment_service_pb2_grpc import PaymentServiceServicer
from app.providers.paypal_provider import PayPalPaymentProvider
from app.utils.exceptions import PaymentError, InvalidProviderConfigError

class PaymentServiceHandler(PaymentServiceServicer):
    """Implémentation gRPC pour le service de paiement."""
    
    def __init__(self, config):
        self.provider = PayPalPaymentProvider(
            client_id=config["PAYPAL_CLIENT_ID"],
            client_secret=config["PAYPAL_CLIENT_SECRET"],
            mode=config["PAYPAL_MODE"]
        )

    def ProcessPayment(self, request, context):
        """Traite un paiement."""
        try:
            result = self.provider.create_payment_intent(
                amount=Decimal(request.amount.amount),
                currency=request.amount.currency,
                payment_method_data={"return_url": request.return_url, "cancel_url": request.webhook_url},
                metadata={"description": request.metadata.get("description", "")}
            )
            return PaymentResponse(
                transaction_id=result.provider_transaction_id,
                status=result.status.value,
                error_message=result.error_message or "",
                amount=PaymentAmount(amount=str(result.amount_processed or 0), currency=request.amount.currency),
                receipt_url=result.payment_method_details.get("approval_url", "") if result.success else "",
            )
        except PaymentError as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return PaymentResponse()

    def ConfirmPayment(self, request, context):
        """Confirme un paiement après approbation."""
        try:
            result = self.provider.confirm_payment(
                payment_intent_id=request.transaction_id,
                payment_method_data={"payer_id": request.metadata.get("payer_id", "")}
            )
            return PaymentResponse(
                transaction_id=result.provider_transaction_id,
                status=result.status.value,
                error_message=result.error_message or "",
                amount=PaymentAmount(amount=str(result.amount_processed or 0), currency=request.amount.currency),
                receipt_url=result.payment_method_details.get("approval_url", "") if result.success else "",
            )
        except PaymentError as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return PaymentResponse()

    def RefundPayment(self, request, context):
        """Rembourse un paiement."""
        try:
            result = self.provider.refund_payment(
                transaction_id=request.transaction_id,
                amount=Decimal(request.amount.amount) if request.amount else None,
                reason=request.reason
            )
            return RefundResponse(
                refund_id=result.provider_transaction_id,
                status=result.status.value,
                amount=PaymentAmount(amount=str(result.amount_processed or 0), currency=request.amount.currency),
                error_message=result.error_message or "",
            )
        except PaymentError as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return RefundResponse()

    def GetTransactionStatus(self, request, context):
        """Récupère le statut d'une transaction."""
        try:
            result = self.provider.get_payment_status(request.transaction_id)
            return TransactionStatusResponse(
                transaction_id=result.provider_transaction_id,
                status=result.status.value,
                amount=PaymentAmount(amount=str(result.amount_processed or 0), currency=result.payment_method_details.get("currency", "")),
                created_at=result.created_at.isoformat(),
                updated_at=result.provider_response.get("update_time", ""),
            )
        except PaymentError as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return TransactionStatusResponse()
