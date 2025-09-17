from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class AdminLog(Base):
    """Admin activity logging model"""
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)  # create, update, delete, login, etc.
    entity_type = Column(String(50), nullable=True)  # product, order, user, etc.
    entity_id = Column(Integer, nullable=True)  # ID of the affected entity
    description = Column(Text, nullable=True)  # Human-readable description
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)  # Browser/client info
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    admin = relationship("Admin", back_populates="admin_logs")

    def __repr__(self):
        return f"<AdminLog(id={self.id}, admin_id={self.admin_id}, action='{self.action}')>"

    @property
    def action_description(self):
        """Get human-readable action description"""
        action_descriptions = {
            "login": "Вход в систему",
            "logout": "Выход из системы", 
            "create": "Создание",
            "update": "Обновление",
            "delete": "Удаление",
            "view": "Просмотр",
            "export": "Экспорт данных",
            "import": "Импорт данных"
        }
        return action_descriptions.get(self.action, self.action)

    @property
    def entity_description(self):
        """Get human-readable entity description"""
        entity_descriptions = {
            "product": "Товар",
            "order": "Заказ",
            "user": "Пользователь",
            "admin": "Администратор",
            "category": "Категория",
            "review": "Отзыв"
        }
        return entity_descriptions.get(self.entity_type, self.entity_type)
