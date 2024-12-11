from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Float, Boolean, Enum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class Environment(enum.Enum):
    """Environnements possibles pour les marchands."""
    TEST = "test"
    PRODUCTION = "production"

class PaymentStatus(enum.Enum):
    """Statuts possibles pour une transaction."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(enum.Enum):
    """Méthodes de paiement disponibles."""
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CREDIT_CARD = "credit_card"

class Document(Base):
    """Documents KYC associés aux marchands."""
    __tablename__ = 'documents'
    
    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey('merchants.id'))
    type = Column(String(50))  # Types possibles : ID, PASSPORT, BUSINESS_LICENSE
    file_url = Column(String(500))  # URL du fichier du document.
    status = Column(String(50))  # Statut du document (ex. validé, en attente).
    created_at = Column(DateTime, default=datetime.utcnow)
    
    merchant = relationship("Merchant", back_populates="documents")

class Merchant(Base):
    """Table représentant les marchands inscrits."""
    __tablename__ = 'merchants'
    
    id = Column(String(36), primary_key=True)
    business_name = Column(String(255), nullable=False)  # Nom commercial.
    email = Column(String(255), nullable=False, unique=True)  # Email unique.
    website = Column(String(255))  # Site web de l'entreprise.
    business_type = Column(String(100))  # Type d'entreprise.
    tax_id = Column(String(100))  # Numéro fiscal.
    status = Column(String(50), default="pending")  # Statut du marchand.
    phone_number = Column(String(50))  # Numéro de téléphone.
    legal_entity_type = Column(String(100))  # Type d'entité légale.
    registration_number = Column(String(100))  # Numéro d'enregistrement.
    representative_name = Column(String(255))  # Nom du représentant légal.
    representative_id_number = Column(String(100))  # ID du représentant.
    
    # Adresse
    street_line1 = Column(String(255))  # Ligne 1 de l'adresse.
    street_line2 = Column(String(255))  # Ligne 2 de l'adresse.
    city = Column(String(100))  # Ville.
    state = Column(String(100))  # Région/État.
    postal_code = Column(String(20))  # Code postal.
    country = Column(String(100))  # Pays.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relations
    credentials = relationship("MerchantCredential", back_populates="merchant")
    transactions = relationship("Transaction", back_populates="merchant")
    documents = relationship("Document", back_populates="merchant")
    balances = relationship("MerchantBalance", back_populates="merchant")

class MerchantBalance(Base):
    """Table des soldes par devise pour chaque marchand."""
    __tablename__ = 'merchant_balances'
    
    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey('merchants.id'))
    currency = Column(String(3))  # Devise (ex. USD, EUR).
    available = Column(Float, default=0.0)  # Solde disponible.
    pending = Column(Float, default=0.0)  # Solde en attente.
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    merchant = relationship("Merchant", back_populates="balances")

class Transaction(Base):
    """Table des transactions effectuées par les marchands."""
    __tablename__ = 'transactions'
    
    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey('merchants.id'))
    payment_method = Column(Enum(PaymentMethod))  # Méthode de paiement.
    amount = Column(Float, nullable=False)  # Montant de la transaction.
    currency = Column(String(3), nullable=False)  # Devise.
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)  # Statut.
    provider_transaction_id = Column(String(255))  # ID du fournisseur de paiement.
    order_id = Column(String(255))  # ID de la commande associée.
    
    # Informations client enrichies
    customer_id = Column(String(255))  # ID unique du client.
    customer_email = Column(String(255))  # Email du client.
    customer_phone = Column(String(50))  # Téléphone du client.
    customer_name = Column(String(255))  # Nom complet du client.
    
    # Informations de facturation
    billing_address = Column(JSON)  # Adresse de facturation au format JSON.
    card_holder_name = Column(String(255))  # Nom du titulaire de la carte.
    
    receipt_url = Column(String(500))  # URL du reçu.
    return_url = Column(String(500))  # URL de redirection après paiement.
    webhook_url = Column(String(500))  # URL pour les notifications.
    idempotency_key = Column(String(255))  # Clé pour garantir l'idempotence.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    merchant = relationship("Merchant", back_populates="transactions")
    refunds = relationship("Refund", back_populates="transaction")

class MerchantCredential(Base):
    """Identifiants d'authentification des marchands."""
    __tablename__ = 'merchant_credentials'
    
    id = Column(String(36), primary_key=True)
    merchant_id = Column(String(36), ForeignKey('merchants.id'))
    api_key = Column(String(255), unique=True)  # Clé API.
    api_secret = Column(String(255))  # Secret API.
    environment = Column(Enum(Environment))  # Environnement (test/production).
    is_active = Column(Boolean, default=True)  # Statut actif ou inactif.
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Date d'expiration.
    
    merchant = relationship("Merchant", back_populates="credentials")

class Refund(Base):
    """Table des remboursements liés aux transactions."""
    __tablename__ = 'refunds'
    
    id = Column(String(36), primary_key=True)
    transaction_id = Column(String(36), ForeignKey('transactions.id'))
    amount = Column(Float, nullable=False)  # Montant remboursé.
    reason = Column(String(500))  # Raison du remboursement.
    status = Column(String(50))  # Statut du remboursement (ex. validé, en attente).
    provider_refund_id = Column(String(255))  # ID du remboursement chez le fournisseur.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    transaction = relationship("Transaction", back_populates="refunds")
