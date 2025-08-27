import pytest

from osd_text_extractor import extract_text
from osd_text_extractor.application.exceptions import UnsupportedFormatError
from osd_text_extractor.domain.exceptions import TextLengthError


class TestIntegration:
    @pytest.mark.parametrize("content,format_name", [
        (b"Simple text content", "txt"),
        (b"<html><body>HTML content</body></html>", "html"),
        (b'{"key": "JSON value"}', "json"),
        (b"col1,col2\nval1,val2", "csv"),
        (b"# Markdown header\nContent", "md"),
        (b"<root>XML content</root>", "xml"),
    ])
    def test_extract_text_end_to_end_success(
            self, content: bytes, format_name: str
    ) -> None:

        result = extract_text(content, format_name)

        assert isinstance(result, str)
        assert len(result) > 0
        assert any(char.isalpha() for char in result)

    def test_extract_text_with_txt_format_detailed(self) -> None:
        content = b"This is a test text file.\nWith multiple lines.\nAnd special chars: !@#$%"
        result = extract_text(content, "txt")
        assert "This is a test text file." in result
        assert "With multiple lines." in result
        assert "And special chars: !@#$%" in result

    def test_extract_text_with_html_format_detailed(self) -> None:

        content = b"""
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Main Title</h1>
                <p>Paragraph with <strong>bold</strong> text.</p>
                <script>alert('should be removed');</script>
            </body>
        </html>
        """

        result = extract_text(content, "html")

        assert "Test Page" in result
        assert "Main Title" in result
        assert "Paragraph" in result
        assert "bold" in result
        assert "alert" not in result
        assert "should be removed" not in result

    def test_extract_text_with_json_format_detailed(self) -> None:
        content = b'''
        {
            "title": "Test Document",
            "content": "Main content text",
            "metadata": {
                "author": "Test Author",
                "tags": ["test", "sample", "document"]
            }
        }
        '''

        result = extract_text(content, "json")

        assert "Test Document" in result
        assert "Main content text" in result
        assert "Test Author" in result
        assert "test" in result
        assert "sample" in result
        assert "document" in result

    def test_extract_text_with_csv_format_detailed(self) -> None:
        content = b"Name,Age,City\nJohn Doe,30,New York\nJane Smith,25,Los Angeles"
        result = extract_text(content, "csv")
        assert "Name Age City" in result
        assert "John Doe 30 New York" in result
        assert "Jane Smith 25 Los Angeles" in result

    def test_extract_text_with_markdown_format_detailed(self) -> None:
        content = b"""
        # Main Header

        This is a paragraph with **bold** and *italic* text.

        ## Subheader

        - List item 1
        - List item 2

        [Link text](http://example.com)

        ```python
        # This code should be removed
        print("hello")
        ```

        Regular text after code block.
        """

        result = extract_text(content, "md")

        assert "This is a paragraph with bold and italic text" in result
        assert "List item 1" in result
        assert "List item 2" in result
        assert "Link text" in result
        assert "Regular text after code block" in result

        assert "# Main Header" not in result
        assert "## Subheader" not in result
        assert "**bold**" not in result
        assert "*italic*" not in result
        assert "- List" not in result
        assert "```python" not in result
        assert "print(" not in result

    @pytest.mark.parametrize("unsupported_format", [
        "exe", "dll", "bin", "unknown", "fake", "", "   "
    ])
    def test_extract_text_unsupported_formats(self, unsupported_format: str) -> None:

        content = b"Some content"

        with pytest.raises(UnsupportedFormatError):
            extract_text(content, unsupported_format)

    def test_extract_text_empty_content_handling(self) -> None:

        empty_content = b""
        with pytest.raises(TextLengthError):
            extract_text(empty_content, "txt")

    @pytest.mark.parametrize("format_case", [
        ("TXT", "txt"),
        ("HTML", "html"),
        ("Json", "json"),
        ("CSV", "csv"),
    ])
    def test_extract_text_case_insensitive_formats(
            self, format_case: tuple[str, str]
    ) -> None:
        upper_format, lower_format = format_case
        content = b"Test content"

        result_upper = extract_text(content, upper_format)
        result_lower = extract_text(content, lower_format)

        assert result_upper == result_lower

    def test_extract_text_large_content(self) -> None:
        large_content = ("Large text content " * 10000).encode()

        result = extract_text(large_content, "txt")

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Large text content" in result

    def test_extract_text_unicode_content(self) -> None:
        unicode_content = "Тестовый текст с Unicode: 你好世界 🌍 العربية".encode('utf-8')
        result = extract_text(unicode_content, "txt")
        assert "Тестовый текст с Unicode" in result
        assert "你好世界" in result
        assert "🌍" in result
        assert "العربية" in result

    def test_extract_text_xml_with_namespaces(self) -> None:
        xml_content = b'''<?xml version="1.0" encoding="UTF-8"?>
        <root xmlns:test="http://test.com">
            <test:element>Namespaced content</test:element>
            <regular>Regular content</regular>
        </root>'''
        result = extract_text(xml_content, "xml")
        assert "Namespaced content" in result
        assert "Regular content" in result

    def test_extract_text_html_with_entities(self) -> None:
        html_content = b'<html><body><p>&lt;Test&gt; &amp; &quot;entities&quot;</p></body></html>'

        result = extract_text(html_content, "html")

        assert "<Test>" in result or "&lt;Test&gt;" in result
        assert "&" in result or "&amp;" in result

    def test_extract_text_performance_multiple_calls(self) -> None:
        content = b"Performance test content"
        format_name = "txt"

        results = []
        for _ in range(10):
            result = extract_text(content, format_name)
            results.append(result)

        assert all(result == results[0] for result in results)
        assert all(len(result) > 0 for result in results)

    def test_extract_text_dependency_injection_container_isolation(self) -> None:
        content1 = b"Content for first call"
        content2 = b"Content for second call"
        result1 = extract_text(content1, "txt")
        result2 = extract_text(content2, "txt")
        assert result1 != result2
        assert "first call" in result1
        assert "second call" in result2

    def test_extract_text_error_handling_chain(self) -> None:
        content = b"test content"
        with pytest.raises(UnsupportedFormatError) as exc_info:
            extract_text(content, "definitely_unsupported_format")

        assert "definitely_unsupported_format" in str(exc_info.value)

    @pytest.mark.parametrize("content_encoding", [
        ("Русский текст", "utf-8"),
        ("English text", "ascii"),
        ("Français", "utf-8"),
        ("Español", "latin-1"),
    ])
    def test_extract_text_various_encodings(
            self, content_encoding: tuple[str, str]
    ) -> None:
        text, encoding = content_encoding
        try:
            content = text.encode(encoding)
        except UnicodeEncodeError:
            content = text.encode('utf-8')
        result = extract_text(content, "txt")
        assert len(result) > 0
        assert any(char.isalpha() for char in result)