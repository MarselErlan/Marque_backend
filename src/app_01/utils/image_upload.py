"""
Image Upload Utility

Handles image uploads, validation, processing, and storage.
"""

import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import io
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)


class ImageUploader:
    """
    Handle image uploads with validation and processing
    
    Features:
    - Image validation (format, size)
    - Automatic resizing/optimization
    - Thumbnail generation
    - Multiple size variants
    """
    
    # Supported image formats
    ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    
    # Size limits (in bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Image size presets
    SIZES = {
        "thumbnail": (100, 100),    # Small icons
        "small": (200, 200),        # Category/subcategory icons
        "medium": (500, 500),       # Product images
        "large": (1200, 1200)       # Full-size product images
    }
    
    def __init__(self, upload_dir: str = "static/uploads"):
        """
        Initialize uploader
        
        Args:
            upload_dir: Base directory for uploads (relative to project root)
        """
        self.upload_dir = Path(upload_dir)
        self._ensure_upload_dirs()
    
    def _ensure_upload_dirs(self):
        """Create upload directory structure if it doesn't exist"""
        directories = [
            self.upload_dir,
            self.upload_dir / "categories",
            self.upload_dir / "subcategories",
            self.upload_dir / "products",
            self.upload_dir / "brands",
            self.upload_dir / "banners"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Ensured directory exists: {directory}")
    
    async def validate_image(self, file: UploadFile) -> Tuple[bool, str]:
        """
        Validate uploaded image file
        
        Args:
            file: Uploaded file from FastAPI
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        file_ext = Path(file.filename or "").suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"Недопустимый формат файла. Разрешены: {', '.join(self.ALLOWED_EXTENSIONS)}"
        
        # Read file content
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Check file size
        if len(content) > self.MAX_FILE_SIZE:
            size_mb = len(content) / (1024 * 1024)
            return False, f"Файл слишком большой ({size_mb:.1f}MB). Максимум: 10MB"
        
        # Try to open as image
        try:
            image = Image.open(io.BytesIO(content))
            image.verify()
            
            # Check if format is supported
            if image.format not in self.ALLOWED_FORMATS:
                return False, f"Недопустимый формат изображения. Разрешены: {', '.join(self.ALLOWED_FORMATS)}"
            
            return True, ""
        
        except Exception as e:
            return False, f"Не удалось обработать изображение: {str(e)}"
    
    async def save_image(
        self,
        file: UploadFile,
        category: str,
        resize_to: Optional[str] = "medium",
        optimize: bool = True
    ) -> str:
        """
        Save uploaded image with processing
        
        Args:
            file: Uploaded file
            category: Image category (categories, products, etc.)
            resize_to: Size preset to resize to (or None to keep original)
            optimize: Whether to optimize the image
            
        Returns:
            Relative URL path to saved image
            
        Raises:
            HTTPException: If validation or save fails
        """
        # Validate image
        is_valid, error_msg = await self.validate_image(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Generate unique filename
        file_ext = Path(file.filename or "image.jpg").suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Determine save path
        save_dir = self.upload_dir / category
        save_path = save_dir / unique_filename
        
        # Read and process image
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        
        # Convert RGBA to RGB if saving as JPEG
        if image.mode == "RGBA" and file_ext in [".jpg", ".jpeg"]:
            # Create white background
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # Use alpha channel as mask
            image = background
        
        # Resize if requested
        if resize_to and resize_to in self.SIZES:
            target_size = self.SIZES[resize_to]
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            logger.info(f"📐 Resized image to {resize_to}: {target_size}")
        
        # Save image
        save_kwargs = {"quality": 85} if optimize else {}
        if file_ext in [".jpg", ".jpeg"]:
            save_kwargs["optimize"] = optimize
        
        image.save(save_path, **save_kwargs)
        logger.info(f"✅ Saved image: {save_path}")
        
        # Return relative URL (without 'static/' prefix for serving)
        relative_url = f"/uploads/{category}/{unique_filename}"
        return relative_url
    
    async def save_multiple_sizes(
        self,
        file: UploadFile,
        category: str,
        sizes: list[str] = ["small", "medium", "large"]
    ) -> dict[str, str]:
        """
        Save image in multiple sizes
        
        Args:
            file: Uploaded file
            category: Image category
            sizes: List of size presets to generate
            
        Returns:
            Dictionary mapping size name to URL
        """
        # Validate once
        is_valid, error_msg = await self.validate_image(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Read image
        content = await file.read()
        base_image = Image.open(io.BytesIO(content))
        
        # Convert RGBA to RGB if needed
        if base_image.mode == "RGBA":
            background = Image.new("RGB", base_image.size, (255, 255, 255))
            background.paste(base_image, mask=base_image.split()[3])
            base_image = background
        
        # Generate filename base
        file_ext = Path(file.filename or "image.jpg").suffix.lower()
        base_name = str(uuid.uuid4())
        
        save_dir = self.upload_dir / category
        
        result = {}
        
        for size_name in sizes:
            if size_name not in self.SIZES:
                continue
            
            # Create copy for this size
            image = base_image.copy()
            
            # Resize
            target_size = self.SIZES[size_name]
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Save
            filename = f"{base_name}_{size_name}{file_ext}"
            save_path = save_dir / filename
            image.save(save_path, quality=85, optimize=True)
            
            # Store URL
            result[size_name] = f"/uploads/{category}/{filename}"
            logger.info(f"✅ Saved {size_name} variant: {save_path}")
        
        return result
    
    def delete_image(self, url: str) -> bool:
        """
        Delete image by URL
        
        Args:
            url: Image URL (e.g., /uploads/categories/abc123.jpg)
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Convert URL to file path
            # URL format: /uploads/category/filename.ext
            if url.startswith("/uploads/"):
                relative_path = url.replace("/uploads/", "")
                file_path = self.upload_dir / relative_path
                
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"🗑️ Deleted image: {file_path}")
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"❌ Error deleting image {url}: {e}")
            return False


# Global uploader instance
image_uploader = ImageUploader()

