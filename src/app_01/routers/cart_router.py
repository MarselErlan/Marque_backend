from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models
from ..db import get_db
from ..schemas.cart import CartSchema, CartItemSchema, AddToCartRequest
from ..services.auth_service import get_current_user_from_token
from ..schemas.auth import VerifyTokenResponse

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("/", response_model=CartSchema)
def get_cart(db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    user_id = current_user.user_id
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

@router.post("/items", response_model=CartSchema)
def add_to_cart(request: AddToCartRequest, db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    user_id = current_user.user_id
    cart = db.query(models.orders.cart.Cart).filter(models.orders.cart.Cart.user_id == user_id).first()
    if not cart:
        cart = models.orders.cart.Cart(user_id=user_id)
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
    
    return get_cart(db, current_user)

@router.put("/items/{item_id}", response_model=CartSchema)
def update_cart_item(item_id: int, quantity: int, db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    user_id = current_user.user_id
    cart = db.query(models.orders.cart.Cart).filter(models.orders.cart.Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart_item = db.query(models.orders.cart.CartItem).filter(
        models.orders.cart.CartItem.id == item_id,
        models.orders.cart.CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    cart_item.quantity = quantity
    db.commit()

    return get_cart(db, current_user)

@router.delete("/items/{item_id}", response_model=CartSchema)
def remove_from_cart(item_id: int, db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    user_id = current_user.user_id
    cart = db.query(models.orders.cart.Cart).filter(models.orders.cart.Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart_item = db.query(models.orders.cart.CartItem).filter(
        models.orders.cart.CartItem.id == item_id,
        models.orders.cart.CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()

    return get_cart(db, current_user)
