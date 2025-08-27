"""Тесты для use cases."""

from unittest.mock import Mock

import pytest

from osd_text_extractor.application.exceptions import UnsupportedFormatError
from osd_text_extractor.application.use_cases import ExtractTextUseCase
from osd_text_extractor.domain.exceptions import TextLengthError
from osd_text_extractor.infrastructure.exceptions import ExtractionError
from tests.conftest import MockExtractor


class TestExtractTextUseCase:
    def test_execute_success(
            self,
            extract_text_use_case: ExtractTextUseCase,
            mock_extractor_factory: Mock,
            mock_extractor: MockExtractor,
            test_content: bytes,
            test_format: str
    ) -> None:
        result = extract_text_use_case.execute(test_content, test_format)
        assert result == "test extracted text"
        mock_extractor_factory.get_extractor.assert_called_once_with(test_format)
        assert mock_extractor.extract_calls == [test_content]

    @pytest.mark.parametrize("content,format_name", [
        (b"PDF content", "pdf"),
        (b"DOCX content", "docx"),
        (b"<html>HTML</html>", "html"),
        (b'{"key": "value"}', "json"),
        (b"Plain text", "txt"),
    ])
    def test_execute_with_different_formats(
            self,
            mock_extractor_factory: Mock,
            content: bytes,
            format_name: str
    ) -> None:
        mock_extractor = MockExtractor(f"extracted from {format_name}")
        mock_extractor_factory.get_extractor.return_value = mock_extractor
        use_case = ExtractTextUseCase(mock_extractor_factory)
        result = use_case.execute(content, format_name)
        assert result == f"extracted from {format_name}"
        mock_extractor_factory.get_extractor.assert_called_once_with(format_name)

    def test_execute_with_unsupported_format_raises_error(
            self,
            unsupported_format_factory: Mock,
            test_content: bytes
    ) -> None:
        use_case = ExtractTextUseCase(unsupported_format_factory)
        with pytest.raises(UnsupportedFormatError, match="Unsupported format"):
            use_case.execute(test_content, "unsupported")

    def test_execute_with_extraction_error(
            self,
            failing_extractor_factory: Mock,
            test_content: bytes,
            test_format: str
    ) -> None:
        use_case = ExtractTextUseCase(failing_extractor_factory)
        with pytest.raises(ExtractionError, match="Test extraction error"):
            use_case.execute(test_content, test_format)

    def test_execute_with_empty_extracted_text_raises_error(
            self,
            empty_mock_extractor: MockExtractor,
            test_content: bytes,
            test_format: str
    ) -> None:
        factory = Mock()
        factory.get_extractor.return_value = empty_mock_extractor
        use_case = ExtractTextUseCase(factory)
        with pytest.raises(TextLengthError, match="Text length should be greater than zero"):
            use_case.execute(test_content, test_format)

    @pytest.mark.parametrize("format_case", [
        "PDF",
        "Pdf",
        "pdf",
        "TXT",
        "txt",
        "HTML",
        "html"
    ])
    def test_execute_format_case_insensitive(
            self,
            mock_extractor_factory: Mock,
            test_content: bytes,
            format_case: str
    ) -> None:
        use_case = ExtractTextUseCase(mock_extractor_factory)
        use_case.execute(test_content, format_case)
        mock_extractor_factory.get_extractor.assert_called_once_with(format_case)

    def test_execute_with_large_content(
            self,
            extract_text_use_case: ExtractTextUseCase,
            mock_extractor: MockExtractor,
            test_format: str
    ) -> None:
        large_content = b"Large content " * 10000  # ~140KB
        result = extract_text_use_case.execute(large_content, test_format)
        assert result == "test extracted text"
        assert mock_extractor.extract_calls == [large_content]

    def test_execute_with_binary_content(
            self,
            extract_text_use_case: ExtractTextUseCase,
            mock_extractor: MockExtractor,
            test_format: str
    ) -> None:
        binary_content = bytes(range(256))
        result = extract_text_use_case.execute(binary_content, test_format)
        assert result == "test extracted text"
        assert mock_extractor.extract_calls == [binary_content]

    def test_execute_creates_plain_text_entity(
            self,
            mock_extractor_factory: Mock,
            test_content: bytes,
            test_format: str
    ) -> None:
        mock_extractor = MockExtractor("extracted text for entity test")
        mock_extractor_factory.get_extractor.return_value = mock_extractor
        use_case = ExtractTextUseCase(mock_extractor_factory)
        result = use_case.execute(test_content, test_format)
        assert isinstance(result, str)
        assert result == "extracted text for entity test"

    @pytest.mark.parametrize("whitespace_text", [
        "   text with leading spaces",
        "text with trailing spaces   ",
        "   text with both   ",
        "text\nwith\nnewlines",
        "text\twith\ttabs",
    ])
    def test_execute_preserves_whitespace(
            self,
            mock_extractor_factory: Mock,
            test_content: bytes,
            test_format: str,
            whitespace_text: str
    ) -> None:
        mock_extractor = MockExtractor(whitespace_text)
        mock_extractor_factory.get_extractor.return_value = mock_extractor
        use_case = ExtractTextUseCase(mock_extractor_factory)
        result = use_case.execute(test_content, test_format)
        assert result == whitespace_text