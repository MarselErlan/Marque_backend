from sqladmin import ModelView
from starlette.requests import Request
from ..models import (
    User, PhoneVerification, UserAddress, UserPaymentMethod, UserNotification
)

class UserAdmin(ModelView, model=User):
    """User management interface"""
    
    name = "Пользователи"
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"
    
    column_list = [
        "id", "phone_number", "full_name", "is_verified", "is_active", "last_login", "created_at"
    ]
    column_details_list = [
        "id", "phone_number", "full_name", "profile_image_url", "is_verified", 
        "is_active", "last_login", "created_at", "updated_at"
    ]
    
    form_columns = [
        "phone_number", "full_name", "profile_image_url", "is_verified", "is_active"
    ]
    
    column_searchable_list = ["phone_number", "full_name"]
    column_sortable_list = ["id", "phone_number", "full_name", "is_verified", "is_active", "last_login", "created_at"]
    column_filters = ["is_verified", "is_active"]
    
    column_labels = {
        "id": "ID",
        "phone_number": "Номер телефона",
        "full_name": "Полное имя",
        "profile_image_url": "URL фото профиля",
        "is_verified": "Подтверждён",
        "is_active": "Активен",
        "last_login": "Последний вход",
        "created_at": "Создан",
        "updated_at": "Обновлён"
    }
    
    form_label = "Пользователь"
    form_columns_labels = {
        "phone_number": "Номер телефона (+996 505 23 12 55)",
        "full_name": "Полное имя (Анна Ахматова)",
        "profile_image_url": "URL фотографии профиля",
        "is_verified": "Номер телефона подтверждён",
        "is_active": "Активный пользователь"
    }


class PhoneVerificationAdmin(ModelView, model=PhoneVerification):
    """Phone verification management"""
    
    name = "Верификация телефонов"
    name_plural = "Верификация телефонов"
    icon = "fa-solid fa-mobile"
    
    column_list = [
        "id", "phone_number", "verification_code", "is_used", "expires_at", "created_at"
    ]
    column_details_list = [
        "id", "user_id", "phone_number", "verification_code", "is_used", 
        "expires_at", "created_at", "verified_at"
    ]
    
    # Read-only for security
    can_create = False
    can_edit = False
    can_delete = True
    
    column_searchable_list = ["phone_number", "verification_code"]
    column_sortable_list = ["id", "phone_number", "is_used", "expires_at", "created_at"]
    column_filters = ["is_used"]
    
    column_labels = {
        "id": "ID",
        "user_id": "ID пользователя",
        "phone_number": "Номер телефона",
        "verification_code": "Код верификации",
        "is_used": "Использован",
        "expires_at": "Истекает",
        "created_at": "Создан",
        "verified_at": "Подтверждён"
    }


class UserAddressAdmin(ModelView, model=UserAddress):
    """User addresses management"""
    
    name = "Адреса пользователей"
    name_plural = "Адреса пользователей"
    icon = "fa-solid fa-map-marker-alt"
    
    column_list = [
        "id", "user_id", "title", "full_address", "is_default", "is_active"
    ]
    column_details_list = [
        "id", "user_id", "address_type", "title", "full_address", 
        "street", "building", "apartment", "city", "postal_code", 
        "country", "is_default", "is_active", "created_at"
    ]
    
    form_columns = [
        "user_id", "address_type", "title", "full_address", 
        "street", "building", "apartment", "city", "postal_code", 
        "country", "is_default", "is_active"
    ]
    
    column_searchable_list = ["title", "full_address", "street", "city"]
    column_sortable_list = ["id", "user_id", "title", "is_default", "is_active", "created_at"]
    column_filters = ["address_type", "is_default", "is_active", "city"]
    
    column_labels = {
        "id": "ID",
        "user_id": "ID пользователя",
        "address_type": "Тип адреса",
        "title": "Название",
        "full_address": "Полный адрес",
        "street": "Улица",
        "building": "Дом",
        "apartment": "Квартира",
        "city": "Город",
        "postal_code": "Почтовый индекс",
        "country": "Страна",
        "is_default": "По умолчанию",
        "is_active": "Активен",
        "created_at": "Создан"
    }
    
    form_label = "Адрес пользователя"
    form_columns_labels = {
        "user_id": "ID пользователя",
        "address_type": "Тип адреса (home, work, other)",
        "title": "Название адреса",
        "full_address": "Полный адрес",
        "street": "Название улицы",
        "building": "Номер дома",
        "apartment": "Номер квартиры",
        "city": "Город",
        "postal_code": "Почтовый индекс",
        "country": "Страна",
        "is_default": "Адрес по умолчанию",
        "is_active": "Активный адрес"
    }


