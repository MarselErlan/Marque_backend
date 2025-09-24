"""
API v1 Routes
Main API endpoints organized by feature
"""

from fastapi import APIRouter

from ....routers.auth_router import router as auth_router
from ....routers.product_router import router as product_router
from ....routers.category_router import router as category_router
from ....routers.cart_router import router as cart_router
from ....routers.wishlist_router import router as wishlist_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(product_router, prefix="/products", tags=["products"])
api_router.include_router(category_router, prefix="/categories", tags=["categories"])
api_router.include_router(cart_router, prefix="/cart", tags=["cart"])
api_router.include_router(wishlist_router, prefix="/wishlist", tags=["wishlist"])
