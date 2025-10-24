from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from .. import models
from ..db import get_db
from ..schemas.wishlist import (
    WishlistSchema, 
    WishlistItemSchema, 
    AddToWishlistRequest,
    RemoveFromWishlistRequest,
    GetWishlistRequest,
    ClearWishlistRequest
)
from ..schemas.product import ProductSchema

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

def get_wishlist_by_user_id(user_id: int, db: Session) -> WishlistSchema:
    """Helper function to get wishlist by user_id"""
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

@router.post("/get", response_model=WishlistSchema)
def get_wishlist(request: GetWishlistRequest, db: Session = Depends(get_db)):
    """Get wishlist for a specific user"""
    return get_wishlist_by_user_id(request.user_id, db)

@router.post("/add", response_model=WishlistSchema)
def add_to_wishlist(request: AddToWishlistRequest, db: Session = Depends(get_db)):
    """Add product to user's wishlist"""
    # Verify user exists
    user = db.query(models.users.user.User).filter(models.users.user.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify product exists
    product = db.query(models.products.product.Product).filter(models.products.product.Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get or create wishlist
    wishlist = db.query(models.users.wishlist.Wishlist).filter(models.users.wishlist.Wishlist.user_id == request.user_id).first()
    if not wishlist:
        wishlist = models.users.wishlist.Wishlist(user_id=request.user_id)
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

    return get_wishlist_by_user_id(request.user_id, db)

@router.post("/remove", response_model=WishlistSchema)
def remove_from_wishlist(request: RemoveFromWishlistRequest, db: Session = Depends(get_db)):
    """Remove product from user's wishlist"""
    wishlist = db.query(models.users.wishlist.Wishlist).filter(models.users.wishlist.Wishlist.user_id == request.user_id).first()
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    wishlist_item = db.query(models.users.wishlist.WishlistItem).filter(
        models.users.wishlist.WishlistItem.wishlist_id == wishlist.id,
        models.users.wishlist.WishlistItem.product_id == request.product_id
    ).first()

    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    db.delete(wishlist_item)
    db.commit()

    return get_wishlist_by_user_id(request.user_id, db)

@router.post("/clear", response_model=WishlistSchema)
def clear_wishlist(request: ClearWishlistRequest, db: Session = Depends(get_db)):
    """Clear all items from user's wishlist"""
    wishlist = db.query(models.users.wishlist.Wishlist).filter(models.users.wishlist.Wishlist.user_id == request.user_id).first()
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    # Delete all wishlist items
    db.query(models.users.wishlist.WishlistItem).filter(
        models.users.wishlist.WishlistItem.wishlist_id == wishlist.id
    ).delete()
    db.commit()

    return get_wishlist_by_user_id(request.user_id, db)

# Legacy endpoints for backward compatibility (deprecated)
@router.get("/", response_model=WishlistSchema)
def get_wishlist_legacy(db: Session = Depends(get_db)):
    """Legacy endpoint - requires user_id in request body"""
    raise HTTPException(status_code=400, detail="Use POST /wishlist/get with user_id in request body")

@router.post("/items", response_model=WishlistSchema)
def add_to_wishlist_legacy(request: AddToWishlistRequest, db: Session = Depends(get_db)):
    """Legacy endpoint - redirects to new endpoint"""
    return add_to_wishlist(request, db)

@router.get("/items", response_model=WishlistSchema)
def get_wishlist_items_legacy(db: Session = Depends(get_db)):
    """Legacy endpoint - requires user_id in request body"""
    raise HTTPException(status_code=400, detail="Use POST /wishlist/get with user_id in request body")

@router.delete("/items/{product_id}", response_model=WishlistSchema)
def remove_from_wishlist_legacy(product_id: int, db: Session = Depends(get_db)):
    """Legacy endpoint - requires user_id in request body"""
    raise HTTPException(status_code=400, detail="Use POST /wishlist/remove with user_id and product_id in request body")

@router.delete("/", response_model=WishlistSchema)
def clear_wishlist_legacy(db: Session = Depends(get_db)):
    """Legacy endpoint - requires user_id in request body"""
    raise HTTPException(status_code=400, detail="Use POST /wishlist/clear with user_id in request body")
