# coding: utf-8
import argparse
import logging
import os
import sys
import uvicorn

from ..main import create_app
from ..__version__ import __description__, __version__
from ..common import find_scrapydash_settings_py, handle_metadata
from ..vars import ROOT_DIR, SCRAPYDASH_SETTINGS_PY

logger = logging.getLogger(__name__)

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
