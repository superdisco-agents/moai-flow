"""
Pytest configuration for hooks tests.
"""

import pytest


# Configure pytest-asyncio if available
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async test (requires pytest-asyncio)"
    )


# Set asyncio mode to auto if pytest-asyncio is available
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
