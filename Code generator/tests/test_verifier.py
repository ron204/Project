from datetime import datetime, timedelta, timezone

import pytest

from verification.verifier import VerificationService


def make_service():
    service = VerificationService()
    service.create("request-1", "ABC123", expires_in=timedelta(minutes=5), max_attempts=3)
    return service


def test_correct_code_is_accepted_once():
    service = make_service()
    assert service.verify("request-1", "ABC123").success
    result = service.verify("request-1", "ABC123")
    assert not result.success
    assert result.status == "invalid"


def test_invalid_code_is_rejected():
    result = make_service().verify("request-1", "WRONG1")
    assert not result.success
    assert "Incorrect" in result.message


def test_expired_code_is_rejected():
    service = VerificationService()
    service.create("expired", "ABC123", expires_in=timedelta(minutes=1), max_attempts=3)
    service._records["expired"].expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    result = service.verify("expired", "ABC123")
    assert not result.success
    assert "expired" in result.message.lower()
    assert result.status == "expired"


def test_maximum_attempts_lock_the_request():
    service = make_service()
    for _ in range(3):
        result = service.verify("request-1", "WRONG1")
    assert not result.success
    assert "Too many" in result.message
    assert not service.verify("request-1", "ABC123").success


def test_plaintext_code_is_not_stored():
    service = make_service()
    record = service._records["request-1"]
    assert not hasattr(record, "code")
    assert b"ABC123" not in record.digest
    assert len(record.salt) == 16
    assert service.HASH_ITERATIONS >= 200_000


def test_empty_input_is_rejected_without_consuming_an_attempt():
    service = make_service()
    result = service.verify("request-1", "  ")
    assert not result.success
    assert "Enter" in result.message
    assert result.attempts_remaining == 3


def test_invalid_create_configuration_is_rejected():
    service = VerificationService()
    with pytest.raises(ValueError):
        service.create("", "ABC123", expires_in=timedelta(minutes=1), max_attempts=3)
    with pytest.raises(ValueError):
        service.create("id", "ABC123", expires_in=timedelta(0), max_attempts=3)
