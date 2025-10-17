from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Index
from sqlalchemy.sql import func
from ....db import Base


class OrderAdminStats(Base):
    """Daily statistics for order management admins"""
    __tablename__ = "order_admin_stats"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    
    # Today's orders
    today_orders_count = Column(Integer, default=0)
    today_orders_pending = Column(Integer, default=0)
    today_orders_processing = Column(Integer, default=0)
    today_orders_shipped = Column(Integer, default=0)
    today_orders_delivered = Column(Integer, default=0)
    today_orders_cancelled = Column(Integer, default=0)
    
    # Financial data
    today_sales_total = Column(Float, default=0.0)
    today_sales_count = Column(Integer, default=0)
    
    # Performance metrics
    avg_order_value = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)  # Delivered/Total orders
    
    # Timestamps
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # INDEXES for performance
    __table_args__ = (
        Index('idx_order_stats_date', 'date'),
        Index('idx_order_stats_sales', 'today_sales_total'),
        Index('idx_order_stats_last_updated', 'last_updated'),
    )

    def __repr__(self):
        return f"<OrderAdminStats(date={self.date}, orders={self.today_orders_count}, sales={self.today_sales_total})>"

    @property
    def formatted_sales_total(self):
        """Get formatted sales total with currency"""
        return f"{self.today_sales_total} KGS"

    @property
    def orders_status_summary(self):
        """Get summary of orders by status"""
        return {
            "pending": self.today_orders_pending,
            "processing": self.today_orders_processing,
            "shipped": self.today_orders_shipped,
            "delivered": self.today_orders_delivered,
            "cancelled": self.today_orders_cancelled
        }

    @property
    def status_labels(self):
        """Get Russian labels for status summary"""
        return {
            "pending": "В обработке",
            "processing": "Обрабатывается", 
            "shipped": "Отправлен",
            "delivered": "Доставлен",
            "cancelled": "Отменен"
        }

    def update_statistics(self, orders_data):
        """Update statistics from orders data"""
        self.today_orders_count = len(orders_data)
        self.today_sales_total = sum(order.total_amount for order in orders_data if order.status.value == "delivered")
        self.today_sales_count = len([order for order in orders_data if order.status.value == "delivered"])
        
        # Count by status
        status_counts = {}
        for order in orders_data:
            status = order.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        self.today_orders_pending = status_counts.get("pending", 0)
        self.today_orders_processing = status_counts.get("processing", 0)
        self.today_orders_shipped = status_counts.get("shipped", 0)
        self.today_orders_delivered = status_counts.get("delivered", 0)
        self.today_orders_cancelled = status_counts.get("cancelled", 0)
        
        # Calculate metrics
        if self.today_sales_count > 0:
            self.avg_order_value = self.today_sales_total / self.today_sales_count
        
        if self.today_orders_count > 0:
            self.completion_rate = (self.today_orders_delivered / self.today_orders_count) * 100
    
    @classmethod
    def get_stats_by_date(cls, session, date):
        """Get statistics for a specific date"""
        return session.query(cls).filter(cls.date == date).first()
    
    @classmethod
    def get_stats_range(cls, session, start_date, end_date):
        """Get statistics for a date range"""
        return session.query(cls).filter(
            cls.date >= start_date,
            cls.date <= end_date
        ).order_by(cls.date.desc()).all()
    
    @classmethod
    def get_recent_stats(cls, session, days=7):
        """Get statistics for last N days"""
        from datetime import datetime, timedelta
        start_date = datetime.now().date() - timedelta(days=days)
        return session.query(cls).filter(
            cls.date >= start_date
        ).order_by(cls.date.desc()).all()
    
    @classmethod
    def get_best_sales_days(cls, session, limit=10):
        """Get days with highest sales"""
        return session.query(cls).order_by(
            cls.today_sales_total.desc()
        ).limit(limit).all()
