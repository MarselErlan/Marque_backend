from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models
from ..db import get_db
from ..schemas.wishlist import WishlistSchema, WishlistItemSchema, AddToWishlistRequest
from ..services.auth_service import get_current_user_from_token
from ..schemas.auth import VerifyTokenResponse
from ..routers.product_router import get_product

router = APIRouter(prefix="/wishlist", tags=["wishlist"])

@router.get("/", response_model=WishlistSchema)
def get_wishlist(db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    user_id = current_user.user_id
    wishlist = db.query(models.users.wishlist.Wishlist).filter(models.users.wishlist.Wishlist.user_id == user_id).first()
    if not wishlist:
        wishlist = models.users.wishlist.Wishlist(user_id=user_id)
        db.add(wishlist)
        db.commit()
        db.refresh(wishlist)

    wishlist_items = []
    for item in wishlist.items:
        product_schema = get_product(item.product_id, db)
        wishlist_items.append(WishlistItemSchema(id=item.id, product=product_schema))

    return WishlistSchema(
        id=wishlist.id,
        user_id=wishlist.user_id,
        items=wishlist_items
    )

@router.post("/items", response_model=WishlistSchema)
def add_to_wishlist(request: AddToWishlistRequest, db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    user_id = current_user.user_id
    wishlist = db.query(models.users.wishlist.Wishlist).filter(models.users.wishlist.Wishlist.user_id == user_id).first()
    if not wishlist:
        wishlist = models.users.wishlist.Wishlist(user_id=user_id)
        db.add(wishlist)
        db.commit()
        db.refresh(wishlist)

    # Check if item already in wishlist
    wishlist_item = db.query(models.users.wishlist.WishlistItem).filter(
        models.users.wishlist.WishlistItem.wishlist_id == wishlist.id,
        models.users.wishlist.WishlistItem.product_id == request.product_id
    ).first()

    if not wishlist_item:
        wishlist_item = models.users.wishlist.WishlistItem(wishlist_id=wishlist.id, product_id=request.product_id)
        db.add(wishlist_item)
        db.commit()

    return get_wishlist(db, current_user)

@router.delete("/items/{product_id}", response_model=WishlistSchema)
def remove_from_wishlist(product_id: int, db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    user_id = current_user.user_id
    wishlist = db.query(models.users.wishlist.Wishlist).filter(models.users.wishlist.Wishlist.user_id == user_id).first()
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    wishlist_item = db.query(models.users.wishlist.WishlistItem).filter(
        models.users.wishlist.WishlistItem.wishlist_id == wishlist.id,
        models.users.wishlist.WishlistItem.product_id == product_id
    ).first()

    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    db.delete(wishlist_item)
    db.commit()

    return get_wishlist(db, current_user)
