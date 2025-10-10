"""
Image Upload Router

API endpoints for uploading and managing images.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, List
from pydantic import BaseModel
from ..utils.image_upload import image_uploader
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ImageUploadResponse(BaseModel):
    """Response model for successful image upload"""
    success: bool
    url: str
    message: str
    size: Optional[str] = None


class MultiSizeUploadResponse(BaseModel):
    """Response model for multi-size upload"""
    success: bool
    urls: dict[str, str]
    message: str


@router.post("/upload/image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    category: str = Form(..., description="Image category: categories, subcategories, products, brands, banners"),
    resize_to: Optional[str] = Form("medium", description="Size preset: thumbnail, small, medium, large, or null for original"),
    optimize: bool = Form(True)
):
    """
    Upload a single image
    
    **Category options:**
    - `categories` - Category icons/images
    - `subcategories` - Subcategory icons/images
    - `products` - Product images
    - `brands` - Brand logos
    - `banners` - Homepage banners
    
    **Size presets:**
    - `thumbnail` - 100x100px (small icons)
    - `small` - 200x200px (category/subcategory icons)
    - `medium` - 500x500px (product images)
    - `large` - 1200x1200px (full-size images)
    - `null` - Keep original size
    
    **Returns:**
    - `url`: Direct URL to access the uploaded image
    """
    try:
        # Validate category
        allowed_categories = ["categories", "subcategories", "products", "brands", "banners"]
        if category not in allowed_categories:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Allowed: {', '.join(allowed_categories)}"
            )
        
        # Upload and save
        url = await image_uploader.save_image(
            file=file,
            category=category,
            resize_to=resize_to if resize_to != "null" else None,
            optimize=optimize
        )
        
        logger.info(f"✅ Image uploaded successfully: {url}")
        
        return ImageUploadResponse(
            success=True,
            url=url,
            message="Image uploaded successfully",
            size=resize_to if resize_to != "null" else "original"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Image upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload/image/multi-size", response_model=MultiSizeUploadResponse)
async def upload_image_multi_size(
    file: UploadFile = File(...),
    category: str = Form(...),
    sizes: str = Form("small,medium,large", description="Comma-separated size presets")
):
    """
    Upload image in multiple sizes
    
    Generates multiple variants of the same image in different sizes.
    Useful for responsive images and performance optimization.
    
    **Example:**
    ```
    sizes = "thumbnail,small,medium"
    ```
    
    **Returns:**
    Dictionary with size names as keys and URLs as values.
    """
    try:
        # Validate category
        allowed_categories = ["categories", "subcategories", "products", "brands", "banners"]
        if category not in allowed_categories:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Allowed: {', '.join(allowed_categories)}"
            )
        
        # Parse sizes
        size_list = [s.strip() for s in sizes.split(",") if s.strip()]
        
        # Upload and save multiple sizes
        urls = await image_uploader.save_multiple_sizes(
            file=file,
            category=category,
            sizes=size_list
        )
        
        logger.info(f"✅ Multi-size image uploaded: {len(urls)} variants")
        
        return MultiSizeUploadResponse(
            success=True,
            urls=urls,
            message=f"Image uploaded in {len(urls)} sizes"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Multi-size upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.delete("/upload/image")
async def delete_image(url: str):
    """
    Delete an uploaded image
    
    **Args:**
    - `url`: Image URL (e.g., /uploads/categories/abc123.jpg)
    
    **Returns:**
    Success message if deleted, error if not found.
    """
    try:
        deleted = image_uploader.delete_image(url)
        
        if deleted:
            return {"success": True, "message": "Image deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Image deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

