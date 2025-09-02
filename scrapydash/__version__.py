# coding: utf-8
import os
import sys
from pathlib import Path

def _get_version_from_pyproject():
    """Read version and metadata from pyproject.toml"""
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            # Fallback for older Python versions
            return {
                '__title__': 'scrapydweb',
                '__version__': '1.6.0',
                '__author__': 'my8100',
                '__author_email__': 'my8100@gmail.com',
                '__url__': 'https://github.com/my8100/scrapydweb',
                '__license__': 'GNU General Public License v3.0',
                '__description__': ("Web app for Scrapyd cluster management, "
                                   "with support for Scrapy log analysis & visualization.")
            }
    
    # Find pyproject.toml file
    current_dir = Path(__file__).parent
    pyproject_path = current_dir.parent / "pyproject.toml"
    
    if not pyproject_path.exists():
        # Fallback values if pyproject.toml not found
        return {
            '__title__': 'scrapydweb',
            '__version__': '1.6.0',
            '__author__': 'my8100',
            '__author_email__': 'my8100@gmail.com',
            '__url__': 'https://github.com/my8100/scrapydweb',
            '__license__': 'GNU General Public License v3.0',
            '__description__': ("Web app for Scrapyd cluster management, "
                               "with support for Scrapy log analysis & visualization.")
        }
    
    try:
        with open(pyproject_path, 'rb') as f:
            data = tomllib.load(f)
        
        project = data.get('project', {})
        
        # Extract author info
        authors = project.get('authors', [{}])
        author_info = authors[0] if authors else {}
        
        return {
            '__title__': project.get('name', 'scrapydweb'),
            '__version__': project.get('version', '1.6.0'),
            '__author__': author_info.get('name', 'my8100'),
            '__author_email__': author_info.get('email', 'my8100@gmail.com'),
            '__url__': project.get('urls', {}).get('Homepage', 'https://github.com/my8100/scrapydweb'),
            '__license__': 'GNU General Public License v3.0',  # Convert from GPL-3.0
            '__description__': project.get('description', 
                                         "Web app for Scrapyd cluster management, "
                                         "with support for Scrapy log analysis & visualization.")
        }
    except Exception:
        # Fallback values if reading fails
        return {
            '__title__': 'scrapydweb',
            '__version__': '1.6.0',
            '__author__': 'my8100',
            '__author_email__': 'my8100@gmail.com',
            '__url__': 'https://github.com/my8100/scrapydweb',
            '__license__': 'GNU General Public License v3.0',
            '__description__': ("Web app for Scrapyd cluster management, "
                               "with support for Scrapy log analysis & visualization.")
        }

# Load metadata from pyproject.toml
_metadata = _get_version_from_pyproject()

__title__ = _metadata['__title__']
__version__ = _metadata['__version__']
__author__ = _metadata['__author__']
__author_email__ = _metadata['__author_email__']
__url__ = _metadata['__url__']
__license__ = _metadata['__license__']
__description__ = _metadata['__description__']
