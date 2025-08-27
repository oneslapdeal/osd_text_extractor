from unittest.mock import Mock, patch
import pytest

from osd_text_extractor.application.exceptions import UnsupportedFormatError
from osd_text_extractor.application.use_cases import ExtractTextUseCase
from osd_text_extractor.domain.exceptions import TextLengthError
from osd_text_extractor.infrastructure.exceptions import ExtractionError
from osd_text_extractor.presentation.facade import extract_text


class TestExtractTextFacade:
    """Test the facade function with proper mocking."""

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_success_flow(self, mock_create_container: Mock) -> None:
        """Test successful extraction flow."""
        # Setup mocks
        mock_use_case = Mock(spec=ExtractTextUseCase)
        mock_use_case.execute.return_value = "successfully extracted text"

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        # Test execution
        content = b"test file content"
        format_name = "txt"
        result = extract_text(content, format_name)

        # Assertions
        assert result == "successfully extracted text"
        mock_create_container.assert_called_once()
        mock_container.get.assert_called_once_with(ExtractTextUseCase)
        mock_use_case.execute.assert_called_once_with(content, format_name)
        mock_container.close.assert_called_once()

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_unsupported_format_error(self, mock_create_container: Mock) -> None:
        """Test handling of unsupported format error."""
        mock_use_case = Mock(spec=ExtractTextUseCase)
        mock_use_case.execute.side_effect = UnsupportedFormatError("Unsupported format: unknown")

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        with pytest.raises(UnsupportedFormatError, match="Unsupported format: unknown"):
            extract_text(b"content", "unknown")

        # Container should still be closed
        mock_container.close.assert_called_once()

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_extraction_error(self, mock_create_container: Mock) -> None:
        """Test handling of extraction error."""
        mock_use_case = Mock(spec=ExtractTextUseCase)
        mock_use_case.execute.side_effect = ExtractionError("File is corrupted")

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        with pytest.raises(ExtractionError, match="File is corrupted"):
            extract_text(b"corrupted content", "pdf")

        mock_container.close.assert_called_once()

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_domain_validation_error(self, mock_create_container: Mock) -> None:
        """Test handling of domain validation error."""
        mock_use_case = Mock(spec=ExtractTextUseCase)
        mock_use_case.execute.side_effect = TextLengthError("No valid text content after cleaning")

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        with pytest.raises(TextLengthError, match="No valid text content after cleaning"):
            extract_text(b"content", "txt")

        mock_container.close.assert_called_once()

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_container_creation_error(self, mock_create_container: Mock) -> None:
        """Test handling of container creation error."""
        mock_create_container.side_effect = Exception("Container creation failed")

        with pytest.raises(Exception, match="Container creation failed"):
            extract_text(b"content", "txt")

        # No container to close in this case
        mock_create_container.assert_called_once()

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_use_case_retrieval_error(self, mock_create_container: Mock) -> None:
        """Test handling of use case retrieval error."""
        mock_container = Mock()
        mock_container.get.side_effect = Exception("Use case retrieval failed")
        mock_create_container.return_value = mock_container

        with pytest.raises(Exception, match="Use case retrieval failed"):
            extract_text(b"content", "txt")

        # Container should still be closed even on error
        mock_container.close.assert_called_once()

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_container_close_error_handling(self, mock_create_container: Mock) -> None:
        """Test that container close errors don't interfere with results."""
        mock_use_case = Mock(spec=ExtractTextUseCase)
        mock_use_case.execute.return_value = "extracted text"

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_container.close.side_effect = Exception("Close error")
        mock_create_container.return_value = mock_container

        # Should still get the result despite close error
        result = extract_text(b"content", "txt")

        assert result == "extracted text"
        mock_container.close.assert_called_once()

    @pytest.mark.parametrize("content,format_name,expected_substring", [
        (b"Simple text content", "txt", "Simple text"),
        (b"<html><body>HTML content</body></html>", "html", "HTML"),
        (b'{"key": "JSON content"}', "json", "JSON"),
        (b"CSV,Header\nValue,Data", "csv", "CSV"),
    ])
    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_various_formats(
            self,
            mock_create_container: Mock,
            content: bytes,
            format_name: str,
            expected_substring: str
    ) -> None:
        """Test extraction with various formats and content."""
        mock_use_case = Mock(spec=ExtractTextUseCase)
        mock_use_case.execute.return_value = f"Extracted {expected_substring} content"

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        result = extract_text(content, format_name)

        assert expected_substring in result
        mock_use_case.execute.assert_called_once_with(content, format_name)

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_large_content_handling(self, mock_create_container: Mock) -> None:
        """Test extraction with large content."""
        mock_use_case = Mock(spec=ExtractTextUseCase)
        mock_use_case.execute.return_value = "Large content extracted"

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        # Create large content (1MB)
        large_content = b"Large content " * 70000  # ~1MB

        result = extract_text(large_content, "txt")

        assert result == "Large content extracted"
        mock_use_case.execute.assert_called_once_with(large_content, "txt")

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_binary_content_handling(self, mock_create_container: Mock) -> None:
        """Test extraction with binary content."""
        mock_use_case = Mock(spec=ExtractTextUseCase)
        mock_use_case.execute.return_value = "Binary content processed"

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        # Binary content with null bytes
        binary_content = bytes([0, 1, 2, 255, 254, 253]) + b"text"

        result = extract_text(binary_content, "txt")

        assert result == "Binary content processed"
        mock_use_case.execute.assert_called_once_with(binary_content, "txt")

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_dependency_injection_isolation(self, mock_create_container: Mock) -> None:
        """Test that each call gets its own container instance."""
        call_count = 0

        def mock_execute(content, format_name):
            nonlocal call_count
            call_count += 1
            return f"Result {call_count} for {format_name}"

        mock_use_case = Mock(spec=ExtractTextUseCase)
        mock_use_case.execute.side_effect = mock_execute

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        # Make multiple calls
        result1 = extract_text(b"content1", "txt")
        result2 = extract_text(b"content2", "pdf")

        assert result1 == "Result 1 for txt"
        assert result2 == "Result 2 for pdf"

        # Each call should create and close a container
        assert mock_create_container.call_count == 2
        assert mock_container.close.call_count == 2

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_preserves_use_case_return_type(self, mock_create_container: Mock) -> None:
        """Test that facade preserves the exact return type from use case."""
        mock_use_case = Mock(spec=ExtractTextUseCase)
        mock_use_case.execute.return_value = "exact string result"

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        result = extract_text(b"content", "txt")

        assert isinstance(result, str)
        assert result == "exact string result"

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_unicode_content_handling(self, mock_create_container: Mock) -> None:
        """Test extraction with Unicode content."""
        mock_use_case = Mock(spec=ExtractTextUseCase)
        mock_use_case.execute.return_value = "Unicode content processed"

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        # Unicode content
        unicode_content = "Тест with 中文 and العربية".encode('utf-8')

        result = extract_text(unicode_content, "txt")

        assert result == "Unicode content processed"
        mock_use_case.execute.assert_called_once_with(unicode_content, "txt")

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_format_parameter_passthrough(self, mock_create_container: Mock) -> None:
        """Test that format parameter is passed through correctly."""
        mock_use_case = Mock(spec=ExtractTextUseCase)
        mock_use_case.execute.return_value = "format test result"

        mock_container = Mock()
        mock_container.get.return_value = mock_use_case
        mock_create_container.return_value = mock_container

        test_formats = ["txt", "PDF", "Html", "JSON", "csv"]

        for test_format in test_formats:
            result = extract_text(b"test content", test_format)
            assert result == "format test result"

        # Verify all formats were passed correctly
        expected_calls = [(b"test content", fmt) for fmt in test_formats]
        actual_calls = [call.args for call in mock_use_case.execute.call_args_list]

        assert actual_calls == expected_calls

    @patch('osd_text_extractor.presentation.facade.create_container')
    def test_extract_text_concurrent_safety(self, mock_create_container: Mock) -> None:
        """Test that facade is safe for concurrent use (each call isolated)."""
        import threading
        import time

        results = {}

        def extraction_worker(worker_id: int):
            mock_use_case = Mock(spec=ExtractTextUseCase)
            mock_use_case.execute.return_value = f"Worker {worker_id} result"

            mock_container = Mock()
            mock_container.get.return_value = mock_use_case
            mock_create_container.return_value = mock_container

            # Simulate some processing time
            time.sleep(0.01)

            result = extract_text(f"Content {worker_id}".encode(), "txt")
            results[worker_id] = result

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=extraction_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Each worker should have its own result
        assert len(results) == 5
        for i in range(5):
            assert i in results