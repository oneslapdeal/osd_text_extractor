import pytest
from osd_text_extractor.application.exceptions import UnsupportedFormatError
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.extractors import ExtractorFactory


class MockExtractor:
    """Mock extractor for testing."""

    @staticmethod
    def extract_plain_text(content: bytes) -> str:
        _content = content
        return "mock extracted text"


class TestExtractorFactory:
    def test_get_extractor_success(self) -> None:
        """Test getting extractor for supported format."""
        mapping = {"txt": MockExtractor}
        factory = ExtractorFactory(mapping)

        extractor_class = factory.get_extractor("txt")
        assert extractor_class == MockExtractor
        assert hasattr(extractor_class, "extract_plain_text")

    @pytest.mark.parametrize("supported_format", ["txt", "pdf", "docx"])
    def test_get_extractor_for_supported_formats(self, supported_format: str) -> None:
        """Test getting extractor for supported formats."""
        mapping = {
            "txt": MockExtractor,
            "pdf": MockExtractor,
            "docx": MockExtractor,
        }
        factory = ExtractorFactory(mapping)

        # Act
        extractor_class = factory.get_extractor(supported_format)

        # Assert
        assert extractor_class == MockExtractor
        assert hasattr(extractor_class, "extract_plain_text")

    @pytest.mark.parametrize(
        "unsupported_format",
        ["unsupported", "fake", "unknown", "exe", "bin"],
    )
    def test_get_extractor_for_unsupported_format_raises_error(
        self,
        unsupported_format: str,
    ) -> None:
        """Test getting extractor for unsupported formats."""
        mapping = {"txt": MockExtractor}
        factory = ExtractorFactory(mapping)

        # Act & Assert
        with pytest.raises(UnsupportedFormatError) as exc_info:
            factory.get_extractor(unsupported_format)

        assert f"Unsupported format: {unsupported_format}" in str(exc_info.value)

    @pytest.mark.parametrize(
        "format_case",
        [
            ("TXT", "txt"),
            ("PDF", "pdf"),
            ("Docx", "docx"),
            ("DOCX", "docx"),
        ],
    )
    def test_get_extractor_case_insensitive(self, format_case: tuple[str, str]) -> None:
        """Test that getting extractor is case insensitive."""
        # Arrange
        upper_format, lower_format = format_case
        mapping = {
            "txt": MockExtractor,
            "pdf": MockExtractor,
            "docx": MockExtractor,
        }
        factory = ExtractorFactory(mapping)

        # Act
        extractor_upper = factory.get_extractor(upper_format)
        extractor_lower = factory.get_extractor(lower_format)

        # Assert
        assert extractor_upper == extractor_lower

    def test_get_extractor_with_empty_format_raises_error(self) -> None:
        """Test getting extractor with empty format."""
        mapping = {"txt": MockExtractor}
        factory = ExtractorFactory(mapping)

        # Act & Assert
        with pytest.raises(UnsupportedFormatError, match="Unsupported format: "):
            factory.get_extractor("")

    def test_get_extractor_with_whitespace_format_raises_error(self) -> None:
        """Test getting extractor with whitespace format."""
        mapping = {"txt": MockExtractor}
        factory = ExtractorFactory(mapping)

        # Act & Assert
        with pytest.raises(UnsupportedFormatError, match="Unsupported format:"):
            factory.get_extractor("   ")

    def test_factory_initialization_with_empty_mapping(self) -> None:
        """Test factory initialization with empty mapping."""
        # Arrange
        empty_mapping: dict[str, type[TextExtractor]] = {}
        factory = ExtractorFactory(empty_mapping)

        # Act & Assert
        with pytest.raises(UnsupportedFormatError):
            factory.get_extractor("any_format")

    def test_factory_initialization_with_custom_mapping(self) -> None:
        """Test factory initialization with custom mapping."""
        # Arrange
        custom_mapping = {
            "custom": MockExtractor,
            "test": MockExtractor,
        }
        factory = ExtractorFactory(custom_mapping)

        # Act
        extractor_class = factory.get_extractor("custom")

        # Assert
        assert extractor_class == MockExtractor

    def test_factory_mapping_is_case_insensitive(self) -> None:
        """Test that factory mapping is case insensitive."""
        # Arrange - factory does lower() on format, so mapping should use lowercase keys
        mapping_lower = {"txt": MockExtractor}
        factory_lower = ExtractorFactory(mapping_lower)

        # Act & Assert - should find by exact match after lower()
        extractor = factory_lower.get_extractor("TXT")
        assert extractor == MockExtractor

    @pytest.mark.parametrize(
        "special_format",
        [
            "format.with.dots",
            "format-with-dashes",
            "format_with_underscores",
            "format123",
            "123format",
        ],
    )
    def test_get_extractor_with_special_characters_in_format(
        self,
        special_format: str,
    ) -> None:
        """Test getting extractor with special characters in format."""
        # Arrange
        mapping = {special_format.lower(): MockExtractor}
        factory = ExtractorFactory(mapping)

        # Act
        extractor_class = factory.get_extractor(special_format)

        # Assert
        assert extractor_class == MockExtractor
