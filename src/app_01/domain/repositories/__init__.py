"""
Repository Pattern Implementation
Abstract data access layer with market-specific implementations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete
from datetime import datetime

from ..core.config import Market
from ..core.exceptions import create_database_error, ErrorCode

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository interface"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update entity"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """List entities with pagination"""
        pass

class UserRepository(BaseRepository):
    """User repository interface"""
    
    @abstractmethod
    async def get_by_phone(self, phone: str, market: Market) -> Optional[T]:
        """Get user by phone number and market"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str, market: Market) -> Optional[T]:
        """Get user by email and market"""
        pass
    
    @abstractmethod
    async def get_active_users(self, market: Market, skip: int = 0, limit: int = 100) -> List[T]:
        """Get active users for market"""
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: int, login_time: datetime) -> bool:
        """Update user's last login time"""
        pass

class PhoneVerificationRepository(BaseRepository):
    """Phone verification repository interface"""
    
    @abstractmethod
    async def get_active_verification(self, phone: str, market: Market) -> Optional[T]:
        """Get active verification for phone number"""
        pass
    
    @abstractmethod
    async def create_verification(self, phone: str, code: str, market: Market, user_id: Optional[int] = None) -> T:
        """Create new phone verification"""
        pass
    
    @abstractmethod
    async def mark_as_used(self, verification_id: int) -> bool:
        """Mark verification as used"""
        pass
    
    @abstractmethod
    async def cleanup_expired(self, market: Market) -> int:
        """Clean up expired verifications"""
        pass

class UserAddressRepository(BaseRepository):
    """User address repository interface"""
    
    @abstractmethod
    async def get_user_addresses(self, user_id: int, market: Market) -> List[T]:
        """Get all addresses for user"""
        pass
    
    @abstractmethod
    async def get_default_address(self, user_id: int, market: Market) -> Optional[T]:
        """Get user's default address"""
        pass
    
    @abstractmethod
    async def set_default_address(self, address_id: int, user_id: int) -> bool:
        """Set address as default"""
        pass

class UserPaymentMethodRepository(BaseRepository):
    """User payment method repository interface"""
    
    @abstractmethod
    async def get_user_payment_methods(self, user_id: int, market: Market) -> List[T]:
        """Get all payment methods for user"""
        pass
    
    @abstractmethod
    async def get_default_payment_method(self, user_id: int, market: Market) -> Optional[T]:
        """Get user's default payment method"""
        pass
    
    @abstractmethod
    async def set_default_payment_method(self, payment_method_id: int, user_id: int) -> bool:
        """Set payment method as default"""
        pass

class UserNotificationRepository(BaseRepository):
    """User notification repository interface"""
    
    @abstractmethod
    async def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[T]:
        """Get user notifications"""
        pass
    
    @abstractmethod
    async def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        pass
    
    @abstractmethod
    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark notification as read"""
        pass
    
    @abstractmethod
    async def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read"""
        pass

