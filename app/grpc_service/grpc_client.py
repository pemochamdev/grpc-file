import grpc
from protos.payment_service_pb2 import PaymentRequest, PaymentAmount
from protos.payment_service_pb2_grpc import PaymentServiceStub

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../protos'))))


def test_process_payment():
    channel = grpc.insecure_channel('localhost:50051')
    stub = PaymentServiceStub(channel)
    request = PaymentRequest(
        merchant_id="merchant_id_example",
        amount=PaymentAmount(amount="100.00", currency="USD"),
        return_url="http://localhost/return",
        webhook_url="http://localhost/cancel",
        metadata={"description": "Test payment"}
    )
    response = stub.ProcessPayment(request)
    print(response)

if __name__ == '__main__':
    test_process_payment()
