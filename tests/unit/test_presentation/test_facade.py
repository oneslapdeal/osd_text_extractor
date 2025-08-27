from unittest.mock import Mock, patch
import pytest
from osd_text_extractor.application.exceptions import UnsupportedFormatError
from osd_text_extractor.domain.exceptions import TextLengthError
from osd_text_extractor.infrastructure.exceptions import ExtractionError
from osd_text_extractor.presentation.facade import extract_text


class TestExtractTextFacade:
    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_success(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_use_case.execute.return_value = "extracted text"

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        content = b"test content"
        format_name = "txt"

        result = extract_text(content, format_name)

        assert result == "extracted text"
        mock_create_container.assert_called_once()
        mock_container.get.assert_called_once()
        mock_use_case.execute.assert_called_once_with(content, format_name)
        mock_container.close.assert_called_once()

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_with_unsupported_format(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_use_case.execute.side_effect = UnsupportedFormatError("Unsupported format: unknown")

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container
        with pytest.raises(UnsupportedFormatError, match="Unsupported format: unknown"):
            extract_text(b"content", "unknown")
        mock_container.close.assert_called_once()

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_with_extraction_error(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_use_case.execute.side_effect = ExtractionError("Extraction failed")

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container
        with pytest.raises(ExtractionError, match="Extraction failed"):
            extract_text(b"content", "pdf")

        mock_container.close.assert_called_once()

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_with_empty_text_error(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_use_case.execute.side_effect = TextLengthError("Text length should be greater than zero")

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container
        with pytest.raises(TextLengthError, match="Text length should be greater than zero"):
            extract_text(b"content", "txt")

        mock_container.close.assert_called_once()

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_container_cleanup_on_exception(self, mock_create_container: Mock) -> None:
        mock_container = Mock()
        mock_container.get.side_effect = Exception("Container error")
        mock_create_container.return_value = mock_container
        with pytest.raises(Exception, match="Container error"):
            extract_text(b"content", "txt")
        mock_container.close.assert_called_once()

    @pytest.mark.parametrize("content,format_name,expected_calls", [
        (b"PDF content", "pdf", 1),
        (b"DOCX content", "docx", 1),
        (b"", "txt", 1),
        (b"Large content " * 1000, "html", 1),
    ])
    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_various_inputs(
            self,
            mock_create_container: Mock,
            content: bytes,
            format_name: str,
            expected_calls: int
    ) -> None:
        mock_use_case = Mock()
        mock_use_case.execute.return_value = "result text"

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container
        result = extract_text(content, format_name)
        assert result == "result text"
        assert mock_use_case.execute.call_count == expected_calls
        mock_use_case.execute.assert_called_with(content, format_name)

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_container_get_called_correctly(self, mock_create_container: Mock) -> None:
        from osd_text_extractor.application.use_cases import ExtractTextUseCase

        mock_use_case = Mock()
        mock_use_case.execute.return_value = "text"

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container
        extract_text(b"content", "txt")
        mock_container.get.assert_called_once_with(ExtractTextUseCase)

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_integration_like(self, mock_create_container: Mock) -> None:
        expected_result = "Successfully extracted text from test file"

        mock_use_case = Mock()
        mock_use_case.execute.return_value = expected_result

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        test_content = b"Test file content for extraction"
        test_format = "txt"
        result = extract_text(test_content, test_format)
        assert result == expected_result
        mock_create_container.assert_called_once()
        mock_container.get.assert_called_once()
        mock_use_case.execute.assert_called_once_with(test_content, test_format)
        mock_container.close.assert_called_once()

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_preserves_use_case_return_type(self, mock_create_container: Mock) -> None:
        mock_use_case = Mock()
        mock_use_case.execute.return_value = "string result"

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container
        result = extract_text(b"content", "txt")
        assert isinstance(result, str)
        assert result == "string result"