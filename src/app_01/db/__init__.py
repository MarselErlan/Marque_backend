"""
Database configuration and base classes
"""

from .market_db import (
    Base,
    Market,
    MarketConfig,
    db_manager,
    get_base,
    get_db,
    detect_market_from_phone,
    format_phone_for_market,
    get_market_config
)

__all__ = [
    'Base',
    'Market', 
    'MarketConfig',
    'db_manager',
    'get_base',
    'get_db',
    'detect_market_from_phone',
    'format_phone_for_market',
    'get_market_config'
]
