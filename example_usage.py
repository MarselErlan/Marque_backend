"""
Example usage of the Marque e-commerce models
This demonstrates how to create and work with products, SKUs, reviews, etc.
"""

from src.app_01.db import SessionLocal, engine
from src.app_01.models import User, Product, SKU, ProductAsset, Review, CartOrder, Interaction
from src.app_01.db import Base

# Create tables (this would normally be done via Alembic migrations)
Base.metadata.create_all(bind=engine)

def create_sample_data():
    """Create sample data to demonstrate the models"""
    db = SessionLocal()
    
    try:
        # Create a user
        user = User(
            email="ana.dearmas@example.com",
            username="ana_dearmas",
            hashed_password="hashed_password_here",
            full_name="Ana De Armas"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create a product (like the H&M t-shirt from the Figma design)
        product = Product(
            brand="H&M",
            title="Футболка спорт. из хлопка",  # Sport t-shirt, made of cotton
            slug="hm-sport-cotton-tshirt",
            description="Спортивная футболка из качественного хлопка. Удобная и практичная для повседневной носки.",
            sold_count=120,
            rating_avg=4.4,
            rating_count=32,
            attributes={
                "gender": "Мужской/Женский",
                "season": "Мульти",
                "composition": "66% полиэстер, 34% хлопок",
                "article": "236412"
            }
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Create SKUs for different sizes and colors
        skus = [
            SKU(
                product_id=product.id,
                sku_code="Артикул/236412-BLK-40",
                size="RUS 40",
                color="black",
                price=2999.0,
                stock=15
            ),
            SKU(
                product_id=product.id,
                sku_code="Артикул/236412-BLK-42",
                size="RUS 42", 
                color="black",
                price=2999.0,
                stock=12
            ),
            SKU(
                product_id=product.id,
                sku_code="Артикул/236412-BLK-44",
                size="RUS 44",
                color="black", 
                price=2999.0,
                stock=8
            )
        ]
        
        for sku in skus:
            db.add(sku)
        db.commit()
        
        # Create product assets (images)
        assets = [
            ProductAsset(
                product_id=product.id,
                url="https://example.com/images/hm-tshirt-main.jpg",
                type="image"
            ),
            ProductAsset(
                product_id=product.id,
                url="https://example.com/images/hm-tshirt-side.jpg", 
                type="image"
            )
        ]
        
        for asset in assets:
            db.add(asset)
        db.commit()
        
        # Create reviews
        review = Review(
            product_id=product.id,
            user_id=user.id,
            rating=5,
            text="Отличная футболка! Качество хорошее, размер соответствует."
        )
        db.add(review)
        db.commit()
        
        # Add item to cart
        cart_item = CartOrder(
            user_id=user.id,
            sku_id=skus[0].id,  # Size 40
            quantity=2,
            price=2999.0
        )
        db.add(cart_item)
        db.commit()
        
        # Track user interaction
        interaction = Interaction(
            user_id=user.id,
            product_id=product.id,
            interaction_type="view",
            metadata="Product page view from search results"
        )
        db.add(interaction)
        db.commit()
        
        print("Sample data created successfully!")
        print(f"Created user: {user.username}")
        print(f"Created product: {product.title}")
        print(f"Created {len(skus)} SKUs")
        print(f"Created {len(assets)} assets")
        print(f"Created {1} review")
        print(f"Created {1} cart item")
        print(f"Created {1} interaction")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating sample data: {e}")
    finally:
        db.close()

def query_examples():
    """Examples of querying the models"""
    db = SessionLocal()
    
    try:
        # Get all products with their SKUs
        products = db.query(Product).all()
        for product in products:
            print(f"\nProduct: {product.title} by {product.brand}")
            print(f"Rating: {product.rating_avg}/5 ({product.rating_count} reviews)")
            print(f"SKUs:")
            for sku in product.skus:
                print(f"  - {sku.size} ({sku.color}): {sku.price} сом, Stock: {sku.stock}")
        
        # Get user's cart
        user = db.query(User).first()
        if user:
            cart_items = db.query(CartOrder).filter(
                CartOrder.user_id == user.id,
                CartOrder.is_ordered == False
            ).all()
            
            print(f"\n{user.full_name}'s cart:")
            for item in cart_items:
                print(f"  - SKU: {item.sku.sku_code}, Quantity: {item.quantity}, Price: {item.price}")
        
        # Get product reviews
        product = db.query(Product).first()
        if product:
            reviews = db.query(Review).filter(Review.product_id == product.id).all()
            print(f"\nReviews for {product.title}:")
            for review in reviews:
                print(f"  - {review.user.full_name}: {review.rating}/5 - {review.text}")
        
    except Exception as e:
        print(f"Error querying data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating sample data...")
    create_sample_data()
    
    print("\nQuerying examples...")
    query_examples()
