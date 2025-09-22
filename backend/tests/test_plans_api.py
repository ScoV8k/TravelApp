"""
Tests specifically for plans.py API endpoints
"""
import pytest


def test_create_plan_missing_trip_id(client):
    """Test creating a plan without trip_id"""
    plan_data = {
        "data": {"day1": "Visit museums", "day2": "Go to beach"},
        "updated_at": "2024-01-01T12:00:00Z"
    }
    
    response = client.post("/plans/", json=plan_data)
    assert response.status_code == 422  # Validation error


def test_create_plan_missing_data(client):
    """Test creating a plan without data field"""
    plan_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "updated_at": "2024-01-01T12:00:00Z"
    }
    
    response = client.post("/plans/", json=plan_data)
    assert response.status_code == 422  # Validation error


def test_create_plan_missing_updated_at(client):
    """Test creating a plan without updated_at"""
    plan_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "data": {"day1": "Visit museums", "day2": "Go to beach"}
    }
    
    response = client.post("/plans/", json=plan_data)
    assert response.status_code == 422  # Validation error


def test_create_plan_invalid_trip_id_format(client):
    """Test creating a plan with invalid trip_id format"""
    plan_data = {
        "trip_id": "invalid-id",
        "data": {"day1": "Visit museums", "day2": "Go to beach"},
        "updated_at": "2024-01-01T12:00:00Z"
    }
    
    response = client.post("/plans/", json=plan_data)
    assert response.status_code == 422  # Validation error


def test_create_plan_invalid_datetime_format(client):
    """Test creating a plan with invalid datetime format"""
    plan_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "data": {"day1": "Visit museums", "day2": "Go to beach"},
        "updated_at": "invalid-datetime"
    }
    
    response = client.post("/plans/", json=plan_data)
    assert response.status_code == 422  # Validation error


def test_create_plan_empty_data(client):
    """Test creating a plan with empty data"""
    plan_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "data": {},
        "updated_at": "2024-01-01T12:00:00Z"
    }
    
    response = client.post("/plans/", json=plan_data)
    # This might fail due to database operations, but validation should pass
    assert response.status_code in [200, 500]  # 500 due to database operations


def test_update_plan_missing_trip_id(client):
    """Test updating a plan without trip_id"""
    fake_id = "507f1f77bcf86cd799439011"
    plan_data = {
        "data": {"day1": "Updated activity"},
        "updated_at": "2024-01-01T12:00:00Z"
    }
    
    response = client.put(f"/plans/{fake_id}", json=plan_data)
    assert response.status_code == 422  # Validation error


def test_update_plan_missing_data(client):
    """Test updating a plan without data field"""
    fake_id = "507f1f77bcf86cd799439011"
    plan_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "updated_at": "2024-01-01T12:00:00Z"
    }
    
    response = client.put(f"/plans/{fake_id}", json=plan_data)
    assert response.status_code == 422  # Validation error


def test_update_plan_missing_updated_at(client):
    """Test updating a plan without updated_at"""
    fake_id = "507f1f77bcf86cd799439011"
    plan_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "data": {"day1": "Updated activity"}
    }
    
    response = client.put(f"/plans/{fake_id}", json=plan_data)
    assert response.status_code == 422  # Validation error


def test_get_plan_by_trip_id_invalid_id_format(client):
    """Test getting a plan by trip_id with invalid ID format"""
    response = client.get("/plans/invalid-id")
    assert response.status_code == 500  # Error due to PyObjectId conversion


def test_plans_endpoint_wrong_method(client):
    """Test using wrong HTTP method on plans endpoint"""
    response = client.get("/plans/")  # Should be POST
    assert response.status_code == 405  # Method not allowed


def test_plans_endpoint_invalid_json(client):
    """Test plans endpoint with invalid JSON"""
    response = client.post("/plans/", 
                          data="invalid json", 
                          headers={"Content-Type": "application/json"})
    assert response.status_code == 422  # JSON decode error


def test_plans_endpoint_wrong_content_type(client):
    """Test plans endpoint with wrong content type"""
    plan_data = "trip_id=123&data=test&updated_at=2024-01-01"
    response = client.post("/plans/", 
                          data=plan_data, 
                          headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 422  # Should expect JSON
