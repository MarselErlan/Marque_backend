"""
Product Asset Router

API endpoints for managing product images and videos with advanced features:
- Upload product images/videos
- Set primary image
- Manage image dimensions and file sizes
- Get product media gallery
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..db import get_db
from ..models.products.product_asset import ProductAsset
from ..models.products.product import Product
from ..utils.image_upload import image_uploader
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/product-assets", tags=["Product Assets"])


# ========================
# PYDANTIC SCHEMAS
# ========================

class ProductAssetResponse(BaseModel):
    """Product asset response model"""
    id: int
    product_id: int
    url: str
    type: str
    alt_text: Optional[str] = None
    order: int
    is_primary: bool
    is_active: bool
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    file_size_mb: Optional[float] = None
    aspect_ratio: Optional[float] = None
    is_landscape: Optional[bool] = None
    is_portrait: Optional[bool] = None
    
    class Config:
        from_attributes = True


class ProductGalleryResponse(BaseModel):
    """Product gallery with all media"""
    product_id: int
    product_name: str
    primary_image: Optional[ProductAssetResponse] = None
    all_images: List[ProductAssetResponse] = []
    videos: List[ProductAssetResponse] = []
    total_assets: int


class UploadProductAssetRequest(BaseModel):
    """Upload product asset request"""
    product_id: int
    alt_text: Optional[str] = None
    order: int = 0
    is_primary: bool = False


class UpdateProductAssetRequest(BaseModel):
    """Update product asset request"""
    alt_text: Optional[str] = None
    order: Optional[int] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


# ========================
# API ENDPOINTS
# ========================

@router.post("/upload", response_model=ProductAssetResponse)
async def upload_product_asset(
    file: UploadFile = File(...),
    product_id: int = Form(...),
    asset_type: str = Form("image", description="Asset type: image or video"),
    alt_text: Optional[str] = Form(None),
    order: int = Form(0),
    is_primary: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Upload a product image or video
    
    **Features:**
    - Automatically extracts image dimensions
    - Tracks file size
    - Can set as primary image
    - Supports alt text for SEO
    - Customizable display order
    
    **Args:**
    - `file`: Image or video file
    - `product_id`: Product ID
    - `asset_type`: "image" or "video"
    - `alt_text`: Alternative text for accessibility/SEO
    - `order`: Display order (0 = first)
    - `is_primary`: Set as primary product image
    """
    try:
        # Verify product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Upload file
        url = await image_uploader.save_image(
            file=file,
            category="products",
            resize_to="large",
            optimize=True
        )
        
        # Get file info
        content = await file.read()
        file_size = len(content)
        
        # Extract dimensions if image
        width = None
        height = None
        if asset_type == "image":
            try:
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(content))
                width, height = img.size
            except Exception as e:
                logger.warning(f"Could not extract image dimensions: {e}")
        
        # Create asset record
        asset = ProductAsset(
            product_id=product_id,
            url=url,
            type=asset_type,
            alt_text=alt_text or f"{product.title} - {asset_type}",
            order=order,
            is_primary=is_primary,
            is_active=True,
            width=width,
            height=height,
            file_size=file_size
        )
        
        db.add(asset)
        
        # If setting as primary, unset others
        if is_primary:
            db.query(ProductAsset).filter(
                ProductAsset.product_id == product_id,
                ProductAsset.id != asset.id
            ).update({"is_primary": False})
        
        db.commit()
        db.refresh(asset)
        
        logger.info(f"✅ Uploaded {asset_type} for product {product_id}: {url}")
        
        return ProductAssetResponse(
            id=asset.id,
            product_id=asset.product_id,
            url=asset.url,
            type=asset.type,
            alt_text=asset.alt_text,
            order=asset.order,
            is_primary=asset.is_primary,
            is_active=asset.is_active,
            width=asset.width,
            height=asset.height,
            file_size=asset.file_size,
            file_size_mb=asset.file_size_mb,
            aspect_ratio=asset.aspect_ratio,
            is_landscape=asset.is_landscape,
            is_portrait=asset.is_portrait
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to upload product asset: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/product/{product_id}/gallery", response_model=ProductGalleryResponse)
def get_product_gallery(
    product_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get complete product gallery
    
    **Returns:**
    - Primary image
    - All images (sorted by order)
    - All videos
    - Total asset count
    
    **Args:**
    - `product_id`: Product ID
    - `include_inactive`: Include deactivated assets
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get primary image
    primary_image = ProductAsset.get_primary_image(db, product_id)
    
    # Get all images
    query = db.query(ProductAsset).filter(
        ProductAsset.product_id == product_id,
        ProductAsset.type == 'image'
    )
    if not include_inactive:
        query = query.filter(ProductAsset.is_active == True)
    all_images = query.order_by(ProductAsset.order, ProductAsset.created_at).all()
    
    # Get all videos
    query = db.query(ProductAsset).filter(
        ProductAsset.product_id == product_id,
        ProductAsset.type == 'video'
    )
    if not include_inactive:
        query = query.filter(ProductAsset.is_active == True)
    videos = query.order_by(ProductAsset.order, ProductAsset.created_at).all()
    
    return ProductGalleryResponse(
        product_id=product_id,
        product_name=product.title,
        primary_image=ProductAssetResponse.model_validate(primary_image) if primary_image else None,
        all_images=[ProductAssetResponse.model_validate(img) for img in all_images],
        videos=[ProductAssetResponse.model_validate(vid) for vid in videos],
        total_assets=len(all_images) + len(videos)
    )


@router.patch("/{asset_id}/set-primary")
def set_primary_image(
    asset_id: int,
    db: Session = Depends(get_db)
):
    """
    Set an asset as the primary product image
    
    Automatically unsets other primary images for the same product.
    
    **Args:**
    - `asset_id`: Asset ID to set as primary
    """
    asset = db.query(ProductAsset).filter(ProductAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Check if asset is an image
    if asset.type.lower() != 'image':
        raise HTTPException(status_code=400, detail="Only images can be set as primary")
    
    # Set as primary (this method handles unsetting others and commits)
    asset.set_as_primary(db)
    db.refresh(asset)  # Refresh to ensure state is current
    
    return {
        "success": True,
        "message": f"Asset {asset_id} set as primary for product {asset.product_id}"
    }


@router.patch("/{asset_id}", response_model=ProductAssetResponse)
def update_product_asset(
    asset_id: int,
    update_data: UpdateProductAssetRequest,
    db: Session = Depends(get_db)
):
    """
    Update product asset details
    
    **Can update:**
    - Alt text
    - Display order
    - Primary status
    - Active status
    
    **Args:**
    - `asset_id`: Asset ID
    - Update fields (all optional)
    """
    asset = db.query(ProductAsset).filter(ProductAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Update fields if provided
    if update_data.alt_text is not None:
        asset.alt_text = update_data.alt_text
    if update_data.order is not None:
        asset.order = update_data.order
    if update_data.is_active is not None:
        asset.is_active = update_data.is_active
    
    # Handle primary status
    if update_data.is_primary is not None and update_data.is_primary:
        if asset.type == 'image':
            asset.set_as_primary(db)
        else:
            raise HTTPException(status_code=400, detail="Only images can be set as primary")
    
    db.commit()
    db.refresh(asset)
    
    return ProductAssetResponse.model_validate(asset)


@router.delete("/{asset_id}")
def delete_product_asset(
    asset_id: int,
    hard_delete: bool = False,
    db: Session = Depends(get_db)
):
    """
    Delete or deactivate a product asset
    
    **Two modes:**
    - `hard_delete=False` (default): Soft delete (deactivate, can be restored)
    - `hard_delete=True`: Permanently delete from database and filesystem
    
    **Args:**
    - `asset_id`: Asset ID
    - `hard_delete`: Permanent deletion (default: False)
    """
    asset = db.query(ProductAsset).filter(ProductAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    if hard_delete:
        # Delete file from filesystem
        try:
            image_uploader.delete_image(asset.url)
        except Exception as e:
            logger.warning(f"Could not delete file {asset.url}: {e}")
        
        # Delete from database
        db.delete(asset)
        db.commit()
        db.flush()  # Ensure deletion is processed
        
        return {
            "success": True,
            "message": f"Asset {asset_id} permanently deleted"
        }
    else:
        # Soft delete (deactivate)
        asset.is_active = False
        db.commit()
        db.refresh(asset)  # Refresh to ensure state is current
        
        return {
            "success": True,
            "message": f"Asset {asset_id} deactivated (can be restored)"
        }


@router.post("/{asset_id}/restore")
def restore_product_asset(
    asset_id: int,
    db: Session = Depends(get_db)
):
    """
    Restore a deactivated product asset
    
    **Args:**
    - `asset_id`: Asset ID to restore
    """
    asset = db.query(ProductAsset).filter(ProductAsset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset.is_active = True
    db.commit()
    db.refresh(asset)  # Refresh to ensure state is current
    
    return {
        "success": True,
        "message": f"Asset {asset_id} restored"
    }


@router.get("/stats")
def get_asset_stats(db: Session = Depends(get_db)):
    """
    Get statistics about product assets
    
    **Returns:**
    - Total images
    - Total videos
    - Total file size
    - Average file size
    - Largest images
    """
    from sqlalchemy import func
    
    total_images = db.query(func.count(ProductAsset.id)).filter(
        ProductAsset.type == 'image',
        ProductAsset.is_active == True
    ).scalar()
    
    total_videos = db.query(func.count(ProductAsset.id)).filter(
        ProductAsset.type == 'video',
        ProductAsset.is_active == True
    ).scalar()
    
    total_size = db.query(func.sum(ProductAsset.file_size)).filter(
        ProductAsset.is_active == True
    ).scalar() or 0
    
    avg_size = db.query(func.avg(ProductAsset.file_size)).filter(
        ProductAsset.is_active == True,
        ProductAsset.file_size.isnot(None)
    ).scalar() or 0
    
    return {
        "total_images": total_images,
        "total_videos": total_videos,
        "total_assets": total_images + total_videos,
        "total_file_size_bytes": total_size,
        "total_file_size_mb": round(total_size / (1024 * 1024), 2),
        "average_file_size_bytes": round(avg_size, 2),
        "average_file_size_mb": round(avg_size / (1024 * 1024), 2)
    }

