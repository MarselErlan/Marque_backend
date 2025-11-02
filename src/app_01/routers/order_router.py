"""
Order Management Router
Handles order creation, retrieval, and management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, validator
import random

from ..db.market_db import get_db, Market
from ..models.orders.order import Order, OrderStatus
from ..models.orders.order_item import OrderItem
from ..models.products.sku import SKU
from ..models.products.product import Product
from ..models.orders.cart import Cart, CartItem
from ..routers.auth_router import get_current_user_from_token
from ..schemas.auth import VerifyTokenResponse


router = APIRouter(prefix="/orders", tags=["orders"])


# ==================== Schemas ====================

class OrderItemCreate(BaseModel):
    """Order item creation schema"""
    sku_id: int
    quantity: int
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError('Quantity must be at least 1')
        if v > 100:
            raise ValueError('Quantity cannot exceed 100')
        return v


class CreateOrderRequest(BaseModel):
    """Create order request"""
    # Customer info
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    
    # Delivery info
    delivery_address: str
    delivery_city: Optional[str] = None
    delivery_notes: Optional[str] = None
    
    # Payment info
    payment_method: str  # 'card', 'cash', 'online'
    
    # Items (if not using cart)
    items: Optional[List[OrderItemCreate]] = None
    
    # Use cart items if items not provided
    use_cart: bool = True
    
    @validator('customer_phone')
    def validate_phone(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Invalid phone number')
        return v
    
    @validator('delivery_address')
    def validate_address(cls, v):
        if not v or len(v) < 5:
            raise ValueError('Delivery address is too short')
        return v


class OrderItemResponse(BaseModel):
    """Order item response"""
    id: int
    product_name: str
    sku_code: str
    size: str
    color: str
    unit_price: float
    quantity: int
    total_price: float
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Order response"""
    id: int
    order_number: str
    status: str
    
    customer_name: str
    customer_phone: str
    delivery_address: str
    
    subtotal: float
    shipping_cost: float
    total_amount: float
    currency: str
    
    order_date: datetime
    
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


# ==================== Helper Functions ====================

def generate_order_number(db: Session) -> str:
    """Generate unique order number like #1001"""
    # Get the highest order number
    last_order = db.query(Order).order_by(Order.id.desc()).first()
    
    if last_order and last_order.order_number:
        # Extract number from "#1001"
        try:
            last_num = int(last_order.order_number.replace('#', ''))
            next_num = last_num + 1
        except:
            next_num = 1001
    else:
        next_num = 1001
    
    return f"#{next_num}"


def calculate_shipping_cost(subtotal: float, city: Optional[str] = None) -> float:
    """Calculate shipping cost based on order value and location"""
    # Free shipping for orders over 5000 KGS
    if subtotal >= 5000:
        return 0.0
    
    # Standard shipping cost
    return 150.0


def validate_and_get_sku(sku_id: int, db: Session) -> SKU:
    """Validate SKU exists and is in stock"""
    sku = db.query(SKU).options(
        joinedload(SKU.product)
    ).filter(
        SKU.id == sku_id,
        SKU.is_active == True
    ).first()
    
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU with id {sku_id} not found"
        )
    
    if sku.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product '{sku.product.title}' (size: {sku.size}, color: {sku.color}) is out of stock"
        )
    
    return sku


# ==================== Endpoints ====================

