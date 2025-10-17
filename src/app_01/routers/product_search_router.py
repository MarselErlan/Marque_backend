"""
Product Search Analytics Router

API endpoints for search analytics and insights:
- Track search queries
- Popular searches
- Trending searches
- Zero-result searches (to improve catalog)
- Search suggestions
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..db import get_db
from ..models.products.product_filter import ProductSearch

router = APIRouter(prefix="/api/v1/search", tags=["Product Search"])


# ========================
# PYDANTIC SCHEMAS
# ========================

class SearchTermResponse(BaseModel):
    """Search term response"""
    id: int
    search_term: str
    search_count: int
    result_count: int
    last_searched: datetime
    
    class Config:
        from_attributes = True


class SearchStatsResponse(BaseModel):
    """Search statistics response"""
    total_searches: int
    unique_terms: int
    avg_results_per_search: float
    zero_result_searches: int
    most_popular_term: Optional[str] = None


class RecordSearchRequest(BaseModel):
    """Record search request"""
    search_term: str
    result_count: int = 0


# ========================
# SEARCH TRACKING API
# ========================

@router.post("/track")
def track_search(
    request: RecordSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Track a search query
    
    **Automatically tracks:**
    - Search term
    - Number of results found
    - Search timestamp
    - Increments search count
    
    **Use this endpoint:**
    When user performs a search to track analytics
    
    **Args:**
    - `search_term`: The search query
    - `result_count`: Number of products found
    
    **Returns:** Confirmation message
    """
    try:
        ProductSearch.record_search(db, request.search_term, request.result_count)
        
        return {
            "success": True,
            "message": "Search tracked successfully",
            "search_term": request.search_term,
            "result_count": request.result_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track search: {str(e)}")


# ========================
# POPULAR SEARCHES API
# ========================

@router.get("/popular", response_model=List[SearchTermResponse])
def get_popular_searches(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get most popular search terms
    
    **Use for:**
    - Search suggestions
    - Homepage "Popular Searches" section
    - SEO keywords
    
    **Args:**
    - `limit`: Number of results (1-100)
    
    **Returns:** Most searched terms sorted by count
    """
    searches = ProductSearch.get_popular_searches(db, limit)
    return [SearchTermResponse.from_orm(s) for s in searches]


@router.get("/recent", response_model=List[SearchTermResponse])
def get_recent_searches(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get most recent search terms
    
    **Use for:**
    - Real-time search trends
    - Admin dashboard
    
    **Args:**
    - `limit`: Number of results
    
    **Returns:** Recent searches sorted by timestamp
    """
    searches = ProductSearch.get_recent_searches(db, limit)
    return [SearchTermResponse.from_orm(s) for s in searches]


@router.get("/trending", response_model=List[SearchTermResponse])
def get_trending_searches(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get trending searches from last N days
    
    **Use for:**
    - "Trending Now" section
    - Marketing campaigns
    - Stock planning
    
    **Args:**
    - `days`: Number of days to look back (1-90)
    - `limit`: Number of results
    
    **Returns:** Trending searches in specified period
    """
    searches = ProductSearch.get_trending_searches(db, days, limit)
    return [SearchTermResponse.from_orm(s) for s in searches]


# ========================
# ZERO-RESULT SEARCHES API
# ========================

@router.get("/zero-results", response_model=List[SearchTermResponse])
def get_zero_result_searches(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get searches that returned no results
    
    **Critical for business:**
    - Identify missing products
    - Find new product opportunities
    - Improve catalog completeness
    - Add synonyms/translations
    
    **Example use cases:**
    1. User searches "winter jacket" → 0 results
    2. You add winter jackets to catalog
    3. Next search finds products!
    
    **Args:**
    - `limit`: Number of results
    
    **Returns:** Failed searches sorted by popularity
    """
    searches = ProductSearch.get_zero_result_searches(db, limit)
    return [SearchTermResponse.from_orm(s) for s in searches]


# ========================
# SEARCH STATISTICS API
# ========================

@router.get("/stats", response_model=SearchStatsResponse)
def get_search_stats(db: Session = Depends(get_db)):
    """
    Get comprehensive search statistics
    
    **Returns:**
    - Total number of searches
    - Unique search terms
    - Average results per search
    - Number of zero-result searches
    - Most popular search term
    
    **Use for:**
    - Dashboard metrics
    - Business intelligence
    - Performance tracking
    """
    from sqlalchemy import func
    
    # Total searches (sum of all search counts)
    total = db.query(func.sum(ProductSearch.search_count)).scalar() or 0
    
    # Unique terms
    unique = db.query(func.count(ProductSearch.id)).scalar() or 0
    
    # Average results
    avg_results = db.query(func.avg(ProductSearch.result_count)).filter(
        ProductSearch.result_count > 0
    ).scalar() or 0
    
    # Zero result searches
    zero_results = db.query(func.count(ProductSearch.id)).filter(
        ProductSearch.result_count == 0
    ).scalar() or 0
    
    # Most popular term
    most_popular = db.query(ProductSearch).order_by(
        ProductSearch.search_count.desc()
    ).first()
    
    return SearchStatsResponse(
        total_searches=total,
        unique_terms=unique,
        avg_results_per_search=round(avg_results, 2),
        zero_result_searches=zero_results,
        most_popular_term=most_popular.search_term if most_popular else None
    )


# ========================
# SEARCH SUGGESTIONS API
# ========================

@router.get("/suggestions")
def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on partial query
    
    **Real-time autocomplete:**
    User types "win" → Suggests "winter jacket", "windbreaker"
    
    **Args:**
    - `q`: Partial search query (min 2 characters)
    - `limit`: Number of suggestions
    
    **Returns:** Matching search terms sorted by popularity
    """
    suggestions = db.query(ProductSearch).filter(
        ProductSearch.search_term.ilike(f"%{q}%"),
        ProductSearch.result_count > 0  # Only suggest searches that found results
    ).order_by(
        ProductSearch.search_count.desc()
    ).limit(limit).all()
    
    return {
        "query": q,
        "suggestions": [
            {
                "term": s.search_term,
                "search_count": s.search_count,
                "result_count": s.result_count
            }
            for s in suggestions
        ]
    }


# ========================
# SEARCH INSIGHTS API
# ========================

@router.get("/insights")
def get_search_insights(db: Session = Depends(get_db)):
    """
    Get actionable search insights
    
    **Provides:**
    - Top 5 popular searches
    - Top 5 zero-result searches
    - Top 5 trending searches
    - Key metrics
    
    **Use for:**
    - Admin dashboard
    - Weekly reports
    - Business decisions
    """
    return {
        "popular_searches": [
            SearchTermResponse.from_orm(s)
            for s in ProductSearch.get_popular_searches(db, 5)
        ],
        "zero_result_searches": [
            SearchTermResponse.from_orm(s)
            for s in ProductSearch.get_zero_result_searches(db, 5)
        ],
        "trending_searches": [
            SearchTermResponse.from_orm(s)
            for s in ProductSearch.get_trending_searches(db, 7, 5)
        ],
        "recommendations": generate_recommendations(db)
    }


def generate_recommendations(db: Session) -> List[str]:
    """Generate actionable recommendations based on search data"""
    recommendations = []
    
    # Check for zero-result searches
    zero_results = ProductSearch.get_zero_result_searches(db, 3)
    if zero_results:
        top_term = zero_results[0].search_term
        recommendations.append(
            f"🎯 Add products for '{top_term}' - searched {zero_results[0].search_count} times with no results"
        )
    
    # Check for trending searches
    trending = ProductSearch.get_trending_searches(db, 7, 3)
    if trending:
        top_trending = trending[0].search_term
        recommendations.append(
            f"📈 '{top_trending}' is trending - consider featuring these products"
        )
    
    # Check search success rate
    from sqlalchemy import func
    total = db.query(func.count(ProductSearch.id)).scalar() or 1
    zero_count = db.query(func.count(ProductSearch.id)).filter(
        ProductSearch.result_count == 0
    ).scalar() or 0
    
    success_rate = ((total - zero_count) / total) * 100
    
    if success_rate < 70:
        recommendations.append(
            f"⚠️ Search success rate is {success_rate:.1f}% - improve product catalog or search algorithm"
        )
    elif success_rate > 90:
        recommendations.append(
            f"✅ Excellent search success rate: {success_rate:.1f}%"
        )
    
    return recommendations


# ========================
# SEARCH ADMIN API
# ========================

@router.delete("/admin/clear-old-searches")
def clear_old_searches(
    days: int = Query(90, ge=30, le=365),
    db: Session = Depends(get_db)
):
    """
    Clear old search records (admin only)
    
    **Use for:**
    - Database maintenance
    - Remove outdated search data
    
    **Args:**
    - `days`: Delete searches older than N days (30-365)
    
    **Returns:** Number of deleted records
    """
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    deleted = db.query(ProductSearch).filter(
        ProductSearch.last_searched < cutoff_date
    ).delete()
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Deleted {deleted} search records older than {days} days",
        "deleted_count": deleted
    }

