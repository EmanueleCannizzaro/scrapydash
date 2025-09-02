# coding: utf-8
import json
import logging
import os
import time
import traceback

# Removed Flask imports - functionality moved to FastAPI
# from flask import current_app as app
# from flask import Response
import requests
from requests.adapters import HTTPAdapter
from w3lib.http import basic_auth_header

from .__version__ import __version__
from .models import Metadata, db

logger = logging.getLogger(__name__)

# Legacy Flask Response class replacement
class LegacyResponse:
    """Legacy Response class for backward compatibility"""
    def __init__(self, response=None, status=200, headers=None, mimetype='text/html'):
        self.response = response
        self.status = status
        self.headers = headers or {}
        self.mimetype = mimetype

# Legacy Flask app reference - replaced by FastAPI dependency injection
class LegacyApp:
    """Legacy app reference for backward compatibility"""
    def __init__(self):
        self.config = {}

# Global legacy app instance for backward compatibility
app = LegacyApp()

session = requests.Session()
session.mount('http://', HTTPAdapter(pool_connections=1000, pool_maxsize=1000))
session.mount('https://', HTTPAdapter(pool_connections=1000, pool_maxsize=1000))


# http://flask.pocoo.org/snippets/category/authentication/
def authenticate():
    """Sends a 401 response that enables basic auth"""
    return LegacyResponse("<script>alert('Fail to login: basic auth for ScrapydWeb has been enabled');</script>",
                    401, {'WWW-Authenticate': 'Basic realm="ScrapydWeb Basic Auth Required"'})


def find_scrapydash_settings_py(filename, path, prevpath=None):
    if path == prevpath:
        return ''
    path = os.path.abspath(path)
    cfgfile = os.path.join(path, filename)
    if os.path.exists(cfgfile):
        return cfgfile
    # In vars.py, try to import module scrapydash_settings_vN in cwd only
    # return find_scrapydash_settings_py(filename, os.path.dirname(path), path)


def get_now_string(allow_space=False):
    if allow_space:
        return time.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return time.strftime('%Y-%m-%dT%H_%M_%S')


def get_response_from_view(url, auth=None, data=None, as_json=False):
    # https://stackoverflow.com/a/21342070/10517783  How do I call one Flask view from another one?
    # https://stackoverflow.com/a/30250045/10517783
    # python - Flask test_client() doesn't have request.authorization with pytest
    # client = app.test_client()
    # if auth is not None:
    #     headers = {'Authorization': basic_auth_header(*auth)}
    # else:
    #     headers = {}
    # if data is not None:
    #     response = client.post(url, headers=headers, data=data, content_type='multipart/form-data')
    #     # response = client.post(url, headers=headers, data=data, content_type='application/json')
    # else:
    #     response = client.get(url, headers=headers)

    # text = response.get_data(as_text=True)
    # if as_json:
    #     # e.g. when used in schedule_task()
    #     # 'node index error: %s, which should be between 1 and %s' % (self.node, self.SCRAPYD_SERVERS_AMOUNT)
    #     # json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
    #     try:
    #         return json.loads(text)
    #     except ValueError:
    #         # '_status': '500 INTERNAL SERVER ERROR',
    #         # '_status_code': 500,
    #         # See 500.html
    #         # <tr><th>Error</th><td>node index error: 2, which should be between 1 and 1</td></tr>
    #         # <pre>Traceback...AssertionError: node index error: 2, which should be between 1 and 1 </pre>
    #         m = re.search(r'<tr><th>Error</th><td>(.+?)</td></tr>', text, re.S)
    #         message = m.group(1) if m else text
    #         return dict(status_code=getattr(response, '_status_code', 500), status='error', message=message)
    # else:
    #     return text
    pass


def handle_metadata(key=None, value=None):
    """Handle metadata operations with graceful error handling"""
    try:
        # Import models locally to avoid circular imports
        from .models import Metadata, db
        
        # Ensure database tables exist
        try:
            db.create_all()
        except Exception:
            pass  # Tables might already exist
        
        # Perform database operation
        try:
            metadata = db.session.query(Metadata).filter_by(version=__version__).first()
            
            if key is None:
                # Return all metadata as dict
                if metadata:
                    return dict((k, v) for (k, v) in metadata.__dict__.items() if not k.startswith('_'))
                else:
                    return {}
            else:
                # Set or update metadata value
                if not metadata:
                    # Create new metadata record
                    metadata = Metadata(version=__version__)
                    db.session.add(metadata)
                
                if value is not None:
                    setattr(metadata, key, value)
                
                db.session.commit()
                return metadata
                
        except Exception as e:
            print(f"Database operation failed: {e}")
            try:
                db.session.rollback()
            except:
                pass
            return {} if key is None else None
            
    except Exception as e:
        print(f"Error in handle_metadata: {e}")
        return {} if key is None else None


def handle_slash(string):
    if not string:
        return string
    else:
        return string.replace('\\', '/')


def json_dumps(obj, sort_keys=True, indent=4, ensure_ascii=False):
    return json.dumps(obj, sort_keys=sort_keys, indent=indent, ensure_ascii=ensure_ascii)
