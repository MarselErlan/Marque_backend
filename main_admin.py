"""
Marque Website Content Admin - SQLAdmin Interface
This is the main entry point for the website content admin interface.
"""

import uvicorn
from fastapi import FastAPI
from src.app_01.admin.admin_app import create_website_content_admin_app
from src.app_01.db import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app with SQLAdmin
app = create_website_content_admin_app()

if __name__ == "__main__":
    uvicorn.run(
        "main_admin:app",
        host="0.0.0.0",
        port=8001,  # Different port for admin interface
        reload=True,
        log_level="info"
    )
