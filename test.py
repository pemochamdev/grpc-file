import os
import sys

# Chemin absolu du fichier et des modules
print("Current file:", __file__)
print("Absolute path:", os.path.abspath(os.path.join(os.path.dirname(__file__), '../../protos')))
print("Python path:", sys.path)

# Vérifiez si les modules sont bien trouvés
try:
    from protos.payment_service_pb2_grpc import PaymentServiceStub
    from protos.payment_service_pb2 import google_dot_protobuf_dot_empty__pb2
    print("Modules imported successfully.")
except ModuleNotFoundError as e:
    print("Error importing modules:", e)
