"""
Tests specifically for trips.py API endpoints
"""
import pytest


def test_create_trip_missing_user_id(client):
    """Test creating a trip without user_id"""
    trip_data = {
        "name": "Test Trip",
        "created_at": "2024-01-01T00:00:00Z",
        "status": "draft"
    }
    
    response = client.post("/trips/", json=trip_data)
    assert response.status_code == 422  # Validation error


def test_create_trip_missing_name(client):
    """Test creating a trip without name"""
    trip_data = {
        "user_id": "507f1f77bcf86cd799439011",
        "created_at": "2024-01-01T00:00:00Z",
        "status": "draft"
    }
    
    response = client.post("/trips/", json=trip_data)
    assert response.status_code == 422  # Validation error


def test_create_trip_missing_created_at(client):
    """Test creating a trip without created_at"""
    trip_data = {
        "user_id": "507f1f77bcf86cd799439011",
        "name": "Test Trip",
        "status": "draft"
    }
    
    response = client.post("/trips/", json=trip_data)
    assert response.status_code == 422  # Validation error


def test_create_trip_missing_status(client):
    """Test creating a trip without status"""
    trip_data = {
        "user_id": "507f1f77bcf86cd799439011",
        "name": "Test Trip",
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    response = client.post("/trips/", json=trip_data)
    assert response.status_code == 422  # Validation error


def test_create_trip_invalid_user_id_format(client):
    """Test creating a trip with invalid user_id format"""
    trip_data = {
        "user_id": "invalid-id",
        "name": "Test Trip",
        "created_at": "2024-01-01T00:00:00Z",
        "status": "draft"
    }
    
    response = client.post("/trips/", json=trip_data)
    assert response.status_code == 422  # Validation error


def test_create_trip_invalid_datetime_format(client):
    """Test creating a trip with invalid datetime format"""
    trip_data = {
        "user_id": "507f1f77bcf86cd799439011",
        "name": "Test Trip",
        "created_at": "invalid-datetime",
        "status": "draft"
    }
    
    response = client.post("/trips/", json=trip_data)
    assert response.status_code == 422  # Validation error


def test_get_trip_invalid_id_format(client):
    """Test getting a trip with invalid ID format"""
    response = client.get("/trips/invalid-id")
    assert response.status_code == 400


def test_get_trip_status_invalid_id_format(client):
    """Test getting trip status with invalid ID format"""
    response = client.get("/trips/status/invalid-id")
    assert response.status_code == 400


def test_get_trips_by_user_invalid_id_format(client):
    """Test getting trips by user with invalid ID format"""
    response = client.get("/trips/user/invalid-id")
    assert response.status_code == 500  # Internal server error due to PyObjectId conversion


def test_update_trip_invalid_id_format(client):
    """Test updating a trip with invalid ID format"""
    update_data = {"name": "Updated Trip Name"}
    response = client.patch("/trips/invalid-id", json=update_data)
    assert response.status_code == 500  # Error due to PyObjectId conversion


def test_delete_trip_invalid_id_format(client):
    """Test deleting a trip with invalid ID format"""
    response = client.delete("/trips/invalid-id")
    assert response.status_code == 400


def test_trips_endpoint_wrong_method(client):
    """Test using wrong HTTP method on trips endpoint"""
    response = client.get("/trips/")  # Should be POST
    assert response.status_code == 405  # Method not allowed


def test_trips_endpoint_invalid_json(client):
    """Test trips endpoint with invalid JSON"""
    response = client.post("/trips/", 
                          data="invalid json", 
                          headers={"Content-Type": "application/json"})
    assert response.status_code == 422  # JSON decode error


def test_trips_endpoint_wrong_content_type(client):
    """Test trips endpoint with wrong content type"""
    trip_data = "user_id=123&name=Test&created_at=2024-01-01&status=draft"
    response = client.post("/trips/", 
                          data=trip_data, 
                          headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 422  # Should expect JSON
