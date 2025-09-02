# coding: utf-8
import argparse
import logging
import os
import sys
import uvicorn
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

from .routers import api, system
from .auth import get_current_user_optional
from .scheduler import scheduler_manager
from .__version__ import __description__, __version__
from .common import find_scrapydweb_settings_py, handle_metadata
from .vars import ROOT_DIR, SCRAPYDWEB_SETTINGS_PY

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager"""
    # Startup
    print(f"Starting ScrapydWeb FastAPI v{__version__}")
    try:
        scheduler_manager.start()
        print("Scheduler started successfully")
    except Exception as e:
        print(f"Warning: Could not start scheduler: {e}")
    
    yield
    
    # Shutdown
    try:
        scheduler_manager.shutdown()
        print("Scheduler stopped")
    except Exception as e:
        print(f"Warning: Error stopping scheduler: {e}")


def create_app(test_config=None):
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="ScrapydWeb",
        description="Web UI for Scrapyd cluster management",
        version=__version__,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Setup templates
    template_path = os.path.join(os.path.dirname(__file__), "templates")
    templates = Jinja2Templates(directory=template_path)
    
    # Flask 'g' compatibility class
    class FlaskG:
        """Flask 'g' object compatibility class that supports attribute access"""
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    # Add Flask compatibility functions to Jinja2 environment
    def get_flashed_messages(with_categories=False, category_filter=[]):
        """Flask compatibility - return empty list for now"""
        if with_categories:
            return []  # Should return list of (category, message) tuples
        return []  # Should return list of messages
    
    def url_for(endpoint, **values):
        """Flask compatibility - basic URL generation"""
        # Basic URL mapping for common endpoints
        url_map = {
            'static': '/static',
            'index': '/1/',
            'servers': '/1/servers/',
            'jobs': '/1/jobs/',
            'schedule': '/1/schedule/',
            'deploy': '/1/deploy/',
        }
        base_url = url_map.get(endpoint, f'/{endpoint}/')
        if values:
            # Simple query string handling
            query = '&'.join(f'{k}={v}' for k, v in values.items())
            return f'{base_url}?{query}' if query else base_url
        return base_url
    
    # Add functions to Jinja2 globals
    templates.env.globals['get_flashed_messages'] = get_flashed_messages
    templates.env.globals['url_for'] = url_for
    
    # Setup static files
    static_path = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    # Setup app state for system router compatibility
    app.state.templates = templates
    app.state.config = {
        'SCRAPYDWEB_BIND': '0.0.0.0',
        'SCRAPYDWEB_PORT': 5000,
        'ENABLE_AUTH': False,
        'USERNAME': '',
        'PASSWORD': '',
        'ENABLE_HTTPS': False,
        'SCRAPY_PROJECTS_DIR': '/path/to/projects',
        'SCRAPYD_LOGS_DIR': '/path/to/logs',
        'SCRAPYD_ITEMS_DIR': '/path/to/items',
        'SCRAPYD_SERVERS': ["127.0.0.1:6800", "127.0.0.1:6801", "127.0.0.1:6802"],
        'SCRAPYD_SERVERS_GROUPS': ["Group 1"],
        'SCRAPYD_SERVERS_AUTHS': [None, None, None],
        'CHECK_SCRAPYD_SERVERS': True,
        'ENABLE_LOGPARSER': False,
        'JOBS_TO_KEEP': 100,
        'LOGS_TO_KEEP': 100,
        'SHOW_SCRAPYD_ITEMS': True,
        'SHOW_JOBS_JOB_COLUMN': True,
        'JOBS_PER_PAGE': 100,
        'DEBUG': False,
        'VERBOSE': False,
        'DATA_PATH': '',
        'DATABASE_URL': 'sqlite:///scrapydweb.db',
    }
    
    def get_template_context():
        """Template context factory for system router"""
        return {
            "GITHUB_URL": "https://github.com/my8100/scrapydweb",
            "SCRAPYDWEB_VERSION": __version__,
            "python_version": "3.8+",
            "scrapydweb_version": __version__,
            "scrapy_version": "2.5+",
            "scrapyd_version": "1.2+",
        }
    
    app.state.template_context = get_template_context
    
    # Include routers
    app.include_router(api.router, prefix="/api")
    app.include_router(system.router, prefix="/system")
    
    # Root route
    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        """Root endpoint - redirect to main page"""
        return RedirectResponse(url="/1/")
    
    @app.get("/1/", response_class=HTMLResponse)
    async def main_page(request: Request, user=get_current_user_optional):
        """Main ScrapydWeb page"""
        # Create Flask 'g' compatibility context
        g_context = FlaskG(
            IS_MOBILE=False,  # Default to desktop
            url_jobs_list=[f"/{i}/jobs/" for i in range(1, 6)],  # Default job URLs
            url_menu_servers="/1/servers/",
            url_menu_tasks="/1/tasks/",
            url_menu_jobs="/1/jobs/",
            url_menu_nodereports="/1/reports/",
            url_menu_clusterreports="/1/cluster/reports/",
            url_menu_deploy="/1/deploy/",
            url_menu_schedule="/1/schedule/",
            url_menu_projects="/1/projects/",
            url_menu_logs="/1/logs/",
            url_menu_items="/1/items/",
            url_menu_sendtext="/1/sendtext/",
            url_menu_parse="/1/parse/",
            url_menu_settings="/system/settings/",
            url_menu_mobileui="/1/mobileui/",
            url_daemonstatus="/api/daemonstatus/",
            scheduler_state_paused=False,
            scheduler_state_running=True,
        )
        
        # Static file URLs (placeholder values)
        static_context = {
            "static_css_style": "/static/v160/style.css",
            "static_js_icons_menu": "/static/v160/js/icons_menu.js",
            "static_css_icon_upload_icon_right": "/static/v160/css/icon_upload_icon_right.css",
            "static_css_dropdown_mobileui": "/static/v160/css/dropdown_mobileui.css",
            "static_css_dropdown": "/static/v160/css/dropdown.css",
            "static_css_element_ui_index": "/static/v160/css/element_ui_index.css",
            "static_js_github_buttons": "/static/v160/js/github_buttons.js",
            "static_icon": "/static/v160/favicon.ico",
            "static_icon_shortcut": "/static/v160/favicon.ico",
            "static_icon_apple_touch": "/static/v160/apple-touch-icon.png",
        }
        
        # Global template variables
        global_context = {
            "GITHUB_URL": "https://github.com/my8100/scrapydweb",
            "SCRAPYD_SERVERS_GROUPS": ["Group 1"],
            "SCRAPYD_SERVERS_AMOUNT": 1,
            "SCRAPYD_SERVERS": ["127.0.0.1:6800"],
            "SCRAPYD_SERVERS_PUBLIC_URLS": [""],
            "SHOW_SCRAPYD_ITEMS": True,
            "ENABLE_AUTH": False,
            "SCRAPYDWEB_VERSION": __version__,
            "DAEMONSTATUS_REFRESH_INTERVAL": 10,
            "node": 1,
        }
        
        return templates.TemplateResponse("scrapydweb/index.html", {
            "request": request,
            "version": __version__,
            "user": user,
            "g": g_context,
            **static_context,
            **global_context
        })
    
    @app.get("/1/servers/", response_class=HTMLResponse)
    async def servers_page(request: Request, user=get_current_user_optional):
        """Servers management page"""
        g_context = FlaskG(
            IS_MOBILE=False,
            url_menu_servers="/1/servers/",
            url_menu_jobs="/1/jobs/",
            url_menu_deploy="/1/deploy/",
            url_menu_schedule="/1/schedule/",
            url_menu_logs="/1/logs/",
            url_menu_settings="/system/settings/",
        )
        
        global_context = {
            "GITHUB_URL": "https://github.com/my8100/scrapydweb",
            "SCRAPYD_SERVERS_GROUPS": ["Group 1"],
            "SCRAPYD_SERVERS_AMOUNT": 3,
            "SCRAPYD_SERVERS": ["127.0.0.1:6800", "127.0.0.1:6801", "127.0.0.1:6802"],
            "SCRAPYD_SERVERS_PUBLIC_URLS": ["", "", ""],
            "ENABLE_AUTH": False,
            "SCRAPYDWEB_VERSION": __version__,
            "node": 1,
        }
        
        return templates.TemplateResponse("scrapydweb/servers.html", {
            "request": request,
            "user": user,
            "g": g_context,
            **global_context
        })
    
    @app.get("/1/jobs/", response_class=HTMLResponse)
    async def jobs_page(request: Request, user=get_current_user_optional):
        """Jobs management page"""
        g_context = FlaskG(
            IS_MOBILE=False,
            url_menu_servers="/1/servers/",
            url_menu_jobs="/1/jobs/",
            url_menu_deploy="/1/deploy/",
            url_menu_schedule="/1/schedule/",
            url_menu_logs="/1/logs/",
            url_menu_settings="/system/settings/",
        )
        
        global_context = {
            "GITHUB_URL": "https://github.com/my8100/scrapydweb",
            "SCRAPYD_SERVERS_GROUPS": ["Group 1"],
            "SCRAPYD_SERVERS_AMOUNT": 3,
            "SCRAPYD_SERVERS": ["127.0.0.1:6800", "127.0.0.1:6801", "127.0.0.1:6802"],
            "ENABLE_AUTH": False,
            "SCRAPYDWEB_VERSION": __version__,
            "node": 1,
        }
        
        return templates.TemplateResponse("scrapydweb/jobs.html", {
            "request": request,
            "user": user,
            "g": g_context,
            **global_context
        })
    
    @app.get("/1/schedule/", response_class=HTMLResponse)
    async def schedule_page(request: Request, user=get_current_user_optional):
        """Schedule spider page"""
        g_context = FlaskG(
            IS_MOBILE=False,
            url_menu_servers="/1/servers/",
            url_menu_jobs="/1/jobs/",
            url_menu_deploy="/1/deploy/",
            url_menu_schedule="/1/schedule/",
            url_menu_logs="/1/logs/",
            url_menu_settings="/system/settings/",
        )
        
        global_context = {
            "GITHUB_URL": "https://github.com/my8100/scrapydweb",
            "SCRAPYD_SERVERS_GROUPS": ["Group 1"],
            "SCRAPYD_SERVERS_AMOUNT": 3,
            "SCRAPYD_SERVERS": ["127.0.0.1:6800", "127.0.0.1:6801", "127.0.0.1:6802"],
            "ENABLE_AUTH": False,
            "SCRAPYDWEB_VERSION": __version__,
            "node": 1,
            "projects": ["project1", "project2", "project3"],
            "spiders": {"project1": ["spider1", "spider2"], "project2": ["spider3"], "project3": ["spider4", "spider5"]},
        }
        
        return templates.TemplateResponse("scrapydweb/schedule.html", {
            "request": request,
            "user": user,
            "g": g_context,
            **global_context
        })
    
    @app.get("/1/deploy/", response_class=HTMLResponse)
    async def deploy_page(request: Request, user=get_current_user_optional):
        """Deploy project page"""
        g_context = FlaskG(
            IS_MOBILE=False,
            url_menu_servers="/1/servers/",
            url_menu_jobs="/1/jobs/",
            url_menu_deploy="/1/deploy/",
            url_menu_schedule="/1/schedule/",
            url_menu_logs="/1/logs/",
            url_menu_settings="/system/settings/",
        )
        
        global_context = {
            "GITHUB_URL": "https://github.com/my8100/scrapydweb",
            "SCRAPYD_SERVERS_GROUPS": ["Group 1"],
            "SCRAPYD_SERVERS_AMOUNT": 3,
            "SCRAPYD_SERVERS": ["127.0.0.1:6800", "127.0.0.1:6801", "127.0.0.1:6802"],
            "ENABLE_AUTH": False,
            "SCRAPYDWEB_VERSION": __version__,
            "node": 1,
            "SCRAPY_PROJECTS_DIR": "/path/to/projects",
            "folders": ["project1", "project2", "project3"],
            "projects": ["project1", "project2", "project3"],
            "modification_times": ["2024-01-01_12-00-00", "2024-01-02_13-00-00", "2024-01-03_14-00-00"],
            "latest_folder": "project1",
            "url": "https://scrapyd.readthedocs.io/en/stable/api.html#addversion-json",
            "url_projects": "/1/projects/",
            "url_deploy_upload": "/1/deploy/upload/",
            "selected_nodes": [],
        }
        
        return templates.TemplateResponse("scrapydweb/deploy.html", {
            "request": request,
            "user": user,
            "g": g_context,
            **global_context
        })
    
    @app.get("/1/logs/", response_class=HTMLResponse)
    async def logs_page(request: Request, user=get_current_user_optional):
        """Logs page"""
        g_context = FlaskG(
            IS_MOBILE=False,
            url_menu_servers="/1/servers/",
            url_menu_jobs="/1/jobs/",
            url_menu_deploy="/1/deploy/",
            url_menu_schedule="/1/schedule/",
            url_menu_logs="/1/logs/",
            url_menu_settings="/system/settings/",
        )
        
        global_context = {
            "GITHUB_URL": "https://github.com/my8100/scrapydweb",
            "SCRAPYD_SERVERS_GROUPS": ["Group 1"],
            "SCRAPYD_SERVERS_AMOUNT": 3,
            "SCRAPYD_SERVERS": ["127.0.0.1:6800", "127.0.0.1:6801", "127.0.0.1:6802"],
            "ENABLE_AUTH": False,
            "SCRAPYDWEB_VERSION": __version__,
            "node": 1,
        }
        
        return templates.TemplateResponse("scrapydweb/logs.html", {
            "request": request,
            "user": user,
            "g": g_context,
            **global_context
        })
    
    @app.get("/1/settings/", response_class=HTMLResponse)
    async def settings_page(request: Request, user=get_current_user_optional):
        """Settings page - redirect to system settings"""
        return RedirectResponse(url="/system/settings/")
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "ok", "version": __version__}
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler"""
        return HTMLResponse(
            content=f"<h1>Internal Server Error</h1><p>{str(exc)}</p>",
            status_code=500
        )
    
    return app


# Create app instance for direct uvicorn access
app = create_app()


def main():
    """Main entry point for FastAPI version"""
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--version', action='version', version=__version__)
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger.info(f"Starting ScrapydWeb FastAPI v{__version__}")
    logger.info(f"Server will be available at http://{args.host}:{args.port}")
    logger.info(f"API documentation available at http://{args.host}:{args.port}/docs")
    
    # Create FastAPI app
    app = create_app()
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="debug" if args.debug else "info"
    )


if __name__ == "__main__":
    main()
