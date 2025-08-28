import pytest
from osd_text_extractor.domain.exceptions import TextLengthError


class TestDomainExceptions:
    def test_text_length_error_creation(self) -> None:
        message = "Text is too short"
        exception = TextLengthError(message)
        assert str(exception) == message

    def test_text_length_error_without_message(self) -> None:
        exception = TextLengthError()
        assert isinstance(exception, TextLengthError)

    def test_text_length_error_raising(self) -> None:
        message = "Invalid text length"
        with pytest.raises(TextLengthError, match=message):
            raise TextLengthError(message)

    def test_domain_exception_can_be_caught_as_exception(self) -> None:
        with pytest.raises(TextLengthError):
            raise TextLengthError("test")
