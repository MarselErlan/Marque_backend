#!/bin/bash

# Upload product image to Railway backend
# This will upload the image via the API and get back the uploaded URL

IMAGE_FILE="static/uploads/product/deb31057-8c00-4ebe-b2ea-76ad15e9e730.png"
BACKEND_URL="https://marquebackend-production.up.railway.app"

echo "📤 Uploading product image to Railway..."
echo "   File: $IMAGE_FILE"
echo ""

# Upload the image using the upload API
RESPONSE=$(curl -s -X POST \
  "$BACKEND_URL/api/v1/upload/product" \
  -F "file=@$IMAGE_FILE" \
  -H "Content-Type: multipart/form-data")

echo "Response:"
echo "$RESPONSE" | jq '.'

# Extract the uploaded image URL
IMAGE_URL=$(echo "$RESPONSE" | jq -r '.url // .image_url // .path')

if [ "$IMAGE_URL" != "null" ] && [ -n "$IMAGE_URL" ]; then
    echo ""
    echo "✅ Image uploaded successfully!"
    echo "   URL: $IMAGE_URL"
    echo ""
    echo "📝 Now update the product in database:"
    echo "   UPDATE products SET main_image = '$IMAGE_URL' WHERE id = 42;"
else
    echo ""
    echo "❌ Upload failed or no URL returned"
    echo "   You may need to upload through the admin panel instead:"
    echo "   https://marquebackend-production.up.railway.app/admin"
fi

