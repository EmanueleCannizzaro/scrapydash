# coding: utf-8
"""
System router for ScrapydWeb FastAPI - settings and system info
Based on the previous Flask system views migration
"""
import platform
import os
import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Metadata
from ..common import handle_metadata
from ..__version__ import __version__
from ..vars import PYTHON_VERSION, SCRAPY_VERSION, SCRAPYD_VERSION

router = APIRouter()

class SettingsHelper:
    """Helper class for processing settings data"""
    
    @staticmethod
    def protect_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive information like passwords and tokens"""
        protected = data.copy()
        sensitive_keys = ['password', 'token', 'key', 'secret']
        
        for key, value in protected.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                if value:
                    protected[key] = '*' * 8
        return protected
    
    @staticmethod
    def format_json_settings(data: Dict[str, Any]) -> str:
        """Format settings as pretty JSON"""
        return json.dumps(data, indent=2, default=str)

@router.get("/{node:int}/settings/")
@router.get("/settings/")
async def settings_view(
    request: Request,
    node: int = 1,
    db: Session = Depends(get_db)
):
    """System settings page with comprehensive configuration display"""
    templates = request.app.state.templates
    config = request.app.state.config
    template_context = request.app.state.template_context()
    
    # Get all configuration categories
    settings_categories = {
        'ScrapydWeb Server': {
            'SCRAPYDASH_BIND': config.get('SCRAPYDASH_BIND', '0.0.0.0'),
            'SCRAPYDASH_PORT': config.get('SCRAPYDASH_PORT', 5000),
            'ENABLE_AUTH': config.get('ENABLE_AUTH', False),
            'USERNAME': config.get('USERNAME', ''),
            'PASSWORD': '********' if config.get('PASSWORD') else '',
            'ENABLE_HTTPS': config.get('ENABLE_HTTPS', False),
        },
        'Scrapy': {
            'SCRAPY_PROJECTS_DIR': config.get('SCRAPY_PROJECTS_DIR', ''),
            'SCRAPYD_LOGS_DIR': config.get('SCRAPYD_LOGS_DIR', ''),
            'SCRAPYD_ITEMS_DIR': config.get('SCRAPYD_ITEMS_DIR', ''),
        },
        'Scrapyd': {
            'SCRAPYD_SERVERS': config.get('SCRAPYD_SERVERS', []),
            'SCRAPYD_SERVERS_GROUPS': config.get('SCRAPYD_SERVERS_GROUPS', []),
            'SCRAPYD_SERVERS_AUTHS': ['********' if auth else None for auth in config.get('SCRAPYD_SERVERS_AUTHS', [])],
            'CHECK_SCRAPYD_SERVERS': config.get('CHECK_SCRAPYD_SERVERS', True),
        },
        'LogParser': {
            'ENABLE_LOGPARSER': config.get('ENABLE_LOGPARSER', False),
            'LOGPARSER_PID': handle_metadata().get('logparser_pid'),
        },
        'Timer Tasks': {
            'SCHEDULER_STATE': handle_metadata().get('scheduler_state', 1),
            'JOBS_TO_KEEP': config.get('JOBS_TO_KEEP', 100),
            'LOGS_TO_KEEP': config.get('LOGS_TO_KEEP', 100),
        },
        'Page Display': {
            'SHOW_SCRAPYD_ITEMS': config.get('SHOW_SCRAPYD_ITEMS', True),
            'SHOW_JOBS_JOB_COLUMN': config.get('SHOW_JOBS_JOB_COLUMN', True),
            'JOBS_PER_PAGE': config.get('JOBS_PER_PAGE', 100),
        },
        'System': {
            'DEBUG': config.get('DEBUG', False),
            'VERBOSE': config.get('VERBOSE', False),
            'DATA_PATH': config.get('DATA_PATH', ''),
            'DATABASE_URL': config.get('DATABASE_URL', ''),
        }
    }
    
    # Process sensitive data
    helper = SettingsHelper()
    for category, settings in settings_categories.items():
        settings_categories[category] = helper.protect_sensitive_data(settings)
    
    context = {
        "request": request,
        "node": node,
        "settings_categories": settings_categories,
        "scrapydash_version": __version__,
        "python_version": PYTHON_VERSION,
        "scrapy_version": SCRAPY_VERSION,
        "scrapyd_version": SCRAPYD_VERSION,
        "platform_info": platform.platform(),
        **template_context
    }
    
    return templates.TemplateResponse("settings.html", context)

@router.get("/{node:int}/system-info")
@router.get("/system-info")
async def system_info(
    request: Request,
    node: int = 1,
    db: Session = Depends(get_db)
):
    """System information API endpoint"""
    config = request.app.state.config
    
    return {
        "system": {
            "platform": platform.platform(),
            "python_version": PYTHON_VERSION,
            "scrapydash_version": __version__,
            "scrapy_version": SCRAPY_VERSION,
            "scrapyd_version": SCRAPYD_VERSION,
        },
        "configuration": {
            "scrapyd_servers": config.get('SCRAPYD_SERVERS', []),
            "servers_amount": len(config.get('SCRAPYD_SERVERS', [])),
            "auth_enabled": config.get('ENABLE_AUTH', False),
            "debug_mode": config.get('DEBUG', False),
        },
        "process": {
            "main_pid": handle_metadata().get('main_pid'),
            "logparser_pid": handle_metadata().get('logparser_pid'),
            "scheduler_state": handle_metadata().get('scheduler_state', 1),
        }
    }

@router.get("/{node:int}/metadata")
@router.get("/metadata")
async def metadata_view(
    request: Request,
    node: int = 1,
    db: Session = Depends(get_db)
):
    """System metadata endpoint"""
    metadata_record = db.query(Metadata).filter_by(version=__version__).first()
    
    if not metadata_record:
        return {"error": "Metadata not found"}
    
    return {
        "version": metadata_record.version,
        "main_pid": metadata_record.main_pid,
        "logparser_pid": metadata_record.logparser_pid,
        "poll_pid": metadata_record.poll_pid,
        "pageview": metadata_record.pageview,
        "scheduler_state": metadata_record.scheduler_state,
        "last_check_update": metadata_record.last_check_update_timestamp,
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "version": __version__,
        "timestamp": handle_metadata().get('last_check_update_timestamp')
    }

@router.get("/{node:int}/config")
@router.get("/config")
async def config_info(
    request: Request,
    node: int = 1
):
    """Configuration information endpoint"""
    config = request.app.state.config
    helper = SettingsHelper()
    
    # Return protected configuration
    protected_config = helper.protect_sensitive_data(dict(config))
    
    return {
        "config": protected_config,
        "node": node,
        "servers": config.get('SCRAPYD_SERVERS', [])
    }

@router.get("/{node:int}/server-status")
@router.get("/server-status")
async def server_status(
    request: Request,
    node: int = 1
):
    """Server status information"""
    config = request.app.state.config
    
    return {
        "node": node,
        "servers": config.get('SCRAPYD_SERVERS', []),
        "bind": config.get('SCRAPYDASH_BIND', '0.0.0.0'),
        "port": config.get('SCRAPYDASH_PORT', 5000),
        "auth_enabled": config.get('ENABLE_AUTH', False),
        "https_enabled": config.get('ENABLE_HTTPS', False),
    }

@router.get("/{node:int}/logs-info")
@router.get("/logs-info")
async def logs_info(
    request: Request,
    node: int = 1
):
    """Log directory and configuration information"""
    config = request.app.state.config
    
    logs_info = {
        "scrapyd_logs_dir": config.get('SCRAPYD_LOGS_DIR', ''),
        "scrapyd_items_dir": config.get('SCRAPYD_ITEMS_DIR', ''),
        "enable_logparser": config.get('ENABLE_LOGPARSER', False),
        "logparser_pid": handle_metadata().get('logparser_pid'),
    }
    
    # Check if directories exist
    for key, path in logs_info.items():
        if key.endswith('_dir') and path:
            logs_info[f"{key}_exists"] = os.path.exists(path)
    
    return logs_info

@router.post("/{node:int}/restart-scheduler")
@router.post("/restart-scheduler")
async def restart_scheduler(
    request: Request,
    node: int = 1
):
    """Restart the task scheduler"""
    try:
        # This would integrate with APScheduler when implemented
        # For now, just return success
        return {
            "status": "success",
            "message": "Scheduler restart requested",
            "node": node
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to restart scheduler: {str(e)}",
            "node": node
        }
