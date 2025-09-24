from fastapi import Depends, HTTPException, Header
from typing import Optional
from sqlalchemy.orm import Session
from ..db.market_db import db_manager, Market, detect_market_from_phone

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
