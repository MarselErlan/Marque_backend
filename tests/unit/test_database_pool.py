"""
Unit tests for database connection pool configuration (TDD)
Tests proper pool settings for production use
"""

import pytest
from sqlalchemy.pool import QueuePool, NullPool
from src.app_01.db.market_db import db_manager, Market


class TestDatabaseConnectionPool:
    """Test database connection pool configuration"""
    
    def test_engine_uses_queue_pool(self):
        """
        GIVEN: Database engine for KG market
        WHEN: Engine is created
        THEN: Should use QueuePool for connection management
        """
        engine = db_manager.get_engine(Market.KG)
        
        # Engine should use QueuePool (not NullPool or SingletonThreadPool)
        assert isinstance(engine.pool, QueuePool), \
            f"Expected QueuePool but got {type(engine.pool).__name__}"
    
    def test_pool_size_is_configured(self):
        """
        GIVEN: Database engine
        WHEN: Checking pool configuration
        THEN: Pool size should be set (not default 5)
        """
        engine = db_manager.get_engine(Market.KG)
        
        # Pool size should be configured for production
        # Recommended: 10 for production workloads
        assert engine.pool.size() >= 10, \
            f"Pool size should be at least 10 for production, got {engine.pool.size()}"
    
    def test_pool_max_overflow_is_configured(self):
        """
        GIVEN: Database engine
        WHEN: Checking pool configuration
        THEN: Max overflow should be set for burst capacity
        """
        engine = db_manager.get_engine(Market.KG)
        
        # Max overflow allows temporary extra connections
        # Recommended: 20 for handling traffic spikes
        assert engine.pool._max_overflow >= 20, \
            f"Max overflow should be at least 20, got {engine.pool._max_overflow}"
    
    def test_pool_pre_ping_is_enabled(self):
        """
        GIVEN: Database engine
        WHEN: Checking pool configuration
        THEN: Pool pre_ping should be enabled to handle stale connections
        """
        engine = db_manager.get_engine(Market.KG)
        
        # Pre-ping prevents "connection has been closed" errors
        assert engine.pool._pre_ping is True, \
            "Pre-ping should be enabled to test connections before use"
    
    def test_pool_recycle_is_configured(self):
        """
        GIVEN: Database engine
        WHEN: Checking pool configuration
        THEN: Pool recycle should be set to prevent stale connections
        """
        engine = db_manager.get_engine(Market.KG)
        
        # Recycle connections after this many seconds
        # Recommended: 3600 (1 hour) to prevent MySQL "gone away" errors
        assert engine.pool._recycle >= 3600, \
            f"Pool recycle should be at least 3600 seconds, got {engine.pool._recycle}"
    
    def test_pool_timeout_is_configured(self):
        """
        GIVEN: Database engine
        WHEN: Checking pool configuration
        THEN: Pool timeout should be reasonable (not too long)
        """
        engine = db_manager.get_engine(Market.KG)
        
        # Timeout for getting connection from pool
        # Recommended: 30 seconds (default is 30)
        timeout = engine.pool._timeout
        assert timeout >= 10 and timeout <= 60, \
            f"Pool timeout should be between 10-60 seconds, got {timeout}"
    
    def test_both_markets_have_pool_configured(self):
        """
        GIVEN: Multiple market databases
        WHEN: Checking all market engines
        THEN: All should have proper pool configuration
        """
        for market in Market:
            engine = db_manager.get_engine(market)
            
            # All markets should use QueuePool
            assert isinstance(engine.pool, QueuePool), \
                f"Market {market.value} should use QueuePool"
            
            # All should have minimum pool size
            assert engine.pool.size() >= 10, \
                f"Market {market.value} pool size should be at least 10"
    
    def test_pool_echo_pool_is_disabled_in_production(self):
        """
        GIVEN: Database engine
        WHEN: Checking pool configuration
        THEN: echo_pool should be disabled for performance
        """
        engine = db_manager.get_engine(Market.KG)
        
        # echo_pool logs all pool checkouts/checkins (verbose, for debugging only)
        # Should be False in production
        assert engine.pool._echo is False, \
            "echo_pool should be disabled in production for performance"


class TestPoolPerformance:
    """Test that pool configuration improves performance"""
    
    def test_pool_can_handle_concurrent_connections(self):
        """
        GIVEN: Database pool with configured size
        WHEN: Multiple sessions requested concurrently
        THEN: Should handle without blocking (up to pool size + overflow)
        """
        engine = db_manager.get_engine(Market.KG)
        
        # Pool should support at least 30 concurrent connections
        # (pool_size=10 + max_overflow=20)
        total_capacity = engine.pool.size() + engine.pool._max_overflow
        assert total_capacity >= 30, \
            f"Total pool capacity should be at least 30, got {total_capacity}"
    
    def test_pool_settings_are_production_ready(self):
        """
        GIVEN: Database engine configuration
        WHEN: Checking all pool settings
        THEN: Settings should match production best practices
        """
        engine = db_manager.get_engine(Market.KG)
        
        production_checklist = {
            "uses_queue_pool": isinstance(engine.pool, QueuePool),
            "pool_size_at_least_10": engine.pool.size() >= 10,
            "max_overflow_at_least_20": engine.pool._max_overflow >= 20,
            "pre_ping_enabled": engine.pool._pre_ping is True,
            "recycle_configured": engine.pool._recycle >= 3600,
            "echo_disabled": engine.pool._echo is False,
        }
        
        failed_checks = [k for k, v in production_checklist.items() if not v]
        
        assert len(failed_checks) == 0, \
            f"Production readiness checks failed: {', '.join(failed_checks)}"


class TestPoolResourceManagement:
    """Test proper resource management"""
    
    def test_sessions_are_returned_to_pool(self):
        """
        GIVEN: Database session from pool
        WHEN: Session is closed
        THEN: Connection should be returned to pool
        """
        engine = db_manager.get_engine(Market.KG)
        initial_checked_out = engine.pool.checkedout()
        
        # Create and close a session
        SessionLocal = db_manager.get_session_factory(Market.KG)
        session = SessionLocal()
        session.close()
        
        # Connection should be back in pool
        final_checked_out = engine.pool.checkedout()
        assert final_checked_out <= initial_checked_out, \
            "Connection should be returned to pool after session close"
    
    def test_pool_has_overflow_capacity(self):
        """
        GIVEN: Database pool configuration
        WHEN: Checking overflow settings
        THEN: Should allow temporary extra connections for traffic spikes
        """
        engine = db_manager.get_engine(Market.KG)
        
        # Max overflow should be at least 2x pool size
        min_overflow = engine.pool.size() * 2
        assert engine.pool._max_overflow >= min_overflow, \
            f"Max overflow should be at least {min_overflow} (2x pool size)"

