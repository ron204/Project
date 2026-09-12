"""Cryptographically secure, policy-validated code generation."""

import secrets
import string


class InvalidCodeConfiguration(ValueError):
    """Raised when a requested code policy is unsafe or unsupported."""


class CodeGenerator:
    """Generate codes from an OS-backed cryptographic random source."""

    NUMERIC_ALPHABET = string.digits
    ALPHANUMERIC_ALPHABET = string.ascii_uppercase + string.digits
    VALID_TYPES = {"numeric", "alphanumeric"}
    MIN_LENGTH = 4
    MAX_LENGTH = 64

    @classmethod
    def generate(cls, code_type: str, length: int) -> str:
        if code_type not in cls.VALID_TYPES:
            raise InvalidCodeConfiguration("Code type must be numeric or alphanumeric.")
        if not isinstance(length, int) or not cls.MIN_LENGTH <= length <= cls.MAX_LENGTH:
            raise InvalidCodeConfiguration(
                f"Code length must be between {cls.MIN_LENGTH} and {cls.MAX_LENGTH}."
            )

        alphabet = (
            cls.NUMERIC_ALPHABET
            if code_type == "numeric"
            else cls.ALPHANUMERIC_ALPHABET
        )
        # secrets.choice uses a cryptographically secure OS entropy source, unlike random.
        return "".join(secrets.choice(alphabet) for _ in range(length))
