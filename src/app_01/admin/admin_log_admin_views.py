"""
Admin Log Views for SQLAdmin
Allows viewing and filtering admin activity logs
"""

from sqladmin import ModelView
from sqlalchemy.orm import Session
from ..models.admins.admin_log import AdminLog


class AdminLogAdmin(ModelView, model=AdminLog):
    """Admin interface for viewing admin activity logs"""
    
    name = "Лог активности"
    name_plural = "Логи активности"
    icon = "fa-solid fa-clipboard-list"
    category = "Система"
    
    # Columns to display in list view
    column_list = [
        "id",
        "admin_id",
        "action",
        "entity_type",
        "entity_id",
        "description",
        "ip_address",
        "created_at"
    ]
    
    # Columns that can be searched
    column_searchable_list = [
        "action",
        "entity_type",
        "description",
        "ip_address"
    ]
    
    # Columns that can be filtered
    column_filters = [
        "admin_id",
        "action",
        "entity_type",
        "created_at",
        "ip_address"
    ]
    
    # Default sort order (newest first)
    column_default_sort = ("created_at", True)
    
    # Columns to display in detail view
    column_details_list = [
        "id",
        "admin_id",
        "action",
        "entity_type",
        "entity_id",
        "description",
        "ip_address",
        "user_agent",
        "created_at"
    ]
    
    # Read-only fields (logs should not be edited)
    can_create = False
    can_edit = False
    can_delete = False  # Set to True if you want to allow deletion
    can_export = True
    
    # Labels for Russian translation
    column_labels = {
        "id": "ID",
        "admin_id": "Администратор",
        "action": "Действие",
        "entity_type": "Тип объекта",
        "entity_id": "ID объекта",
        "description": "Описание",
        "ip_address": "IP адрес",
        "user_agent": "User Agent",
        "created_at": "Дата и время",
        "admin": "Администратор"
    }
    
    # Custom formatters for better display
    column_formatters = {
        "action": lambda m, a: AdminLogAdmin._format_action(m.action),
        "entity_type": lambda m, a: AdminLogAdmin._format_entity_type(m.entity_type),
        "description": lambda m, a: AdminLogAdmin._truncate_text(m.description, 100),
        "created_at": lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else "",
        "user_agent": lambda m, a: AdminLogAdmin._truncate_text(m.user_agent, 50)
    }
    
    # Add pagination
    page_size = 50
    page_size_options = [25, 50, 100, 200]
    
    @staticmethod
    def _format_action(action: str) -> str:
        """Format action for display"""
        action_map = {
            "login_success": "✅ Вход в систему",
            "login_failed": "❌ Неудачный вход",
            "logout": "🚪 Выход",
            "create": "➕ Создание",
            "update": "✏️ Обновление",
            "delete": "🗑️ Удаление",
            "view": "👁️ Просмотр",
            "export": "📤 Экспорт",
            "import": "📥 Импорт",
            "error": "⚠️ Ошибка"
        }
        return action_map.get(action, action)
    
    @staticmethod
    def _format_entity_type(entity_type: str) -> str:
        """Format entity type for display"""
        if not entity_type:
            return ""
        
        entity_map = {
            "product": "Товар",
            "order": "Заказ",
            "user": "Пользователь",
            "admin": "Администратор",
            "category": "Категория",
            "subcategory": "Подкатегория",
            "brand": "Бренд",
            "banner": "Баннер",
            "review": "Отзыв",
            "cart": "Корзина",
            "wishlist": "Избранное"
        }
        return entity_map.get(entity_type, entity_type)
    
    @staticmethod
    def _truncate_text(text: str, max_length: int) -> str:
        """Truncate text to max length"""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

