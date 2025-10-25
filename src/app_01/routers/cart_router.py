from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models
from ..db import get_db
from ..schemas.cart import (
    CartSchema, 
    CartItemSchema, 
    AddToCartRequest,
    GetCartRequest,
    RemoveFromCartRequest,
    UpdateCartItemRequest,
    ClearCartRequest
)
from .auth_router import get_current_user_from_token
from ..schemas.auth import VerifyTokenResponse
from ..models.users.user import User

router = APIRouter(prefix="/cart", tags=["cart"])

def get_cart_by_user_id(user_id: int, db: Session) -> CartSchema:
    """Helper function to get cart by user_id"""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    cart = db.query(models.orders.cart.Cart).filter(models.orders.cart.Cart.user_id == user_id).first()
    if not cart:
        # Create a cart if it doesn't exist
        cart = models.orders.cart.Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    cart_items = []
    total_price = 0
    for item in cart.items:
        product = item.sku.product
        cart_items.append(CartItemSchema(
            id=item.id,
            sku_id=item.sku_id,
            quantity=item.quantity,
            name=product.title,
            price=item.sku.price,
            image=product.main_image.url if product.main_image else ""
        ))
        total_price += item.sku.price * item.quantity

    return CartSchema(
        id=cart.id,
        user_id=cart.user_id,
        items=cart_items,
        total_items=len(cart_items),
        total_price=total_price
    )

# ==================== New Stateless Endpoints ====================

@router.post("/get", response_model=CartSchema)
def get_cart_stateless(request: GetCartRequest, db: Session = Depends(get_db)):
    """Get cart for specific user (stateless)"""
    return get_cart_by_user_id(request.user_id, db)

@router.post("/add", response_model=CartSchema)
def add_to_cart_stateless(request: AddToCartRequest, db: Session = Depends(get_db)):
    """Add to cart (stateless)"""
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    cart = db.query(models.orders.cart.Cart).filter(models.orders.cart.Cart.user_id == request.user_id).first()
    if not cart:
        cart = models.orders.cart.Cart(user_id=request.user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    # Check if item already in cart
    cart_item = db.query(models.orders.cart.CartItem).filter(
        models.orders.cart.CartItem.cart_id == cart.id,
        models.orders.cart.CartItem.sku_id == request.sku_id
    ).first()

    if cart_item:
        cart_item.quantity += request.quantity
    else:
        cart_item = models.orders.cart.CartItem(cart_id=cart.id, sku_id=request.sku_id, quantity=request.quantity)
        db.add(cart_item)

    db.commit()
    
    return get_cart_by_user_id(request.user_id, db)

@router.post("/update", response_model=CartSchema)
def update_cart_item_stateless(request: UpdateCartItemRequest, db: Session = Depends(get_db)):
    """Update cart item quantity (stateless)"""
    cart = db.query(models.orders.cart.Cart).filter(models.orders.cart.Cart.user_id == request.user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart_item = db.query(models.orders.cart.CartItem).filter(
        models.orders.cart.CartItem.id == request.cart_item_id,
        models.orders.cart.CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    cart_item.quantity = request.quantity
    db.commit()

    return get_cart_by_user_id(request.user_id, db)

@router.post("/remove", response_model=CartSchema)
def remove_from_cart_stateless(request: RemoveFromCartRequest, db: Session = Depends(get_db)):
    """Remove item from cart (stateless)"""
    cart = db.query(models.orders.cart.Cart).filter(models.orders.cart.Cart.user_id == request.user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart_item = db.query(models.orders.cart.CartItem).filter(
        models.orders.cart.CartItem.id == request.cart_item_id,
        models.orders.cart.CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()

    return get_cart_by_user_id(request.user_id, db)

@router.post("/clear", response_model=CartSchema)
def clear_cart_stateless(request: ClearCartRequest, db: Session = Depends(get_db)):
    """Clear all items from cart (stateless)"""
    cart = db.query(models.orders.cart.Cart).filter(models.orders.cart.Cart.user_id == request.user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    # Delete all cart items
    db.query(models.orders.cart.CartItem).filter(
        models.orders.cart.CartItem.cart_id == cart.id
    ).delete()
    db.commit()

    return get_cart_by_user_id(request.user_id, db)

# ==================== Legacy JWT Endpoints (for backward compatibility) ====================

@router.get("/", response_model=CartSchema)
def get_cart(db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    """Legacy JWT-based get cart"""
    return get_cart_by_user_id(current_user.user_id, db)

@router.post("/items", response_model=CartSchema)
def add_to_cart(request: AddToCartRequest, db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    """Legacy JWT-based add to cart - redirects to stateless endpoint"""
    request.user_id = current_user.user_id
    return add_to_cart_stateless(request, db)

@router.put("/items/{item_id}", response_model=CartSchema)
def update_cart_item(item_id: int, quantity: int, db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    """Legacy JWT-based update cart item"""
    request = UpdateCartItemRequest(
        user_id=current_user.user_id,
        cart_item_id=item_id,
        quantity=quantity
    )
    return update_cart_item_stateless(request, db)

@router.get("/items", response_model=CartSchema)
def get_cart_items(db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    """Legacy JWT-based get cart items (alias for get_cart)"""
    return get_cart_by_user_id(current_user.user_id, db)

@router.delete("/items/{item_id}", response_model=CartSchema)
def remove_from_cart(item_id: int, db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    """Legacy JWT-based remove from cart"""
    request = RemoveFromCartRequest(
        user_id=current_user.user_id,
        cart_item_id=item_id
    )
    return remove_from_cart_stateless(request, db)

@router.delete("/", response_model=CartSchema)
def clear_cart(db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    """Legacy JWT-based clear cart"""
    request = ClearCartRequest(user_id=current_user.user_id)
    return clear_cart_stateless(request, db)
