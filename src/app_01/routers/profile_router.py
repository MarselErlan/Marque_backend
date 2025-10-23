"""
Profile Router - Complete user profile management
Handles addresses, payment methods, orders, and notifications
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db.market_db import get_db, Market
from ..models.users.market_user import UserKG, UserUS
from ..models.users.market_user_address import UserAddressKG, UserAddressUS
from ..models.users.market_user_payment_method import UserPaymentMethodKG, UserPaymentMethodUS
from ..models.users.user_notification import UserNotification
from ..models.orders.order import Order, OrderStatus
from ..models.orders.order_item import OrderItem
from ..routers.auth_router import get_current_user_from_token
from ..schemas.auth import VerifyTokenResponse
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["profile"])


# ==================== Schemas ====================

class AddressCreate(BaseModel):
    title: str
    full_address: str
    street: Optional[str] = None
    building: Optional[str] = None
    apartment: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "Kyrgyzstan"
    is_default: bool = False


class AddressUpdate(BaseModel):
    title: Optional[str] = None
    full_address: Optional[str] = None
    street: Optional[str] = None
    building: Optional[str] = None
    apartment: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_default: Optional[bool] = None


class PaymentMethodCreate(BaseModel):
    card_number: str
    card_holder_name: str
    expiry_month: str
    expiry_year: str
    is_default: bool = False


class PaymentMethodUpdate(BaseModel):
    is_default: Optional[bool] = None


# ==================== Helper Functions ====================

def get_user_model(market: str):
    """Get the appropriate User model based on market"""
    if market == "kg":
        return UserKG
    elif market == "us":
        return UserUS
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid market: {market}"
        )


def get_address_model(market: str):
    """Get the appropriate Address model based on market"""
    if market == "kg":
        return UserAddressKG
    elif market == "us":
        return UserAddressUS
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid market: {market}"
        )


def get_payment_model(market: str):
    """Get the appropriate Payment model based on market"""
    if market == "kg":
        return UserPaymentMethodKG
    elif market == "us":
        return UserPaymentMethodUS
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid market: {market}"
        )


# ==================== Address Endpoints ====================

@router.get("/addresses")
def get_user_addresses(
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get all user addresses"""
    try:
        AddressModel = get_address_model(current_user.market)
        
        addresses = db.query(AddressModel).filter(
            AddressModel.user_id == current_user.user_id,
            AddressModel.is_active == True
        ).order_by(
            AddressModel.is_default.desc(),
            AddressModel.created_at.desc()
        ).all()
        
        return {
            "success": True,
            "addresses": [
                {
                    "id": addr.id,
                    "title": addr.title,
                    "full_address": addr.full_address,
                    "street": addr.street,
                    "building": addr.building,
                    "apartment": addr.apartment,
                    "city": addr.city,
                    "postal_code": addr.postal_code,
                    "country": addr.country,
                    "is_default": addr.is_default,
                    "created_at": addr.created_at.isoformat() if addr.created_at else None
                }
                for addr in addresses
            ],
            "total": len(addresses)
        }
    except Exception as e:
        logger.error(f"Error fetching addresses for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch addresses"
        )


