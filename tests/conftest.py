from typing import Any
from unittest.mock import Mock

import pytest
from osd_text_extractor.application.use_cases import ExtractTextUseCase
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.extractors import ExtractorFactory


class MockExtractor:
    """Mock extractor that follows TextExtractor protocol correctly."""

    def __init__(self, return_value: str = "extracted text"):
        self.return_value = return_value
        self.extract_calls = []
        self.extract_calls = []

    @staticmethod
    def create_with_return_value(return_value: str) -> type:
        """Create a mock extractor class that returns specific value."""

        class SpecificMockExtractor:
            @staticmethod
            def extract_plain_text(content: bytes) -> str:
                _content = content
                return return_value

        return SpecificMockExtractor

    @staticmethod
    def extract_plain_text(content: bytes) -> str:
        # This won't work for instance tracking, but follows protocol
        _content = content
        return "default extracted text"


class TrackingMockExtractor:
    """Mock extractor that tracks calls (for testing purposes only)."""

    calls: list[bytes] = []
    return_value: str = "extracted text"

    @classmethod
    def extract_plain_text(cls, content: bytes) -> str:
        cls.calls.append(content)
        return cls.return_value

    @classmethod
    def reset(cls) -> None:
        cls.calls.clear()

    @classmethod
    def set_return_value(cls, value: str) -> None:
        cls.return_value = value


class MockFailingExtractor:
    def __init__(self, exception: Exception):
        self.exception = exception

    @staticmethod
    def extract_plain_text(content: bytes) -> str:
        _content = content
        raise Exception("Mock extraction error")


@pytest.fixture
def tracking_mock_extractor() -> type[TrackingMockExtractor]:
    """Returns extractor class that tracks calls."""
    TrackingMockExtractor.reset()
    TrackingMockExtractor.set_return_value("test extracted text")
    return TrackingMockExtractor


@pytest.fixture
def empty_mock_extractor() -> type:
    """Returns extractor that produces empty text."""
    return MockExtractor.create_with_return_value("")


@pytest.fixture
def failing_mock_extractor() -> type:
    """Returns extractor that raises an error."""
    from osd_text_extractor.infrastructure.exceptions import ExtractionError

    class FailingExtractor:
        @staticmethod
        def extract_plain_text(content: bytes) -> str:
            _content = content
            raise ExtractionError("Test extraction error")

    return FailingExtractor


@pytest.fixture
def mock_extractor_factory(tracking_mock_extractor: type) -> Mock:
    factory = Mock(spec=ExtractorFactory)
    factory.get_extractor.return_value = tracking_mock_extractor
    return factory


@pytest.fixture
def failing_extractor_factory(failing_mock_extractor: type) -> Mock:
    factory = Mock(spec=ExtractorFactory)
    factory.get_extractor.return_value = failing_mock_extractor
    return factory


@pytest.fixture
def unsupported_format_factory() -> Mock:
    from osd_text_extractor.application.exceptions import UnsupportedFormatError

    factory = Mock(spec=ExtractorFactory)
    factory.get_extractor.side_effect = UnsupportedFormatError("Unsupported format")
    return factory


@pytest.fixture
def extract_text_use_case(mock_extractor_factory: Mock) -> ExtractTextUseCase:
    return ExtractTextUseCase(mock_extractor_factory)


@pytest.fixture
def test_content() -> bytes:
    return b"test file content"


@pytest.fixture
def test_format() -> str:
    return "txt"


@pytest.fixture(
    params=[
        ("pdf", b"PDF content"),
        ("docx", b"DOCX content"),
        ("txt", b"TXT content"),
        ("html", b"<html>HTML content</html>"),
        ("json", b'{"key": "value"}'),
    ],
)
def format_content_pair(request: Any) -> tuple[str, bytes]:
    return request.param


@pytest.fixture(
    params=[
        "pdf",
        "docx",
        "xlsx",
        "txt",
        "html",
        "xml",
        "json",
        "md",
        "rtf",
        "csv",
        "epub",
        "fb2",
        "ods",
        "odt",
    ],
)
def supported_format(request: Any) -> str:
    return request.param


@pytest.fixture(params=["unsupported", "fake", "unknown", "", "   ", "123", "test.exe"])
def unsupported_format(request: Any) -> str:
    return request.param


@pytest.fixture(
    params=[
        b"",
        b"   ",
        b"\n\n\n",
        b"\t\t\t",
    ],
)
def empty_content(request: Any) -> bytes:
    return request.param


@pytest.fixture(
    params=[
        ("Very long text " * 1000).encode(),
        b"Unicode test: \xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82",
        bytes(range(256)),
    ],
)
def edge_case_content(request: Any) -> bytes:
    return request.param


@pytest.fixture
def extractor_mapping() -> dict[str, type[TextExtractor]]:
    return {
        "txt": MockExtractor.create_with_return_value("txt content"),
        "pdf": MockExtractor.create_with_return_value("pdf content"),
        "docx": MockExtractor.create_with_return_value("docx content"),
    }


@pytest.fixture
def real_extractor_factory(
    extractor_mapping: dict[str, type[TextExtractor]],
) -> ExtractorFactory:
    return ExtractorFactory(extractor_mapping)


# Real test data fixtures
@pytest.fixture
def sample_txt_content() -> bytes:
    return b"This is a simple text file.\nWith multiple lines.\nAnd some content."


@pytest.fixture
def sample_html_content() -> bytes:
    return b"""<!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Main Title</h1>
        <p>Paragraph with <strong>bold</strong> text.</p>
        <script>alert('should be removed');</script>
    </body>
    </html>"""


@pytest.fixture
def sample_json_content() -> bytes:
    return b"""{
        "title": "Test Document",
        "content": "Main content text",
        "metadata": {
            "author": "Test Author",
            "tags": ["test", "sample"]
        }
    }"""


@pytest.fixture
def sample_csv_content() -> bytes:
    return b"Name,Age,City\nJohn Doe,30,New York\nJane Smith,25,Los Angeles"


@pytest.fixture
def unicode_test_content() -> bytes:
    return "Latin text with Русский 中文 العربية 🌍 symbols".encode()
