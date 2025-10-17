"""
Admin Analytics Router

API endpoints for admin dashboard analytics and statistics:
- Daily order statistics
- Sales metrics
- Performance tracking
- Business intelligence
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date, timedelta
from ..db import get_db_session
from ..models.admins.order_management.order_admin_stats import OrderAdminStats

router = APIRouter(prefix="/api/v1/admin/analytics", tags=["Admin Analytics"])


# ========================
# PYDANTIC SCHEMAS
# ========================

class DailyStatsResponse(BaseModel):
    """Daily statistics response"""
    date: date
    today_orders_count: int
    today_orders_pending: int
    today_orders_processing: int
    today_orders_shipped: int
    today_orders_delivered: int
    today_orders_cancelled: int
    today_sales_total: float
    today_sales_count: int
    avg_order_value: float
    completion_rate: float
    formatted_sales_total: str
    
    class Config:
        from_attributes = True


class StatsRangeResponse(BaseModel):
    """Statistics range response"""
    start_date: date
    end_date: date
    total_days: int
    stats: List[DailyStatsResponse]
    summary: dict


class DashboardOverviewResponse(BaseModel):
    """Dashboard overview response"""
    today: DailyStatsResponse
    yesterday: Optional[DailyStatsResponse]
    this_week: dict
    this_month: dict
    best_sales_days: List[DailyStatsResponse]


# ========================
# DAILY STATISTICS API
# ========================

@router.get("/today", response_model=DailyStatsResponse)
def get_today_stats(db: Session = Depends(get_db_session)):
    """
    Get today's statistics
    
    **Returns:**
    - Today's order count
    - Orders by status
    - Sales total
    - Average order value
    - Completion rate
    
    **Use for:**
    - Real-time dashboard
    - Performance monitoring
    """
    today = date.today()
    stats = OrderAdminStats.get_stats_by_date(db, today)
    
    if not stats:
        # Return empty stats if no data
        return DailyStatsResponse(
            date=today,
            today_orders_count=0,
            today_orders_pending=0,
            today_orders_processing=0,
            today_orders_shipped=0,
            today_orders_delivered=0,
            today_orders_cancelled=0,
            today_sales_total=0.0,
            today_sales_count=0,
            avg_order_value=0.0,
            completion_rate=0.0,
            formatted_sales_total="0.0 KGS"
        )
    
    return DailyStatsResponse.from_orm(stats)


@router.get("/date/{target_date}", response_model=DailyStatsResponse)
def get_stats_by_date(
    target_date: date,
    db: Session = Depends(get_db_session)
):
    """
    Get statistics for a specific date
    
    **Args:**
    - `target_date`: Date in YYYY-MM-DD format
    
    **Returns:** Statistics for that date
    """
    stats = OrderAdminStats.get_stats_by_date(db, target_date)
    
    if not stats:
        raise HTTPException(status_code=404, detail=f"No statistics found for {target_date}")
    
    return DailyStatsResponse.from_orm(stats)


# ========================
# RANGE STATISTICS API
# ========================

@router.get("/range", response_model=StatsRangeResponse)
def get_stats_range(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db_session)
):
    """
    Get statistics for a date range
    
    **Perfect for:**
    - Weekly reports
    - Monthly summaries
    - Custom date ranges
    
    **Args:**
    - `start_date`: Range start
    - `end_date`: Range end
    
    **Returns:**
    - Daily stats for each day
    - Aggregated summary
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")
    
    stats_list = OrderAdminStats.get_stats_range(db, start_date, end_date)
    
    # Calculate summary
    total_orders = sum(s.today_orders_count for s in stats_list)
    total_sales = sum(s.today_sales_total for s in stats_list)
    total_delivered = sum(s.today_orders_delivered for s in stats_list)
    total_cancelled = sum(s.today_orders_cancelled for s in stats_list)
    
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    completion_rate = (total_delivered / total_orders * 100) if total_orders > 0 else 0
    
    summary = {
        "total_orders": total_orders,
        "total_sales": total_sales,
        "total_delivered": total_delivered,
        "total_cancelled": total_cancelled,
        "avg_order_value": round(avg_order_value, 2),
        "completion_rate": round(completion_rate, 2),
        "formatted_total_sales": f"{total_sales} KGS"
    }
    
    return StatsRangeResponse(
        start_date=start_date,
        end_date=end_date,
        total_days=(end_date - start_date).days + 1,
        stats=[DailyStatsResponse.from_orm(s) for s in stats_list],
        summary=summary
    )


@router.get("/recent", response_model=List[DailyStatsResponse])
def get_recent_stats(
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
    db: Session = Depends(get_db_session)
):
    """
    Get statistics for last N days
    
    **Args:**
    - `days`: Number of days (1-90)
    
    **Returns:** Daily stats for last N days sorted by date (newest first)
    """
    stats = OrderAdminStats.get_recent_stats(db, days)
    return [DailyStatsResponse.from_orm(s) for s in stats]


