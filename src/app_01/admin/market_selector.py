"""
Market Selector for Admin Panel

Allows admins to choose which market database (KG or US) to work with.
All CRUD operations will use the selected market's database.
"""

from sqladmin import BaseView, expose
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse
from ..db.market_db import db_manager, Market
import logging

logger = logging.getLogger(__name__)


class MarketSelectorView(BaseView):
    """Market selection interface for admins"""
    
    name = "Market Selector"
    icon = "fa-solid fa-globe"
    
    @expose("/market-selector", methods=["GET", "POST"])
    async def market_selector(self, request: Request):
        """Display market selector and handle market selection"""
        
        # Check if user is authenticated
        if not request.session.get("token"):
            return RedirectResponse(url="/admin/login", status_code=302)
        
        # Handle POST request (market selection)
        if request.method == "POST":
            form = await request.form()
            selected_market = form.get("market")
            
            if selected_market in ["kg", "us"]:
                # Update session with selected market
                request.session["selected_market"] = selected_market
                logger.info(f"✅ Admin '{request.session.get('admin_username')}' selected market: {selected_market.upper()}")
                
                # Redirect to admin home
                return RedirectResponse(url="/admin", status_code=302)
        
        # Get current market from session (if any)
        current_market = request.session.get("selected_market", "kg")
        admin_username = request.session.get("admin_username", "Admin")
        
        # HTML for market selector page
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Select Market - Marque Admin</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }}
                
                .container {{
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    padding: 40px;
                    max-width: 600px;
                    width: 100%;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                }}
                
                .header h1 {{
                    color: #333;
                    font-size: 32px;
                    margin-bottom: 10px;
                }}
                
                .header p {{
                    color: #666;
                    font-size: 16px;
                }}
                
                .welcome {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    text-align: center;
                }}
                
                .welcome i {{
                    color: #667eea;
                    margin-right: 10px;
                }}
                
                .market-options {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                
                .market-card {{
                    background: #f8f9fa;
                    border: 3px solid transparent;
                    border-radius: 15px;
                    padding: 30px 20px;
                    text-align: center;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    position: relative;
                }}
                
                .market-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                }}
                
                .market-card.selected {{
                    border-color: #667eea;
                    background: #f0f3ff;
                }}
                
                .market-card input[type="radio"] {{
                    position: absolute;
                    opacity: 0;
                }}
                
                .market-card .flag {{
                    font-size: 48px;
                    margin-bottom: 15px;
                }}
                
                .market-card h3 {{
                    color: #333;
                    font-size: 20px;
                    margin-bottom: 8px;
                }}
                
                .market-card p {{
                    color: #666;
                    font-size: 14px;
                    margin-bottom: 10px;
                }}
                
                .market-card .badge {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 12px;
                    margin-top: 10px;
                }}
                
                .market-card.selected .badge {{
                    background: #28a745;
                }}
                
                .submit-btn {{
                    width: 100%;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 15px;
                    border-radius: 10px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }}
                
                .submit-btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
                }}
                
                .current-market {{
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                    margin-top: 20px;
                }}
                
                .info-box {{
                    background: #e3f2fd;
                    border-left: 4px solid #2196f3;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                
                .info-box i {{
                    color: #2196f3;
                    margin-right: 10px;
                }}
                
                .info-box p {{
                    color: #555;
                    font-size: 14px;
                    margin: 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1><i class="fas fa-globe"></i> Select Market</h1>
                    <p>Choose which database you want to manage</p>
                </div>
                
                <div class="welcome">
                    <i class="fas fa-user-shield"></i>
                    <strong>Welcome, {admin_username}!</strong>
                </div>
                
                <form method="POST">
                    <div class="market-options">
                        <label class="market-card {'selected' if current_market == 'kg' else ''}" for="market-kg">
                            <input type="radio" name="market" value="kg" id="market-kg" 
                                   {'checked' if current_market == 'kg' else ''}
                                   onchange="this.closest('form').querySelectorAll('.market-card').forEach(c => c.classList.remove('selected')); this.closest('.market-card').classList.add('selected');">
                            <div class="flag">🇰🇬</div>
                            <h3>Kyrgyzstan</h3>
                            <p>Кыргызстан</p>
                            <span class="badge">KG Database</span>
                        </label>
                        
                        <label class="market-card {'selected' if current_market == 'us' else ''}" for="market-us">
                            <input type="radio" name="market" value="us" id="market-us"
                                   {'checked' if current_market == 'us' else ''}
                                   onchange="this.closest('form').querySelectorAll('.market-card').forEach(c => c.classList.remove('selected')); this.closest('.market-card').classList.add('selected');">
                            <div class="flag">🇺🇸</div>
                            <h3>United States</h3>
                            <p>USA Market</p>
                            <span class="badge">US Database</span>
                        </label>
                    </div>
                    
                    <button type="submit" class="submit-btn">
                        <i class="fas fa-check"></i> Confirm Selection
                    </button>
                </form>
                
                <div class="current-market">
                    <i class="fas fa-database"></i> 
                    Currently managing: <strong>{current_market.upper()}</strong> database
                </div>
                
                <div class="info-box">
                    <i class="fas fa-info-circle"></i>
                    <p>All products, orders, and content you create will be saved to the selected market's database. You can switch markets anytime from the admin panel.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html)


class MarketSwitcherView(BaseView):
    """Quick market switcher in admin panel"""
    
    name = "🌍 Switch Market"
    icon = "fa-solid fa-globe"
    category = "⚙️ Settings"
    
    @expose("/switch-market", methods=["GET"])
    async def switch_market(self, request: Request):
        """Switch between markets"""
        
        # Check if user is authenticated
        if not request.session.get("token"):
            return RedirectResponse(url="/admin/login", status_code=302)
        
        # Get current market
        current_market = request.session.get("selected_market", "kg")
        
        # Toggle market
        new_market = "us" if current_market == "kg" else "kg"
        
        # Update session
        request.session["selected_market"] = new_market
        
        logger.info(f"✅ Admin '{request.session.get('admin_username')}' switched market: {current_market.upper()} → {new_market.upper()}")
        
        # Redirect back to market selector for confirmation
        return RedirectResponse(url="/admin/market-selector", status_code=302)


def get_current_market(request: Request) -> Market:
    """
    Get the current market from session.
    
    This function should be used by all admin views to determine
    which database to use for operations.
    """
    market_str = request.session.get("selected_market", "kg")
    
    if market_str == "us":
        return Market.US
    else:
        return Market.KG


def get_market_session(request: Request):
    """
    Get database session for the current market.
    
    Usage in admin views:
        db = next(get_market_session(request))
        try:
            # Perform database operations
            pass
        finally:
            db.close()
    """
    market = get_current_market(request)
    return db_manager.get_db_session(market)


def get_market_engine(request: Request):
    """
    Get database engine for the current market.
    
    This is used by SQLAdmin for queries.
    """
    market = get_current_market(request)
    return db_manager.get_engine(market)

