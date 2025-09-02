# coding: utf-8
"""
API router for ScrapydWeb FastAPI - Scrapyd API endpoints
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..common import get_response_from_view, json_dumps
import requests

router = APIRouter()

@router.get("/{node:int}/api/{opt}")
@router.get("/{node:int}/api/{opt}/{project}")
@router.get("/{node:int}/api/{opt}/{project}/{version_spider_job}")
@router.get("/api/{opt}")
@router.get("/api/{opt}/{project}")
@router.get("/api/{opt}/{project}/{version_spider_job}")
async def api_endpoint(
    request: Request,
    opt: str,
    node: int = 1,
    project: Optional[str] = None,
    version_spider_job: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Proxy API calls to Scrapyd servers
    Handles: listprojects, listversions, listspiders, listjobs, delproject, delversion, schedule, cancel, etc.
    """
    config = request.app.state.config
    scrapyd_servers = config.get('SCRAPYD_SERVERS', []) or ['127.0.0.1:6800']
    
    if node < 1 or node > len(scrapyd_servers):
        raise HTTPException(status_code=404, detail="Node not found")
    
    server = scrapyd_servers[node - 1]
    
    # Parse server URL and auth
    if '@' in server:
        auth_part, server_part = server.split('@', 1)
        if ':' in auth_part:
            username, password = auth_part.split(':', 1)
            auth = (username, password)
        else:
            auth = None
    else:
        server_part = server
        auth = None
    
    # Build Scrapyd API URL
    if '://' not in server_part:
        server_part = f'http://{server_part}'
    
    scrapyd_url = f"{server_part}/{opt}.json"
    
    # Prepare parameters
    params = {}
    query_params = dict(request.query_params)
    
    # Handle different API endpoints
    if opt == 'listprojects':
        pass  # No additional params needed
    elif opt == 'listversions':
        if project:
            params['project'] = project
    elif opt == 'listspiders':
        if project:
            params['project'] = project
        if version_spider_job:
            params['_version'] = version_spider_job
    elif opt == 'listjobs':
        if project:
            params['project'] = project
    elif opt == 'delproject':
        if project:
            params['project'] = project
    elif opt == 'delversion':
        if project:
            params['project'] = project
        if version_spider_job:
            params['version'] = version_spider_job
    elif opt == 'schedule':
        # Handle schedule parameters from query string
        params.update(query_params)
    elif opt == 'cancel':
        if project:
            params['project'] = project
        if version_spider_job:
            params['job'] = version_spider_job
    elif opt == 'daemonstatus':
        pass  # No additional params needed
    
    try:
        # Make request to Scrapyd
        if request.method == 'POST':
            # Get form data for POST requests
            form_data = await request.form()
            params.update(dict(form_data))
            response = requests.post(scrapyd_url, data=params, auth=auth, timeout=30)
        else:
            response = requests.get(scrapyd_url, params=params, auth=auth, timeout=30)
        
        response.raise_for_status()
        
        # Return JSON response
        try:
            json_data = response.json()
            return JSONResponse(content=json_data)
        except ValueError:
            # If not JSON, return text response
            return JSONResponse(content={"status": "ok", "message": response.text})
            
    except requests.exceptions.RequestException as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error", 
                "message": f"Failed to connect to Scrapyd server: {str(e)}",
                "server": server_part
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"API error: {str(e)}"
            }
        )

@router.post("/{node:int}/api/{opt}")
@router.post("/{node:int}/api/{opt}/{project}")
@router.post("/{node:int}/api/{opt}/{project}/{version_spider_job}")
@router.post("/api/{opt}")
@router.post("/api/{opt}/{project}")
@router.post("/api/{opt}/{project}/{version_spider_job}")
async def api_endpoint_post(
    request: Request,
    opt: str,
    node: int = 1,
    project: Optional[str] = None,
    version_spider_job: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle POST requests to API endpoints"""
    return await api_endpoint(request, opt, node, project, version_spider_job, db)

@router.get("/{node:int}/api/status")
@router.get("/api/status")
async def api_status(
    request: Request,
    node: int = 1
):
    """Get API and server status"""
    config = request.app.state.config
    scrapyd_servers = config.get('SCRAPYD_SERVERS', []) or ['127.0.0.1:6800']
    
    if node < 1 or node > len(scrapyd_servers):
        raise HTTPException(status_code=404, detail="Node not found")
    
    server = scrapyd_servers[node - 1]
    
    # Parse server URL
    if '@' in server:
        _, server_part = server.split('@', 1)
    else:
        server_part = server
    
    if '://' not in server_part:
        server_part = f'http://{server_part}'
    
    try:
        # Test connection to Scrapyd
        response = requests.get(f"{server_part}/daemonstatus.json", timeout=10)
        response.raise_for_status()
        daemon_status = response.json()
        
        return {
            "status": "ok",
            "node": node,
            "server": server_part,
            "scrapyd_status": daemon_status.get("status", "unknown"),
            "running_jobs": daemon_status.get("running", 0),
            "pending_jobs": daemon_status.get("pending", 0),
            "finished_jobs": daemon_status.get("finished", 0)
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "node": node,
                "server": server_part,
                "message": f"Cannot connect to Scrapyd: {str(e)}"
            }
        )
