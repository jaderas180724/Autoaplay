from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.account import AccountCheck
from workers.netflix_checker import NetflixChecker
import json

router = APIRouter()

class CheckRequest(BaseModel):
    service: str
    combos: List[str]  # Formato: "email:password"

class CheckResponse(BaseModel):
    check_id: int
    status: str
    results: List[dict]

@router.post("/check", response_model=CheckResponse)
async def create_check(
    request: CheckRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar créditos
    cost_per_check = 0.1  # $0.10 por check
    total_cost = len(request.combos) * cost_per_check
    
    if current_user.credits < total_cost:
        raise HTTPException(status_code=402, detail="Créditos insuficientes")
        
    # Descontar créditos
    current_user.credits -= total_cost
    db.commit()
    
    results = []
    
    # Procesar checks
    for combo in request.combos:
        try:
            email, password = combo.strip().split(":", 1)
            
            # Crear registro de check
            check_record = AccountCheck(
                user_id=current_user.id,
                service=request.service,
                email=email,
                password=password,  # En producción: cifrar
                status="checking"
            )
            db.add(check_record)
            db.commit()
            
            # Realizar check async
            if request.service == "netflix":
                async with NetflixChecker() as checker:
                    result = await checker.check(email, password)
                    
                check_record.status = result["status"]
                check_record.capture = result.get("capture")
                check_record.checked_at = func.now()
                db.commit()
                
                results.append({
                    "id": check_record.id,
                    "email": email,
                    "status": result["status"],
                    "capture": result.get("capture")
                })
                
        except Exception as e:
            results.append({
                "combo": combo,
                "status": "error",
                "error": str(e)
            })
            
    return {
        "check_id": check_record.id if 'check_record' in locals() else 0,
        "status": "completed",
        "results": results
    }

@router.get("/history")
async def get_check_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    checks = db.query(AccountCheck).filter(
        AccountCheck.user_id == current_user.id
    ).order_by(
        AccountCheck.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return checks