"""
Banner Router
API endpoints for managing main page banners
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import datetime

from ..db import get_db
from ..models.banners.banner import Banner, BannerType
from ..schemas.banner import (
    BannerCreate, BannerUpdate, BannerResponse, 
    BannersListResponse, BannerActionResponse
)
from .auth_router import get_current_user_from_token
from ..schemas.auth import VerifyTokenResponse

router = APIRouter(prefix="/banners", tags=["banners"])

# Public Endpoints (for displaying on main page)

@router.get("/", response_model=BannersListResponse)
def get_active_banners(db: Session = Depends(get_db)):
    """
    Get all active banners for main page display
    Returns separate lists for sale and model banners
    """
    now = datetime.utcnow()
    
    # Get active sale banners
    sale_banners = db.query(Banner).filter(
        and_(
            Banner.is_active == True,
            Banner.banner_type == BannerType.SALE,
            # Check date ranges
            (Banner.start_date == None) | (Banner.start_date <= now),
            (Banner.end_date == None) | (Banner.end_date >= now)
        )
    ).order_by(Banner.display_order, Banner.created_at.desc()).all()
    
    # Get active model banners
    model_banners = db.query(Banner).filter(
        and_(
            Banner.is_active == True,
            Banner.banner_type == BannerType.MODEL,
            # Check date ranges
            (Banner.start_date == None) | (Banner.start_date <= now),
            (Banner.end_date == None) | (Banner.end_date >= now)
        )
    ).order_by(Banner.display_order, Banner.created_at.desc()).all()
    
    return BannersListResponse(
        sale_banners=sale_banners,
        model_banners=model_banners,
        total=len(sale_banners) + len(model_banners)
    )

@router.get("/sale", response_model=List[BannerResponse])
def get_sale_banners(db: Session = Depends(get_db)):
    """Get only active sale banners"""
    now = datetime.utcnow()
    
    banners = db.query(Banner).filter(
        and_(
            Banner.is_active == True,
            Banner.banner_type == BannerType.SALE,
            (Banner.start_date == None) | (Banner.start_date <= now),
            (Banner.end_date == None) | (Banner.end_date >= now)
        )
    ).order_by(Banner.display_order, Banner.created_at.desc()).all()
    
    return banners

@router.get("/model", response_model=List[BannerResponse])
def get_model_banners(db: Session = Depends(get_db)):
    """Get only active model banners"""
    now = datetime.utcnow()
    
    banners = db.query(Banner).filter(
        and_(
            Banner.is_active == True,
            Banner.banner_type == BannerType.MODEL,
            (Banner.start_date == None) | (Banner.start_date <= now),
            (Banner.end_date == None) | (Banner.end_date >= now)
        )
    ).order_by(Banner.display_order, Banner.created_at.desc()).all()
    
    return banners

# Admin Endpoints (protected)

@router.get("/admin/all", response_model=List[BannerResponse])
def get_all_banners_admin(
    db: Session = Depends(get_db),
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    """
    Get all banners (including inactive) for admin panel
    Requires authentication
    """
    banners = db.query(Banner).order_by(
        Banner.banner_type, 
        Banner.display_order, 
        Banner.created_at.desc()
    ).all()
    
    return banners

@router.post("/admin/create", response_model=BannerActionResponse, status_code=status.HTTP_201_CREATED)
def create_banner(
    banner_data: BannerCreate,
    db: Session = Depends(get_db),
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    """
    Create a new banner
    Requires authentication
    """
    try:
        # Create new banner
        new_banner = Banner(
            title=banner_data.title,
            description=banner_data.description,
            image_url=banner_data.image_url,
            banner_type=banner_data.banner_type,
            link_url=banner_data.link_url,
            is_active=banner_data.is_active,
            display_order=banner_data.display_order,
            start_date=banner_data.start_date,
            end_date=banner_data.end_date
        )
        
        db.add(new_banner)
        db.commit()
        db.refresh(new_banner)
        
        return BannerActionResponse(
            success=True,
            message=f"Banner '{new_banner.title}' created successfully",
            banner=new_banner
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create banner: {str(e)}"
        )

@router.get("/admin/{banner_id}", response_model=BannerResponse)
def get_banner_by_id(
    banner_id: int,
    db: Session = Depends(get_db),
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    """
    Get a specific banner by ID
    Requires authentication
    """
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Banner with ID {banner_id} not found"
        )
    
    return banner

@router.put("/admin/{banner_id}", response_model=BannerActionResponse)
def update_banner(
    banner_id: int,
    banner_data: BannerUpdate,
    db: Session = Depends(get_db),
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    """
    Update an existing banner
    Requires authentication
    """
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Banner with ID {banner_id} not found"
        )
    
    try:
        # Update only provided fields
        update_data = banner_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(banner, field, value)
        
        db.commit()
        db.refresh(banner)
        
        return BannerActionResponse(
            success=True,
            message=f"Banner '{banner.title}' updated successfully",
            banner=banner
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update banner: {str(e)}"
        )

@router.delete("/admin/{banner_id}", response_model=BannerActionResponse)
def delete_banner(
    banner_id: int,
    db: Session = Depends(get_db),
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    """
    Delete a banner
    Requires authentication
    """
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Banner with ID {banner_id} not found"
        )
    
    try:
        banner_title = banner.title
        db.delete(banner)
        db.commit()
        
        return BannerActionResponse(
            success=True,
            message=f"Banner '{banner_title}' deleted successfully",
            banner=None
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete banner: {str(e)}"
        )

@router.patch("/admin/{banner_id}/toggle", response_model=BannerActionResponse)
def toggle_banner_status(
    banner_id: int,
    db: Session = Depends(get_db),
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    """
    Toggle banner active/inactive status
    Requires authentication
    """
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    
    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Banner with ID {banner_id} not found"
        )
    
    try:
        banner.is_active = not banner.is_active
        db.commit()
        db.refresh(banner)
        
        status_text = "activated" if banner.is_active else "deactivated"
        
        return BannerActionResponse(
            success=True,
            message=f"Banner '{banner.title}' {status_text} successfully",
            banner=banner
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle banner status: {str(e)}"
        )

