from typing import Optional, List
from starlette.requests import Request
from PIL import Image
import io
import logging
from wtforms import FileField, MultipleFileField
from wtforms.validators import Optional as OptionalValidator

from ..utils.image_upload import image_uploader
from ..db.market_db import db_manager

# Setup logging
logger = logging.getLogger(__name__)

class ImageUploadMixin:
    """
    A mixin for SQLAdmin ModelViews to handle Pillow-based image uploads.

    To use this mixin:
    1. Inherit from it in your ModelView:
       `class MyAdmin(ImageUploadMixin, ModelView, model=MyModel):`

    2. Define the fields to be handled:
       `image_fields: List[str] = ["image_url"]`
       `multiple_image_fields: List[str] = ["gallery_images"]`

    3. Add `FileField` and `MultipleFileField` to `form_extra_fields`.

    4. The mixin's `insert_model` and `update_model` will automatically
       process and save the images.
    """
    image_fields: List[str] = []
    multiple_image_fields: List[str] = []

    async def scaffold_form(self) -> type:
        """
        Forcefully add FileField widgets to the form.
        This is a workaround for environments where `form_extra_fields` fails.
        """
        Form = await super().scaffold_form()
        
        # Add single image upload fields
        for field_name in self.image_fields:
            setattr(Form, field_name, FileField(
                label=self.column_labels.get(field_name, field_name.replace("_", " ").title()),
                validators=[OptionalValidator()],
                description=getattr(self, 'column_descriptions', {}).get(field_name, "")
            ))

        # Add multiple image upload fields
        for field_name in self.multiple_image_fields:
            setattr(Form, field_name, MultipleFileField(
                label=self.column_labels.get(field_name, field_name.replace("_", " ").title()),
                validators=[OptionalValidator()],
                description=getattr(self, 'column_descriptions', {}).get(field_name, "")
            ))
            
        return Form

    async def _save_image(self, file_data, model_name: str) -> Optional[str]:
        """Generic method to save an uploaded image using Pillow."""
        if not (file_data and hasattr(file_data, 'filename') and file_data.filename):
            return None

        try:
            file_bytes = await file_data.read()
            # Validate with Pillow
            try:
                img = Image.open(io.BytesIO(file_bytes))
                img.verify()
                logger.info(f"✅ Valid image uploaded: {file_data.filename} ({img.format}, {img.size})")
            except Exception as e:
                logger.error(f"❌ Invalid image file: {file_data.filename}. Error: {e}")
                return None
            
            await file_data.seek(0)
            
            from fastapi import UploadFile
            upload_file = UploadFile(filename=file_data.filename, file=io.BytesIO(file_bytes))

            # Use the central image uploader utility
            url = await image_uploader.save_image(
                file=upload_file,
                category=model_name.lower(),
                resize_to="medium",
                optimize=True
            )
            logger.info(f"✅ Image saved successfully: {url}")
            return url
        except Exception as e:
            logger.error(f"❌ Critical error saving image '{file_data.filename}': {e}")
            return None

    async def on_model_change(self, data: dict, model: any, is_created: bool, request: Request) -> None:
        """
        Overridden to handle image uploads after model is saved.
        This is safer than insert_model/update_model as it guarantees an ID exists.
        """
        db_session = self.session_maker()
        
        # Process single image fields
        for field in self.image_fields:
            file_data = getattr(request, f"_image_{field}", None)
            if file_data:
                url = await self._save_image(file_data, model.__class__.__name__)
                if url:
                    setattr(model, field, url)

        # Process multiple image fields
        for field in self.multiple_image_fields:
            files_data = getattr(request, f"_images_{field}", None)
            if files_data:
                new_urls = []
                for file_data in files_data:
                    url = await self._save_image(file_data, model.__class__.__name__)
                    if url:
                        new_urls.append(url)
                
                if new_urls:
                    # For updates, append to existing images
                    if not is_created and hasattr(model, field) and getattr(model, field):
                        existing_urls = getattr(model, field)
                        setattr(model, field, existing_urls + new_urls)
                    else:
                        setattr(model, field, new_urls)
        
        try:
            db_session.add(model)
            db_session.commit()
        except Exception as e:
            logger.error(f"Error saving model after image upload: {e}")
            db_session.rollback()
        finally:
            db_session.close()

    async def insert_model(self, request: Request, data: dict) -> any:
        # Temporarily store file data on the request object
        for field in self.image_fields:
            setattr(request, f"_image_{field}", data.pop(field, None))
        for field in self.multiple_image_fields:
            setattr(request, f"_images_{field}", data.pop(field, None))
        
        return await super().insert_model(request, data)

    async def update_model(self, request: Request, pk: str, data: dict) -> any:
        # Temporarily store file data on the request object
        for field in self.image_fields:
            setattr(request, f"_image_{field}", data.pop(field, None))
        for field in self.multiple_image_fields:
            setattr(request, f"_images_{field}", data.pop(field, None))
            
        return await super().update_model(request, pk, data)
