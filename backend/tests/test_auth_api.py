"""
Tests specifically for auth.py API endpoints
"""
import pytest


def test_register_user_missing_name(client):
    """Test user registration without name"""
    user_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 422  # Validation error


def test_register_user_missing_email(client):
    """Test user registration without email"""
    user_data = {
        "name": "Test User",
        "password": "password123"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 422  # Validation error


def test_register_user_missing_password(client):
    """Test user registration without password"""
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 422  # Validation error


def test_login_missing_username(client):
    """Test login without username"""
    login_data = {
        "password": "password123"
    }
    
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 422  # Validation error


def test_login_missing_password(client):
    """Test login without password"""
    login_data = {
        "username": "test@example.com"
    }
    
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 422  # Validation error


def test_login_invalid_credentials_format(client):
    """Test login with invalid credentials format"""
    login_data = {
        "invalid_field": "test@example.com",
        "password": "password123"
    }
    
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 422  # Validation error


def test_auth_endpoint_wrong_method(client):
    """Test using wrong HTTP method on auth endpoints"""
    # Test register endpoint
    response = client.get("/auth/register")
    assert response.status_code == 405  # Method not allowed
    
    # Test login endpoint
    response = client.get("/auth/login")
    assert response.status_code == 405  # Method not allowed


def test_auth_endpoint_invalid_json(client):
    """Test auth endpoints with invalid JSON"""
    response = client.post("/auth/register", 
                          data="invalid json", 
                          headers={"Content-Type": "application/json"})
    assert response.status_code == 422  # JSON decode error


def test_auth_endpoint_wrong_content_type_register(client):
    """Test register endpoint with wrong content type"""
    user_data = "name=Test&email=test@example.com&password=password123"
    response = client.post("/auth/register", 
                          data=user_data, 
                          headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 422  # Should expect JSON


def test_auth_endpoint_wrong_content_type_login(client):
    """Test login endpoint with wrong content type"""
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    response = client.post("/auth/login", 
                          json=login_data, 
                          headers={"Content-Type": "application/json"})
    assert response.status_code == 422  # Should expect form data
