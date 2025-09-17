"""
Dependency Injection Container
Manages service registration and dependency resolution
"""

from typing import Any, Dict, Type, TypeVar, Callable, Optional, Union
from abc import ABC, abstractmethod
import inspect
from functools import wraps

T = TypeVar('T')

class ServiceRegistry:
    """Service registry for dependency injection"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._interfaces: Dict[Type, Type] = {}
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service"""
        self._services[interface] = implementation
        self._singletons[interface] = None  # Will be created on first access
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a transient service (new instance each time)"""
        self._services[interface] = implementation
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function for creating instances"""
        self._factories[interface] = factory
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a pre-created instance"""
        self._services[interface] = instance
        self._singletons[interface] = instance
    
    def register_interface(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register interface mapping"""
        self._interfaces[interface] = implementation
    
    def get(self, interface: Type[T]) -> T:
        """Get service instance"""
        # Check if we have a pre-created instance
        if interface in self._singletons and self._singletons[interface] is not None:
            return self._singletons[interface]
        
        # Check if we have a factory
        if interface in self._factories:
            instance = self._factories[interface]()
            if interface in self._singletons:
                self._singletons[interface] = instance
            return instance
        
        # Check if we have a registered service
        if interface in self._services:
            implementation = self._services[interface]
            
            # If it's already an instance, return it
            if not inspect.isclass(implementation):
                return implementation
            
            # Create new instance
            instance = self._create_instance(implementation)
            
            # Store as singleton if registered as such
            if interface in self._singletons:
                self._singletons[interface] = instance
            
            return instance
        
        # Check if interface has a registered implementation
        if interface in self._interfaces:
            implementation = self._interfaces[interface]
            instance = self._create_instance(implementation)
            return instance
        
        raise ValueError(f"Service {interface} not registered")
    
    def _create_instance(self, implementation: Type[T]) -> T:
        """Create instance with dependency injection"""
        # Get constructor parameters
        sig = inspect.signature(implementation.__init__)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Try to resolve dependency
            if param.annotation != inspect.Parameter.empty:
                try:
                    kwargs[param_name] = self.get(param.annotation)
                except ValueError:
                    if param.default == inspect.Parameter.empty:
                        raise ValueError(f"Cannot resolve dependency {param.annotation} for {implementation}")
        
        return implementation(**kwargs)
    
    def is_registered(self, interface: Type[T]) -> bool:
        """Check if service is registered"""
        return (interface in self._services or 
                interface in self._factories or 
                interface in self._interfaces)
    
    def clear(self) -> None:
        """Clear all registrations"""
        self._services.clear()
        self._singletons.clear()
        self._factories.clear()
        self._interfaces.clear()

# Global service registry
_service_registry = ServiceRegistry()

def register_singleton(interface: Type[T], implementation: Type[T]) -> None:
    """Register a singleton service"""
    _service_registry.register_singleton(interface, implementation)

def register_transient(interface: Type[T], implementation: Type[T]) -> None:
    """Register a transient service"""
    _service_registry.register_transient(interface, implementation)

def register_factory(interface: Type[T], factory: Callable[[], T]) -> None:
    """Register a factory function"""
    _service_registry.register_factory(interface, factory)

def register_instance(interface: Type[T], instance: T) -> None:
    """Register a pre-created instance"""
    _service_registry.register_instance(interface, instance)

def get_service(interface: Type[T]) -> T:
    """Get service instance"""
    return _service_registry.get(interface)

def inject(func: Callable) -> Callable:
    """Decorator for automatic dependency injection"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get function signature
        sig = inspect.signature(func)
        
        # Inject dependencies
        for param_name, param in sig.parameters.items():
            if param_name not in kwargs and param.annotation != inspect.Parameter.empty:
                try:
                    kwargs[param_name] = get_service(param.annotation)
                except ValueError:
                    pass  # Skip if not registered
        
        return func(*args, **kwargs)
    return wrapper

class Container:
    """Dependency injection container"""
    
    def __init__(self):
        self._registry = ServiceRegistry()
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> 'Container':
        """Register a singleton service"""
        self._registry.register_singleton(interface, implementation)
        return self
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> 'Container':
        """Register a transient service"""
        self._registry.register_transient(interface, implementation)
        return self
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> 'Container':
        """Register a factory function"""
        self._registry.register_factory(interface, factory)
        return self
    
    def register_instance(self, interface: Type[T], instance: T) -> 'Container':
        """Register a pre-created instance"""
        self._registry.register_instance(interface, instance)
        return self
    
    def get(self, interface: Type[T]) -> T:
        """Get service instance"""
        return self._registry.get(interface)
    
    def wire(self, modules: list) -> None:
        """Wire dependencies to modules"""
        for module in modules:
            if hasattr(module, 'configure'):
                module.configure(self)
    
    def is_registered(self, interface: Type[T]) -> bool:
        """Check if service is registered"""
        return self._registry.is_registered(interface)

# Global container instance
container = Container()

# Convenience functions
def get_container() -> Container:
    """Get global container instance"""
    return container

def configure_services(container: Container) -> None:
    """Configure all services"""
    # Database services
    from ..infrastructure.database.manager import DatabaseManager
    from ..infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
    from ..infrastructure.database.repositories.phone_verification_repository_impl import PhoneVerificationRepositoryImpl
    
    # Application services
    from ..application.services.user_service import UserService
    from ..application.services.auth_service import AuthService
    from ..application.services.phone_verification_service import PhoneVerificationService
    
    # External services
    from ..infrastructure.external.sms_service import SMSService
    from ..infrastructure.external.email_service import EmailService
    
    # Register services
    container.register_singleton(DatabaseManager, DatabaseManager)
    container.register_transient(UserRepositoryImpl, UserRepositoryImpl)
    container.register_transient(PhoneVerificationRepositoryImpl, PhoneVerificationRepositoryImpl)
    container.register_singleton(UserService, UserService)
    container.register_singleton(AuthService, AuthService)
    container.register_singleton(PhoneVerificationService, PhoneVerificationService)
    container.register_singleton(SMSService, SMSService)
    container.register_singleton(EmailService, EmailService)
