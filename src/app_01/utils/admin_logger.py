"""
Admin activity logger utility
Provides comprehensive logging for admin actions and errors
"""

import logging
import traceback
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from ..models.admins.admin_log import AdminLog

# Configure logger
logger = logging.getLogger("admin_logger")
logger.setLevel(logging.INFO)

# Create file handler for admin logs
admin_log_handler = logging.FileHandler("admin_activity.log")
admin_log_handler.setLevel(logging.INFO)

# Create file handler for errors
error_log_handler = logging.FileHandler("admin_errors.log")
error_log_handler.setLevel(logging.ERROR)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

admin_log_handler.setFormatter(formatter)
error_log_handler.setFormatter(formatter)

logger.addHandler(admin_log_handler)
logger.addHandler(error_log_handler)


class AdminLogger:
    """Admin activity and error logger"""
    
    @staticmethod
    def log_action(
        db: Session,
        admin_id: int,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log admin action to database and file
        
        Args:
            db: Database session
            admin_id: ID of the admin performing the action
            action: Type of action (create, update, delete, etc.)
            entity_type: Type of entity affected (product, order, etc.)
            entity_id: ID of the affected entity
            description: Human-readable description
            ip_address: IP address of the admin
            user_agent: User agent string
        """
        try:
            # Create log entry in database
            log_entry = AdminLog(
                admin_id=admin_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(log_entry)
            db.commit()
            
            # Log to file
            log_message = f"Admin {admin_id} - {action}"
            if entity_type:
                log_message += f" {entity_type}"
            if entity_id:
                log_message += f" #{entity_id}"
            if description:
                log_message += f" - {description}"
            
            logger.info(log_message)
            
        except Exception as e:
            logger.error(f"Failed to log admin action: {e}")
            # Don't raise exception to avoid breaking the main operation
    
    @staticmethod
    def log_error(
        db: Session,
        admin_id: int,
        error: Exception,
        context: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """
        Log admin error to database and file
        
        Args:
            db: Database session
            admin_id: ID of the admin encountering the error
            error: The exception that occurred
            context: Context of the error
            entity_type: Type of entity involved
            entity_id: ID of the entity involved
            ip_address: IP address of the admin
        """
        try:
            # Get error details
            error_type = type(error).__name__
            error_message = str(error)
            error_traceback = traceback.format_exc()
            
            # Create description
            description = f"ERROR: {error_type}: {error_message}"
            if context:
                description = f"{context} - {description}"
            
            # Log to database
            log_entry = AdminLog(
                admin_id=admin_id,
                action="error",
                entity_type=entity_type,
                entity_id=entity_id,
                description=description[:1000],  # Truncate if too long
                ip_address=ip_address
            )
            db.add(log_entry)
            db.commit()
            
            # Log to file with full traceback
            error_log_message = f"""
{'='*80}
Admin Error Log
Time: {datetime.now()}
Admin ID: {admin_id}
Context: {context or 'N/A'}
Entity: {entity_type} #{entity_id if entity_id else 'N/A'}
IP: {ip_address or 'N/A'}
Error Type: {error_type}
Error Message: {error_message}
Traceback:
{error_traceback}
{'='*80}
"""
            logger.error(error_log_message)
            
        except Exception as log_error:
            # Last resort: log to console
            print(f"CRITICAL: Failed to log error: {log_error}")
            print(f"Original error: {error}")
    
    @staticmethod
    def log_login(
        db: Session,
        admin_id: int,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log admin login attempt"""
        action = "login_success" if success else "login_failed"
        description = "Успешный вход" if success else "Неудачная попытка входа"
        
        AdminLogger.log_action(
            db=db,
            admin_id=admin_id,
            action=action,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_logout(
        db: Session,
        admin_id: int,
        ip_address: Optional[str] = None
    ):
        """Log admin logout"""
        AdminLogger.log_action(
            db=db,
            admin_id=admin_id,
            action="logout",
            description="Выход из системы",
            ip_address=ip_address
        )
    
    @staticmethod
    def log_create(
        db: Session,
        admin_id: int,
        entity_type: str,
        entity_id: int,
        description: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log entity creation"""
        if not description:
            description = f"Создан {entity_type} #{entity_id}"
        
        AdminLogger.log_action(
            db=db,
            admin_id=admin_id,
            action="create",
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_update(
        db: Session,
        admin_id: int,
        entity_type: str,
        entity_id: int,
        changes: Optional[dict] = None,
        ip_address: Optional[str] = None
    ):
        """Log entity update"""
        description = f"Обновлен {entity_type} #{entity_id}"
        if changes:
            changed_fields = ", ".join(changes.keys())
            description += f" (изменены: {changed_fields})"
        
        AdminLogger.log_action(
            db=db,
            admin_id=admin_id,
            action="update",
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_delete(
        db: Session,
        admin_id: int,
        entity_type: str,
        entity_id: int,
        description: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log entity deletion"""
        if not description:
            description = f"Удален {entity_type} #{entity_id}"
        
        AdminLogger.log_action(
            db=db,
            admin_id=admin_id,
            action="delete",
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address
        )
    
    @staticmethod
    def get_admin_activity(
        db: Session,
        admin_id: Optional[int] = None,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        limit: int = 100
    ):
        """
        Get admin activity logs
        
        Args:
            db: Database session
            admin_id: Filter by admin ID
            action: Filter by action type
            entity_type: Filter by entity type
            limit: Maximum number of logs to return
        
        Returns:
            List of admin log entries
        """
        query = db.query(AdminLog).order_by(AdminLog.created_at.desc())
        
        if admin_id:
            query = query.filter(AdminLog.admin_id == admin_id)
        if action:
            query = query.filter(AdminLog.action == action)
        if entity_type:
            query = query.filter(AdminLog.entity_type == entity_type)
        
        return query.limit(limit).all()

