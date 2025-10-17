"""
Product Discount Router

API endpoints for managing discounts and promotions:
- Active discounts
- Best deals
- Flash sales
- Seasonal promotions
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from ..db import get_db_session
from ..models.products.product_filter import ProductDiscount
from ..models.products.product import Product

router = APIRouter(prefix="/api/v1/discounts", tags=["Product Discounts"])


# ========================
# PYDANTIC SCHEMAS
# ========================

class DiscountResponse(BaseModel):
    """Discount response"""
    id: int
    product_id: int
    product_name: Optional[str] = None
    discount_type: str
    discount_value: float
    original_price: Optional[float]
    discount_percentage: float
    final_price: Optional[float]
    savings_amount: float
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class CreateDiscountRequest(BaseModel):
    """Create discount request"""
    product_id: int
    discount_type: str  # "percentage" or "fixed"
    discount_value: float
    original_price: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class UpdateDiscountRequest(BaseModel):
    """Update discount request"""
    discount_value: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


# ========================
# ACTIVE DISCOUNTS API
# ========================

@router.get("/active", response_model=List[DiscountResponse])
def get_active_discounts(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db_session)
):
    """
    Get all currently active discounts
    
    **Filters by:**
    - is_active = True
    - Current date between start_date and end_date
    
    **Use for:**
    - "On Sale" product listings
    - Homepage deals section
    - Email marketing campaigns
    
    **Args:**
    - `limit`: Maximum number of results
    
    **Returns:** Active discounts with calculated savings
    """
    discounts = ProductDiscount.get_active_discounts(db)[:limit]
    
    response = []
    for discount in discounts:
        # Get product name
        product = db.query(Product).filter(Product.id == discount.product_id).first()
        
        response.append(DiscountResponse(
            id=discount.id,
            product_id=discount.product_id,
            product_name=product.name if product else None,
            discount_type=discount.discount_type,
            discount_value=discount.discount_value,
            original_price=discount.original_price,
            discount_percentage=discount.discount_percentage,
            final_price=discount.final_price,
            savings_amount=discount.savings_amount,
            start_date=discount.start_date,
            end_date=discount.end_date,
            is_active=discount.is_active
        ))
    
    return response


@router.get("/best-deals", response_model=List[DiscountResponse])
def get_best_deals(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db_session)
):
    """
    Get biggest active discounts
    
    **Sorted by:**
    Discount percentage (highest first)
    
    **Perfect for:**
    - "Best Deals" homepage section
    - "Biggest Savings" page
    - Marketing banners
    
    **Args:**
    - `limit`: Number of deals to return
    
    **Returns:** Top discounts sorted by savings
    """
    discounts = ProductDiscount.get_best_discounts(db, limit)
    
    response = []
    for discount in discounts:
        product = db.query(Product).filter(Product.id == discount.product_id).first()
        
        response.append(DiscountResponse(
            id=discount.id,
            product_id=discount.product_id,
            product_name=product.name if product else None,
            discount_type=discount.discount_type,
            discount_value=discount.discount_value,
            original_price=discount.original_price,
            discount_percentage=discount.discount_percentage,
            final_price=discount.final_price,
            savings_amount=discount.savings_amount,
            start_date=discount.start_date,
            end_date=discount.end_date,
            is_active=discount.is_active
        ))
    
    return response


@router.get("/product/{product_id}", response_model=Optional[DiscountResponse])
def get_product_discount(
    product_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Get active discount for a specific product
    
    **Args:**
    - `product_id`: Product ID
    
    **Returns:** Active discount if exists, null otherwise
    """
    from datetime import datetime
    
    discount = db.query(ProductDiscount).filter(
        ProductDiscount.product_id == product_id,
        ProductDiscount.is_active == True
    ).first()
    
    if not discount:
        return None
    
    # Check if discount is currently valid
    now = datetime.now()
    if discount.start_date and now < discount.start_date:
        return None
    if discount.end_date and now > discount.end_date:
        return None
    
    product = db.query(Product).filter(Product.id == product_id).first()
    
    return DiscountResponse(
        id=discount.id,
        product_id=discount.product_id,
        product_name=product.name if product else None,
        discount_type=discount.discount_type,
        discount_value=discount.discount_value,
        original_price=discount.original_price,
        discount_percentage=discount.discount_percentage,
        final_price=discount.final_price,
        savings_amount=discount.savings_amount,
        start_date=discount.start_date,
        end_date=discount.end_date,
        is_active=discount.is_active
    )


# ========================
# DISCOUNT MANAGEMENT API
# ========================

