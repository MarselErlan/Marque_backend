from fastapi import Depends, HTTPException, Header
from typing import Optional
from sqlalchemy.orm import Session
from ..db.market_db import db_manager, Market
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..services.auth_service import auth_service

security = HTTPBearer(auto_error=False)

def get_market_from_header(x_market: Optional[str] = Header(None)) -> Market:
    if x_market:
        try:
            return Market(x_market.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid market header: {x_market}")
    # If no header, we can't determine the market.
    # In a real app, you might fall back to a default or require the header.
    # For now, we'll default to KG for dependency injection to work.
    return Market.KG

def get_db(market: Market = Depends(get_market_from_header)) -> Session:
    session_factory = db_manager.get_session_factory(market)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()

def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user from JWT token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authorization header", headers={"WWW-Authenticate": "Bearer"})
    
    try:
        token_response = auth_service.verify_access_token(credentials.credentials)
        return token_response
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}", headers={"WWW-Authenticate": "Bearer"})
