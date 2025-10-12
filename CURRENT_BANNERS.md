# 🎨 Current Banners in Database

**Last Updated**: October 12, 2025  
**Total Banners**: 4

---

## 📊 Active Banners

### 1. Summer Sale 2025 (Hero)

- **Type**: `hero` (Main carousel)
- **Status**: ✅ Active
- **Order**: 1 (First to display)
- **Subtitle**: Up to 80% Off
- **Description**: Huge discounts on selected items! Don't miss out!
- **CTA**: "Shop Now" → `/products?sale=true`
- **Image**: https://images.unsplash.com/photo-1441986300917-64674bd600d8

---

### 2. New Arrivals (Promo)

- **Type**: `promo` (Promotional)
- **Status**: ✅ Active
- **Order**: 2
- **Subtitle**: Spring Collection 2025
- **Description**: Check out our latest spring fashion collection
- **CTA**: "Explore Collection" → `/products?collection=spring-2025`
- **Image**: https://images.unsplash.com/photo-1445205170230-053b83016050

---

### 3. Accessories (Category)

- **Type**: `category` (Category showcase)
- **Status**: ✅ Active
- **Order**: 3
- **Subtitle**: Complete Your Look
- **Description**: Shop our wide range of accessories
- **CTA**: "Shop Accessories" → `/products?category=accessories`
- **Image**: https://images.unsplash.com/photo-1492707892479-7bc8d5a4ee93

---

### 4. Flash Sale - 50% Off Everything! (Promo) ⭐ NEW

- **Type**: `promo` (Promotional)
- **Status**: ✅ Active
- **Order**: 4
- **Subtitle**: Limited Time Offer
- **Description**: Don't miss out on our biggest flash sale of the year. 50% off all items for the next 48 hours!
- **CTA**: "Shop Flash Sale" → `/products?sale=flash`
- **Image**: https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da
- **Duration**: Active for 2 days (Oct 12-14, 2025)

---

## 📈 Banner Statistics

| Type      | Count | Percentage |
| --------- | ----- | ---------- |
| Hero      | 1     | 25%        |
| Promo     | 2     | 50%        |
| Category  | 1     | 25%        |
| **Total** | **4** | **100%**   |

---

## 🔌 API Endpoints to Test

### Get All Banners

```bash
curl http://localhost:8000/api/v1/banners/
```

**Expected Response**: All 4 banners grouped by type

```json
{
  "hero_banners": [1 banner],
  "promo_banners": [2 banners],
  "category_banners": [1 banner],
  "total": 4
}
```

### Get Hero Banners Only

```bash
curl http://localhost:8000/api/v1/banners/hero
```

**Expected**: 1 banner (Summer Sale 2025)

### Get Promo Banners Only

```bash
curl http://localhost:8000/api/v1/banners/promo
```

**Expected**: 2 banners (New Arrivals + Flash Sale)

### Get Category Banners Only

```bash
curl http://localhost:8000/api/v1/banners/category
```

**Expected**: 1 banner (Accessories)

---

## 🎛️ Admin Panel Access

**URL**: http://localhost:8001/admin/banner/list

You should see all 4 banners in the admin panel with:

- Sortable columns
- Filter by type and status
- Search functionality
- Color-coded badges:
  - 🎬 Hero (Blue)
  - 🏷️ Promo (Yellow)
  - 📂 Category (Info)

---

## 🎯 Banner Display Order

When displayed on the frontend, banners will appear in this order:

1. **Summer Sale 2025** (Order: 1)
2. **New Arrivals** (Order: 2)
3. **Accessories** (Order: 3)
4. **Flash Sale - 50% Off Everything!** (Order: 4)

---

## 📝 Quick Actions

### Add Another Banner

```bash
# Edit add_test_banner.py and run:
python3 add_test_banner.py
```

### View All Banners

```bash
python3 -c "from src.app_01.db import Market, db_manager; from src.app_01.models.banners.banner import Banner; session = db_manager.get_session_factory(Market.KG)(); banners = session.query(Banner).all(); [print(f'{i+1}. {b.title} ({b.banner_type.value})') for i, b in enumerate(banners)]; session.close()"
```

### Delete Last Banner (if needed)

```bash
python3 -c "from src.app_01.db import Market, db_manager; from src.app_01.models.banners.banner import Banner; session = db_manager.get_session_factory(Market.KG)(); banner = session.query(Banner).order_by(Banner.id.desc()).first(); print(f'Deleting: {banner.title}'); session.delete(banner); session.commit(); print('✅ Deleted'); session.close()"
```

---

## ✅ Test Checklist

- [x] 4 banners in database
- [x] All banners active
- [x] All three types represented (hero, promo, category)
- [x] CTAs configured for all banners
- [x] Display order set correctly
- [x] Date range set for Flash Sale
- [ ] Test in admin panel
- [ ] Test API endpoints
- [ ] Test on frontend

---

## 🚀 Next Steps

1. **Test in Admin Panel**:

   - Visit: http://localhost:8001/admin/banner/list
   - Verify all 4 banners appear
   - Try editing the Flash Sale banner

2. **Test API**:

   ```bash
   curl http://localhost:8000/api/v1/banners/ | jq
   ```

3. **Frontend Integration**:

   - Fetch banners from API
   - Display in carousel/grid
   - Test responsive images

4. **Production Deployment**:
   - Fix enum issue in production (see PRODUCTION_BANNER_FIX.md)
   - Deploy updated code
   - Add banners to production database

---

**Status**: ✅ Ready for testing!
