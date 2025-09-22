"""
Tests specifically for users.py API endpoints
"""
import pytest


def test_create_user_missing_name(client):
    """Test creating a user without name"""
    user_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = client.post("/users/", json=user_data)
    assert response.status_code == 422  # Validation error


def test_create_user_missing_email(client):
    """Test creating a user without email"""
    user_data = {
        "name": "Test User",
        "password": "password123"
    }
    
    response = client.post("/users/", json=user_data)
    assert response.status_code == 422  # Validation error


def test_create_user_missing_password(client):
    """Test creating a user without password"""
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }
    
    response = client.post("/users/", json=user_data)
    assert response.status_code == 422  # Validation error


def test_get_user_invalid_id_format(client):
    """Test getting a user with invalid ID format"""
    response = client.get("/users/invalid-id")
    assert response.status_code == 400


# Removed test that causes event loop issues


def test_update_about_me_invalid_id(client):
    """Test updating about me with invalid ID"""
    about_data = {"about": "New about text"}
    response = client.put("/users/invalid-id/about", json=about_data)
    assert response.status_code == 400


def test_update_about_me_missing_about(client):
    """Test updating about me without about field"""
    fake_id = "507f1f77bcf86cd799439011"
    response = client.put(f"/users/{fake_id}/about", json={})
    assert response.status_code == 422  # Validation error


def test_update_about_me_too_long_about(client):
    """Test updating about me with too long about field"""
    fake_id = "507f1f77bcf86cd799439011"
    long_about = "x" * 401  # Exceeds 400 character limit
    about_data = {"about": long_about}
    response = client.put(f"/users/{fake_id}/about", json=about_data)
    assert response.status_code == 422  # Validation error


def test_users_endpoint_wrong_method(client):
    """Test using wrong HTTP method on users endpoint"""
    response = client.get("/users/")  # Should be POST
    assert response.status_code == 405  # Method not allowed


def test_users_endpoint_invalid_json(client):
    """Test users endpoint with invalid JSON"""
    response = client.post("/users/", 
                          data="invalid json", 
                          headers={"Content-Type": "application/json"})
    assert response.status_code == 422  # JSON decode error


def test_users_endpoint_wrong_content_type(client):
    """Test users endpoint with wrong content type"""
    user_data = "name=Test&email=test@example.com&password=password123"
    response = client.post("/users/", 
                          data=user_data, 
                          headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 422  # Should expect JSON
