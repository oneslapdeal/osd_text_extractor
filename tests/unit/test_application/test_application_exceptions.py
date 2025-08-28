import pytest

from osd_text_extractor.application.exceptions import UnsupportedFormatError


class TestApplicationExceptions:
    def test_unsupported_format_error_creation(self) -> None:
        format_name = "unknown_format"
        message = f"Unsupported format: {format_name}"
        exception = UnsupportedFormatError(message)
        assert str(exception) == message

    def test_unsupported_format_error_raising(self) -> None:
        message = "Format not supported"
        with pytest.raises(UnsupportedFormatError, match=message):
            raise UnsupportedFormatError(message)

    @pytest.mark.parametrize(
        "format_name", ["exe", "dll", "unknown", "", "fake_format"]
    )
    def test_unsupported_format_error_with_different_formats(
        self, format_name: str
    ) -> None:
        message = f"Unsupported format: {format_name}"
        exception = UnsupportedFormatError(message)
        assert format_name in str(exception)

    def test_application_exception_can_be_caught_as_exception(self) -> None:
        with pytest.raises(UnsupportedFormatError):
            raise UnsupportedFormatError("test")
