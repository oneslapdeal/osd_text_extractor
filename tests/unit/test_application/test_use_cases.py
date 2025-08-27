from unittest.mock import Mock
import pytest

from osd_text_extractor.application.exceptions import UnsupportedFormatError
from osd_text_extractor.application.use_cases import ExtractTextUseCase
from osd_text_extractor.domain.exceptions import TextLengthError
from osd_text_extractor.infrastructure.exceptions import ExtractionError


class TestExtractTextUseCase:

    def test_execute_success(
        self,
        mock_extractor_factory: Mock,
        tracking_mock_extractor: type,
        test_content: bytes,
        test_format: str
    ) -> None:
        use_case = ExtractTextUseCase(mock_extractor_factory)

        result = use_case.execute(test_content, test_format)

        assert result == "test extracted text"
        mock_extractor_factory.get_extractor.assert_called_once_with(test_format)
        assert test_content in tracking_mock_extractor.calls

    def test_execute_with_different_formats(
        self, mock_extractor_factory: Mock
    ) -> None:
        test_cases = [
            (b"PDF content", "pdf", "extracted from pdf"),
            (b"DOCX content", "docx", "extracted from docx"),
            (b"<html>HTML</html>", "html", "extracted from html"),
            (b'{"key": "value"}', "json", "extracted from json"),
            (b"Plain text", "txt", "extracted from txt"),
        ]

        for content, format_name, expected_result in test_cases:
            class SpecificMockExtractor:
                @staticmethod
                def extract_plain_text(content: bytes) -> str:
                    return expected_result

            mock_extractor_factory.get_extractor.return_value = SpecificMockExtractor
            use_case = ExtractTextUseCase(mock_extractor_factory)

            result = use_case.execute(content, format_name)

            assert result == expected_result
            mock_extractor_factory.get_extractor.assert_called_with(format_name)

            mock_extractor_factory.reset_mock()

    def test_execute_with_unsupported_format_raises_error(
        self, unsupported_format_factory: Mock, test_content: bytes
    ) -> None:
        use_case = ExtractTextUseCase(unsupported_format_factory)

        with pytest.raises(UnsupportedFormatError, match="Unsupported format"):
            use_case.execute(test_content, "unsupported")

    def test_execute_with_extraction_error(
        self, failing_extractor_factory: Mock, test_content: bytes, test_format: str
    ) -> None:
        use_case = ExtractTextUseCase(failing_extractor_factory)

        with pytest.raises(ExtractionError, match="Test extraction error"):
            use_case.execute(test_content, test_format)

    def test_execute_with_empty_extracted_text_raises_error(
        self, empty_mock_extractor: type, test_content: bytes, test_format: str
    ) -> None:
        factory = Mock()
        factory.get_extractor.return_value = empty_mock_extractor
        use_case = ExtractTextUseCase(factory)

        with pytest.raises(TextLengthError, match="Input text cannot be empty"):
            use_case.execute(test_content, test_format)

    def test_execute_format_case_sensitivity(
        self, mock_extractor_factory: Mock, test_content: bytes
    ) -> None:
        format_cases = ["PDF", "Pdf", "pdf", "TXT", "txt", "HTML", "html"]

        use_case = ExtractTextUseCase(mock_extractor_factory)

        for format_case in format_cases:
            use_case.execute(test_content, format_case)
            mock_extractor_factory.get_extractor.assert_called_with(format_case)
            mock_extractor_factory.reset_mock()

    def test_execute_with_large_content(
        self, mock_extractor_factory: Mock, tracking_mock_extractor: type, test_format: str
    ) -> None:
        large_content = b"Large content " * 10000  # ~140KB
        use_case = ExtractTextUseCase(mock_extractor_factory)

        result = use_case.execute(large_content, test_format)

        assert result == "test extracted text"
        assert large_content in tracking_mock_extractor.calls

    def test_execute_with_binary_content(
        self, mock_extractor_factory: Mock, tracking_mock_extractor: type, test_format: str
    ) -> None:
        binary_content = bytes(range(256))
        use_case = ExtractTextUseCase(mock_extractor_factory)

        result = use_case.execute(binary_content, test_format)

        assert result == "test extracted text"
        assert binary_content in tracking_mock_extractor.calls

    def test_execute_creates_and_validates_plain_text_entity(
        self, mock_extractor_factory: Mock, test_content: bytes, test_format: str
    ) -> None:
        class MixedContentExtractor:
            @staticmethod
            def extract_plain_text(content: bytes) -> str:
                return "Latin text with Русский mixed content"

        mock_extractor_factory.get_extractor.return_value = MixedContentExtractor
        use_case = ExtractTextUseCase(mock_extractor_factory)

        result = use_case.execute(test_content, test_format)

        assert isinstance(result, str)
        assert result == "Latin text with mixed content"

    def test_execute_with_non_latin_only_content_raises_error(
        self, mock_extractor_factory: Mock, test_content: bytes, test_format: str
    ) -> None:
        class NonLatinExtractor:
            @staticmethod
            def extract_plain_text(content: bytes) -> str:
                return "Русский текст 中文 العربية"

        mock_extractor_factory.get_extractor.return_value = NonLatinExtractor
        use_case = ExtractTextUseCase(mock_extractor_factory)

        with pytest.raises(TextLengthError, match="No valid text content after cleaning"):
            use_case.execute(test_content, test_format)

    @pytest.mark.parametrize("whitespace_text,expected_clean", [
        ("   text with leading spaces", "text with leading spaces"),
        ("text with trailing spaces   ", "text with trailing spaces"),
        ("   text with both   ", "text with both"),
        ("text\nwith\nnewlines", "text\nwith\nnewlines"),
        ("text\twith\ttabs", "text with tabs"),
        ("text  with  multiple  spaces", "text with multiple spaces"),
    ])
    def test_execute_whitespace_normalization(
        self,
        mock_extractor_factory: Mock,
        test_content: bytes,
        test_format: str,
        whitespace_text: str,
        expected_clean: str
    ) -> None:
        class WhitespaceExtractor:
            @staticmethod
            def extract_plain_text(content: bytes) -> str:
                return whitespace_text

        mock_extractor_factory.get_extractor.return_value = WhitespaceExtractor
        use_case = ExtractTextUseCase(mock_extractor_factory)

        result = use_case.execute(test_content, test_format)
        assert result == expected_clean

    def test_execute_preserves_extractor_error_context(
        self, test_content: bytes, test_format: str
    ) -> None:
        class SpecificErrorExtractor:
            @staticmethod
            def extract_plain_text(content: bytes) -> str:
                raise ExtractionError("Specific extraction failure")

        factory = Mock()
        factory.get_extractor.return_value = SpecificErrorExtractor
        use_case = ExtractTextUseCase(factory)

        with pytest.raises(ExtractionError, match="Specific extraction failure"):
            use_case.execute(test_content, test_format)

    def test_execute_multiple_calls_independence(
        self, mock_extractor_factory: Mock, tracking_mock_extractor: type
    ) -> None:
        use_case = ExtractTextUseCase(mock_extractor_factory)

        content1 = b"First content"
        content2 = b"Second content"

        result1 = use_case.execute(content1, "txt")
        result2 = use_case.execute(content2, "txt")

        assert result1 == "test extracted text"
        assert result2 == "test extracted text"

        assert content1 in tracking_mock_extractor.calls
        assert content2 in tracking_mock_extractor.calls
        assert len(tracking_mock_extractor.calls) == 2

    def test_execute_factory_interaction(
        self, mock_extractor_factory: Mock, test_content: bytes, test_format: str
    ) -> None:
        use_case = ExtractTextUseCase(mock_extractor_factory)

        use_case.execute(test_content, test_format)

        mock_extractor_factory.get_extractor.assert_called_once_with(test_format)

        assert len(mock_extractor_factory.method_calls) == 1