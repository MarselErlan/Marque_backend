"""
Custom SQLAdmin Widgets

Custom form widgets for enhanced admin functionality.
"""

from wtforms import StringField
from wtforms.widgets import TextInput
from markupsafe import Markup


class ImageUploadWidget(TextInput):
    """
    Custom widget for image upload with preview
    
    Renders:
    - Current image preview (if exists)
    - File upload button
    - URL input field (hidden/readonly)
    - Upload to /api/v1/upload/image endpoint
    """
    
    def __call__(self, field, **kwargs):
        """Render the widget"""
        field_id = kwargs.pop('id', field.id)
        field_name = kwargs.pop('name', field.name)
        current_value = field._value()
        
        # Get category from field name
        category = "categories"
        if "subcategor" in field_name.lower():
            category = "subcategories"
        elif "brand" in field_name.lower():
            category = "brands"
        elif "product" in field_name.lower():
            category = "products"
        
        html = f'''
        <div class="image-upload-widget" data-field-id="{field_id}">
            <!-- Hidden URL input (actual form value) -->
            <input type="hidden" id="{field_id}" name="{field_name}" value="{current_value or ''}" />
            
            <!-- Image Preview -->
            <div class="mb-3">
                <label class="form-label">Текущее изображение:</label>
                <div id="{field_id}-preview" class="image-preview">
                    {f'<img src="{current_value}" style="max-width: 200px; max-height: 200px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;" />' if current_value else '<p class="text-muted">Нет изображения</p>'}
                </div>
            </div>
            
            <!-- File Upload -->
            <div class="mb-3">
                <label class="form-label">Загрузить новое изображение:</label>
                <input type="file" id="{field_id}-file" class="form-control" accept="image/*" />
            </div>
            
            <!-- Size Selection -->
            <div class="mb-3">
                <label class="form-label">Размер:</label>
                <select id="{field_id}-size" class="form-control">
                    <option value="small">Маленький (200x200)</option>
                    <option value="medium" selected>Средний (500x500)</option>
                    <option value="large">Большой (1200x1200)</option>
                    <option value="null">Оригинальный</option>
                </select>
            </div>
            
            <!-- Upload Button -->
            <button type="button" id="{field_id}-upload-btn" class="btn btn-primary mb-3">
                📤 Загрузить изображение
            </button>
            
            <!-- Status Message -->
            <div id="{field_id}-status" class="alert" style="display: none;"></div>
            
            <!-- Manual URL Input (fallback) -->
            <div class="mb-3">
                <label class="form-label">Или введите URL вручную:</label>
                <input type="text" id="{field_id}-url" class="form-control" value="{current_value or ''}" 
                       placeholder="https://example.com/image.jpg" />
                <button type="button" id="{field_id}-set-url" class="btn btn-secondary btn-sm mt-2">
                    Использовать этот URL
                </button>
            </div>
            
            <script>
            (function() {{
                const fieldId = '{field_id}';
                const category = '{category}';
                const fileInput = document.getElementById(fieldId + '-file');
                const uploadBtn = document.getElementById(fieldId + '-upload-btn');
                const sizeSelect = document.getElementById(fieldId + '-size');
                const statusDiv = document.getElementById(fieldId + '-status');
                const preview = document.getElementById(fieldId + '-preview');
                const hiddenInput = document.getElementById(fieldId);
                const urlInput = document.getElementById(fieldId + '-url');
                const setUrlBtn = document.getElementById(fieldId + '-set-url');
                
                // Upload handler
                uploadBtn.addEventListener('click', async function() {{
                    const file = fileInput.files[0];
                    if (!file) {{
                        showStatus('Пожалуйста, выберите файл', 'warning');
                        return;
                    }}
                    
                    // Show loading
                    uploadBtn.disabled = true;
                    uploadBtn.innerHTML = '⏳ Загрузка...';
                    
                    try {{
                        const formData = new FormData();
                        formData.append('file', file);
                        formData.append('category', category);
                        formData.append('resize_to', sizeSelect.value);
                        
                        const response = await fetch('/api/v1/upload/image', {{
                            method: 'POST',
                            body: formData
                        }});
                        
                        if (!response.ok) {{
                            const error = await response.json();
                            throw new Error(error.detail || 'Upload failed');
                        }}
                        
                        const result = await response.json();
                        
                        // Update hidden input with URL
                        hiddenInput.value = result.url;
                        urlInput.value = result.url;
                        
                        // Update preview
                        preview.innerHTML = '<img src="' + result.url + '" style="max-width: 200px; max-height: 200px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;" />';
                        
                        showStatus('✅ Изображение загружено успешно!', 'success');
                        
                    }} catch (error) {{
                        showStatus('❌ Ошибка: ' + error.message, 'danger');
                    }} finally {{
                        uploadBtn.disabled = false;
                        uploadBtn.innerHTML = '📤 Загрузить изображение';
                    }}
                }});
                
                // Manual URL setter
                setUrlBtn.addEventListener('click', function() {{
                    const url = urlInput.value.trim();
                    if (url) {{
                        hiddenInput.value = url;
                        preview.innerHTML = '<img src="' + url + '" style="max-width: 200px; max-height: 200px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;" />';
                        showStatus('✅ URL установлен', 'success');
                    }}
                }});
                
                function showStatus(message, type) {{
                    statusDiv.className = 'alert alert-' + type;
                    statusDiv.textContent = message;
                    statusDiv.style.display = 'block';
                    setTimeout(() => {{
                        statusDiv.style.display = 'none';
                    }}, 5000);
                }}
            }})();
            </script>
        </div>
        '''
        
        return Markup(html)


class ImageUploadField(StringField):
    """Custom field that uses ImageUploadWidget"""
    widget = ImageUploadWidget()

