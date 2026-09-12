"""Temporary verification-code storage and validation for the local demo."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class VerificationResult:
    """A safe client-facing result that contains no code value."""

    success: bool
    message: str
    status: str
    attempts_remaining: int = 0
    expires_at: str | None = None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class VerificationRecord:
    """Only derived data and metadata are retained while a code is active."""
    digest: bytes
    salt: bytes
    expires_at: datetime
    attempts: int
    max_attempts: int


class VerificationService:
    """In-memory, one-time verification-code service for local demonstration use."""

    HASH_ITERATIONS = 200_000

    def __init__(self) -> None:
        self._records: dict[str, VerificationRecord] = {}

    @classmethod
    def _hash(cls, code: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", code.encode("utf-8"), salt, cls.HASH_ITERATIONS)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def create(
        self, verification_id: str, code: str, *, expires_in: timedelta, max_attempts: int
    ) -> None:
        if not verification_id or not isinstance(code, str) or not code:
            raise ValueError("A non-empty verification identifier and code are required.")
        if expires_in <= timedelta(0) or max_attempts < 1:
            raise ValueError("Expiration and maximum attempts must be positive.")

        salt = secrets.token_bytes(16)
        self._records[verification_id] = VerificationRecord(
            digest=self._hash(code, salt),
            salt=salt,
            expires_at=self._now() + expires_in,
            attempts=0,
            max_attempts=max_attempts,
        )

    def status(self, verification_id: str) -> VerificationResult:
        """Return non-sensitive state and remove records that have expired."""
        record = self._records.get(verification_id)
        if record is None:
            return VerificationResult(False, "This verification request is no longer active.", "invalid")
        if self._now() >= record.expires_at:
            del self._records[verification_id]
            return VerificationResult(False, "This code has expired. Generate a new one.", "expired")
        return VerificationResult(
            False,
            "Code is ready to verify.",
            "active",
            record.max_attempts - record.attempts,
            record.expires_at.isoformat(),
        )

    def verify(self, verification_id: str, submitted_code: str) -> VerificationResult:
        state = self.status(verification_id)
        if state.status != "active":
            return state

        clean_code = submitted_code.strip() if isinstance(submitted_code, str) else ""
        if not clean_code:
            return VerificationResult(
                False, "Enter the verification code before submitting.", "active",
                state.attempts_remaining, state.expires_at,
            )

        record = self._records[verification_id]
        candidate = self._hash(clean_code, record.salt)
        if hmac.compare_digest(candidate, record.digest):
            del self._records[verification_id]  # one-time use
            return VerificationResult(True, "Code verified successfully.", "verified")

        record.attempts += 1
        remaining = record.max_attempts - record.attempts
        if remaining == 0:
            del self._records[verification_id]
            return VerificationResult(False, "Too many failed attempts. Generate a new code.", "locked")
        return VerificationResult(
            False,
            f"Incorrect code. {remaining} attempt(s) remaining.",
            "active",
            remaining,
            record.expires_at.isoformat(),
        )
