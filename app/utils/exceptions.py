class PaymentError(Exception):
    """Exception de base pour les erreurs liées au paiement."""
    def __init__(self, message: str = "An error occurred in the payment process"):
        super().__init__(message)

class InvalidPaymentProvider(PaymentError):
    """Exception levée lorsqu'un fournisseur de paiement invalide est utilisé."""
    def __init__(self, provider_name: str):
        message = f"The payment provider '{provider_name}' is invalid or not recognized."
        super().__init__(message)

class PaymentValidationError(PaymentError):
    """Exception levée lorsqu'une validation échoue pour un paiement."""
    def __init__(self, field: str, issue: str):
        message = f"Validation error on field '{field}': {issue}."
        super().__init__(message)

class PaymentGatewayError(PaymentError):
    """Exception levée lorsqu'une erreur se produit avec la passerelle de paiement."""
    def __init__(self, gateway_name: str, error_details: str = ""):
        message = f"Error occurred with the payment gateway '{gateway_name}'."
        if error_details:
            message += f" Details: {error_details}"
        super().__init__(message)

class PaymentConfigError(PaymentError):
    """Exception levée lorsqu'il y a un problème de configuration du système de paiement."""
    def __init__(self, missing_keys: list = None):
        if missing_keys:
            message = f"Payment configuration error. Missing keys: {', '.join(missing_keys)}"
        else:
            message = "Payment configuration error."
        super().__init__(message)

class InvalidProviderConfigError(PaymentError):
    """Exception levée lorsqu'une configuration fournisseur est invalide."""
    def __init__(self, provider_name: str, missing_keys: list):
        message = f"Invalid configuration for provider '{provider_name}'. Missing keys: {', '.join(missing_keys)}"
        super().__init__(message)

class ProviderNotSupportedError(PaymentError):
    """Exception levée lorsqu'un fournisseur n'est pas pris en charge."""
    def __init__(self, provider_name: str):
        message = f"The payment provider '{provider_name}' is not supported by the system."
        super().__init__(message)
