import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # backend/
sys.path.insert(0, os.path.dirname(__file__))  # backend/tests/

import pytest


@pytest.fixture(autouse=True)
def no_pagespeed(monkeypatch):
    """Disable real PageSpeed API calls in all tests."""
    async def _noop(url):
        return []
    monkeypatch.setattr("analyzer.pagespeed_analyzer.analyze_pagespeed", _noop)
