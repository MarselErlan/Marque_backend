// Market Indicator - Custom JavaScript for Admin Panel
// This script injects a market indicator badge into the admin sidebar

(function() {
    'use strict';
    
    console.log('🎯 Market Indicator Script Loading...');
    
    // Function to get current market from session (passed via template or API)
    function getCurrentMarket() {
        // Try to get from window object (will be set by backend)
        if (window.ADMIN_MARKET) {
            return window.ADMIN_MARKET;
        }
        
        // Try to get from localStorage as fallback
        const market = localStorage.getItem('admin_market');
        return market || 'kg'; // default to KG
    }
    
    // Function to create market indicator HTML
    function createMarketIndicator(market) {
        const isUS = market === 'us';
        const marketClass = isUS ? 'market-us' : 'market-kg';
        
        const flag = isUS ? '🇺🇸' : '🇰🇬';
        const name = isUS ? 'UNITED STATES' : 'KYRGYZSTAN';
        const currency = isUS ? '$ USD • English' : 'сом KGS • Русский';
        const dbLabel = isUS ? 'US DB' : 'KG DB';
        
        return `
            <div class="market-indicator-badge ${marketClass}">
                <div class="market-indicator-content">
                    <div class="market-indicator-main">
                        <span class="market-indicator-flag">${flag}</span>
                        <div class="market-indicator-info">
                            <div class="market-indicator-name">${name}</div>
                            <div class="market-indicator-details">${currency}</div>
                        </div>
                    </div>
                    <div class="market-indicator-label">${dbLabel}</div>
                </div>
                <div class="market-indicator-status">
                    <div class="market-indicator-dot"></div>
                    <span class="market-indicator-status-text">Connected</span>
                </div>
            </div>
        `;
    }
    
    // Function to inject market indicator into sidebar
    function injectMarketIndicator() {
        console.log('🔍 Looking for sidebar...');
        
        // Try multiple selectors to find the sidebar
        const selectors = [
            '.sidebar',
            '.admin-sidebar', 
            'aside',
            '[role="navigation"]',
            '.nav-sidebar',
            '#sidebar'
        ];
        
        let sidebar = null;
        for (const selector of selectors) {
            sidebar = document.querySelector(selector);
            if (sidebar) {
                console.log(`✅ Found sidebar with selector: ${selector}`);
                break;
            }
        }
        
        if (!sidebar) {
            console.warn('❌ Sidebar not found, trying alternative approach...');
            // If sidebar not found, try to find the brand/logo area
            const brand = document.querySelector('.navbar-brand, .brand, [class*="brand"]');
            if (brand && brand.parentElement) {
                sidebar = brand.parentElement;
                console.log('✅ Using brand parent as insertion point');
            } else {
                console.error('❌ Could not find suitable location for market indicator');
                return false;
            }
        }
        
        // Check if indicator already exists
        if (document.querySelector('.market-indicator-badge')) {
            console.log('ℹ️  Market indicator already exists');
            return true;
        }
        
        // Get current market
        const market = getCurrentMarket();
        console.log(`📊 Current Market: ${market.toUpperCase()}`);
        
        // Create and insert the indicator
        const indicatorHTML = createMarketIndicator(market);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = indicatorHTML;
        const indicator = tempDiv.firstElementChild;
        
        // Insert after the brand/logo (or at the top of sidebar)
        const brand = sidebar.querySelector('.navbar-brand, .brand, [class*="brand"]');
        if (brand) {
            brand.parentNode.insertBefore(indicator, brand.nextSibling);
            console.log('✅ Market indicator inserted after brand');
        } else {
            sidebar.insertBefore(indicator, sidebar.firstChild);
            console.log('✅ Market indicator inserted at top of sidebar');
        }
        
        return true;
    }
    
    // Try to inject immediately
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            console.log('📄 DOM Content Loaded, injecting market indicator...');
            setTimeout(injectMarketIndicator, 100);
        });
    } else {
        console.log('📄 DOM already loaded, injecting market indicator...');
        setTimeout(injectMarketIndicator, 100);
    }
    
    // Also try after a delay in case the sidebar is loaded dynamically
    setTimeout(function() {
        if (!document.querySelector('.market-indicator-badge')) {
            console.log('🔄 Retrying market indicator injection...');
            injectMarketIndicator();
        }
    }, 1000);
    
    // Log success
    console.log('✅ Market Indicator Script Loaded');
    
    // Expose market info to console for debugging
    window.MARKET_INFO = {
        current: getCurrentMarket(),
        timestamp: new Date().toISOString()
    };
    console.log('🌍 Market Info:', window.MARKET_INFO);
})();

