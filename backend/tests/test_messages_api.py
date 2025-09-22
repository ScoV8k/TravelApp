"""
Tests specifically for messages.py API endpoints
"""
import pytest


def test_create_message_missing_trip_id(client):
    """Test creating a message without trip_id"""
    message_data = {
        "text": "Hello, this is a test message!",
        "isUser": True,
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    response = client.post("/messages/", json=message_data)
    assert response.status_code == 422  # Validation error


def test_create_message_missing_text(client):
    """Test creating a message without text"""
    message_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "isUser": True,
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    response = client.post("/messages/", json=message_data)
    assert response.status_code == 422  # Validation error


def test_create_message_missing_isUser(client):
    """Test creating a message without isUser field"""
    message_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "text": "Hello, this is a test message!",
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    response = client.post("/messages/", json=message_data)
    assert response.status_code == 422  # Validation error


def test_create_message_missing_timestamp(client):
    """Test creating a message without timestamp"""
    message_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "text": "Hello, this is a test message!",
        "isUser": True
    }
    
    response = client.post("/messages/", json=message_data)
    assert response.status_code == 422  # Validation error


def test_create_message_invalid_trip_id_format(client):
    """Test creating a message with invalid trip_id format"""
    message_data = {
        "trip_id": "invalid-id",
        "text": "Hello, this is a test message!",
        "isUser": True,
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    response = client.post("/messages/", json=message_data)
    assert response.status_code == 422  # Validation error


def test_create_message_invalid_timestamp_format(client):
    """Test creating a message with invalid timestamp format"""
    message_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "text": "Hello, this is a test message!",
        "isUser": True,
        "timestamp": "invalid-timestamp"
    }
    
    response = client.post("/messages/", json=message_data)
    assert response.status_code == 422  # Validation error


def test_create_message_invalid_isUser_type(client):
    """Test creating a message with invalid isUser type"""
    message_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "text": "Hello, this is a test message!",
        "isUser": "not-a-boolean",
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    response = client.post("/messages/", json=message_data)
    assert response.status_code == 422  # Validation error


def test_get_messages_for_trip_invalid_id_format(client):
    """Test getting messages for trip with invalid ID format"""
    response = client.get("/messages/trip/invalid-id")
    assert response.status_code == 500  # Internal server error due to PyObjectId conversion


def test_get_messages_for_trip_empty_path(client):
    """Test getting messages for trip with empty path"""
    response = client.get("/messages/trip/")
    assert response.status_code == 404  # Not found


def test_messages_endpoint_wrong_method(client):
    """Test using wrong HTTP method on messages endpoint"""
    response = client.get("/messages/")  # Should be POST
    assert response.status_code == 405  # Method not allowed


def test_messages_endpoint_invalid_json(client):
    """Test messages endpoint with invalid JSON"""
    response = client.post("/messages/", 
                          data="invalid json", 
                          headers={"Content-Type": "application/json"})
    assert response.status_code == 422  # JSON decode error


def test_messages_endpoint_wrong_content_type(client):
    """Test messages endpoint with wrong content type"""
    message_data = "trip_id=123&text=Hello&isUser=true&timestamp=2024-01-01"
    response = client.post("/messages/", 
                          data=message_data, 
                          headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 422  # Should expect JSON
