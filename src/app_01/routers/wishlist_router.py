from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from .. import models
from ..db import get_db
from ..schemas.wishlist import WishlistSchema, WishlistItemSchema, AddToWishlistRequest
from ..schemas.product import ProductSchema
from .auth_router import get_current_user_from_token
from ..schemas.auth import VerifyTokenResponse

router = APIRouter(prefix="/wishlist", tags=["wishlist"])

def build_product_schema(product):
    """Build ProductSchema from Product model"""
    # Get images
    images = []
    if product.main_image:
        images.append(product.main_image)
    if product.additional_images and isinstance(product.additional_images, list):
        images.extend(product.additional_images)
    if not images and product.assets:
        images = [asset.url for asset in product.assets if asset.type == 'image']
    
    # Get SKUs for sizes/colors
    skus = product.skus if product.skus else []
    
    return ProductSchema(
        id=str(product.id),
        name=product.title,
        slug=product.slug or "",
        brand=product.brand.name if product.brand else "",
        price=product.display_price,
        originalPrice=product.original_price,
        discount=product.discount_percentage,
        image=images[0] if images else "",
        images=images,
        category=product.category.name if product.category else "",
        subcategory=product.subcategory.name if product.subcategory else "",
        sizes=list(set(s.size for s in skus if s.size)),
        colors=list(set(s.color for s in skus if s.color)),
        rating=product.rating_avg or 0,
        reviews=product.rating_count or 0,
        salesCount=product.sold_count or 0,
        inStock=product.is_in_stock,
        description=product.description or "",
        features=[]
    )

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
        # Load product with relationships
        product = db.query(models.products.product.Product).options(
            joinedload(models.products.product.Product.brand),
            joinedload(models.products.product.Product.category),
            joinedload(models.products.product.Product.subcategory),
            joinedload(models.products.product.Product.skus),
            joinedload(models.products.product.Product.assets)
        ).filter(models.products.product.Product.id == item.product_id).first()
        
        if product:
            product_schema = build_product_schema(product)
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

@router.get("/items", response_model=WishlistSchema)
def get_wishlist_items(db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    """Get wishlist items (alias for get_wishlist)"""
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

@router.delete("/", response_model=WishlistSchema)
def clear_wishlist(db: Session = Depends(get_db), current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    """Clear all items from wishlist"""
    user_id = current_user.user_id
    wishlist = db.query(models.users.wishlist.Wishlist).filter(models.users.wishlist.Wishlist.user_id == user_id).first()
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    # Delete all wishlist items
    db.query(models.users.wishlist.WishlistItem).filter(
        models.users.wishlist.WishlistItem.wishlist_id == wishlist.id
    ).delete()
    db.commit()

    return get_wishlist(db, current_user)
