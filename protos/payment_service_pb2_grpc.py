# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import payment_service_pb2 as payment__service__pb2

GRPC_GENERATED_VERSION = '1.68.1'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in payment_service_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class PaymentServiceStub(object):
    """*
    Service principal pour la gestion des paiements.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RegisterMerchant = channel.unary_unary(
                '/payment.v1.PaymentService/RegisterMerchant',
                request_serializer=payment__service__pb2.MerchantRegistration.SerializeToString,
                response_deserializer=payment__service__pb2.MerchantCredentials.FromString,
                _registered_method=True)
        self.ProcessPayment = channel.unary_unary(
                '/payment.v1.PaymentService/ProcessPayment',
                request_serializer=payment__service__pb2.PaymentRequest.SerializeToString,
                response_deserializer=payment__service__pb2.PaymentResponse.FromString,
                _registered_method=True)
        self.ValidateCredentials = channel.unary_unary(
                '/payment.v1.PaymentService/ValidateCredentials',
                request_serializer=payment__service__pb2.CredentialsValidation.SerializeToString,
                response_deserializer=payment__service__pb2.ValidationResponse.FromString,
                _registered_method=True)
        self.GetTransactionStatus = channel.unary_unary(
                '/payment.v1.PaymentService/GetTransactionStatus',
                request_serializer=payment__service__pb2.TransactionStatusRequest.SerializeToString,
                response_deserializer=payment__service__pb2.TransactionStatusResponse.FromString,
                _registered_method=True)
        self.RefundPayment = channel.unary_unary(
                '/payment.v1.PaymentService/RefundPayment',
                request_serializer=payment__service__pb2.RefundRequest.SerializeToString,
                response_deserializer=payment__service__pb2.RefundResponse.FromString,
                _registered_method=True)
        self.GetMerchantBalance = channel.unary_unary(
                '/payment.v1.PaymentService/GetMerchantBalance',
                request_serializer=payment__service__pb2.MerchantBalanceRequest.SerializeToString,
                response_deserializer=payment__service__pb2.MerchantBalanceResponse.FromString,
                _registered_method=True)
        self.UpdateMerchantProfile = channel.unary_unary(
                '/payment.v1.PaymentService/UpdateMerchantProfile',
                request_serializer=payment__service__pb2.UpdateMerchantRequest.SerializeToString,
                response_deserializer=payment__service__pb2.MerchantProfile.FromString,
                _registered_method=True)
        self.ListTransactions = channel.unary_unary(
                '/payment.v1.PaymentService/ListTransactions',
                request_serializer=payment__service__pb2.ListTransactionsRequest.SerializeToString,
                response_deserializer=payment__service__pb2.ListTransactionsResponse.FromString,
                _registered_method=True)


class PaymentServiceServicer(object):
    """*
    Service principal pour la gestion des paiements.
    """

    def RegisterMerchant(self, request, context):
        """*
        Inscrit un nouveau marchand dans le système.
        @param MerchantRegistration : Informations nécessaires pour l'inscription d'un marchand.
        @return MerchantCredentials : Identifiants générés pour le marchand.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ProcessPayment(self, request, context):
        """*
        Traite un paiement pour un marchand.
        @param PaymentRequest : Détails du paiement.
        @return PaymentResponse : Statut et détails du paiement traité.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ValidateCredentials(self, request, context):
        """*
        Valide les identifiants d'un marchand.
        @param CredentialsValidation : Identifiants fournis par le marchand.
        @return ValidationResponse : Résultat de la validation et permissions associées.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTransactionStatus(self, request, context):
        """*
        Récupère le statut d'une transaction donnée.
        @param TransactionStatusRequest : Identifiant de la transaction et marchand associé.
        @return TransactionStatusResponse : Détails du statut de la transaction.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RefundPayment(self, request, context):
        """*
        Rembourse une transaction.
        @param RefundRequest : Détails du remboursement (montant, raison, etc.).
        @return RefundResponse : Statut et informations sur le remboursement.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMerchantBalance(self, request, context):
        """*
        Récupère le solde d'un marchand dans une devise donnée.
        @param MerchantBalanceRequest : Identifiant du marchand et devise.
        @return MerchantBalanceResponse : Soldes disponibles et en attente.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateMerchantProfile(self, request, context):
        """*
        Met à jour les informations du profil d'un marchand.
        @param UpdateMerchantRequest : Informations mises à jour du marchand.
        @return MerchantProfile : Profil mis à jour du marchand.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListTransactions(self, request, context):
        """*
        Liste les transactions d'un marchand avec des filtres optionnels.
        @param ListTransactionsRequest : Filtres tels que dates, statut, taille de page.
        @return ListTransactionsResponse : Liste des transactions et pagination.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_PaymentServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RegisterMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.RegisterMerchant,
                    request_deserializer=payment__service__pb2.MerchantRegistration.FromString,
                    response_serializer=payment__service__pb2.MerchantCredentials.SerializeToString,
            ),
            'ProcessPayment': grpc.unary_unary_rpc_method_handler(
                    servicer.ProcessPayment,
                    request_deserializer=payment__service__pb2.PaymentRequest.FromString,
                    response_serializer=payment__service__pb2.PaymentResponse.SerializeToString,
            ),
            'ValidateCredentials': grpc.unary_unary_rpc_method_handler(
                    servicer.ValidateCredentials,
                    request_deserializer=payment__service__pb2.CredentialsValidation.FromString,
                    response_serializer=payment__service__pb2.ValidationResponse.SerializeToString,
            ),
            'GetTransactionStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTransactionStatus,
                    request_deserializer=payment__service__pb2.TransactionStatusRequest.FromString,
                    response_serializer=payment__service__pb2.TransactionStatusResponse.SerializeToString,
            ),
            'RefundPayment': grpc.unary_unary_rpc_method_handler(
                    servicer.RefundPayment,
                    request_deserializer=payment__service__pb2.RefundRequest.FromString,
                    response_serializer=payment__service__pb2.RefundResponse.SerializeToString,
            ),
            'GetMerchantBalance': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMerchantBalance,
                    request_deserializer=payment__service__pb2.MerchantBalanceRequest.FromString,
                    response_serializer=payment__service__pb2.MerchantBalanceResponse.SerializeToString,
            ),
            'UpdateMerchantProfile': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateMerchantProfile,
                    request_deserializer=payment__service__pb2.UpdateMerchantRequest.FromString,
                    response_serializer=payment__service__pb2.MerchantProfile.SerializeToString,
            ),
            'ListTransactions': grpc.unary_unary_rpc_method_handler(
                    servicer.ListTransactions,
                    request_deserializer=payment__service__pb2.ListTransactionsRequest.FromString,
                    response_serializer=payment__service__pb2.ListTransactionsResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'payment.v1.PaymentService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('payment.v1.PaymentService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class PaymentService(object):
    """*
    Service principal pour la gestion des paiements.
    """

    @staticmethod
    def RegisterMerchant(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/payment.v1.PaymentService/RegisterMerchant',
            payment__service__pb2.MerchantRegistration.SerializeToString,
            payment__service__pb2.MerchantCredentials.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ProcessPayment(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/payment.v1.PaymentService/ProcessPayment',
            payment__service__pb2.PaymentRequest.SerializeToString,
            payment__service__pb2.PaymentResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ValidateCredentials(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/payment.v1.PaymentService/ValidateCredentials',
            payment__service__pb2.CredentialsValidation.SerializeToString,
            payment__service__pb2.ValidationResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetTransactionStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/payment.v1.PaymentService/GetTransactionStatus',
            payment__service__pb2.TransactionStatusRequest.SerializeToString,
            payment__service__pb2.TransactionStatusResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def RefundPayment(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/payment.v1.PaymentService/RefundPayment',
            payment__service__pb2.RefundRequest.SerializeToString,
            payment__service__pb2.RefundResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetMerchantBalance(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/payment.v1.PaymentService/GetMerchantBalance',
            payment__service__pb2.MerchantBalanceRequest.SerializeToString,
            payment__service__pb2.MerchantBalanceResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UpdateMerchantProfile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/payment.v1.PaymentService/UpdateMerchantProfile',
            payment__service__pb2.UpdateMerchantRequest.SerializeToString,
            payment__service__pb2.MerchantProfile.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ListTransactions(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/payment.v1.PaymentService/ListTransactions',
            payment__service__pb2.ListTransactionsRequest.SerializeToString,
            payment__service__pb2.ListTransactionsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
