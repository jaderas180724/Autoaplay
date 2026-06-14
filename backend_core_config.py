from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Checker Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "tu-secret-key-super-segura-cambiar-en-produccion"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    DATABASE_URL: str = "postgresql://user:pass@db:5432/checker_db"
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Configuración de pagos
    BTC_WALLET: str = "tu-direccion-bitcoin"
    XMR_WALLET: str = "tu-direccion-monero"
    WEBHOOK_SECRET: str = "webhook-secret"
    
    # Configuración de proxies
    PROXY_LIST: List[str] = []
    PROXY_ROTATION: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()