@router.post("/create", response_model=OrderResponse)
async def create_order(
    request: CreateOrderRequest,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    """
    Create a new order from cart or provided items
    
    **Flow:**
    1. Validate user authentication
    2. Get cart items OR use provided items
    3. Validate all SKUs (exist, in stock)
    4. Calculate totals
    5. Create Order
    6. Create OrderItems
    7. Reduce stock quantities
    8. Clear cart (if using cart)
    9. Return order details
    """
    try:
        user_id = current_user.user_id
        
        # ✅ FIX: Use the user's market from token instead of defaulting to KG
        user_market = Market(current_user.market.value) if current_user.market else Market.KG
        from ..db.market_db import db_manager
        SessionLocal = db_manager.get_session_factory(user_market)
        db = SessionLocal()
        
        # Step 1: Get items to order
        items_to_order = []
        
        if request.use_cart and not request.items:
            # Get items from cart
            cart = db.query(Cart).filter(Cart.user_id == user_id).first()
            
            if not cart or not cart.items:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Your cart is empty"
                )
            
            # Convert cart items to order items
            for cart_item in cart.items:
                items_to_order.append({
                    'sku_id': cart_item.sku_id,
                    'quantity': cart_item.quantity
                })
        
        elif request.items:
            # Use provided items
            items_to_order = [{'sku_id': item.sku_id, 'quantity': item.quantity} for item in request.items]
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No items to order. Please add items to cart or provide items."
            )
        
        # Step 2: Validate all SKUs and check stock
        validated_items = []
        subtotal = 0.0
        
        for item in items_to_order:
            sku = validate_and_get_sku(item['sku_id'], db)
            
            # Check if enough stock
            if sku.stock < item['quantity']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough stock for '{sku.product.title}' (size: {sku.size}, color: {sku.color}). Available: {sku.stock}"
                )
            
            item_total = sku.price * item['quantity']
            subtotal += item_total
            
            validated_items.append({
                'sku': sku,
                'quantity': item['quantity'],
                'unit_price': sku.price,
                'total_price': item_total
            })
        
        # Step 3: Calculate costs
        shipping_cost = calculate_shipping_cost(subtotal, request.delivery_city)
        total_amount = subtotal + shipping_cost
        
        # Step 4: Generate order number
        order_number = generate_order_number(db)
        
        # Step 5: Create Order
        new_order = Order(
            order_number=order_number,
            user_id=user_id,
            status=OrderStatus.PENDING,
            customer_name=request.customer_name,
            customer_phone=request.customer_phone,
            customer_email=request.customer_email,
            delivery_address=request.delivery_address,
            delivery_city=request.delivery_city,
            delivery_notes=request.delivery_notes,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total_amount=total_amount,
            currency="KGS"
        )
        
        db.add(new_order)
        db.flush()  # Get order ID
        
        # Step 6: Create OrderItems and reduce stock
        order_items = []
        for item in validated_items:
            sku = item['sku']
            
            # Create order item
            order_item = OrderItem(
                order_id=new_order.id,
                sku_id=sku.id,
                product_name=sku.product.title,
                sku_code=sku.sku_code,
                size=sku.size,
                color=sku.color,
                unit_price=item['unit_price'],
                quantity=item['quantity'],
                total_price=item['total_price']
            )
            
            db.add(order_item)
            order_items.append(order_item)
            
            # Reduce stock
            sku.stock -= item['quantity']
            
            # Update product sold count
            sku.product.sold_count = (sku.product.sold_count or 0) + item['quantity']
        
        # Step 7: Clear cart if using cart
        if request.use_cart:
            cart = db.query(Cart).filter(Cart.user_id == user_id).first()
            if cart:
                # Delete all cart items
                db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        
        # Commit everything
        db.commit()
        db.refresh(new_order)
        
        # Step 8: Return order details
        return OrderResponse(
            id=new_order.id,
            order_number=new_order.order_number,
            status=new_order.status.value,
            customer_name=new_order.customer_name,
            customer_phone=new_order.customer_phone,
            delivery_address=new_order.delivery_address,
            subtotal=new_order.subtotal,
            shipping_cost=new_order.shipping_cost,
            total_amount=new_order.total_amount,
            currency=new_order.currency,
            order_date=new_order.order_date,
            items=[
                OrderItemResponse(
                    id=item.id,
                    product_name=item.product_name,
                    sku_code=item.sku_code,
                    size=item.size,
                    color=item.color,
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                    total_price=item.total_price
                )
                for item in order_items
            ]
        )
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )
    finally:
        db.close()


@router.get("", response_model=List[OrderResponse])
async def get_user_orders(
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    status_filter: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Get all orders for the current user"""
    # ✅ FIX: Use the user's market from token
    user_market = Market(current_user.market.value) if current_user.market else Market.KG
    from ..db.market_db import db_manager
    SessionLocal = db_manager.get_session_factory(user_market)
    db = SessionLocal()
    
    try:
        query = db.query(Order).options(
            joinedload(Order.order_items)
        ).filter(
            Order.user_id == current_user.user_id
        )
        
        # Filter by status if provided
        if status_filter:
            try:
                order_status = OrderStatus[status_filter.upper()]
                query = query.filter(Order.status == order_status)
            except KeyError:
                pass  # Ignore invalid status
        
        # Order by most recent first
        query = query.order_by(Order.order_date.desc())
        
        # Pagination
        orders = query.offset(offset).limit(limit).all()
        
        return [
            OrderResponse(
                id=order.id,
                order_number=order.order_number,
                status=order.status.value,
                customer_name=order.customer_name,
                customer_phone=order.customer_phone,
                delivery_address=order.delivery_address,
                subtotal=order.subtotal,
                shipping_cost=order.shipping_cost,
                total_amount=order.total_amount,
                currency=order.currency,
                order_date=order.order_date,
                items=[
                    OrderItemResponse(
                        id=item.id,
                        product_name=item.product_name,
                        sku_code=item.sku_code,
                        size=item.size,
                        color=item.color,
                        unit_price=item.unit_price,
                        quantity=item.quantity,
                        total_price=item.total_price
                    )
                    for item in order.order_items
                ]
            )
            for order in orders
        ]
    finally:
        db.close()


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    order_id: int,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    """Get order details by ID"""
    # ✅ FIX: Use the user's market from token
    user_market = Market(current_user.market.value) if current_user.market else Market.KG
    from ..db.market_db import db_manager
    SessionLocal = db_manager.get_session_factory(user_market)
    db = SessionLocal()
    
    try:
        order = db.query(Order).options(
            joinedload(Order.order_items)
        ).filter(
            Order.id == order_id,
            Order.user_id == current_user.user_id
        ).first()
    
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status.value,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            delivery_address=order.delivery_address,
            subtotal=order.subtotal,
            shipping_cost=order.shipping_cost,
            total_amount=order.total_amount,
            currency=order.currency,
            order_date=order.order_date,
            items=[
                OrderItemResponse(
                    id=item.id,
                    product_name=item.product_name,
                    sku_code=item.sku_code,
                    size=item.size,
                    color=item.color,
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                    total_price=item.total_price
                )
                for item in order.order_items
            ]
        )
    finally:
        db.close()

