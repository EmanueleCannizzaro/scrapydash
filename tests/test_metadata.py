# coding: utf-8
from scrapydash.__version__ import __version__
from apscheduler.schedulers.base import STATE_PAUSED, STATE_RUNNING
from scrapydash.vars import SCHEDULER_STATE_DICT


def test_version_available():
    assert __version__
    assert isinstance(__version__, str)


def test_scheduler_state_constants():
    assert STATE_RUNNING in SCHEDULER_STATE_DICT
    assert STATE_PAUSED in SCHEDULER_STATE_DICT
    assert isinstance(SCHEDULER_STATE_DICT[STATE_RUNNING], str)
    assert isinstance(SCHEDULER_STATE_DICT[STATE_PAUSED], str)