@router.post("/", response_model=DiscountResponse)
def create_discount(
    request: CreateDiscountRequest,
    db: Session = Depends(get_db_session)
):
    """
    Create a new discount (Admin only)
    
    **Discount types:**
    - `percentage`: e.g., 20 for 20% off
    - `fixed`: e.g., 500 for 500 KGS off
    
    **Args:**
    - `product_id`: Product ID
    - `discount_type`: "percentage" or "fixed"
    - `discount_value`: Discount amount
    - `original_price`: Original price (optional)
    - `start_date`: When discount starts (optional, default: now)
    - `end_date`: When discount ends (optional, default: no end)
    
    **Returns:** Created discount
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Validate discount type
    if request.discount_type not in ["percentage", "fixed"]:
        raise HTTPException(
            status_code=400,
            detail="discount_type must be 'percentage' or 'fixed'"
        )
    
    # Validate percentage
    if request.discount_type == "percentage" and (request.discount_value < 0 or request.discount_value > 100):
        raise HTTPException(
            status_code=400,
            detail="Percentage discount must be between 0 and 100"
        )
    
    # Create discount
    discount = ProductDiscount(
        product_id=request.product_id,
        discount_type=request.discount_type,
        discount_value=request.discount_value,
        original_price=request.original_price,
        start_date=request.start_date,
        end_date=request.end_date,
        is_active=True
    )
    
    db.add(discount)
    db.commit()
    db.refresh(discount)
    
    return DiscountResponse(
        id=discount.id,
        product_id=discount.product_id,
        product_name=product.name,
        discount_type=discount.discount_type,
        discount_value=discount.discount_value,
        original_price=discount.original_price,
        discount_percentage=discount.discount_percentage,
        final_price=discount.final_price,
        savings_amount=discount.savings_amount,
        start_date=discount.start_date,
        end_date=discount.end_date,
        is_active=discount.is_active
    )


@router.patch("/{discount_id}", response_model=DiscountResponse)
def update_discount(
    discount_id: int,
    request: UpdateDiscountRequest,
    db: Session = Depends(get_db_session)
):
    """
    Update an existing discount (Admin only)
    
    **Can update:**
    - Discount value
    - Start/end dates
    - Active status
    
    **Args:**
    - `discount_id`: Discount ID
    - Update fields (all optional)
    
    **Returns:** Updated discount
    """
    discount = db.query(ProductDiscount).filter(ProductDiscount.id == discount_id).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    # Update fields
    if request.discount_value is not None:
        if discount.discount_type == "percentage" and (request.discount_value < 0 or request.discount_value > 100):
            raise HTTPException(status_code=400, detail="Percentage must be 0-100")
        discount.discount_value = request.discount_value
    
    if request.start_date is not None:
        discount.start_date = request.start_date
    
    if request.end_date is not None:
        discount.end_date = request.end_date
    
    if request.is_active is not None:
        discount.is_active = request.is_active
    
    db.commit()
    db.refresh(discount)
    
    product = db.query(Product).filter(Product.id == discount.product_id).first()
    
    return DiscountResponse(
        id=discount.id,
        product_id=discount.product_id,
        product_name=product.name if product else None,
        discount_type=discount.discount_type,
        discount_value=discount.discount_value,
        original_price=discount.original_price,
        discount_percentage=discount.discount_percentage,
        final_price=discount.final_price,
        savings_amount=discount.savings_amount,
        start_date=discount.start_date,
        end_date=discount.end_date,
        is_active=discount.is_active
    )


@router.delete("/{discount_id}")
def delete_discount(
    discount_id: int,
    db: Session = Depends(get_db_session)
):
    """
    Delete a discount (Admin only)
    
    **Args:**
    - `discount_id`: Discount ID
    
    **Returns:** Confirmation message
    """
    discount = db.query(ProductDiscount).filter(ProductDiscount.id == discount_id).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    db.delete(discount)
    db.commit()
    
    return {
        "success": True,
        "message": f"Discount {discount_id} deleted successfully"
    }


# ========================
# DISCOUNT STATISTICS API
# ========================

@router.get("/stats")
def get_discount_stats(db: Session = Depends(get_db_session)):
    """
    Get discount statistics
    
    **Returns:**
    - Total active discounts
    - Average discount percentage
    - Total savings offered
    - Biggest discount
    
    **Use for:**
    - Dashboard metrics
    - Marketing reports
    """
    from sqlalchemy import func
    
    active_discounts = ProductDiscount.get_active_discounts(db)
    
    if not active_discounts:
        return {
            "total_active_discounts": 0,
            "average_discount_percentage": 0,
            "biggest_discount_percentage": 0,
            "total_products_on_sale": 0
        }
    
    # Calculate stats
    percentages = [d.discount_percentage for d in active_discounts if d.discount_percentage]
    
    return {
        "total_active_discounts": len(active_discounts),
        "average_discount_percentage": round(sum(percentages) / len(percentages), 2) if percentages else 0,
        "biggest_discount_percentage": max(percentages) if percentages else 0,
        "total_products_on_sale": len(set(d.product_id for d in active_discounts))
    }


# ========================
# FLASH SALES API
# ========================

@router.get("/flash-sales")
def get_flash_sales(db: Session = Depends(get_db_session)):
    """
    Get flash sales (discounts ending soon)
    
    **Definition:**
    Discounts ending within next 24 hours
    
    **Perfect for:**
    - "Ending Soon" section
    - Urgency marketing
    - Limited time offers
    
    **Returns:** Discounts ending within 24 hours
    """
    from datetime import datetime, timedelta
    
    now = datetime.now()
    tomorrow = now + timedelta(hours=24)
    
    flash_sales = db.query(ProductDiscount).filter(
        ProductDiscount.is_active == True,
        ProductDiscount.end_date.isnot(None),
        ProductDiscount.end_date > now,
        ProductDiscount.end_date <= tomorrow
    ).all()
    
    response = []
    for discount in flash_sales:
        product = db.query(Product).filter(Product.id == discount.product_id).first()
        
        # Calculate hours remaining
        hours_remaining = (discount.end_date - now).total_seconds() / 3600
        
        response.append({
            "discount": DiscountResponse(
                id=discount.id,
                product_id=discount.product_id,
                product_name=product.name if product else None,
                discount_type=discount.discount_type,
                discount_value=discount.discount_value,
                original_price=discount.original_price,
                discount_percentage=discount.discount_percentage,
                final_price=discount.final_price,
                savings_amount=discount.savings_amount,
                start_date=discount.start_date,
                end_date=discount.end_date,
                is_active=discount.is_active
            ),
            "hours_remaining": round(hours_remaining, 1)
        })
    
    return {
        "flash_sales_count": len(response),
        "flash_sales": response
    }

