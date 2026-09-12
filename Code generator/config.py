"""Application configuration with intentionally conservative security limits."""

import os
import secrets


class Config:
    # A configured key is needed for persistent sessions; a secure ephemeral key is
    # safer than shipping a known default for this local-only demonstration.
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", secrets.token_urlsafe(32))
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    MIN_CODE_LENGTH = 4
    MAX_CODE_LENGTH = 64
    MAX_VERIFICATION_ATTEMPTS = 5
    ALLOWED_EXPIRATIONS = (1, 5, 10, 15)
