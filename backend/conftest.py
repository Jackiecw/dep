import sys
try:
    import cgi
except ImportError:
    # Python 3.13 compatibility
    try:
        import standard_cgi as cgi
        sys.modules["cgi"] = cgi
    except ImportError:
        pass

import pytest
from tortoise.contrib.test import finalizer, initializer

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="module", autouse=True)
def initialize_tests(request):
    initializer(["models"], db_url="sqlite://:memory:")
    request.addfinalizer(finalizer)