class UserPaymentMethodAdmin(ModelView, model=UserPaymentMethod):
    """User payment methods management"""
    
    name = "Способы оплаты"
    name_plural = "Способы оплаты"
    icon = "fa-solid fa-credit-card"
    
    column_list = [
        "id", "user_id", "payment_type", "card_type", "card_number_masked", "is_default", "is_active"
    ]
    column_details_list = [
        "id", "user_id", "payment_type", "card_type", "card_number_masked", 
        "card_holder_name", "expiry_month", "expiry_year", "is_default", 
        "is_active", "created_at"
    ]
    
    form_columns = [
        "user_id", "payment_type", "card_type", "card_number_masked", 
        "card_holder_name", "expiry_month", "expiry_year", "is_default", "is_active"
    ]
    
    column_searchable_list = ["card_holder_name", "card_number_masked"]
    column_sortable_list = ["id", "user_id", "payment_type", "card_type", "is_default", "is_active", "created_at"]
    column_filters = ["payment_type", "card_type", "is_default", "is_active"]
    
    column_labels = {
        "id": "ID",
        "user_id": "ID пользователя",
        "payment_type": "Тип оплаты",
        "card_type": "Тип карты",
        "card_number_masked": "Номер карты",
        "card_holder_name": "Имя владельца",
        "expiry_month": "Месяц окончания",
        "expiry_year": "Год окончания",
        "is_default": "По умолчанию",
        "is_active": "Активен",
        "created_at": "Создан"
    }
    
    form_label = "Способ оплаты"
    form_columns_labels = {
        "user_id": "ID пользователя",
        "payment_type": "Тип оплаты (card, wallet, cash)",
        "card_type": "Тип карты (visa, mastercard, mir)",
        "card_number_masked": "Замаскированный номер карты (**** **** 2352)",
        "card_holder_name": "Имя владельца карты",
        "expiry_month": "Месяц окончания (MM)",
        "expiry_year": "Год окончания (YYYY)",
        "is_default": "Способ оплаты по умолчанию",
        "is_active": "Активный способ оплаты"
    }


class UserNotificationAdmin(ModelView, model=UserNotification):
    """User notifications management"""
    
    name = "Уведомления"
    name_plural = "Уведомления"
    icon = "fa-solid fa-bell"
    
    column_list = [
        "id", "user_id", "notification_type", "title", "is_read", "created_at"
    ]
    column_details_list = [
        "id", "user_id", "notification_type", "title", "message", 
        "order_id", "is_read", "is_active", "created_at", "read_at"
    ]
    
    form_columns = [
        "user_id", "notification_type", "title", "message", 
        "order_id", "is_read", "is_active"
    ]
    
    column_searchable_list = ["title", "message"]
    column_sortable_list = ["id", "user_id", "notification_type", "is_read", "created_at"]
    column_filters = ["notification_type", "is_read", "is_active"]
    
    column_labels = {
        "id": "ID",
        "user_id": "ID пользователя",
        "notification_type": "Тип уведомления",
        "title": "Заголовок",
        "message": "Сообщение",
        "order_id": "ID заказа",
        "is_read": "Прочитано",
        "is_active": "Активно",
        "created_at": "Создано",
        "read_at": "Прочитано"
    }
    
    form_label = "Уведомление"
    form_columns_labels = {
        "user_id": "ID пользователя",
        "notification_type": "Тип уведомления (order, promotion, system)",
        "title": "Заголовок уведомления",
        "message": "Текст уведомления",
        "order_id": "ID связанного заказа",
        "is_read": "Уведомление прочитано",
        "is_active": "Активное уведомление"
    }
