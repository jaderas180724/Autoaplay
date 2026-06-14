from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.database import get_db
from core.security import get_current_user
from core.config import settings
from models.user import User
import hashlib
import time

router = APIRouter()

class PaymentRequest(BaseModel):
    amount: float
    currency: str  # BTC, XMR, USDT
    credits: int

class PaymentResponse(BaseModel):
    payment_id: str
    address: str
    amount: float
    currency: str
    status: str

@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    request: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Generar ID único de transacción
    payment_id = hashlib.sha256(
        f"{current_user.id}{time.time()}".encode()
    ).hexdigest()[:16]
    
    # Generar dirección de pago (en producción: llamar a wallet API)
    if request.currency == "BTC":
        address = settings.BTC_WALLET
    elif request.currency == "XMR":
        address = settings.XMR_WALLET
    else:
        address = "unsupported"
        
    # Guardar transacción pendiente en DB
    # ... código para guardar en tabla payments ...
    
    return PaymentResponse(
        payment_id=payment_id,
        address=address,
        amount=request.amount,
        currency=request.currency,
        status="pending"
    )

@router.post("/webhook/{currency}")
async def payment_webhook(
    currency: str,
    request: Request,
    db: Session = Depends(get_db)
):
    # Verificar firma del webhook
    payload = await request.body()
    signature = request.headers.get("X-Signature", "")
    
    # Validar firma con secret
    expected = hashlib.sha256(
        f"{payload.decode()}{settings.WEBHOOK_SECRET}".encode()
    ).hexdigest()
    
    if signature != expected:
        raise HTTPException(status_code=401, detail="Invalid signature")
        
    data = await request.json()
    
    # Procesar confirmación de pago
    # Buscar transacción por txid
    # Actualizar créditos del usuario
    # Marcar como pagado
    
    return {"status": "processed"}

@router.get("/rates")
async def get_exchange_rates():
    # Devolver tasas de cambio actualizadas
    # En producción: llamar a API de exchange
    return {
        "BTC_USD": 43000.00,
        "XMR_USD": 165.00,
        "USDT_USD": 1.00,
        "credit_price": 0.10  # 1 crédito = $0.10
    }