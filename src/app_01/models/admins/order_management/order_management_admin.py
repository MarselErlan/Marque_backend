from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ....db import Base


class OrderManagementAdmin(Base):
    """Order Management Admin specific model"""
    __tablename__ = "order_management_admins"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False, unique=True, index=True)
    
    # Order management specific settings
    can_export_orders = Column(Boolean, default=True)
    can_bulk_update_orders = Column(Boolean, default=True)
    can_cancel_orders = Column(Boolean, default=True)
    can_refund_orders = Column(Boolean, default=False)
    
    # Dashboard preferences
    dashboard_refresh_interval = Column(Integer, default=30)  # seconds
    show_order_notifications = Column(Boolean, default=True)
    show_low_stock_alerts = Column(Boolean, default=True)
    
    # Order processing settings
    auto_confirm_orders = Column(Boolean, default=False)
    require_manual_confirmation = Column(Boolean, default=True)
    default_order_status = Column(String(20), default="pending")
    
    # Notification settings
    notify_on_new_orders = Column(Boolean, default=True)
    notify_on_status_changes = Column(Boolean, default=True)
    notify_on_payment_issues = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    admin = relationship("Admin")
    
    # INDEXES for performance
    __table_args__ = (
        Index('idx_order_mgmt_admin_permissions', 'can_export_orders', 'can_bulk_update_orders', 'can_cancel_orders'),
        Index('idx_order_mgmt_admin_notifications', 'notify_on_new_orders', 'show_order_notifications'),
    )

    def __repr__(self):
        return f"<OrderManagementAdmin(id={self.id}, admin_id={self.admin_id})>"

    @property
    def can_manage_full_order_cycle(self):
        """Check if admin can manage complete order cycle"""
        return all([
            self.can_export_orders,
            self.can_bulk_update_orders,
            self.can_cancel_orders
        ])

    @property
    def notification_settings(self):
        """Get all notification settings"""
        return {
            "new_orders": self.notify_on_new_orders,
            "status_changes": self.notify_on_status_changes,
            "payment_issues": self.notify_on_payment_issues,
            "show_notifications": self.show_order_notifications,
            "show_stock_alerts": self.show_low_stock_alerts
        }

    def update_notification_setting(self, setting, value):
        """Update a specific notification setting"""
        if setting == "new_orders":
            self.notify_on_new_orders = value
        elif setting == "status_changes":
            self.notify_on_status_changes = value
        elif setting == "payment_issues":
            self.notify_on_payment_issues = value
        elif setting == "show_notifications":
            self.show_order_notifications = value
        elif setting == "show_stock_alerts":
            self.show_low_stock_alerts = value

    def enable_full_order_management(self):
        """Enable all order management capabilities"""
        self.can_export_orders = True
        self.can_bulk_update_orders = True
        self.can_cancel_orders = True
        self.can_refund_orders = True

    def enable_basic_order_management(self):
        """Enable basic order management capabilities"""
        self.can_export_orders = True
        self.can_bulk_update_orders = False
        self.can_cancel_orders = True
        self.can_refund_orders = False

    def setup_dashboard_preferences(self, refresh_interval=30):
        """Setup dashboard display preferences"""
        self.dashboard_refresh_interval = refresh_interval
        self.show_order_notifications = True
        self.show_low_stock_alerts = True

    def configure_order_processing(self, auto_confirm=False, manual_confirmation=True):
        """Configure order processing workflow"""
        self.auto_confirm_orders = auto_confirm
        self.require_manual_confirmation = manual_confirmation
        self.default_order_status = "pending" if manual_confirmation else "confirmed"
