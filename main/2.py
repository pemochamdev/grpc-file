# payment/infrastructure/config.py
from dataclasses import dataclass
from enum import Enum

class Environment(Enum):
    TEST = "test"
    PRODUCTION = "production"

@dataclass
class PayPalConfig:
    client_id: str
    client_secret: str
    environment: Environment

@dataclass
class DatabaseConfig:
    url: str
    pool_size: int
    max_overflow: int

# payment/domain/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID

@dataclass
class Merchant:
    id: UUID
    business_name: str
    email: str
    api_key: str
    api_secret: str
    environment: str
    status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class PaymentTransaction:
    id: UUID
    merchant_id: UUID
    amount: float
    currency: str
    status: str
    payment_method: str
    payment_provider_ref: Optional[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, str]

# payment/domain/interfaces.py
from abc import ABC, abstractmethod
from typing import Optional
from .models import Merchant, PaymentTransaction

class PaymentProvider(ABC):
    @abstractmethod
    async def process_payment(self, transaction: PaymentTransaction) -> dict:
        pass
    
    @abstractmethod
    async def refund_payment(self, transaction: PaymentTransaction, amount: float) -> dict:
        pass

class MerchantRepository(ABC):
    @abstractmethod
    async def save(self, merchant: Merchant) -> Merchant:
        pass
    
    @abstractmethod
    async def find_by_api_key(self, api_key: str) -> Optional[Merchant]:
        pass

class TransactionRepository(ABC):
    @abstractmethod
    async def save(self, transaction: PaymentTransaction) -> PaymentTransaction:
        pass
    
    @abstractmethod
    async def find_by_id(self, transaction_id: UUID) -> Optional[PaymentTransaction]:
        pass

# payment/infrastructure/paypal_provider.py
import paypalrestsdk
from typing import Dict
from ..domain.interfaces import PaymentProvider
from ..domain.models import PaymentTransaction

class PayPalProvider(PaymentProvider):
    def __init__(self, config: Dict):
        self.api = paypalrestsdk.Api({
            'mode': config['environment'],
            'client_id': config['client_id'],
            'client_secret': config['client_secret']
        })

    async def process_payment(self, transaction: PaymentTransaction) -> dict:
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "transactions": [{
                "amount": {
                    "total": str(transaction.amount),
                    "currency": transaction.currency
                }
            }]
        })

        if payment.create():
            return {
                "status": "PENDING",
                "provider_ref": payment.id,
                "redirect_url": payment.links[1].href
            }
        else:
            raise Exception(payment.error)

    async def refund_payment(self, transaction: PaymentTransaction, amount: float) -> dict:
        sale = paypalrestsdk.Sale.find(transaction.payment_provider_ref)
        refund = sale.refund({
            "amount": {
                "total": str(amount),
                "currency": transaction.currency
            }
        })
        
        if refund.success():
            return {
                "status": "COMPLETED",
                "provider_ref": refund.id
            }
        else:
            raise Exception(refund.error)

# payment/application/services.py
from typing import Optional
import uuid
from datetime import datetime
from ..domain.models import Merchant, PaymentTransaction
from ..domain.interfaces import PaymentProvider, MerchantRepository, TransactionRepository

class PaymentService:
    def __init__(
        self,
        payment_provider: PaymentProvider,
        merchant_repo: MerchantRepository,
        transaction_repo: TransactionRepository
    ):
        self.payment_provider = payment_provider
        self.merchant_repo = merchant_repo
        self.transaction_repo = transaction_repo

    async def process_payment(self, payment_request) -> PaymentTransaction:
        # Validate merchant
        merchant = await self.merchant_repo.find_by_api_key(payment_request.api_key)
        if not merchant:
            raise Exception("Invalid merchant credentials")

        # Create transaction
        transaction = PaymentTransaction(
            id=uuid.uuid4(),
            merchant_id=merchant.id,
            amount=payment_request.amount.amount,
            currency=payment_request.amount.currency,
            status="PENDING",
            payment_method=payment_request.payment_method,
            payment_provider_ref=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata=payment_request.metadata
        )

        # Process payment with provider
        try:
            payment_result = await self.payment_provider.process_payment(transaction)
            transaction.status = payment_result["status"]
            transaction.payment_provider_ref = payment_result["provider_ref"]
        except Exception as e:
            transaction.status = "FAILED"
            raise e
        finally:
            await self.transaction_repo.save(transaction)

        return transaction

# payment/infrastructure/grpc_server.py
from concurrent import futures
import grpc
from typing import Dict
import payment_pb2
import payment_pb2_grpc
from ..application.services import PaymentService

class PaymentServicer(payment_pb2_grpc.PaymentServiceServicer):
    def __init__(self, payment_service: PaymentService):
        self.payment_service = payment_service

    async def ProcessPayment(
        self,
        request: payment_pb2.PaymentRequest,
        context: grpc.aio.ServicerContext
    ) -> payment_pb2.PaymentResponse:
        try:
            transaction = await self.payment_service.process_payment(request)
            
            return payment_pb2.PaymentResponse(
                transaction_id=str(transaction.id),
                status=transaction.status,
                amount=payment_pb2.PaymentAmount(
                    amount=transaction.amount,
                    currency=transaction.currency
                ),
                processed_at=transaction.created_at.timestamp(),
                payment_method_details=transaction.payment_method
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return payment_pb2.PaymentResponse()

# main.py
import asyncio
import grpc
from payment.infrastructure.config import PayPalConfig, DatabaseConfig, Environment
from payment.infrastructure.paypal_provider import PayPalProvider
from payment.infrastructure.grpc_server import PaymentServicer
from payment.application.services import PaymentService

async def serve():
    # Configuration
    paypal_config = PayPalConfig(
        client_id="your_client_id",
        client_secret="your_client_secret",
        environment=Environment.TEST
    )
    
    db_config = DatabaseConfig(
        url="postgresql://user:pass@localhost/dbname",
        pool_size=5,
        max_overflow=10
    )

    # Initialize dependencies
    payment_provider = PayPalProvider(paypal_config)
    merchant_repo = PostgresMerchantRepository(db_config)  # À implémenter
    transaction_repo = PostgresTransactionRepository(db_config)  # À implémenter
    
    payment_service = PaymentService(
        payment_provider=payment_provider,
        merchant_repo=merchant_repo,
        transaction_repo=transaction_repo
    )

    # Create gRPC server
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    payment_pb2_grpc.add_PaymentServiceServicer_to_server(
        PaymentServicer(payment_service), server
    )
    
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())