from concurrent import futures
import grpc
from protos.payment_service_pb2_grpc import add_PaymentServiceServicer_to_server
from app.grpc_service.grpc_handlers import PaymentServiceHandler
from app.config import Config

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_PaymentServiceServicer_to_server(PaymentServiceHandler(Config.PAYPAL_CONFIG), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC server is running on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
