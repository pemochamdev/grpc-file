Je vais enrichir votre API gRPC pour le système de paiement avec des fonctionnalités supplémentaires et des bonnes pratiques.



```protobuf
syntax = "proto3";

package payment.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

// Service principal de paiement
service PaymentService {
    // Inscription d'un nouveau marchand
    rpc RegisterMerchant (MerchantRegistration) returns (MerchantCredentials);
    
    // Traitement d'un paiement
    rpc ProcessPayment (PaymentRequest) returns (PaymentResponse);
    
    // Validation des credentials
    rpc ValidateCredentials (CredentialsValidation) returns (ValidationResponse);
    
    // Nouvelles méthodes ajoutées
    rpc GetTransactionStatus (TransactionStatusRequest) returns (TransactionStatusResponse);
    rpc RefundPayment (RefundRequest) returns (RefundResponse);
    rpc GetMerchantBalance (MerchantBalanceRequest) returns (MerchantBalanceResponse);
    rpc UpdateMerchantProfile (UpdateMerchantRequest) returns (MerchantProfile);
    rpc ListTransactions (ListTransactionsRequest) returns (ListTransactionsResponse);
}

message MerchantRegistration {
    string business_name = 1;
    string email = 2;
    string website = 3;
    string business_type = 4;
    string tax_id = 5;
    Address business_address = 6;
    string phone_number = 7;
    repeated string accepted_payment_methods = 8;
    KYCInformation kyc_info = 9;
}

message Address {
    string street_line1 = 1;
    string street_line2 = 2;
    string city = 3;
    string state = 4;
    string postal_code = 5;
    string country = 6;
}

message KYCInformation {
    string legal_entity_type = 1;
    string registration_number = 2;
    repeated Document verification_documents = 3;
    string representative_name = 4;
    string representative_id_number = 5;
}

message Document {
    string type = 1;  // "ID", "PASSPORT", "BUSINESS_LICENSE"
    string file_url = 2;
    string status = 3;
}

message MerchantCredentials {
    string merchant_id = 1;
    string api_key = 2;
    string api_secret = 3;
    string environment = 4;  // "test" ou "production"
    google.protobuf.Timestamp created_at = 5;
    google.protobuf.Timestamp expires_at = 6;
    repeated string permissions = 7;
}

message PaymentRequest {
    string merchant_id = 1;
    string api_key = 2;
    string payment_method = 3;
    PaymentAmount amount = 4;
    string order_id = 5;
    map<string, string> metadata = 6;
    CustomerInfo customer = 7;
    BillingInfo billing = 8;
    string return_url = 9;
    string webhook_url = 10;
    string idempotency_key = 11;
}

message PaymentAmount {
    double amount = 1;
    string currency = 2;
}

message CustomerInfo {
    string customer_id = 1;
    string email = 2;
    string phone = 3;
    string name = 4;
}

message BillingInfo {
    Address billing_address = 1;
    string card_holder_name = 2;
}

message PaymentResponse {
    string transaction_id = 1;
    string status = 2;  // "PENDING", "COMPLETED", "FAILED", "CANCELLED"
    string error_code = 3;
    string error_message = 4;
    PaymentAmount amount = 5;
    google.protobuf.Timestamp processed_at = 6;
    string payment_method_details = 7;
    string receipt_url = 8;
}

message TransactionStatusRequest {
    string merchant_id = 1;
    string transaction_id = 2;
}

message TransactionStatusResponse {
    string transaction_id = 1;
    string status = 2;
    PaymentAmount amount = 3;
    google.protobuf.Timestamp created_at = 4;
    google.protobuf.Timestamp updated_at = 5;
}

message RefundRequest {
    string merchant_id = 1;
    string transaction_id = 2;
    PaymentAmount amount = 3;
    string reason = 4;
}

message RefundResponse {
    string refund_id = 1;
    string status = 2;
    PaymentAmount amount = 3;
    google.protobuf.Timestamp processed_at = 4;
}

message MerchantBalanceRequest {
    string merchant_id = 1;
    string currency = 2;
}

message MerchantBalanceResponse {
    repeated Balance balances = 1;
    google.protobuf.Timestamp as_of = 2;
}

message Balance {
    string currency = 1;
    double available = 2;
    double pending = 3;
}

message UpdateMerchantRequest {
    string merchant_id = 1;
    MerchantProfile profile = 2;
}

message MerchantProfile {
    string business_name = 1;
    string email = 2;
    string website = 3;
    Address business_address = 4;
    string phone_number = 5;
    repeated string accepted_payment_methods = 6;
    map<string, string> settings = 7;
}

message ListTransactionsRequest {
    string merchant_id = 1;
    google.protobuf.Timestamp start_date = 2;
    google.protobuf.Timestamp end_date = 3;
    string status = 4;
    int32 page_size = 5;
    string page_token = 6;
}

message ListTransactionsResponse {
    repeated Transaction transactions = 1;
    string next_page_token = 2;
    int32 total_count = 3;
}

message Transaction {
    string transaction_id = 1;
    string status = 2;
    PaymentAmount amount = 3;
    string payment_method = 4;
    google.protobuf.Timestamp created_at = 5;
    CustomerInfo customer = 6;
    map<string, string> metadata = 7;
}

message CredentialsValidation {
    string merchant_id = 1;
    string api_key = 2;
}

message ValidationResponse {
    bool is_valid = 1;
    repeated string permissions = 2;
    google.protobuf.Timestamp expires_at = 3;
}

```

Voici les principales améliorations apportées :

1. Structure et Organisation :
   - Ajout du versioning dans le package (`payment.v1`)
   - Import des types Google Protobuf pour la gestion des timestamps
   - Organisation logique des messages par fonctionnalité

2. Nouvelles Fonctionnalités :
   - Gestion des remboursements (RefundPayment)
   - Consultation du solde marchand (GetMerchantBalance)
   - Mise à jour du profil marchand (UpdateMerchantProfile)
   - Liste des transactions avec pagination (ListTransactions)
   - Suivi du statut des transactions (GetTransactionStatus)

3. Sécurité et Validation :
   - Ajout d'informations KYC pour l'enregistrement
   - Gestion des permissions dans le1s credentials
   - Validation renforcée des credentials
   - Clé d'idempotence pour éviter les doubles paiements

4. Gestion des Paiements :
   - Structure détaillée pour les montants (PaymentAmount)
   - Informations client enrichies (CustomerInfo)
   - Gestion des webhooks et URLs de retour
   - Support des métadonnées flexibles

5. Gestion des Erreurs :
   - Codes d'erreur standardisés
   - Messages d'erreur détaillés
   - Statuts de transaction explicites

Voulez-vous que je détaille certains aspects spécifiques ou que j'ajoute d'autres fonctionnalités ?