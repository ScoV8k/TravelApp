"""
Tests specifically for google_photo.py API endpoints
"""
import pytest


def test_proxy_photo_missing_photoreference(client):
    """Test proxy photo without photoreference parameter"""
    response = client.get("/plans/proxy/photo")
    assert response.status_code == 422  # Validation error - missing required parameter


def test_proxy_photo_empty_photoreference(client):
    """Test proxy photo with empty photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=")
    # This might return 200 with empty content or 422, depending on validation
    assert response.status_code in [200, 422]


def test_proxy_photo_invalid_photoreference(client):
    """Test proxy photo with invalid photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=invalid-reference")
    # This should return 200 but with empty image content
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_valid_photoreference(client):
    """Test proxy photo with valid photoreference format"""
    # Using a fake but valid-looking photoreference
    fake_reference = "CmRaAAAA1234567890abcdefghijklmnopqrstuvwxyz"
    response = client.get(f"/plans/proxy/photo?photoreference={fake_reference}")
    # This should return 200 but with empty image content (since it's fake)
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_special_characters(client):
    """Test proxy photo with special characters in photoreference"""
    special_reference = "CmRaAAAA!@#$%^&*()_+-=[]{}|;':\",./<>?"
    response = client.get(f"/plans/proxy/photo?photoreference={special_reference}")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_unicode_characters(client):
    """Test proxy photo with unicode characters in photoreference"""
    unicode_reference = "CmRaAAAAこんにちはЗдравствуйтеمرحبا"
    response = client.get(f"/plans/proxy/photo?photoreference={unicode_reference}")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_long_photoreference(client):
    """Test proxy photo with very long photoreference"""
    long_reference = "CmRaAAAA" + "x" * 1000  # Very long reference
    response = client.get(f"/plans/proxy/photo?photoreference={long_reference}")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_short_photoreference(client):
    """Test proxy photo with very short photoreference"""
    short_reference = "abc"
    response = client.get(f"/plans/proxy/photo?photoreference={short_reference}")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_numeric_photoreference(client):
    """Test proxy photo with numeric photoreference"""
    numeric_reference = "1234567890"
    response = client.get(f"/plans/proxy/photo?photoreference={numeric_reference}")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_alphanumeric_photoreference(client):
    """Test proxy photo with alphanumeric photoreference"""
    alphanumeric_reference = "CmRaAAAA1234567890abcdefghijklmnopqrstuvwxyz"
    response = client.get(f"/plans/proxy/photo?photoreference={alphanumeric_reference}")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_wrong_method(client):
    """Test using wrong HTTP method for proxy photo"""
    response = client.post("/plans/proxy/photo?photoreference=test")
    assert response.status_code == 405  # Method not allowed


def test_proxy_photo_with_additional_params(client):
    """Test proxy photo with additional query parameters"""
    response = client.get("/plans/proxy/photo?photoreference=test&extra=param&another=value")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_with_slash(client):
    """Test proxy photo with trailing slash"""
    response = client.get("/plans/proxy/photo/?photoreference=test")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_multiple_photoreference_params(client):
    """Test proxy photo with multiple photoreference parameters"""
    response = client.get("/plans/proxy/photo?photoreference=first&photoreference=second")
    # Should use the last parameter value
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_encoded_photoreference(client):
    """Test proxy photo with URL encoded photoreference"""
    import urllib.parse
    encoded_reference = urllib.parse.quote("CmRaAAAA test reference with spaces")
    response = client.get(f"/plans/proxy/photo?photoreference={encoded_reference}")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_whitespace_photoreference(client):
    """Test proxy photo with whitespace in photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=test reference with spaces")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_newline_photoreference(client):
    """Test proxy photo with newline in photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=test%0Areference%0Awith%0Anewlines")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_tab_photoreference(client):
    """Test proxy photo with tab in photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=test%09reference%09with%09tabs")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_quotes_photoreference(client):
    """Test proxy photo with quotes in photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=test%22reference%22with%22quotes")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_single_quotes_photoreference(client):
    """Test proxy photo with single quotes in photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=test%27reference%27with%27quotes")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_backslash_photoreference(client):
    """Test proxy photo with backslash in photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=test%5Creference%5Cwith%5Cbackslashes")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_forward_slash_photoreference(client):
    """Test proxy photo with forward slash in photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=test/reference/with/slashes")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_question_mark_photoreference(client):
    """Test proxy photo with question mark in photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=test%3Freference%3Fwith%3Fquestions")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_hash_photoreference(client):
    """Test proxy photo with hash in photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=test%23reference%23with%23hashes")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_ampersand_photoreference(client):
    """Test proxy photo with ampersand in photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=test%26reference%26with%26ampersands")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_plus_photoreference(client):
    """Test proxy photo with plus in photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=test+reference+with+pluses")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_equal_photoreference(client):
    """Test proxy photo with equal sign in photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=test%3Dreference%3Dwith%3Dequals")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"


def test_proxy_photo_percent_photoreference(client):
    """Test proxy photo with percent in photoreference"""
    response = client.get("/plans/proxy/photo?photoreference=test%25reference%25with%25percents")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "image/jpeg"
