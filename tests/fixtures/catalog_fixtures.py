"""
Fixtures for catalog testing
"""

import pytest
from sqlalchemy.orm import Session

from src.app_01.models import Category, Subcategory, Product, Brand, SKU


@pytest.fixture
def sample_categories(test_db: Session):
    """Create sample main categories"""
    categories = [
        Category(
            name="Мужчинам",
            slug="men",
            description="Одежда для мужчин",
            icon="fa-solid fa-mars",
            sort_order=1,
            is_active=True
        ),
        Category(
            name="Женщинам",
            slug="women",
            description="Одежда для женщин",
            icon="fa-solid fa-venus",
            sort_order=2,
            is_active=True
        ),
        Category(
            name="Детям",
            slug="kids",
            description="Детская одежда",
            icon="fa-solid fa-child",
            sort_order=3,
            is_active=True
        ),
        Category(
            name="Спорт",
            slug="sport",
            description="Спортивная одежда",
            icon="fa-solid fa-dumbbell",
            sort_order=4,
            is_active=True
        )
    ]
    
    for category in categories:
        test_db.add(category)
    test_db.commit()
    
    for category in categories:
        test_db.refresh(category)
    
    return categories


@pytest.fixture
def sample_categories_with_subcategories(test_db: Session, sample_categories):
    """Create categories with subcategories"""
    men_category = sample_categories[0]  # Мужчинам
    
    subcategories = [
        Subcategory(
            category_id=men_category.id,
            name="Футболки и поло",
            slug="t-shirts-polos",
            description="Футболки и поло для мужчин",
            image_url="https://example.com/t-shirts.jpg",
            sort_order=1,
            is_active=True
        ),
        Subcategory(
            category_id=men_category.id,
            name="Свитшоты и худи",
            slug="sweatshirts-hoodies",
            description="Свитшоты и худи для мужчин",
            image_url="https://example.com/sweatshirts.jpg",
            sort_order=2,
            is_active=True
        ),
        Subcategory(
            category_id=men_category.id,
            name="Брюки и шорты",
            slug="pants-shorts",
            description="Брюки и шорты для мужчин",
            image_url="https://example.com/pants.jpg",
            sort_order=3,
            is_active=True
        ),
        Subcategory(
            category_id=men_category.id,
            name="Верхняя одежда",
            slug="outerwear",
            description="Куртки и пальто",
            image_url="https://example.com/outerwear.jpg",
            sort_order=4,
            is_active=True
        )
    ]
    
    for subcategory in subcategories:
        test_db.add(subcategory)
    test_db.commit()
    
    for subcategory in subcategories:
        test_db.refresh(subcategory)
    
    return (men_category, subcategories)


@pytest.fixture
def sample_brand(test_db: Session):
    """Create a sample brand"""
    brand = Brand(
        name="H&M",
        slug="hm",
        description="Шведский бренд модной одежды",
        country="Sweden",
        is_active=True
    )
    test_db.add(brand)
    test_db.commit()
    test_db.refresh(brand)
    return brand


@pytest.fixture
def sample_products_in_category(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create products in a category"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    products = []
    for i in range(5):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Футболка тестовая {i}",
            slug=f"test-tshirt-{i}",
            sku_code=f"BASE-TEST-TSHIRT-{i}",
            description=f"Тестовая футболка номер {i}",
            is_active=True,
            is_featured=False
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    # Create SKUs for each product
    for product in products:
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}-BLK-42",
            size="RUS 42",
            color="black",
            price=2999.0,
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    
    return products


