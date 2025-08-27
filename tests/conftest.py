from typing import Any
from unittest.mock import Mock
import pytest
from osd_text_extractor.application.use_cases import ExtractTextUseCase
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.extractors import ExtractorFactory


class MockExtractor(TextExtractor):
    def __init__(self, return_value: str = "extracted text"):
        self.return_value = return_value
        self.extract_calls = []

    def extract_plain_text(self, content: bytes) -> str:
        self.extract_calls.append(content)
        return self.return_value


class MockFailingExtractor(TextExtractor):
    def __init__(self, exception: Exception):
        self.exception = exception

    def extract_plain_text(self, content: bytes) -> str:
        raise self.exception


@pytest.fixture
def mock_extractor() -> MockExtractor:
    return MockExtractor("test extracted text")


@pytest.fixture
def empty_mock_extractor() -> MockExtractor:
    return MockExtractor("")


@pytest.fixture
def failing_mock_extractor() -> MockFailingExtractor:
    from osd_text_extractor.infrastructure.exceptions import ExtractionError
    return MockFailingExtractor(ExtractionError("Test extraction error"))


@pytest.fixture
def mock_extractor_factory(mock_extractor: MockExtractor) -> Mock:
    factory = Mock(spec=ExtractorFactory)
    factory.get_extractor.return_value = mock_extractor
    return factory


@pytest.fixture
def failing_extractor_factory(failing_mock_extractor: MockFailingExtractor) -> Mock:
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


@pytest.fixture(params=[
    ("pdf", b"PDF content"),
    ("docx", b"DOCX content"),
    ("txt", b"TXT content"),
    ("html", b"<html>HTML content</html>"),
    ("json", b'{"key": "value"}'),
])
def format_content_pair(request: Any) -> tuple[str, bytes]:
    return request.param


@pytest.fixture(params=[
    "pdf", "docx", "xlsx", "txt", "html", "xml", "json", "md", "rtf",
    "csv", "epub", "fb2", "ods", "odt"
])
def supported_format(request: Any) -> str:
    return request.param


@pytest.fixture(params=[
    "unsupported", "fake", "unknown", "", "   ", "123", "test.exe"
])
def unsupported_format(request: Any) -> str:
    return request.param


@pytest.fixture(params=[
    b"",
    b"   ",
    b"\n\n\n",
    b"\t\t\t",
])
def empty_content(request: Any) -> bytes:
    return request.param


@pytest.fixture(params=[
    ("Very long text " * 1000).encode(),
    b"Unicode test: \xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82",
    bytes(range(256)),
])
def edge_case_content(request: Any) -> bytes:
    return request.param


@pytest.fixture
def extractor_mapping() -> dict[str, type[TextExtractor]]:
    return {
        "txt": MockExtractor,
        "pdf": MockExtractor,
        "docx": MockExtractor,
    }


@pytest.fixture
def real_extractor_factory(extractor_mapping: dict[str, type[TextExtractor]]) -> ExtractorFactory:
    return ExtractorFactory(extractor_mapping)