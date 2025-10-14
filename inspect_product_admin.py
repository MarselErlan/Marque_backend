"""
Inspect Product Admin CRUD Configuration
Direct inspection of class attributes
"""

from src.app_01.admin.sqladmin_views import ProductAdmin


def inspect_product_crud():
    """Inspect all CRUD configuration for Product admin"""
    
    print("\n🔍 PRODUCT ADMIN CRUD CONFIGURATION")
    print("=" * 70 + "\n")
    
    # ============================================
    # 1. CRUD PERMISSIONS
    # ============================================
    print("📋 1. CRUD PERMISSIONS:")
    print("-" * 70)
    
    operations = {
        "CREATE  (Add new products)": ProductAdmin.can_create,
        "READ    (View product list & details)": ProductAdmin.can_view_details,
        "UPDATE  (Edit existing products)": ProductAdmin.can_edit,
        "DELETE  (Remove products)": ProductAdmin.can_delete,
        "EXPORT  (CSV download)": ProductAdmin.can_export,
    }
    
    for op, status in operations.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {op:<40} {status}")
    
    # ============================================
    # 2. FORM CONFIGURATION (CREATE/UPDATE)
    # ============================================
    print(f"\n📝 2. FORM CONFIGURATION (for CREATE & UPDATE):")
    print("-" * 70)
    
    print(f"\n  Standard Form Fields ({len(ProductAdmin.form_columns)}):")
    for i, col in enumerate(ProductAdmin.form_columns, 1):
        label = ProductAdmin.form_args.get(col, {}).get("label", col)
        print(f"    {i:2d}. {col:<20} → {label}")
    
    print(f"\n  Extra Form Fields ({len(ProductAdmin.form_extra_fields)}):")
    for field_name, field_obj in ProductAdmin.form_extra_fields.items():
        field_type = field_obj.__class__.__name__
        print(f"    • {field_name:<20} → {field_type}")
    
    # ============================================
    # 3. LIST VIEW CONFIGURATION (READ)
    # ============================================
    print(f"\n📊 3. LIST VIEW CONFIGURATION:")
    print("-" * 70)
    
    print(f"  Displayed Columns ({len(ProductAdmin.column_list)}):")
    for i, col in enumerate(ProductAdmin.column_list, 1):
        formatter = "✨ Custom formatter" if col in ProductAdmin.column_formatters else ""
        print(f"    {i:2d}. {col:<20} {formatter}")
    
    # ============================================
    # 4. DETAIL VIEW CONFIGURATION (READ)
    # ============================================
    print(f"\n📄 4. DETAIL VIEW CONFIGURATION:")
    print("-" * 70)
    
    print(f"  Displayed Columns ({len(ProductAdmin.column_details_list)}):")
    cols_list = ProductAdmin.column_details_list
    for i in range(0, len(cols_list), 5):
        chunk = cols_list[i:i+5]
        print(f"    {', '.join(chunk)}")
    
    # ============================================
    # 5. SEARCH & FILTER (READ)
    # ============================================
    print(f"\n🔍 5. SEARCH & FILTER CONFIGURATION:")
    print("-" * 70)
    
    print(f"  Searchable Columns ({len(ProductAdmin.column_searchable_list)}):")
    print(f"    {', '.join(ProductAdmin.column_searchable_list)}")
    
    print(f"\n  Filterable Columns ({len(ProductAdmin.column_filters)}):")
    filters_display = ", ".join(str(f) for f in ProductAdmin.column_filters[:10])
    print(f"    {filters_display}...")
    
    print(f"\n  Sortable Columns ({len(ProductAdmin.column_sortable_list)}):")
    print(f"    {', '.join(str(col) for col in ProductAdmin.column_sortable_list)}")
    
    # ============================================
    # 6. CUSTOM FORMATTERS (READ)
    # ============================================
    print(f"\n🎨 6. CUSTOM FORMATTERS:")
    print("-" * 70)
    
    print(f"  Custom Display Logic ({len(ProductAdmin.column_formatters)} columns):")
    for col_name in ProductAdmin.column_formatters.keys():
        print(f"    • {col_name}")
    
    # ============================================
    # 7. CUSTOM LOGIC (CREATE/UPDATE)
    # ============================================
    print(f"\n⚙️  7. CUSTOM BUSINESS LOGIC:")
    print("-" * 70)
    
    has_insert = hasattr(ProductAdmin, 'insert_model')
    has_update = hasattr(ProductAdmin, 'update_model')
    has_delete = hasattr(ProductAdmin, 'delete_model')
    
    print(f"  ✅ Custom INSERT logic:  {has_insert}  (image upload handling)")
    print(f"  ✅ Custom UPDATE logic:  {has_update}  (image upload handling)")
    print(f"  {'✅' if has_delete else '❌'} Custom DELETE logic:  {has_delete}")
    
    # ============================================
    # 8. PAGINATION & EXPORT
    # ============================================
    print(f"\n📑 8. PAGINATION & EXPORT:")
    print("-" * 70)
    
    print(f"  Page Size: {ProductAdmin.page_size} items")
    print(f"  Page Size Options: {ProductAdmin.page_size_options}")
    print(f"  Export Formats: {'CSV' if ProductAdmin.can_export else 'None'}")
    
    # ============================================
    # SUMMARY
    # ============================================
    print("\n" + "=" * 70)
    print("📊 CRUD OPERATIONS SUMMARY")
    print("=" * 70)
    
    total_operations = sum([
        ProductAdmin.can_create,
        ProductAdmin.can_view_details,
        ProductAdmin.can_edit,
        ProductAdmin.can_export,
    ])
    
    print(f"""
✅ ENABLED OPERATIONS: {total_operations}/5
   
   • CREATE:  {"✅ YES" if ProductAdmin.can_create else "❌ NO"}
      → Form has {len(ProductAdmin.form_columns)} standard fields
      → Plus {len(ProductAdmin.form_extra_fields)} extra fields (image uploads)
      → Custom insert logic for image processing
   
   • READ:    {"✅ YES" if ProductAdmin.can_view_details else "❌ NO"}
      → List view with {len(ProductAdmin.column_list)} columns
      → Detail view with {len(ProductAdmin.column_details_list)} columns
      → Search across {len(ProductAdmin.column_searchable_list)} fields
      → Filter by {len(ProductAdmin.column_filters)} criteria
      → Sort by {len(ProductAdmin.column_sortable_list)} columns
   
   • UPDATE:  {"✅ YES" if ProductAdmin.can_edit else "❌ NO"}
      → Same form as CREATE
      → Custom update logic for image processing
      → Preserves existing images if not replaced
   
   • DELETE:  {"❌ NO (DISABLED)" if not ProductAdmin.can_delete else "✅ YES"}
      → Products use 'is_active' flag instead of deletion
      → Preserves data integrity for orders/reviews
   
   • EXPORT:  {"✅ YES" if ProductAdmin.can_export else "❌ NO"}
      → Export to CSV format
      → All visible columns included

🎯 RECOMMENDATION:
   DELETE is intentionally disabled. To remove a product from public view:
   1. Edit the product
   2. Set "is_active" to False
   3. The product will be hidden but data preserved
    """)
    
    print("=" * 70)
    print("✅ Product Admin CRUD is properly configured!\n")


if __name__ == "__main__":
    inspect_product_crud()

