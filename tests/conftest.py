"""
Test configuration and shared fixtures for FastAPI backend tests.

This module provides:
- client: FastAPI TestClient for making HTTP requests to endpoints
- reset_activities: autouse fixture that isolates test state by saving/restoring
  the global activities dictionary before/after each test
"""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provide a TestClient instance for making HTTP requests to the FastAPI app.
    
    Returns:
        TestClient: A client for testing FastAPI endpoints
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Automatically reset the in-memory activities dictionary before and after each test.
    
    This fixture ensures test isolation by:
    1. Creating a deep copy of the original activities state before the test
    2. Allowing the test to run (and potentially modify activities)
    3. Restoring the original activities state after the test
    
    This prevents test pollution where one test's modifications affect subsequent tests.
    """
    # Arrange: Save the original state
    original_activities = copy.deepcopy(activities)
    
    # Allow test to run
    yield
    
    # Assert/Cleanup: Restore original state
    activities.clear()
    activities.update(original_activities)
