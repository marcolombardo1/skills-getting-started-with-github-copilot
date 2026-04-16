"""
FastAPI backend tests for the Mergington High School Activities API.

All tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the action being tested
- Assert: Verify the results match expectations

Each test is isolated via the reset_activities fixture to prevent state pollution.
"""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for the GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """
        Given: No preconditions needed
        When: Making a GET request to the root endpoint /
        Then: Should redirect (status 307) to /static/index.html
        """
        # Arrange
        expected_redirect_url = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """
        Given: The application with predefined activities in memory
        When: Making a GET request to /activities
        Then: Should return status 200 with all activities as a dictionary
        """
        # Arrange
        expected_activity_names = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Theater Club",
            "Debate Team",
            "Science Club"
        ]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities_dict = response.json()
        assert isinstance(activities_dict, dict)
        assert len(activities_dict) >= 9
        for activity_name in expected_activity_names:
            assert activity_name in activities_dict
    
    def test_get_activities_returns_activity_structure(self, client):
        """
        Given: The application with activities data
        When: Making a GET request to /activities
        Then: Each activity should contain description, schedule, max_participants, and participants
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities_dict = response.json()
        
        # Assert
        for activity_name, activity_data in activities_dict.items():
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys()), \
                f"Activity '{activity_name}' missing required fields"
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_success(self, client):
        """
        Given: A new student email not yet signed up for an activity
        When: Making a POST request to signup for a valid activity
        Then: Should return status 200 with success message
        """
        # Arrange
        activity_name = "Chess Club"
        new_student_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert new_student_email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Given: A request to signup for an activity that does not exist
        When: Making a POST request with an invalid activity name
        Then: Should return status 404 with "Activity not found" message
        """
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_duplicate_email_returns_400(self, client):
        """
        Given: A student already signed up for an activity
        When: Attempting to signup the same student again
        Then: Should return status 400 with "already signed up" message
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants endpoint"""
    
    def test_unregister_existing_student_success(self, client):
        """
        Given: A student currently signed up for an activity
        When: Making a DELETE request to remove them
        Then: Should return status 200 with success message
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]
        assert student_email in data["message"]
        assert activity_name in data["message"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Given: A request to unregister from an activity that does not exist
        When: Making a DELETE request with an invalid activity name
        Then: Should return status 404 with "Activity not found" message
        """
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_student_not_in_activity_returns_404(self, client):
        """
        Given: A student not currently signed up for an activity
        When: Attempting to unregister them from that activity
        Then: Should return status 404 with "not signed up" message
        """
        # Arrange
        activity_name = "Programming Class"
        student_email = "alex@mergington.edu"  # Not in Programming Class
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()
    
    def test_signup_after_unregister_succeeds(self, client):
        """
        Given: A student who was previously signed up and then unregistered
        When: That student attempts to signup again
        Then: Should successfully re-register (status 200)
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"
        
        # Act - First, unregister the student
        unregister_response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": student_email}
        )
        
        # Then, attempt to sign them up again
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert unregister_response.status_code == 200
        assert signup_response.status_code == 200
        assert "Signed up" in signup_response.json()["message"]
