from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class Admin(Base):
    """Admin user model for administrative access"""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    admin_role = Column(String(50), nullable=False, default="order_management")  # order_management, website_content, super_admin
    permissions = Column(String(500), nullable=True)  # JSON string of permissions
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="admin_profile")
    admin_logs = relationship("AdminLog", back_populates="admin", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Admin(id={self.id}, role='{self.admin_role}', user_id={self.user_id})>"

    @property
    def is_super_admin(self):
        """Check if admin has super admin privileges"""
        return self.admin_role == "super_admin"

    @property
    def is_order_management_admin(self):
        """Check if admin manages orders"""
        return self.admin_role == "order_management"

    @property
    def is_website_content_admin(self):
        """Check if admin manages website content"""
        return self.admin_role == "website_content"

    @property
    def role_display_name(self):
        """Get display name for admin role"""
        role_names = {
            "order_management": "Администратор заказов",
            "website_content": "Администратор контента",
            "super_admin": "Супер администратор"
        }
        return role_names.get(self.admin_role, self.admin_role)

    def has_permission(self, permission):
        """Check if admin has specific permission"""
        if not self.permissions:
            return False
        # Assuming permissions is a comma-separated string
        return permission in self.permissions.split(",")

    def add_permission(self, permission):
        """Add permission to admin"""
        if not self.permissions:
            self.permissions = permission
        elif permission not in self.permissions.split(","):
            self.permissions += f",{permission}"

    def remove_permission(self, permission):
        """Remove permission from admin"""
        if not self.permissions:
            return
        perms = [p.strip() for p in self.permissions.split(",")]
        if permission in perms:
            perms.remove(permission)
            self.permissions = ",".join(perms) if perms else None

    def get_default_permissions(self):
        """Get default permissions based on admin role"""
        if self.is_super_admin:
            return "orders.view,orders.update,orders.delete,products.create,products.update,products.delete,users.view,users.update,admins.create,admins.update"
        elif self.is_order_management_admin:
            return "orders.view,orders.update,orders.status_change,orders.export"
        elif self.is_website_content_admin:
            return "products.create,products.update,products.delete,products.assets,reviews.moderate"
        return ""

    def setup_default_permissions(self):
        """Setup default permissions for the admin role"""
        if not self.permissions:
            self.permissions = self.get_default_permissions()

    def can_manage_orders(self):
        """Check if admin can manage orders"""
        return self.is_super_admin or self.is_order_management_admin

    def can_manage_products(self):
        """Check if admin can manage products"""
        return self.is_super_admin or self.is_website_content_admin

    def can_manage_users(self):
        """Check if admin can manage users"""
        return self.is_super_admin

    def can_manage_admins(self):
        """Check if admin can manage other admins"""
        return self.is_super_admin
