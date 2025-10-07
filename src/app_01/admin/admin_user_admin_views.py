"""
Admin User Management Admin Views
SQLAdmin interface for managing admin accounts and permissions
"""

from sqladmin import ModelView
from starlette.requests import Request
from passlib.hash import bcrypt

from ..models.admins.admin import Admin


class AdminUserAdmin(ModelView, model=Admin):
    """Admin user management interface"""
    
    # Display settings
    name = "Администраторы"
    name_plural = "Администраторы"
    icon = "fa-solid fa-user-shield"
    
    # Column configuration
    column_list = [
        "id", "username", "email", "admin_role", 
        "is_active", "is_super_admin", "last_login"
    ]
    
    column_details_list = [
        "id", "username", "email", "full_name",
        "admin_role", "permissions", "is_active", "is_super_admin",
        "last_login", "created_at", "updated_at"
    ]
    
    # Form configuration (password handled separately)
    # Note: hashed_password, last_login, created_at, updated_at are automatically excluded
    form_columns = [
        "username", "email", "full_name", "admin_role",
        "permissions", "is_active", "is_super_admin"
    ]
    
    # Search and filters
    column_searchable_list = ["username", "email", "full_name"]
    column_sortable_list = ["id", "username", "email", "admin_role", "last_login", "created_at"]
    column_filters = ["admin_role", "is_active", "is_super_admin"]
    
    # Default sorting (newest first)
    column_default_sort = [("created_at", True)]
    
    # Column labels (Russian)
    column_labels = {
        "id": "ID",
        "username": "Имя пользователя",
        "email": "Email",
        "full_name": "Полное имя",
        "admin_role": "Роль",
        "permissions": "Права доступа",
        "is_active": "Активен",
        "is_super_admin": "Супер-админ",
        "last_login": "Последний вход",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }
    
    # Form labels
    form_label = "Администратор"
    form_columns_labels = {
        "username": "Имя пользователя (логин)",
        "email": "Email адрес",
        "full_name": "Полное имя",
        "admin_role": "Роль (order_management/website_content/super_admin)",
        "permissions": "Права доступа (JSON)",
        "is_active": "Активный аккаунт",
        "is_super_admin": "Супер-администратор (полный доступ)"
    }
    
    # Custom formatting
    column_formatters = {
        "is_active": lambda model, _: "✅" if model.is_active else "❌",
        "is_super_admin": lambda model, _: "✅" if model.is_super_admin else "❌",
        "last_login": lambda model, _: model.last_login.strftime("%d.%m.%Y %H:%M") if model.last_login else "Никогда",
        "admin_role": lambda model, _: {
            "order_management": "Управление заказами",
            "website_content": "Управление контентом",
            "super_admin": "Супер-администратор"
        }.get(model.admin_role, model.admin_role)
    }
    
    # Permissions
    can_create = True
    can_edit = True
    can_delete = True  # Can deactivate admins
    can_view_details = True
    can_export = False  # Don't export admin data for security
    
    # Page size
    page_size = 25
    page_size_options = [10, 25, 50]
    
    # Help text for permissions
    form_widget_args = {
        "permissions": {
            "placeholder": '{"orders": ["view", "update"], "products": ["view", "create", "update"]}'
        },
        "username": {
            "placeholder": "admin_username"
        },
        "email": {
            "placeholder": "admin@example.com"
        }
    }
    
    # Custom methods
    def on_model_change(self, form, model, is_created, request):
        """
        Hook called when a model is created or updated.
        Use this to set default permissions based on role.
        """
        # Set default permissions if not provided
        if not model.permissions and model.admin_role:
            if model.admin_role == "super_admin":
                model.is_super_admin = True
                model.permissions = '{"all": ["*"]}'
            elif model.admin_role == "order_management":
                model.permissions = '{"orders": ["view", "update", "delete"], "users": ["view"]}'
            elif model.admin_role == "website_content":
                model.permissions = '{"products": ["create", "update", "delete"], "categories": ["create", "update", "delete"], "banners": ["create", "update", "delete"]}'
        
        # Note: Password must be set separately using create_admin.py script
        # This admin interface is for managing roles and permissions only

