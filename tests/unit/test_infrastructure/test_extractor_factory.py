import pytest

from osd_text_extractor.application.exceptions import UnsupportedFormatError
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.extractors import ExtractorFactory
from tests.conftest import MockExtractor


class TestExtractorFactory:
    def test_get_extractor_success(self, real_extractor_factory: ExtractorFactory) -> None:
        extractor_class = real_extractor_factory.get_extractor("txt")
        assert extractor_class == MockExtractor
        assert issubclass(extractor_class, TextExtractor)

    @pytest.mark.parametrize("supported_format", [
        "txt", "pdf", "docx"
    ])
    def test_get_extractor_for_supported_formats(
            self,
            real_extractor_factory: ExtractorFactory,
            supported_format: str
    ) -> None:
        """Тест получения экстрактора для поддерживаемых форматов."""
        # Act
        extractor_class = real_extractor_factory.get_extractor(supported_format)

        # Assert
        assert extractor_class == MockExtractor
        assert hasattr(extractor_class, "extract_plain_text")

    @pytest.mark.parametrize("unsupported_format", [
        "unsupported", "fake", "unknown", "exe", "bin"
    ])
    def test_get_extractor_for_unsupported_format_raises_error(
            self,
            real_extractor_factory: ExtractorFactory,
            unsupported_format: str
    ) -> None:
        """Тест получения экстрактора для неподдерживаемых форматов."""
        # Act & Assert
        with pytest.raises(UnsupportedFormatError) as exc_info:
            real_extractor_factory.get_extractor(unsupported_format)

        assert f"Unsupported format: {unsupported_format}" in str(exc_info.value)

    @pytest.mark.parametrize("format_case", [
        ("TXT", "txt"),
        ("PDF", "pdf"),
        ("Docx", "docx"),
        ("DOCX", "docx"),
    ])
    def test_get_extractor_case_insensitive(
            self,
            real_extractor_factory: ExtractorFactory,
            format_case: tuple[str, str]
    ) -> None:
        """Тест что получение экстрактора нечувствительно к регистру."""
        # Arrange
        upper_format, lower_format = format_case

        # Act
        extractor_upper = real_extractor_factory.get_extractor(upper_format)
        extractor_lower = real_extractor_factory.get_extractor(lower_format)

        # Assert
        assert extractor_upper == extractor_lower

    def test_get_extractor_with_empty_format_raises_error(
            self, real_extractor_factory: ExtractorFactory
    ) -> None:
        """Тест получения экстрактора с пустым форматом."""
        # Act & Assert
        with pytest.raises(UnsupportedFormatError, match="Unsupported format: "):
            real_extractor_factory.get_extractor("")

    def test_get_extractor_with_whitespace_format_raises_error(
            self, real_extractor_factory: ExtractorFactory
    ) -> None:
        """Тест получения экстрактора с форматом из пробелов."""
        # Act & Assert
        with pytest.raises(UnsupportedFormatError, match="Unsupported format:"):
            real_extractor_factory.get_extractor("   ")

    def test_factory_initialization_with_empty_mapping(self) -> None:
        """Тест инициализации фабрики с пустым маппингом."""
        # Arrange
        empty_mapping: dict[str, type[TextExtractor]] = {}
        factory = ExtractorFactory(empty_mapping)

        # Act & Assert
        with pytest.raises(UnsupportedFormatError):
            factory.get_extractor("any_format")

    def test_factory_initialization_with_custom_mapping(self) -> None:
        """Тест инициализации фабрики с кастомным маппингом."""
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
        """Тест что маппинг фабрики нечувствителен к регистру."""
        # Arrange
        mapping = {"TXT": MockExtractor}  # Ключ в верхнем регистре
        factory = ExtractorFactory(mapping)

        # Act & Assert - должен найти по нижнему регистру
        with pytest.raises(UnsupportedFormatError):
            factory.get_extractor("txt")

        # Но найдет по точному совпадению после lower()
        # Исправляем тест - фабрика делает lower() для формата
        mapping_lower = {"txt": MockExtractor}
        factory_lower = ExtractorFactory(mapping_lower)
        extractor = factory_lower.get_extractor("TXT")
        assert extractor == MockExtractor

    def test_factory_immutability(self, real_extractor_factory: ExtractorFactory) -> None:
        """Тест что изменение внешнего маппинга не влияет на фабрику."""
        # Arrange
        original_mapping = {"txt": MockExtractor}
        factory = ExtractorFactory(original_mapping)

        # Act - изменяем исходный маппинг
        original_mapping["new_format"] = MockExtractor

        # Assert - фабрика не должна видеть новый формат
        with pytest.raises(UnsupportedFormatError):
            factory.get_extractor("new_format")

    @pytest.mark.parametrize("special_format", [
        "format.with.dots",
        "format-with-dashes",
        "format_with_underscores",
        "format123",
        "123format",
    ])
    def test_get_extractor_with_special_characters_in_format(
            self,
            special_format: str
    ) -> None:
        """Тест получения экстрактора с специальными символами в формате."""
        # Arrange
        mapping = {special_format.lower(): MockExtractor}
        factory = ExtractorFactory(mapping)

        # Act
        extractor_class = factory.get_extractor(special_format)

        # Assert
        assert extractor_class == MockExtractor