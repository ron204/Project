import re

from app import create_app
from config import Config


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-key"


def test_home_page_loads_with_professional_header():
    client = create_app(TestConfig).test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Secure Code Generator" in response.data


def test_generation_and_ajax_verification_flow():
    client = create_app(TestConfig).test_client()
    generated = client.post("/generate", data={"purpose": "verification", "code_type": "numeric", "length": "6", "expires_in": "1"})
    page = generated.get_data(as_text=True)
    code = re.search(r'<output id="generated-code"[^>]*>([^<]+)</output>', page).group(1).strip()
    verification_id = re.search(r'name="verification_id" value="([^"]+)"', page).group(1)
    assert code.isdigit() and len(code) == 6
    assert "Expires in" in page
    invalid = client.post("/verify", data={"verification_id": verification_id, "submitted_code": "000000"}, headers={"X-Requested-With": "XMLHttpRequest"})
    assert invalid.get_json()["status"] == "active"
    assert invalid.get_json()["attempts_remaining"] == 4
    valid = client.post("/verify", data={"verification_id": verification_id, "submitted_code": code}, headers={"X-Requested-With": "XMLHttpRequest"})
    assert valid.get_json()["success"] is True
    assert valid.get_json()["status"] == "verified"


def test_invalid_generation_length_redirects_with_message():
    client = create_app(TestConfig).test_client()
    response = client.post("/generate", data={"purpose": "suggested", "code_type": "numeric", "length": "2", "expires_in": "1"}, follow_redirects=True)
    assert b"Code length must be between" in response.data