@pytest.fixture
def sample_products_in_subcategory(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create products in a specific subcategory"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    products = []
    for i in range(10):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Футболка {i}",
            slug=f"tshirt-{i}",
            sku_code=f"BASE-TSHIRT-{i}",
            description=f"Описание футболки {i}",
            is_active=True,
            sold_count=i * 10,
            rating_avg=4.0 + (i * 0.1)
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    # Create SKUs with varying prices and attributes
    for i, product in enumerate(products):
        test_db.refresh(product)
        
        # Create multiple SKUs per product
        colors = ["black", "white", "blue"]
        sizes = ["RUS 40", "RUS 42", "RUS 44"]
        
        for j, (color, size) in enumerate(zip(colors, sizes)):
            sku = SKU(
                product_id=product.id,
                sku_code=f"SKU-{product.id}-{color.upper()[:3]}-{size.split()[-1]}",
                size=size,
                color=color,
                price=2000.0 + (i * 100) + (j * 50),
                original_price=3000.0 + (i * 100) + (j * 50),
                stock=5 + j
            )
            test_db.add(sku)
    
    test_db.commit()
    
    return products


@pytest.fixture
def inactive_category(test_db: Session):
    """Create an inactive category"""
    category = Category(
        name="Неактивная",
        slug="inactive-category",
        description="Неактивная категория",
        icon="fa-solid fa-ban",
        sort_order=99,
        is_active=False
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture
def many_products_for_pagination(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create many products to test pagination"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    products = []
    for i in range(50):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Продукт {i:03d}",
            slug=f"product-{i:03d}",
            sku_code=f"BASE-PROD-{i:03d}",
            description=f"Описание продукта {i}",
            is_active=True,
            sold_count=i,
            rating_avg=3.0 + (i % 5) * 0.4
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    # Create SKUs
    for product in products:
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size="RUS 42",
            color="black",
            price=2500.0,
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    
    return products


# Product Detail Fixtures

@pytest.fixture
def sample_product_with_details(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create a product with full details for detail page testing"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    product = Product(
        brand_id=sample_brand.id,
        category_id=men_category.id,
        subcategory_id=tshirt_subcategory.id,
        title="Футболка спорт. из хлопка",
        slug="sport-cotton-tshirt",
        sku_code="BASE-SPORT-COTTON-TSHIRT",
        description="Спортивная футболка из качественного хлопка. Удобная и практичная для повседневной носки.",
        is_active=True,
        sold_count=456,
        rating_avg=4.5,
        rating_count=123,
        attributes={
            "gender": "Мужской",
            "season": "Мульти",
            "composition": "66% полиэстер, 34% хлопок",
            "article": "236412"
        }
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    
    return product


@pytest.fixture
def sample_product_with_images(test_db: Session, sample_product_with_details):
    """Create product with multiple images"""
    from src.app_01.models.products.product_asset import ProductAsset
    
    images = [
        ProductAsset(
            product_id=sample_product_with_details.id,
            url="https://example.com/images/product-main.jpg",
            type="image",
            alt_text="Main product image",
            order=1
        ),
        ProductAsset(
            product_id=sample_product_with_details.id,
            url="https://example.com/images/product-side.jpg",
            type="image",
            alt_text="Side view",
            order=2
        ),
        ProductAsset(
            product_id=sample_product_with_details.id,
            url="https://example.com/images/product-back.jpg",
            type="image",
            alt_text="Back view",
            order=3
        ),
    ]
    
    for image in images:
        test_db.add(image)
    test_db.commit()
    
    return sample_product_with_details


@pytest.fixture
def sample_product_with_skus(test_db: Session, sample_product_with_details):
    """Create product with multiple SKUs (sizes and colors)"""
    product = sample_product_with_details
    
    sizes = ["RUS 40", "RUS 42", "RUS 44", "RUS 46"]
    colors = ["black", "white", "blue"]
    
    skus = []
    for color in colors:
        for i, size in enumerate(sizes):
            sku = SKU(
                product_id=product.id,
                sku_code=f"SKU-{product.id}-{color.upper()[:3]}-{size.split()[-1]}",
                size=size,
                color=color,
                price=2999.0 + (i * 100),
                original_price=3999.0 + (i * 100),
                stock=10 + i
            )
            test_db.add(sku)
            skus.append(sku)
    
    test_db.commit()
    
    for sku in skus:
        test_db.refresh(sku)
    
    return product


@pytest.fixture
def sample_product_with_reviews(test_db: Session, sample_product_with_details):
    """Create product with reviews"""
    from src.app_01.models.products.review import Review
    from src.app_01.models.users.user import User
    
    product = sample_product_with_details
    
    # Create a test user for reviews
    user = User(
        phone_number="+996555999888",
        full_name="Test Reviewer",
        is_verified=True,
        is_active=True,
        market="kg"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Create reviews
    reviews = [
        Review(
            product_id=product.id,
            user_id=user.id,
            rating=5,
            text="Отличная футболка! Качество супер!",
        ),
        Review(
            product_id=product.id,
            user_id=user.id,
            rating=4,
            text="Хорошая футболка, но размер маловат",
        ),
        Review(
            product_id=product.id,
            user_id=user.id,
            rating=5,
            text="Рекомендую! Очень удобная",
        ),
    ]
    
    for review in reviews:
        test_db.add(review)
    test_db.commit()
    
    return product


@pytest.fixture
def sample_product_with_similar(test_db: Session, sample_product_with_details, sample_brand):
    """Create similar products in the same category"""
    main_product = sample_product_with_details
    
    similar_products = []
    for i in range(4):
        product = Product(
            brand_id=sample_brand.id,
            category_id=main_product.category_id,
            subcategory_id=main_product.subcategory_id,
            title=f"Похожая футболка {i+1}",
            slug=f"similar-tshirt-{i+1}",
            sku_code=f"BASE-SIMILAR-{i+1}",
            description=f"Похожий товар номер {i+1}",
            is_active=True,
            sold_count=100 + i,
            rating_avg=4.0 + (i * 0.1),
            rating_count=50 + i
        )
        test_db.add(product)
        similar_products.append(product)
    
    test_db.commit()
    
    for product in similar_products:
        test_db.refresh(product)
        # Add at least one SKU to each
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size="RUS 42",
            color="black",
            price=2500.0,
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    
    return main_product


@pytest.fixture
def inactive_product(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create an inactive product"""
    men_category, subcategories = sample_categories_with_subcategories
    
    product = Product(
        brand_id=sample_brand.id,
        category_id=men_category.id,
        subcategory_id=subcategories[0].id,
        title="Неактивный товар",
        slug="inactive-product",
        sku_code="BASE-INACTIVE-PROD",
        description="Этот товар неактивен",
        is_active=False
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    
    return product


@pytest.fixture
def sample_product_with_discount(test_db: Session, sample_product_with_details):
    """Create product with discounted SKUs"""
    product = sample_product_with_details
    
    # Add SKUs with discounts
    skus = [
        SKU(
            product_id=product.id,
            sku_code="SKU-DISCOUNT-1",
            size="RUS 42",
            color="black",
            price=2499.0,  # Discounted
            original_price=3999.0,  # Original
            stock=10
        ),
        SKU(
            product_id=product.id,
            sku_code="SKU-DISCOUNT-2",
            size="RUS 44",
            color="white",
            price=2499.0,  # Discounted
            original_price=3999.0,  # Original
            stock=5
        ),
    ]
    
    for sku in skus:
        test_db.add(sku)
    test_db.commit()
    
    return product


# Product Listing Fixtures

@pytest.fixture
def sample_products_in_subcategory(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create basic products in a subcategory"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    products = []
    for i in range(5):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"T-Shirt {i+1}",
            slug=f"t-shirt-{i+1}",
            sku_code=f"BASE-TSHIRT-{i+1}",
            description=f"Description {i+1}",
            is_active=True,
            rating_avg=4.0 + (i * 0.1),
            rating_count=10
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    # Add SKUs to each product
    for product in products:
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size="M",
            color="black",
            price=2500.0 + (product.id * 100),
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    return products


@pytest.fixture
def sample_many_products_in_subcategory(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create 25 products for pagination testing"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    products = []
    for i in range(25):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Product {i+1}",
            slug=f"product-{i+1}",
            sku_code=f"BASE-PROD-{i+1}",
            description=f"Description {i+1}",
            is_active=True
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    for product in products:
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size="M",
            color="black",
            price=2500.0,
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    return products


@pytest.fixture
def sample_empty_subcategory(test_db: Session, sample_categories_with_subcategories):
    """Create an empty subcategory"""
    men_category, subcategories = sample_categories_with_subcategories
    
    empty_subcat = Subcategory(
        category_id=men_category.id,
        name="Empty Category",
        slug="empty-subcategory",
        is_active=True
    )
    test_db.add(empty_subcat)
    test_db.commit()
    test_db.refresh(empty_subcat)
    
    return empty_subcat


@pytest.fixture
def sample_products_active_and_inactive(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create mix of active and inactive products"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    products = []
    for i in range(5):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Product {i+1}",
            slug=f"product-active-{i+1}",
            sku_code=f"BASE-PROD-ACT-{i+1}",
            is_active=(i < 3)  # First 3 are active, last 2 are inactive
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    for product in products:
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size="M",
            color="black",
            price=2500.0,
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    return products


@pytest.fixture
def sample_products_with_and_without_skus(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create products with and without SKUs"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    products = []
    for i in range(5):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Product {i+1}",
            slug=f"product-sku-{i+1}",
            sku_code=f"BASE-PROD-SKU-{i+1}",
            is_active=True
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    # Add SKUs only to first 3 products
    for idx, product in enumerate(products[:3]):
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size="M",
            color="black",
            price=2500.0,
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    return products


@pytest.fixture
def sample_products_various_prices(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create products with different prices"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    prices = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
    products = []
    
    for idx, price in enumerate(prices):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Product Price {price}",
            slug=f"product-price-{price}",
            sku_code=f"BASE-PRICE-{price}",
            is_active=True
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    for product, price in zip(products, prices):
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size="M",
            color="black",
            price=float(price),
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    return products


@pytest.fixture
def sample_products_different_dates(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create products with different creation dates"""
    from datetime import datetime, timedelta
    
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    products = []
    for i in range(5):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Product {i+1}",
            slug=f"product-date-{i+1}",
            sku_code=f"BASE-DATE-{i+1}",
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=i)
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    for product in products:
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size="M",
            color="black",
            price=2500.0,
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    return products


@pytest.fixture
def sample_products_different_popularity(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create products with different sold_count"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    sold_counts = [100, 50, 200, 75, 150]
    products = []
    
    for idx, sold_count in enumerate(sold_counts):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Product Popularity {sold_count}",
            slug=f"product-popularity-{idx+1}",
            sku_code=f"BASE-POP-{idx+1}",
            is_active=True,
            sold_count=sold_count
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    for product in products:
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size="M",
            color="black",
            price=2500.0,
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    return products


@pytest.fixture
def sample_products_different_ratings(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create products with different ratings"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    ratings = [5.0, 4.5, 4.0, 3.5, 3.0]
    products = []
    
    for idx, rating in enumerate(ratings):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Product Rating {rating}",
            slug=f"product-rating-{idx+1}",
            sku_code=f"BASE-RATE-{idx+1}",
            is_active=True,
            rating_avg=rating,
            rating_count=10
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    for product in products:
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size="M",
            color="black",
            price=2500.0,
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    return products


@pytest.fixture
def sample_products_various_sizes(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create products with different sizes"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    sizes = ["S", "M", "L", "XL", "XXL"]
    products = []
    
    for idx, size in enumerate(sizes):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Product Size {size}",
            slug=f"product-size-{size.lower()}",
            sku_code=f"BASE-SIZE-{size}",
            is_active=True
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    for product, size in zip(products, sizes):
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size=size,
            color="black",
            price=2500.0,
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    return products


@pytest.fixture
def sample_products_various_colors(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create products with different colors"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    colors = ["black", "white", "blue", "red", "green"]
    products = []
    
    for idx, color in enumerate(colors):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Product Color {color}",
            slug=f"product-color-{color}",
            sku_code=f"BASE-COLOR-{color}",
            is_active=True
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    for product, color in zip(products, colors):
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size="M",
            color=color,
            price=2500.0,
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    return products


@pytest.fixture
def sample_products_multiple_brands(test_db: Session, sample_categories_with_subcategories):
    """Create products from multiple brands"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    # Create brands
    brands = []
    for brand_name in ["Nike", "Adidas", "Puma"]:
        brand = Brand(name=brand_name, slug=brand_name.lower())
        test_db.add(brand)
        brands.append(brand)
    
    test_db.commit()
    
    # Create products for each brand
    products = []
    for brand in brands:
        test_db.refresh(brand)
        for i in range(2):  # 2 products per brand
            product = Product(
                brand_id=brand.id,
                category_id=men_category.id,
                subcategory_id=tshirt_subcategory.id,
                title=f"{brand.name} Product {i+1}",
                slug=f"{brand.slug}-product-{i+1}",
                sku_code=f"BASE-{brand.slug.upper()}-{i+1}",
                is_active=True
            )
            test_db.add(product)
            products.append(product)
    
    test_db.commit()
    
    for product in products:
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size="M",
            color="black",
            price=2500.0,
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    return products


@pytest.fixture
def sample_products_for_filtering(test_db: Session, sample_categories_with_subcategories):
    """Create comprehensive product set for filter testing - 10 products, 5 black, 5 white"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    # Create Nike brand
    nike = Brand(name="Nike", slug="nike")
    test_db.add(nike)
    test_db.commit()
    test_db.refresh(nike)
    
    # Create 10 products with various attributes
    products = []
    prices = [1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000]
    sizes = ["M", "L", "M", "L", "M", "L", "M", "L", "M", "L"]
    colors = ["black", "black", "black", "black", "black", "white", "white", "white", "white", "white"]
    
    for i, (price, size, color) in enumerate(zip(prices, sizes, colors)):
        product = Product(
            brand_id=nike.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Filter Test Product {i+1}",
            slug=f"filter-test-{i+1}",
            sku_code=f"BASE-FILTER-{i+1}",
            is_active=True
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    for product, price, size, color in zip(products, prices, sizes, colors):
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size=size,
            color=color,
            price=float(price),
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    return products


@pytest.fixture
def sample_many_products_for_filtering(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create many products for filter + pagination testing"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    products = []
    for i in range(20):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=f"Many Filter Product {i+1}",
            slug=f"many-filter-{i+1}",
            sku_code=f"BASE-MANY-FILTER-{i+1}",
            is_active=True
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    for product in products:
        test_db.refresh(product)
        sku = SKU(
            product_id=product.id,
            sku_code=f"SKU-{product.id}",
            size="M",
            color="black",
            price=2500.0,
            stock=10
        )
        test_db.add(sku)
    
    test_db.commit()
    return products


@pytest.fixture
def sample_products_for_search(test_db: Session, sample_categories_with_subcategories, sample_brand):
    """Create products for search testing"""
    men_category, subcategories = sample_categories_with_subcategories
    tshirt_subcategory = subcategories[0]
    
    titles = [
        "Cotton T-Shirt",
        "Cotton Polo Shirt",
        "Polyester T-Shirt",
        "Silk Shirt",
        "Linen Shirt"
    ]
    
    products = []
    for idx, title in enumerate(titles):
        product = Product(
            brand_id=sample_brand.id,
            category_id=men_category.id,
            subcategory_id=tshirt_subcategory.id,
            title=title,
            slug=f"search-product-{idx+1}",
            sku_code=f"BASE-SEARCH-{idx+1}",
            is_active=True
        )
        test_db.add(product)
        products.append(product)
    
    test_db.commit()
    
    for product in products:
        test_db.refresh(product)
        # Add SKUs with different colors
        for color in ["black", "white"]:
            sku = SKU(
                product_id=product.id,
                sku_code=f"SKU-{product.id}-{color}",
                size="M",
                color=color,
                price=2500.0,
                stock=10
            )
            test_db.add(sku)
    
    test_db.commit()
    return products
