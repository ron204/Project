import string
from unittest.mock import patch

import pytest

from generator.code_generator import CodeGenerator, InvalidCodeConfiguration


def test_numeric_code_has_requested_length_and_only_digits():
    code = CodeGenerator.generate("numeric", 8)
    assert len(code) == 8
    assert code.isdigit()


def test_alphanumeric_code_has_requested_length_and_valid_characters():
    code = CodeGenerator.generate("alphanumeric", 16)
    assert len(code) == 16
    assert set(code) <= set(string.ascii_uppercase + string.digits)


def test_unsafe_lengths_and_unknown_types_are_rejected():
    with pytest.raises(InvalidCodeConfiguration):
        CodeGenerator.generate("numeric", 3)
    with pytest.raises(InvalidCodeConfiguration):
        CodeGenerator.generate("words", 8)


def test_generator_uses_secrets_choice_not_random():
    with patch("generator.code_generator.secrets.choice", return_value="7") as choice:
        assert CodeGenerator.generate("numeric", 6) == "777777"
        assert choice.call_count == 6
