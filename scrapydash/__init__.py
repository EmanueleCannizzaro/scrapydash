# coding: utf-8
import logging
from logging.config import dictConfig
import platform
import re
import time
import traceback

# Removed Flask imports - now using FastAPI
# from flask import Flask, current_app, render_template, url_for
# from flask_compress import Compress
# from logparser import __version__ as LOGPARSER_VERSION

# from .__version__ import __url__, __version__
from .common import handle_metadata
# Removed Flask-SQLAlchemy import
# from .models import Metadata, db
from .vars import PYTHON_VERSION, SCRAPY_VERSION, SCRAPYD_VERSION, SQLALCHEMY_BINDS, SQLALCHEMY_DATABASE_URI
# from .utils.scheduler import scheduler

# Configure logging for FastAPI
logging.getLogger('sqlalchemy.engine.base.Engine').setLevel(logging.WARNING)
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)-8s in %(name)s: %(message)s',
    }},
    'handlers': {'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    }
})

# This file is kept for backward compatibility but Flask functionality moved to app.py
# The create_app function is now in app.py for FastAPI

def internal_server_error(error):
    """Legacy function - moved to FastAPI exception handler in app.py"""
    kwargs = dict(
        error=error,
        traceback=traceback.format_exc(),
        url_issues=__url__ + '/issues',
        os=platform.platform(),
        python_version=PYTHON_VERSION,
        scrapydweb_version=__version__,
        logparser_version=LOGPARSER_VERSION,
        scrapy_version=SCRAPY_VERSION,
        scrapyd_version=SCRAPYD_VERSION,
    )
    return kwargs

# Legacy Flask functions - functionality moved to FastAPI app.py
def create_app(test_config=None):
    """
    Legacy Flask app factory - now redirects to FastAPI
    This is kept for backward compatibility with existing imports
    """
    try:
        from .app import create_app as create_fastapi_app
        return create_fastapi_app(test_config)
    except ImportError as e:
        print(f"FastAPI components not available: {e}")
        print("For FastAPI version, use: python -m scrapydweb.run_fastapi")
        
        # Return a minimal app object to prevent crashes
        class MinimalConfig:
            def __init__(self):
                self.data = {}
            
            def from_pyfile(self, filename):
                """Mock Flask config.from_pyfile method"""
                import os
                if os.path.exists(filename):
                    # Execute the config file and extract uppercase variables
                    config_vars = {}
                    with open(filename) as f:
                        exec(f.read(), config_vars)
                    
                    # Add uppercase variables to config
                    for key, value in config_vars.items():
                        if key.isupper():
                            self.data[key] = value
                    return True
                return False
            
            def get(self, key, default=None):
                return self.data.get(key, default)
            
            def __getitem__(self, key):
                return self.data[key]
            
            def __setitem__(self, key, value):
                self.data[key] = value
            
            def __contains__(self, key):
                return key in self.data
        
        class MinimalApp:
            def __init__(self):
                self.config = MinimalConfig()
            
            def run(self, **kwargs):
                print("Cannot run Flask app. Use 'python -m scrapydweb.run_fastapi' instead.")
        
        return MinimalApp()

def handle_db(app):
    """Legacy Flask database handler - replaced by FastAPI database.py"""
    pass

def handle_route(app):
    """Legacy Flask route handler - replaced by FastAPI routers"""
    pass

def handle_template_context(app):
    """Legacy Flask template context - replaced by FastAPI template context"""
    pass