# ========================
# BEST PERFORMANCE API
# ========================

@router.get("/best-sales-days", response_model=List[DailyStatsResponse])
def get_best_sales_days(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db_session)
):
    """
    Get days with highest sales
    
    **Use for:**
    - Identifying peak sales days
    - Pattern analysis
    - Staffing decisions
    - Marketing timing
    
    **Args:**
    - `limit`: Number of top days
    
    **Returns:** Top sales days sorted by revenue
    """
    stats = OrderAdminStats.get_best_sales_days(db, limit)
    return [DailyStatsResponse.from_orm(s) for s in stats]


# ========================
# DASHBOARD OVERVIEW API
# ========================

@router.get("/dashboard", response_model=DashboardOverviewResponse)
def get_dashboard_overview(db: Session = Depends(get_db_session)):
    """
    Get complete dashboard overview
    
    **Returns:**
    - Today's stats
    - Yesterday's stats
    - This week summary
    - This month summary
    - Top 5 best sales days
    
    **Perfect for:**
    - Admin dashboard homepage
    - Quick business overview
    - Performance snapshot
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    week_start = today - timedelta(days=6)
    month_start = today.replace(day=1)
    
    # Get today's stats
    today_stats = OrderAdminStats.get_stats_by_date(db, today)
    yesterday_stats = OrderAdminStats.get_stats_by_date(db, yesterday)
    
    # Get week stats
    week_stats = OrderAdminStats.get_stats_range(db, week_start, today)
    week_summary = {
        "total_orders": sum(s.today_orders_count for s in week_stats),
        "total_sales": sum(s.today_sales_total for s in week_stats),
        "avg_daily_orders": round(sum(s.today_orders_count for s in week_stats) / 7, 1),
        "avg_daily_sales": round(sum(s.today_sales_total for s in week_stats) / 7, 2)
    }
    
    # Get month stats
    month_stats = OrderAdminStats.get_stats_range(db, month_start, today)
    month_summary = {
        "total_orders": sum(s.today_orders_count for s in month_stats),
        "total_sales": sum(s.today_sales_total for s in month_stats),
        "days_in_period": len(month_stats),
        "avg_daily_orders": round(sum(s.today_orders_count for s in month_stats) / len(month_stats), 1) if month_stats else 0,
        "avg_daily_sales": round(sum(s.today_sales_total for s in month_stats) / len(month_stats), 2) if month_stats else 0
    }
    
    # Get best sales days
    best_days = OrderAdminStats.get_best_sales_days(db, 5)
    
    return DashboardOverviewResponse(
        today=DailyStatsResponse.from_orm(today_stats) if today_stats else None,
        yesterday=DailyStatsResponse.from_orm(yesterday_stats) if yesterday_stats else None,
        this_week=week_summary,
        this_month=month_summary,
        best_sales_days=[DailyStatsResponse.from_orm(s) for s in best_days]
    )


# ========================
# TRENDS & INSIGHTS API
# ========================

@router.get("/trends")
def get_trends(
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db_session)
):
    """
    Get trends and insights
    
    **Analyzes:**
    - Sales trends
    - Order trends
    - Day-of-week patterns
    - Growth rates
    
    **Args:**
    - `days`: Period to analyze (7-90 days)
    
    **Returns:** Trend analysis and insights
    """
    stats = OrderAdminStats.get_recent_stats(db, days)
    
    if not stats:
        return {
            "message": "No data available for trend analysis",
            "period_days": days
        }
    
    # Calculate trends
    total_orders = sum(s.today_orders_count for s in stats)
    total_sales = sum(s.today_sales_total for s in stats)
    avg_daily_orders = total_orders / len(stats)
    avg_daily_sales = total_sales / len(stats)
    
    # Get recent vs older comparison
    mid_point = len(stats) // 2
    recent_half = stats[:mid_point]
    older_half = stats[mid_point:]
    
    recent_avg_orders = sum(s.today_orders_count for s in recent_half) / len(recent_half) if recent_half else 0
    older_avg_orders = sum(s.today_orders_count for s in older_half) / len(older_half) if older_half else 0
    
    recent_avg_sales = sum(s.today_sales_total for s in recent_half) / len(recent_half) if recent_half else 0
    older_avg_sales = sum(s.today_sales_total for s in older_half) / len(older_half) if older_half else 0
    
    order_growth = ((recent_avg_orders - older_avg_orders) / older_avg_orders * 100) if older_avg_orders > 0 else 0
    sales_growth = ((recent_avg_sales - older_avg_sales) / older_avg_sales * 100) if older_avg_sales > 0 else 0
    
    # Day of week analysis
    day_of_week_stats = {}
    for stat in stats:
        dow = stat.date.strftime("%A")
        if dow not in day_of_week_stats:
            day_of_week_stats[dow] = {"orders": 0, "sales": 0, "count": 0}
        day_of_week_stats[dow]["orders"] += stat.today_orders_count
        day_of_week_stats[dow]["sales"] += stat.today_sales_total
        day_of_week_stats[dow]["count"] += 1
    
    # Calculate averages
    day_averages = {}
    for dow, data in day_of_week_stats.items():
        day_averages[dow] = {
            "avg_orders": round(data["orders"] / data["count"], 1),
            "avg_sales": round(data["sales"] / data["count"], 2)
        }
    
    # Find best day
    best_day = max(day_averages.items(), key=lambda x: x[1]["avg_sales"])[0] if day_averages else None
    
    return {
        "period": {
            "days": days,
            "start_date": stats[-1].date if stats else None,
            "end_date": stats[0].date if stats else None
        },
        "overall": {
            "total_orders": total_orders,
            "total_sales": round(total_sales, 2),
            "avg_daily_orders": round(avg_daily_orders, 1),
            "avg_daily_sales": round(avg_daily_sales, 2)
        },
        "growth": {
            "order_growth_percentage": round(order_growth, 1),
            "sales_growth_percentage": round(sales_growth, 1),
            "trend": "📈 Growing" if sales_growth > 0 else "📉 Declining" if sales_growth < 0 else "➡️ Stable"
        },
        "best_day_of_week": {
            "day": best_day,
            "avg_sales": day_averages[best_day]["avg_sales"] if best_day else 0
        },
        "day_of_week_performance": day_averages,
        "insights": generate_insights(order_growth, sales_growth, avg_daily_sales, day_averages)
    }


def generate_insights(order_growth: float, sales_growth: float, avg_daily_sales: float, day_averages: dict) -> List[str]:
    """Generate actionable insights from data"""
    insights = []
    
    # Growth insights
    if sales_growth > 20:
        insights.append(f"🚀 Excellent growth! Sales increased {sales_growth:.1f}% - keep up the momentum!")
    elif sales_growth > 10:
        insights.append(f"📈 Good growth of {sales_growth:.1f}% - consider scaling marketing efforts")
    elif sales_growth < -10:
        insights.append(f"⚠️ Sales declined {abs(sales_growth):.1f}% - analyze what changed")
    
    # Order insights
    if order_growth > 15:
        insights.append(f"🎯 Order volume up {order_growth:.1f}% - customer acquisition is working")
    elif order_growth < -15:
        insights.append(f"📊 Order volume down {abs(order_growth):.1f}% - review marketing channels")
    
    # Performance insights
    if avg_daily_sales > 50000:
        insights.append("💰 Strong daily sales - consider expanding inventory")
    elif avg_daily_sales < 10000:
        insights.append("💡 Low daily sales - focus on customer acquisition")
    
    # Day of week insights
    if day_averages:
        best_day = max(day_averages.items(), key=lambda x: x[1]["avg_sales"])
        worst_day = min(day_averages.items(), key=lambda x: x[1]["avg_sales"])
        insights.append(f"📅 Best day: {best_day[0]} - run promotions then!")
        insights.append(f"📅 Slowest day: {worst_day[0]} - boost with special offers")
    
    return insights


# ========================
# EXPORT DATA API
# ========================

@router.get("/export")
def export_stats(
    start_date: date = Query(...),
    end_date: date = Query(...),
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db_session)
):
    """
    Export statistics data
    
    **Formats:**
    - JSON: Default, structured data
    - CSV: For Excel/spreadsheet analysis
    
    **Args:**
    - `start_date`: Range start
    - `end_date`: Range end
    - `format`: "json" or "csv"
    
    **Returns:** Statistics in requested format
    """
    stats = OrderAdminStats.get_stats_range(db, start_date, end_date)
    
    if format == "csv":
        # Generate CSV
        csv_lines = ["Date,Orders,Pending,Processing,Shipped,Delivered,Cancelled,Sales,Avg Order Value,Completion Rate"]
        for s in stats:
            csv_lines.append(
                f"{s.date},{s.today_orders_count},{s.today_orders_pending},{s.today_orders_processing},"
                f"{s.today_orders_shipped},{s.today_orders_delivered},{s.today_orders_cancelled},"
                f"{s.today_sales_total},{s.avg_order_value},{s.completion_rate}"
            )
        
        return {
            "format": "csv",
            "data": "\n".join(csv_lines)
        }
    else:
        # Return JSON
        return {
            "format": "json",
            "start_date": start_date,
            "end_date": end_date,
            "record_count": len(stats),
            "data": [DailyStatsResponse.from_orm(s) for s in stats]
        }

