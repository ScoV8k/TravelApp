"""
Tests specifically for ai.py API endpoints
"""
import pytest


def test_generate_plan_nonexistent_trip_id(client):
    """Test generating plan for non-existent trip"""
    fake_id = "507f1f77bcf86cd799439011"
    response = client.post(f"/generate-plan/{fake_id}")
    assert response.status_code == 404  # Trip not found


def test_generate_plan_wrong_method(client):
    """Test using wrong HTTP method for generate plan"""
    fake_id = "507f1f77bcf86cd799439011"
    response = client.get(f"/generate-plan/{fake_id}")
    assert response.status_code == 405  # Method not allowed


def test_generate_message_missing_trip_id(client):
    """Test generating message without trip_id"""
    message_data = {
        "user_message": "Hello, I want to plan a trip",
        "last_messages": []
    }
    
    response = client.post("/generate-message-and-update-information/", json=message_data)
    assert response.status_code == 422  # Validation error


def test_generate_message_missing_user_message(client):
    """Test generating message without user_message"""
    message_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "last_messages": []
    }
    
    response = client.post("/generate-message-and-update-information/", json=message_data)
    assert response.status_code == 422  # Validation error


def test_generate_message_missing_last_messages(client):
    """Test generating message without last_messages"""
    message_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "user_message": "Hello, I want to plan a trip"
    }
    
    response = client.post("/generate-message-and-update-information/", json=message_data)
    assert response.status_code == 422  # Validation error


def test_generate_message_invalid_last_messages_type(client):
    """Test generating message with invalid last_messages type"""
    message_data = {
        "trip_id": "507f1f77bcf86cd799439011",
        "user_message": "Hello, I want to plan a trip",
        "last_messages": "not-a-list"
    }
    
    response = client.post("/generate-message-and-update-information/", json=message_data)
    assert response.status_code == 422  # Validation error


def test_ai_endpoint_invalid_json(client):
    """Test AI endpoints with invalid JSON"""
    response = client.post("/generate-message-and-update-information/", 
                          data="invalid json", 
                          headers={"Content-Type": "application/json"})
    assert response.status_code == 422  # JSON decode error


def test_ai_endpoint_wrong_content_type(client):
    """Test AI endpoints with wrong content type"""
    message_data = "trip_id=123&user_message=Hello&last_messages=[]"
    response = client.post("/generate-message-and-update-information/", 
                          data=message_data, 
                          headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 422  # Should expect JSON
