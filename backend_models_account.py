from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from core.database import Base

class AccountCheck(Base):
    __tablename__ = "account_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service = Column(String(50))  # netflix, spotify, etc.
    email = Column(String(255))
    password = Column(Text)  # Cifrado
    status = Column(String(20))  # valid, invalid, checking, error
    capture = Column(Text)  # Info adicional (plan, expiración)
    price_paid = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    checked_at = Column(DateTime(timezone=True))

class AccountStock(Base):
    __tablename__ = "account_stock"
    
    id = Column(Integer, primary_key=True, index=True)
    service = Column(String(50))
    email = Column(String(255))
    password = Column(Text)
    capture = Column(Text)
    price = Column(Float)
    sold = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())