"""
User Profile Management API Endpoints
FastAPI routes for user profile, addresses, payment methods, and notifications
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime

from ..db import get_db
from ..models import User, UserAddress, UserPaymentMethod, UserNotification
from .auth import get_current_user

router = APIRouter(prefix="/profile", tags=["user-profile"])

# Address Models
class AddressBase(BaseModel):
    """Base address model"""
    address_type: str = "home"
    title: str
    full_address: str
    street: Optional[str] = None
    building: Optional[str] = None
    apartment: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Kyrgyzstan"
    is_default: bool = False

class AddressCreate(AddressBase):
    """Address creation model"""
    pass

class AddressUpdate(BaseModel):
    """Address update model"""
    address_type: Optional[str] = None
    title: Optional[str] = None
    full_address: Optional[str] = None
    street: Optional[str] = None
    building: Optional[str] = None
    apartment: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None

class AddressResponse(AddressBase):
    """Address response model"""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Payment Method Models
class PaymentMethodBase(BaseModel):
    """Base payment method model"""
    payment_type: str = "card"
    card_type: Optional[str] = None
    card_number: str  # Full card number for creation
    card_holder_name: str
    expiry_month: str
    expiry_year: str
    is_default: bool = False

class PaymentMethodCreate(PaymentMethodBase):
    """Payment method creation model"""
    @validator('expiry_month')
    def validate_expiry_month(cls, v):
        if not v.isdigit() or len(v) != 2 or not (1 <= int(v) <= 12):
            raise ValueError('Expiry month must be MM format (01-12)')
        return v
    
    @validator('expiry_year')
    def validate_expiry_year(cls, v):
        if not v.isdigit() or len(v) != 4 or int(v) < 2024:
            raise ValueError('Expiry year must be YYYY format and not expired')
        return v

class PaymentMethodResponse(BaseModel):
    """Payment method response model"""
    id: int
    user_id: int
    payment_type: str
    card_type: Optional[str]
    card_number_masked: Optional[str]
    card_holder_name: str
    expiry_month: Optional[str]
    expiry_year: Optional[str]
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Notification Models
class NotificationResponse(BaseModel):
    """Notification response model"""
    id: int
    user_id: int
    notification_type: str
    title: str
    message: Optional[str]
    order_id: Optional[int]
    is_read: bool
    is_active: bool
    metadata: Optional[dict]
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True

# Address Endpoints
@router.get("/addresses", response_model=List[AddressResponse])
async def get_user_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all user addresses"""
    addresses = UserAddress.get_user_addresses(db, current_user.id)
    return addresses

@router.post("/addresses", response_model=AddressResponse)
async def create_address(
    address: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new user address"""
    try:
        new_address = UserAddress.create_address(
            db=db,
            user_id=current_user.id,
            title=address.title,
            full_address=address.full_address,
            address_type=address.address_type,
            street=address.street,
            building=address.building,
            apartment=address.apartment,
            city=address.city,
            postal_code=address.postal_code,
            country=address.country,
            is_default=address.is_default
        )
        
        # If this is set as default, unset others
        if address.is_default:
            new_address.set_as_default(db)
        
        return new_address
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create address: {str(e)}"
        )

@router.put("/addresses/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    address_update: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user address"""
    try:
        address = db.query(UserAddress).filter(
            UserAddress.id == address_id,
            UserAddress.user_id == current_user.id
        ).first()
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )
        
        # Update fields
        update_data = address_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(address, field, value)
        
        # If setting as default, unset others
        if address_update.is_default:
            address.set_as_default(db)
        
        db.commit()
        db.refresh(address)
        
        return address
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update address: {str(e)}"
        )

@router.delete("/addresses/{address_id}")
async def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user address"""
    try:
        address = db.query(UserAddress).filter(
            UserAddress.id == address_id,
            UserAddress.user_id == current_user.id
        ).first()
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )
        
        address.is_active = False
        db.commit()
        
        return {"success": True, "message": "Address deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete address: {str(e)}"
        )

# Payment Method Endpoints
@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_user_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all user payment methods"""
    payment_methods = UserPaymentMethod.get_user_payment_methods(db, current_user.id)
    return payment_methods

@router.post("/payment-methods", response_model=PaymentMethodResponse)
async def create_payment_method(
    payment_method: PaymentMethodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new payment method"""
    try:
        new_payment_method = UserPaymentMethod.create_card(
            db=db,
            user_id=current_user.id,
            card_number=payment_method.card_number,
            card_holder_name=payment_method.card_holder_name,
            expiry_month=payment_method.expiry_month,
            expiry_year=payment_method.expiry_year
        )
        
        # If this is set as default, unset others
        if payment_method.is_default:
            new_payment_method.set_as_default(db)
        
        return new_payment_method
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment method: {str(e)}"
        )

@router.delete("/payment-methods/{payment_method_id}")
async def delete_payment_method(
    payment_method_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete payment method"""
    try:
        payment_method = db.query(UserPaymentMethod).filter(
            UserPaymentMethod.id == payment_method_id,
            UserPaymentMethod.user_id == current_user.id
        ).first()
        
        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        
        payment_method.is_active = False
        db.commit()
        
        return {"success": True, "message": "Payment method deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete payment method: {str(e)}"
        )

# Notification Endpoints
@router.get("/notifications", response_model=List[NotificationResponse])
async def get_user_notifications(
    notification_type: Optional[str] = None,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    notifications = UserNotification.get_user_notifications(
        db, current_user.id, notification_type, unread_only
    )
    return notifications

@router.get("/notifications/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    count = UserNotification.get_unread_count(db, current_user.id)
    return {"unread_count": count}

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    try:
        notification = db.query(UserNotification).filter(
            UserNotification.id == notification_id,
            UserNotification.user_id == current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        notification.mark_as_read()
        db.commit()
        
        return {"success": True, "message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

@router.put("/notifications/mark-all-read")
async def mark_all_notifications_read(
    notification_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    try:
        UserNotification.mark_all_as_read(db, current_user.id, notification_type)
        return {"success": True, "message": "All notifications marked as read"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notifications as read: {str(e)}"
        )
