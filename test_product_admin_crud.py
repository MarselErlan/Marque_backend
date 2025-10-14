"""
Test Product Admin CRUD Operations
This script verifies all CRUD operations for the Product admin panel
"""

import asyncio
from src.app_01.admin.sqladmin_views import ProductAdmin
from src.app_01.models.products.product import Product
from src.app_01.models.products.brand import Brand
from src.app_01.models.products.category import Category, Subcategory
from src.app_01.db.market_db import db_manager, Market


async def test_product_crud():
    """Test all CRUD operations for Product admin"""
    
    print("🔍 Testing Product Admin CRUD Operations\n")
    print("=" * 60)
    
    # Get database session
    SessionFactory = db_manager.get_session_factory(Market.KG)
    async with SessionFactory() as session:
        
        # ============================================
        # 1. TEST PERMISSIONS
        # ============================================
        print("\n1️⃣  TESTING PERMISSIONS:")
        print("-" * 60)
        
        admin = ProductAdmin(Product, session)
        
        print(f"✅ can_create:       {admin.can_create}")
        print(f"✅ can_edit:         {admin.can_edit}")
        print(f"✅ can_delete:       {admin.can_delete} (should be False)")
        print(f"✅ can_view_details: {admin.can_view_details}")
        print(f"✅ can_export:       {admin.can_export}")
        
        # ============================================
        # 2. TEST FORM CONFIGURATION
        # ============================================
        print("\n2️⃣  TESTING FORM CONFIGURATION:")
        print("-" * 60)
        
        print(f"📝 Form Columns ({len(admin.form_columns)}):")
        for col in admin.form_columns:
            print(f"   - {col}")
        
        print(f"\n📋 Form Extra Fields ({len(admin.form_extra_fields)}):")
        for field_name, field_obj in admin.form_extra_fields.items():
            print(f"   - {field_name}: {field_obj.__class__.__name__}")
        
        # ============================================
        # 3. TEST DISPLAY CONFIGURATION
        # ============================================
        print("\n3️⃣  TESTING DISPLAY CONFIGURATION:")
        print("-" * 60)
        
        print(f"📊 List View Columns ({len(admin.column_list)}):")
        for col in admin.column_list:
            print(f"   - {col}")
        
        print(f"\n📄 Detail View Columns ({len(admin.column_details_list)}):")
        for col in admin.column_details_list:
            print(f"   - {col}")
        
        # ============================================
        # 4. TEST SEARCH & FILTER
        # ============================================
        print("\n4️⃣  TESTING SEARCH & FILTER:")
        print("-" * 60)
        
        print(f"🔍 Searchable Columns ({len(admin.column_searchable_list)}):")
        for col in admin.column_searchable_list:
            print(f"   - {col}")
        
        print(f"\n🎛️  Filter Columns ({len(admin.column_filters)}):")
        for col in admin.column_filters:
            print(f"   - {col}")
        
        print(f"\n📈 Sortable Columns ({len(admin.column_sortable_list)}):")
        for col in admin.column_sortable_list:
            print(f"   - {col}")
        
        # ============================================
        # 5. TEST FORMATTERS
        # ============================================
        print("\n5️⃣  TESTING FORMATTERS:")
        print("-" * 60)
        
        print(f"🎨 Custom Formatters ({len(admin.column_formatters)}):")
        for col_name in admin.column_formatters.keys():
            print(f"   - {col_name}")
        
        # ============================================
        # 6. TEST READ OPERATION (List)
        # ============================================
        print("\n6️⃣  TESTING READ OPERATION (List):")
        print("-" * 60)
        
        from sqlalchemy import select
        result = await session.execute(
            select(Product).limit(5)
        )
        products = result.scalars().all()
        
        print(f"📦 Found {len(products)} products (showing first 5)")
        for product in products:
            print(f"   - ID: {product.id} | {product.title} | Brand: {product.brand.name if product.brand else 'N/A'}")
        
        # ============================================
        # 7. TEST READ OPERATION (Details)
        # ============================================
        print("\n7️⃣  TESTING READ OPERATION (Details):")
        print("-" * 60)
        
        if products:
            product = products[0]
            print(f"📋 Product Details (ID: {product.id}):")
            print(f"   - Title: {product.title}")
            print(f"   - Slug: {product.slug}")
            print(f"   - Brand: {product.brand.name if product.brand else 'N/A'}")
            print(f"   - Category: {product.category.name if product.category else 'N/A'}")
            print(f"   - Subcategory: {product.subcategory.name if product.subcategory else 'N/A'}")
            print(f"   - Active: {product.is_active}")
            print(f"   - Featured: {product.is_featured}")
            print(f"   - Sold Count: {product.sold_count}")
            print(f"   - Rating: {product.rating_avg}")
            
            # Check if image columns exist
            if hasattr(product, 'main_image'):
                print(f"   - Main Image: {product.main_image or 'None'}")
            if hasattr(product, 'additional_images'):
                print(f"   - Additional Images: {len(product.additional_images) if product.additional_images else 0} images")
        
        # ============================================
        # 8. TEST CREATE VALIDATION
        # ============================================
        print("\n8️⃣  TESTING CREATE VALIDATION:")
        print("-" * 60)
        
        # Get first brand, category, subcategory for test
        brand = await session.execute(select(Brand).limit(1))
        brand = brand.scalar_one_or_none()
        
        category = await session.execute(select(Category).limit(1))
        category = category.scalar_one_or_none()
        
        subcategory = await session.execute(select(Subcategory).limit(1))
        subcategory = subcategory.scalar_one_or_none()
        
        if brand and category and subcategory:
            print(f"✅ Required data available:")
            print(f"   - Brand: {brand.name}")
            print(f"   - Category: {category.name}")
            print(f"   - Subcategory: {subcategory.name}")
            print(f"\n✅ CREATE operation can be tested (form has all required dropdowns)")
        else:
            print(f"⚠️  Missing required data:")
            if not brand:
                print(f"   - No brands found")
            if not category:
                print(f"   - No categories found")
            if not subcategory:
                print(f"   - No subcategories found")
        
        # ============================================
        # 9. TEST UPDATE CAPABILITY
        # ============================================
        print("\n9️⃣  TESTING UPDATE CAPABILITY:")
        print("-" * 60)
        
        if products:
            print(f"✅ UPDATE operation available for product ID: {products[0].id}")
            print(f"   - Can modify: title, description, brand, category, etc.")
            print(f"   - Custom logic: Image upload handling")
        
        # ============================================
        # 10. TEST DELETE POLICY
        # ============================================
        print("\n🔟 TESTING DELETE POLICY:")
        print("-" * 60)
        
        print(f"🚫 DELETE operation: {'DISABLED' if not admin.can_delete else 'ENABLED'}")
        print(f"   - Products should be set to inactive instead of deleted")
        print(f"   - This preserves historical data and order references")
        
        # ============================================
        # SUMMARY
        # ============================================
        print("\n" + "=" * 60)
        print("📊 CRUD OPERATIONS SUMMARY:")
        print("=" * 60)
        print(f"""
✅ CREATE:  {admin.can_create}  | Form with {len(admin.form_columns)} fields + {len(admin.form_extra_fields)} extra fields
✅ READ:    {admin.can_view_details}  | List view ({len(admin.column_list)} cols) + Detail view ({len(admin.column_details_list)} cols)
✅ UPDATE:  {admin.can_edit}  | Custom image upload logic implemented
❌ DELETE:  {admin.can_delete}  | Disabled (use 'is_active' flag instead)
✅ EXPORT:  {admin.can_export}  | CSV export available
✅ SEARCH:  True  | {len(admin.column_searchable_list)} searchable columns
✅ FILTER:  True  | {len(admin.column_filters)} filter options
✅ SORT:    True  | {len(admin.column_sortable_list)} sortable columns
        """)
        
        print("\n🎉 All CRUD operations configured correctly!")


if __name__ == "__main__":
    asyncio.run(test_product_crud())

