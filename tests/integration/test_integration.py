import pytest
from osd_text_extractor import extract_text
from osd_text_extractor.application.exceptions import UnsupportedFormatError
from osd_text_extractor.domain.exceptions import TextLengthError


class TestIntegration:
    """Integration tests using REAL extractors (not mocks)."""

    def test_extract_text_txt_format_real(self, sample_txt_content: bytes) -> None:
        """Test real TXT extraction."""
        result = extract_text(sample_txt_content, "txt")

        assert isinstance(result, str)
        assert len(result) > 0
        assert "This is a simple text file" in result
        assert "With multiple lines" in result
        assert "And some content" in result

    def test_extract_text_html_format_real(self, sample_html_content: bytes) -> None:
        """Test real HTML extraction."""
        result = extract_text(sample_html_content, "html")

        assert isinstance(result, str)
        assert len(result) > 0

        # Should contain text content
        assert "Test Page" in result
        assert "Main Title" in result
        assert "Paragraph with bold text" in result

        # Should NOT contain HTML tags or script content
        assert "<html>" not in result
        assert "<title>" not in result
        assert "alert" not in result
        assert "should be removed" not in result

    def test_extract_text_json_format_real(self, sample_json_content: bytes) -> None:
        """Test real JSON extraction."""
        result = extract_text(sample_json_content, "json")

        assert isinstance(result, str)
        assert len(result) > 0

        # Should contain all string values from JSON
        assert "Test Document" in result
        assert "Main content text" in result
        assert "Test Author" in result
        assert "test" in result
        assert "sample" in result

    def test_extract_text_csv_format_real(self, sample_csv_content: bytes) -> None:
        """Test real CSV extraction."""
        result = extract_text(sample_csv_content, "csv")

        assert isinstance(result, str)
        assert len(result) > 0

        # Should contain CSV data as text
        assert "Name Age City" in result
        assert "John Doe 30 New York" in result
        assert "Jane Smith 25 Los Angeles" in result

    def test_extract_text_markdown_format_real(self) -> None:
        """Test real Markdown extraction."""
        md_content = b"""# Main Header

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

        result = extract_text(md_content, "md")

        assert isinstance(result, str)
        assert len(result) > 0

        # Should contain cleaned text
        assert "This is a paragraph with bold and italic text" in result
        assert "List item 1" in result
        assert "List item 2" in result
        assert "Link text" in result
        assert "Regular text after code block" in result

        # Should NOT contain markdown syntax
        assert "# Main Header" not in result
        assert "## Subheader" not in result
        assert "**bold**" not in result
        assert "*italic*" not in result
        assert "```python" not in result
        assert "print(" not in result

    def test_extract_text_xml_format_real(self) -> None:
        """Test real XML extraction."""
        xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <title>XML Document Title</title>
            <content>
                <paragraph>First paragraph content</paragraph>
                <paragraph>Second paragraph content</paragraph>
            </content>
            <metadata>
                <author>XML Author</author>
                <date>2024-01-01</date>
            </metadata>
        </root>"""

        result = extract_text(xml_content, "xml")

        assert isinstance(result, str)
        assert len(result) > 0

        # Should contain text content from XML
        assert "XML Document Title" in result
        assert "First paragraph content" in result
        assert "Second paragraph content" in result
        assert "XML Author" in result
        assert "2024" in result

    def test_extract_text_unicode_handling_real(self, unicode_test_content: bytes) -> None:
        """Test that Unicode characters are properly filtered out."""
        result = extract_text(unicode_test_content, "txt")

        assert isinstance(result, str)
        assert len(result) > 0

        # Should only contain Latin text
        assert "Latin text with" in result
        assert "symbols" in result

        # Should NOT contain non-Latin characters
        assert "Русский" not in result
        assert "中文" not in result
        assert "العربية" not in result
        assert "🌍" not in result

    @pytest.mark.parametrize("unsupported_format", [
        "exe", "dll", "bin", "unknown", "fake", "pptx", "xls"
    ])
    def test_extract_text_unsupported_formats_real(self, unsupported_format: str) -> None:
        """Test that unsupported formats raise appropriate error."""
        content = b"Some content"

        with pytest.raises(UnsupportedFormatError):
            extract_text(content, unsupported_format)

    def test_extract_text_empty_content_real(self) -> None:
        """Test handling of empty content."""
        empty_content = b""

        with pytest.raises(TextLengthError):
            extract_text(empty_content, "txt")

    def test_extract_text_whitespace_only_content_real(self) -> None:
        """Test handling of whitespace-only content."""
        whitespace_content = b"   \n\n\t   "

        with pytest.raises(TextLengthError):
            extract_text(whitespace_content, "txt")

    @pytest.mark.parametrize("format_case", [
        ("TXT", "txt"),
        ("HTML", "html"),
        ("Json", "json"),
        ("CSV", "csv"),
        ("XML", "xml"),
    ])
    def test_extract_text_case_insensitive_formats_real(
            self, format_case: tuple[str, str]
    ) -> None:
        """Test that format matching is case insensitive."""
        upper_format, lower_format = format_case
        content = b"Test content for case sensitivity"

        result_upper = extract_text(content, upper_format)
        result_lower = extract_text(content, lower_format)

        assert result_upper == result_lower
        assert isinstance(result_upper, str)
        assert len(result_upper) > 0

    def test_extract_text_large_content_real(self) -> None:
        """Test extraction with large content."""
        large_content = ("Large text content with valid characters " * 1000).encode()

        result = extract_text(large_content, "txt")

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Large text content with valid characters" in result

    def test_extract_text_mixed_valid_invalid_chars_real(self) -> None:
        """Test extraction with mixed valid/invalid characters."""
        mixed_content = "Valid English text mixed with Русский текст and 中文 and symbols @#$%".encode('utf-8')

        result = extract_text(mixed_content, "txt")

        assert isinstance(result, str)
        assert len(result) > 0

        # Should contain only Latin parts
        assert "Valid English text mixed with" in result
        assert "and and symbols" in result

        # Should not contain non-Latin parts
        assert "Русский" not in result
        assert "текст" not in result
        assert "中文" not in result
        assert "@#$%" not in result

    def test_extract_text_performance_multiple_calls_real(self) -> None:
        """Test performance and consistency of multiple extractions."""
        content = b"Performance test content with consistent results"
        format_name = "txt"

        results = []
        for _ in range(5):
            result = extract_text(content, format_name)
            results.append(result)

        # All results should be identical
        assert all(result == results[0] for result in results)
        assert all(len(result) > 0 for result in results)
        assert all("Performance test content" in result for result in results)

    def test_extract_text_container_isolation_real(self) -> None:
        """Test that dependency injection container is properly isolated."""
        content1 = b"Content for first extraction call"
        content2 = b"Content for second extraction call"

        result1 = extract_text(content1, "txt")
        result2 = extract_text(content2, "txt")

        # Results should be different and correct
        assert result1 != result2
        assert "first extraction call" in result1
        assert "second extraction call" in result2

    def test_extract_text_error_propagation_real(self) -> None:
        """Test that errors are properly propagated through layers."""
        content = b"test content"

        with pytest.raises(UnsupportedFormatError) as exc_info:
            extract_text(content, "definitely_unsupported_format_12345")

        assert "definitely_unsupported_format_12345" in str(exc_info.value)

    @pytest.mark.parametrize("content_encoding", [
        ("English text", "utf-8"),
        ("English text", "ascii"),
        ("English with numbers 123", "utf-8"),
        ("UPPERCASE and lowercase", "utf-8"),
    ])
    def test_extract_text_various_encodings_real(
            self, content_encoding: tuple[str, str]
    ) -> None:
        """Test extraction with various text encodings."""
        text, encoding = content_encoding
        content = text.encode(encoding)

        result = extract_text(content, "txt")

        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain the original text (since it's all Latin)
        assert text == result

    def test_extract_text_html_with_special_entities_real(self) -> None:
        """Test HTML extraction with HTML entities."""
        html_content = b'''<html><body>
            <p>&lt;Special&gt; &amp; &quot;entities&quot;</p>
            <p>Regular text</p>
        </body></html>'''

        result = extract_text(html_content, "html")

        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain decoded entities or raw entities (depends on BeautifulSoup behavior)
        assert "Special" in result
        assert "entities" in result
        assert "Regular text" in result

    def test_extract_text_csv_with_empty_cells_real(self) -> None:
        """Test CSV extraction with empty cells."""
        csv_content = b"Name,Age,City,Empty1,Empty2,Empty3,ShouldNotAppear\nJohn,30,NYC,,,,"

        result = extract_text(csv_content, "csv")

        assert isinstance(result, str)
        assert len(result) > 0

        # Should stop processing after consecutive empty cells
        assert "Name Age City" in result
        assert "John 30 NYC" in result
        # Should not process columns after empty limit
        assert "ShouldNotAppear" not in result

    def test_extract_text_json_nested_structures_real(self) -> None:
        """Test JSON extraction with deeply nested structures."""
        json_content = b'''{
            "level1": {
                "level2": {
                    "level3": {
                        "deep_text": "Deep nested content",
                        "array": ["item1", "item2", {"nested_in_array": "nested value"}]
                    }
                }
            },
            "simple": "Simple value"
        }'''

        result = extract_text(json_content, "json")

        assert isinstance(result, str)
        assert len(result) > 0

        # Should extract all string values regardless of nesting
        assert "Deep nested content" in result
        assert "item1" in result
        assert "item2" in result
        assert "nested value" in result
        assert "Simple value" in result

    def test_extract_text_xml_with_namespaces_real(self) -> None:
        """Test XML extraction with namespaces."""
        xml_content = b'''<?xml version="1.0" encoding="UTF-8"?>
        <root xmlns:test="http://test.com" xmlns:other="http://other.com">
            <test:element>Namespaced content</test:element>
            <other:element>Other namespace content</other:element>
            <regular>Regular content</regular>
        </root>'''

        result = extract_text(xml_content, "xml")

        assert isinstance(result, str)
        assert len(result) > 0

        # Should extract text from all elements regardless of namespace
        assert "Namespaced content" in result
        assert "Other namespace content" in result
        assert "Regular content" in result

    def test_extract_text_xml_large_file_protection(self) -> None:
        """Test XML extraction with size limits."""
        # Create a very large XML content (over 10MB)
        large_xml_parts = ['<root>']
        for i in range(100000):  # This will create ~12MB XML
            large_xml_parts.append(f'<item{i}>Content {i}</item{i}>')
        large_xml_parts.append('</root>')
        large_xml = ''.join(large_xml_parts).encode()

        with pytest.raises(Exception):  # Should raise ExtractionError for size limit
            extract_text(large_xml, "xml")

    def test_extract_text_xml_deep_nesting_protection(self) -> None:
        """Test XML extraction with nesting depth limits."""
        # Create deeply nested XML (over 50 levels)
        xml_parts = ['<root>']
        for i in range(60):  # 60 levels deep
            xml_parts.append(f'<level{i}>')
        xml_parts.append('Deep content')
        for i in range(59, -1, -1):
            xml_parts.append(f'</level{i}>')
        xml_parts.append('</root>')
        deep_xml = ''.join(xml_parts).encode()

        with pytest.raises(Exception):  # Should raise ExtractionError for nesting limit
            extract_text(deep_xml, "xml")

    def test_extract_text_xml_malformed_protection(self) -> None:
        """Test XML extraction with malformed XML."""
        malformed_xml = b'<root><unclosed_tag>Content without closing</root>'

        with pytest.raises(Exception):  # Should raise ExtractionError for invalid XML
            extract_text(malformed_xml, "xml")

    def test_extract_text_end_to_end_workflow_real(self) -> None:
        """Test complete end-to-end workflow with real extraction."""
        test_cases = [
            (b"Plain text content", "txt", "Plain text content"),
            (b"<html><body>HTML content</body></html>", "html", "HTML content"),
            (b'{"text": "JSON content"}', "json", "JSON content"),
            (b"Header\nCSV,Content", "csv", "Header\nCSV Content"),
        ]

        for content, format_name, expected_substring in test_cases:
            result = extract_text(content, format_name)

            assert isinstance(result, str)
            assert len(result) > 0
            assert expected_substring in result

            # Verify only Latin chars, digits, spaces, newlines
            for char in result:
                assert char.isalnum() or char in " \n", f"Invalid character found: {repr(char)}"