@router.post("/addresses", status_code=status.HTTP_201_CREATED)
def create_user_address(
    address_data: AddressCreate,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Create new delivery address"""
    try:
        AddressModel = get_address_model(current_user.market)
        
        # If this is set as default, unset other defaults
        if address_data.is_default:
            db.query(AddressModel).filter(
                AddressModel.user_id == current_user.user_id
            ).update({"is_default": False})
        
        # Create new address
        new_address = AddressModel(
            user_id=current_user.user_id,
            title=address_data.title,
            full_address=address_data.full_address,
            street=address_data.street,
            building=address_data.building,
            apartment=address_data.apartment,
            city=address_data.city,
            postal_code=address_data.postal_code,
            country=address_data.country,
            is_default=address_data.is_default,
            market=current_user.market
        )
        
        db.add(new_address)
        db.commit()
        db.refresh(new_address)
        
        logger.info(f"Address created for user {current_user.user_id}: {new_address.id}")
        
        return {
            "success": True,
            "message": "Address created successfully",
            "address": {
                "id": new_address.id,
                "title": new_address.title,
                "full_address": new_address.full_address,
                "is_default": new_address.is_default,
                "created_at": new_address.created_at.isoformat() if new_address.created_at else None
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating address for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create address"
        )


@router.put("/addresses/{address_id}")
def update_user_address(
    address_id: int,
    address_data: AddressUpdate,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Update delivery address"""
    try:
        AddressModel = get_address_model(current_user.market)
        
        # Get address
        address = db.query(AddressModel).filter(
            AddressModel.id == address_id,
            AddressModel.user_id == current_user.user_id
        ).first()
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )
        
        # If setting as default, unset other defaults
        if address_data.is_default:
            db.query(AddressModel).filter(
                AddressModel.user_id == current_user.user_id,
                AddressModel.id != address_id
            ).update({"is_default": False})
        
        # Update fields
        update_data = address_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(address, field, value)
        
        db.commit()
        db.refresh(address)
        
        logger.info(f"Address {address_id} updated for user {current_user.user_id}")
        
        return {
            "success": True,
            "message": "Address updated successfully",
            "address": {
                "id": address.id,
                "title": address.title,
                "is_default": address.is_default
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating address {address_id} for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update address"
        )


@router.delete("/addresses/{address_id}")
def delete_user_address(
    address_id: int,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Delete delivery address"""
    try:
        AddressModel = get_address_model(current_user.market)
        
        # Get address
        address = db.query(AddressModel).filter(
            AddressModel.id == address_id,
            AddressModel.user_id == current_user.user_id
        ).first()
        
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )
        
        # Soft delete
        address.is_active = False
        db.commit()
        
        logger.info(f"Address {address_id} deleted for user {current_user.user_id}")
        
        return {
            "success": True,
            "message": "Address deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting address {address_id} for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete address"
        )


# ==================== Payment Method Endpoints ====================

@router.get("/payment-methods")
def get_user_payment_methods(
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get all user payment methods"""
    try:
        PaymentModel = get_payment_model(current_user.market)
        
        payment_methods = db.query(PaymentModel).filter(
            PaymentModel.user_id == current_user.user_id,
            PaymentModel.is_active == True
        ).order_by(
            PaymentModel.is_default.desc(),
            PaymentModel.created_at.desc()
        ).all()
        
        return {
            "success": True,
            "payment_methods": [
                {
                    "id": pm.id,
                    "payment_type": pm.payment_type,
                    "card_type": pm.card_type,
                    "card_number_masked": pm.card_number_masked,
                    "card_holder_name": pm.card_holder_name,
                    "is_default": pm.is_default,
                    "created_at": pm.created_at.isoformat() if pm.created_at else None
                }
                for pm in payment_methods
            ],
            "total": len(payment_methods)
        }
    except Exception as e:
        logger.error(f"Error fetching payment methods for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment methods"
        )


@router.post("/payment-methods", status_code=status.HTTP_201_CREATED)
def create_payment_method(
    payment_data: PaymentMethodCreate,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Create new payment method"""
    try:
        PaymentModel = get_payment_model(current_user.market)
        
        # If this is set as default, unset other defaults
        if payment_data.is_default:
            db.query(PaymentModel).filter(
                PaymentModel.user_id == current_user.user_id
            ).update({"is_default": False})
        
        # Mask card number (show only last 4 digits)
        card_number_masked = payment_data.card_number[-4:] if len(payment_data.card_number) >= 4 else payment_data.card_number
        
        # Determine card type
        card_type = None
        if payment_data.card_number.startswith("4"):
            card_type = "visa"
        elif payment_data.card_number.startswith("5") or payment_data.card_number.startswith("2"):
            card_type = "mastercard"
        elif payment_data.card_number.startswith("2"):
            card_type = "mir"
        
        # Create new payment method
        new_payment = PaymentModel(
            user_id=current_user.user_id,
            payment_type="card",
            card_type=card_type,
            card_number_masked=card_number_masked,
            card_holder_name=payment_data.card_holder_name,
            expiry_month=payment_data.expiry_month,
            expiry_year=payment_data.expiry_year,
            is_default=payment_data.is_default,
            market=current_user.market
        )
        
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
        
        logger.info(f"Payment method created for user {current_user.user_id}: {new_payment.id}")
        
        return {
            "success": True,
            "message": "Payment method added successfully",
            "payment_method": {
                "id": new_payment.id,
                "card_type": new_payment.card_type,
                "card_number_masked": new_payment.card_number_masked,
                "is_default": new_payment.is_default,
                "created_at": new_payment.created_at.isoformat() if new_payment.created_at else None
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating payment method for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment method"
        )


@router.put("/payment-methods/{payment_id}")
def update_payment_method(
    payment_id: int,
    payment_data: PaymentMethodUpdate,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Update payment method"""
    try:
        PaymentModel = get_payment_model(current_user.market)
        
        # Get payment method
        payment = db.query(PaymentModel).filter(
            PaymentModel.id == payment_id,
            PaymentModel.user_id == current_user.user_id
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        
        # If setting as default, unset other defaults
        if payment_data.is_default:
            db.query(PaymentModel).filter(
                PaymentModel.user_id == current_user.user_id,
                PaymentModel.id != payment_id
            ).update({"is_default": False})
            payment.is_default = True
        
        db.commit()
        
        logger.info(f"Payment method {payment_id} updated for user {current_user.user_id}")
        
        return {
            "success": True,
            "message": "Payment method updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating payment method {payment_id} for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update payment method"
        )


@router.delete("/payment-methods/{payment_id}")
def delete_payment_method(
    payment_id: int,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Delete payment method"""
    try:
        PaymentModel = get_payment_model(current_user.market)
        
        # Get payment method
        payment = db.query(PaymentModel).filter(
            PaymentModel.id == payment_id,
            PaymentModel.user_id == current_user.user_id
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        
        # Soft delete
        payment.is_active = False
        db.commit()
        
        logger.info(f"Payment method {payment_id} deleted for user {current_user.user_id}")
        
        return {
            "success": True,
            "message": "Payment method deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting payment method {payment_id} for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete payment method"
        )


# ==================== Order Endpoints ====================

@router.get("/orders")
def get_user_orders(
    status_filter: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get all user orders"""
    try:
        query = db.query(Order).filter(Order.user_id == current_user.user_id)
        
        # Filter by status if provided
        if status_filter:
            query = query.filter(Order.status == status_filter)
        
        # Get total count
        total = query.count()
        
        # Get orders with pagination
        orders = query.order_by(Order.created_at.desc()).limit(limit).offset(offset).all()
        
        result_orders = []
        for order in orders:
            # Get order items
            items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            
            result_orders.append({
                "id": order.id,
                "order_number": order.order_number,
                "status": order.status.value if isinstance(order.status, OrderStatus) else order.status,
                "total_amount": order.total_amount,
                "currency": order.currency,
                "order_date": order.order_date.isoformat() if order.order_date else None,
                "delivery_date": order.delivered_date.isoformat() if order.delivered_date else None,
                "delivery_address": order.delivery_address,
                "items_count": len(items),
                "items": [
                    {
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "price": item.price_at_purchase,
                        "image_url": item.product_image_url if hasattr(item, 'product_image_url') else None
                    }
                    for item in items[:3]  # Show first 3 items
                ]
            })
        
        return {
            "success": True,
            "orders": result_orders,
            "total": total,
            "has_more": (offset + limit) < total
        }
    except Exception as e:
        logger.error(f"Error fetching orders for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch orders"
        )


@router.get("/orders/{order_id}")
def get_order_details(
    order_id: int,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get order details"""
    try:
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user.user_id
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Get order items
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        
        return {
            "success": True,
            "order": {
                "id": order.id,
                "order_number": order.order_number,
                "status": order.status.value if isinstance(order.status, OrderStatus) else order.status,
                "customer_name": order.customer_name,
                "customer_phone": order.customer_phone,
                "delivery_address": order.delivery_address,
                "subtotal": order.subtotal,
                "shipping_cost": order.shipping_cost,
                "total_amount": order.total_amount,
                "currency": order.currency,
                "order_date": order.order_date.isoformat() if order.order_date else None,
                "confirmed_date": order.confirmed_date.isoformat() if order.confirmed_date else None,
                "shipped_date": order.shipped_date.isoformat() if order.shipped_date else None,
                "delivered_date": order.delivered_date.isoformat() if order.delivered_date else None,
                "items": [
                    {
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "price": item.price_at_purchase,
                        "subtotal": item.price_at_purchase * item.quantity,
                        "image_url": item.product_image_url if hasattr(item, 'product_image_url') else None
                    }
                    for item in items
                ]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order {order_id} for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch order details"
        )


@router.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Cancel order"""
    try:
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user.user_id
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check if order can be cancelled
        if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel order with status: {order.status.value}"
            )
        
        # Update order status
        order.status = OrderStatus.CANCELLED
        from datetime import datetime
        order.cancelled_date = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Order {order_id} cancelled by user {current_user.user_id}")
        
        return {
            "success": True,
            "message": "Order cancelled successfully",
            "order_id": order.id,
            "status": order.status.value
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error cancelling order {order_id} for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel order"
        )


# ==================== Notification Endpoints ====================

@router.get("/notifications")
def get_user_notifications(
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get all user notifications"""
    try:
        query = db.query(UserNotification).filter(
            UserNotification.user_id == current_user.user_id,
            UserNotification.is_active == True
        )
        
        # Filter by read status if requested
        if unread_only:
            query = query.filter(UserNotification.is_read == False)
        
        # Get total counts
        total = query.count()
        unread_count = db.query(UserNotification).filter(
            UserNotification.user_id == current_user.user_id,
            UserNotification.is_active == True,
            UserNotification.is_read == False
        ).count()
        
        # Get notifications with pagination
        notifications = query.order_by(UserNotification.created_at.desc()).limit(limit).offset(offset).all()
        
        return {
            "success": True,
            "notifications": [
                {
                    "id": notif.id,
                    "type": notif.notification_type,
                    "title": notif.title,
                    "message": notif.message,
                    "is_read": notif.is_read,
                    "order_id": notif.order_id,
                    "created_at": notif.created_at.isoformat() if notif.created_at else None
                }
                for notif in notifications
            ],
            "total": total,
            "unread_count": unread_count
        }
    except Exception as e:
        logger.error(f"Error fetching notifications for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications"
        )


@router.put("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    try:
        notification = db.query(UserNotification).filter(
            UserNotification.id == notification_id,
            UserNotification.user_id == current_user.user_id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        notification.is_read = True
        from datetime import datetime
        notification.read_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Notification {notification_id} marked as read for user {current_user.user_id}")
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking notification {notification_id} as read for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )


@router.put("/notifications/read-all")
def mark_all_notifications_read(
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    try:
        from datetime import datetime
        
        count = db.query(UserNotification).filter(
            UserNotification.user_id == current_user.user_id,
            UserNotification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        db.commit()
        
        logger.info(f"Marked {count} notifications as read for user {current_user.user_id}")
        
        return {
            "success": True,
            "message": "All notifications marked as read",
            "count": count
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking all notifications as read for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark all notifications as read"
        )

