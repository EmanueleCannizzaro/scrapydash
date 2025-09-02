# coding: utf-8
import os

from scrapydash import create_app
from scrapydash.common import find_scrapydash_settings_py
from scrapydash.vars import SCRAPYDASH_SETTINGS_PY


# FastAPI app creation test
def test_config():
    app = create_app()
    assert app is not None
    assert hasattr(app, 'title')
    
    app_with_test_config = create_app({'TESTING': True})
    assert app_with_test_config is not None


def test_find_scrapydash_settings_py():
    find_scrapydash_settings_py(SCRAPYDASH_SETTINGS_PY, os.getcwd())