# Market-specific repository implementations
class MarketRepositoryFactory:
    """Factory for creating market-specific repositories"""
    
    @staticmethod
    def create_user_repository(session: AsyncSession, market: Market) -> UserRepository:
        """Create user repository for specific market"""
        if market == Market.KG:
            from .implementations.user_repository_kg import UserRepositoryKG
            return UserRepositoryKG(session)
        elif market == Market.US:
            from .implementations.user_repository_us import UserRepositoryUS
            return UserRepositoryUS(session)
        else:
            raise ValueError(f"Unsupported market: {market}")
    
    @staticmethod
    def create_phone_verification_repository(session: AsyncSession, market: Market) -> PhoneVerificationRepository:
        """Create phone verification repository for specific market"""
        if market == Market.KG:
            from .implementations.phone_verification_repository_kg import PhoneVerificationRepositoryKG
            return PhoneVerificationRepositoryKG(session)
        elif market == Market.US:
            from .implementations.phone_verification_repository_us import PhoneVerificationRepositoryUS
            return PhoneVerificationRepositoryUS(session)
        else:
            raise ValueError(f"Unsupported market: {market}")
    
    @staticmethod
    def create_user_address_repository(session: AsyncSession, market: Market) -> UserAddressRepository:
        """Create user address repository for specific market"""
        if market == Market.KG:
            from .implementations.user_address_repository_kg import UserAddressRepositoryKG
            return UserAddressRepositoryKG(session)
        elif market == Market.US:
            from .implementations.user_address_repository_us import UserAddressRepositoryUS
            return UserAddressRepositoryUS(session)
        else:
            raise ValueError(f"Unsupported market: {market}")
    
    @staticmethod
    def create_user_payment_method_repository(session: AsyncSession, market: Market) -> UserPaymentMethodRepository:
        """Create user payment method repository for specific market"""
        if market == Market.KG:
            from .implementations.user_payment_method_repository_kg import UserPaymentMethodRepositoryKG
            return UserPaymentMethodRepositoryKG(session)
        elif market == Market.US:
            from .implementations.user_payment_method_repository_us import UserPaymentMethodRepositoryUS
            return UserPaymentMethodRepositoryUS(session)
        else:
            raise ValueError(f"Unsupported market: {market}")
    
    @staticmethod
    def create_user_notification_repository(session: AsyncSession, market: Market) -> UserNotificationRepository:
        """Create user notification repository for specific market"""
        if market == Market.KG:
            from .implementations.user_notification_repository_kg import UserNotificationRepositoryKG
            return UserNotificationRepositoryKG(session)
        elif market == Market.US:
            from .implementations.user_notification_repository_us import UserNotificationRepositoryUS
            return UserNotificationRepositoryUS(session)
        else:
            raise ValueError(f"Unsupported market: {market}")

# Repository manager for dependency injection
class RepositoryManager:
    """Manages repository instances and database sessions"""
    
    def __init__(self, database_manager):
        self.database_manager = database_manager
        self._repositories = {}
    
    async def get_user_repository(self, market: Market) -> UserRepository:
        """Get user repository for market"""
        key = f"user_repo_{market.value}"
        if key not in self._repositories:
            session = await self.database_manager.get_session(market)
            self._repositories[key] = MarketRepositoryFactory.create_user_repository(session, market)
        return self._repositories[key]
    
    async def get_phone_verification_repository(self, market: Market) -> PhoneVerificationRepository:
        """Get phone verification repository for market"""
        key = f"phone_verification_repo_{market.value}"
        if key not in self._repositories:
            session = await self.database_manager.get_session(market)
            self._repositories[key] = MarketRepositoryFactory.create_phone_verification_repository(session, market)
        return self._repositories[key]
    
    async def get_user_address_repository(self, market: Market) -> UserAddressRepository:
        """Get user address repository for market"""
        key = f"user_address_repo_{market.value}"
        if key not in self._repositories:
            session = await self.database_manager.get_session(market)
            self._repositories[key] = MarketRepositoryFactory.create_user_address_repository(session, market)
        return self._repositories[key]
    
    async def get_user_payment_method_repository(self, market: Market) -> UserPaymentMethodRepository:
        """Get user payment method repository for market"""
        key = f"user_payment_method_repo_{market.value}"
        if key not in self._repositories:
            session = await self.database_manager.get_session(market)
            self._repositories[key] = MarketRepositoryFactory.create_user_payment_method_repository(session, market)
        return self._repositories[key]
    
    async def get_user_notification_repository(self, market: Market) -> UserNotificationRepository:
        """Get user notification repository for market"""
        key = f"user_notification_repo_{market.value}"
        if key not in self._repositories:
            session = await self.database_manager.get_session(market)
            self._repositories[key] = MarketRepositoryFactory.create_user_notification_repository(session, market)
        return self._repositories[key]
    
    async def cleanup(self):
        """Clean up repository instances"""
        for repo in self._repositories.values():
            if hasattr(repo, 'session') and repo.session:
                await repo.session.close()
        self._repositories.clear()
