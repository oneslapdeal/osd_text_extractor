import pytest

from osd_text_extractor.infrastructure.exceptions import ExtractionError


class TestInfrastructureExceptions:
    def test_extraction_error_creation(self) -> None:
        message = "Failed to extract text"
        exception = ExtractionError(message)
        assert str(exception) == message

    def test_extraction_error_raising(self) -> None:
        message = "Extraction failed"
        with pytest.raises(ExtractionError, match=message):
            raise ExtractionError(message)


    def test_infrastructure_exception_can_be_caught_as_exception(self) -> None:
        with pytest.raises(ExtractionError):
            raise ExtractionError("test")
