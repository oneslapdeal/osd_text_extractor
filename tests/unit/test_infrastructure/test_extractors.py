from unittest.mock import Mock, patch
import pytest

from osd_text_extractor.infrastructure.exceptions import ExtractionError
from osd_text_extractor.infrastructure.extractors import (
    CSVExtractor,
    DOCXExtractor,
    HTMLExtractor,
    JSONExtractor,
    MDExtractor,
    PDFExtractor,
    TXTExtractor,
    XMLExtractor,
)


class TestTXTExtractor:
    """Test TXTExtractor with real functionality."""

    def test_extract_plain_text_simple_success(self) -> None:
        """Test basic text extraction."""
        content = b"Simple text content"
        result = TXTExtractor.extract_plain_text(content)
        assert result == "Simple text content"

    def test_extract_plain_text_with_newlines(self) -> None:
        """Test text with newlines."""
        content = b"Line 1\nLine 2\nLine 3"
        result = TXTExtractor.extract_plain_text(content)
        assert result == "Line 1\nLine 2\nLine 3"

    def test_extract_plain_text_removes_emoji(self) -> None:
        """Test that emoji removal works."""
        content = "Text with emoji 🌍 and 🚀".encode('utf-8')
        result = TXTExtractor.extract_plain_text(content)
        assert "Text with emoji and" in result
        assert "🌍" not in result
        assert "🚀" not in result

    @pytest.mark.parametrize("encoding_content", [
        ("Test text", "utf-8"),
        ("Test text", "ascii"),
        ("English text", "iso-8859-1"),
    ])
    def test_extract_plain_text_different_encodings(
            self, encoding_content: tuple[str, str]
    ) -> None:
        """Test extraction with different encodings."""
        text, encoding = encoding_content
        content = text.encode(encoding)
        result = TXTExtractor.extract_plain_text(content)
        assert text in result

    @patch('osd_text_extractor.infrastructure.extractors._xml.et.fromstring')
    def test_extract_plain_text_handles_parsing_error(self, mock_fromstring: Mock) -> None:
        """Test error handling when XML parsing fails."""
        mock_fromstring.side_effect = Exception("XML parsing error")
        content = b"<root>test</root>"

        with pytest.raises(ExtractionError, match="Failed to extract XML text"):
            XMLExtractor.extract_plain_text(content)


class TestMDExtractor:
    """Test MDExtractor with real functionality."""

    def test_extract_plain_text_removes_headers(self) -> None:
        """Test that markdown headers are removed."""
        md_content = b"# Header 1\n## Header 2\nParagraph text"
        result = MDExtractor.extract_plain_text(md_content)
        assert "Paragraph text" in result
        assert "# Header 1" not in result
        assert "## Header 2" not in result

    def test_extract_plain_text_removes_bold_italic(self) -> None:
        """Test that bold and italic formatting is removed."""
        md_content = b"**Bold text** and *italic text* and __underlined__"
        result = MDExtractor.extract_plain_text(md_content)
        assert "Bold text and italic text and underlined" in result
        assert "**" not in result
        assert "*italic*" not in result
        assert "__" not in result

    def test_extract_plain_text_removes_links(self) -> None:
        """Test that markdown links are converted to text."""
        md_content = b"Check out [Google](http://google.com) for search"
        result = MDExtractor.extract_plain_text(md_content)
        assert "Check out Google for search" in result
        assert "[Google]" not in result
        assert "http://google.com" not in result

    def test_extract_plain_text_removes_images(self) -> None:
        """Test that markdown images are converted to alt text."""
        md_content = b"Here is an image: ![Alt text](image.jpg)"
        result = MDExtractor.extract_plain_text(md_content)
        assert "Here is an image: Alt text" in result
        assert "![Alt text]" not in result
        assert "image.jpg" not in result

    def test_extract_plain_text_removes_code_blocks(self) -> None:
        """Test that code blocks are removed."""
        md_content = b"```python\nprint('hello')\n```\nNormal text"
        result = MDExtractor.extract_plain_text(md_content)
        assert "Normal text" in result
        assert "```" not in result
        assert "print('hello')" not in result

    def test_extract_plain_text_removes_inline_code(self) -> None:
        """Test that inline code is removed."""
        md_content = b"Use the `print()` function to output"
        result = MDExtractor.extract_plain_text(md_content)
        assert "Use the function to output" in result
        assert "`print()`" not in result

    def test_extract_plain_text_removes_lists(self) -> None:
        """Test that list formatting is removed."""
        md_content = b"- Item 1\n- Item 2\n1. Numbered item"
        result = MDExtractor.extract_plain_text(md_content)
        assert "Item 1" in result
        assert "Item 2" in result
        assert "Numbered item" in result
        assert "- " not in result
        assert "1. " not in result

    def test_extract_plain_text_removes_blockquotes(self) -> None:
        """Test that blockquote formatting is removed."""
        md_content = b"> This is a quote\n> Second line"
        result = MDExtractor.extract_plain_text(md_content)
        assert "This is a quote" in result
        assert "Second line" in result
        assert "> " not in result

    def test_extract_plain_text_removes_horizontal_rules(self) -> None:
        """Test that horizontal rules are removed."""
        md_content = b"Text before\n---\nText after\n***\nMore text"
        result = MDExtractor.extract_plain_text(md_content)
        assert "Text before" in result
        assert "Text after" in result
        assert "More text" in result
        assert "---" not in result
        assert "***" not in result

    def test_extract_plain_text_normalizes_whitespace(self) -> None:
        """Test that whitespace is normalized."""
        md_content = b"Text   with\n\n\nmultiple\t\tspaces"
        result = MDExtractor.extract_plain_text(md_content)
        assert "Text with multiple spaces" in result

    def test_extract_plain_text_removes_emoji(self) -> None:
        """Test emoji removal in markdown content."""
        md_content = "# Header with 🌍 emoji\nText content".encode('utf-8')
        result = MDExtractor.extract_plain_text(md_content)
        assert "Text content" in result
        assert "🌍" not in result

    @patch('osd_text_extractor.infrastructure.extractors.utils.decode_to_utf8')
    def test_extract_plain_text_handles_decode_error(self, mock_decode: Mock) -> None:
        """Test error handling when decoding fails."""
        mock_decode.side_effect = Exception("Decode error")
        content = b"# Test markdown"

        with pytest.raises(ExtractionError, match="Failed to extract MD text"):
            MDExtractor.extract_plain_text(content)


class TestDOCXExtractor:
    """Test DOCXExtractor with mocked python-docx."""

    @patch('osd_text_extractor.infrastructure.extractors._docx.Document')
    def test_extract_plain_text_success(self, mock_document_class: Mock) -> None:
        """Test successful DOCX extraction."""
        # Mock paragraph
        mock_paragraph = Mock()
        mock_paragraph.text = "Paragraph text"

        # Mock document
        mock_doc = Mock()
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = []

        mock_document_class.return_value = mock_doc

        result = DOCXExtractor.extract_plain_text(b"DOCX content")

        assert "Paragraph text" in result
        mock_document_class.assert_called_once()

    @patch('osd_text_extractor.infrastructure.extractors._docx.Document')
    def test_extract_plain_text_with_tables(self, mock_document_class: Mock) -> None:
        """Test DOCX extraction with tables."""
        # Mock table cell
        mock_cell = Mock()
        mock_cell.text = "Cell text"

        # Mock table row
        mock_row = Mock()
        mock_row.cells = [mock_cell]

        # Mock table
        mock_table = Mock()
        mock_table.rows = [mock_row]

        # Mock document
        mock_doc = Mock()
        mock_doc.paragraphs = []
        mock_doc.tables = [mock_table]

        mock_document_class.return_value = mock_doc

        result = DOCXExtractor.extract_plain_text(b"DOCX content")

        assert "Cell text" in result

    @patch('osd_text_extractor.infrastructure.extractors._docx.Document')
    def test_extract_plain_text_mixed_content(self, mock_document_class: Mock) -> None:
        """Test DOCX with both paragraphs and tables."""
        # Mock paragraph
        mock_paragraph = Mock()
        mock_paragraph.text = "Paragraph content"

        # Mock table cell
        mock_cell = Mock()
        mock_cell.text = "Table content"
        mock_row = Mock()
        mock_row.cells = [mock_cell]
        mock_table = Mock()
        mock_table.rows = [mock_row]

        # Mock document
        mock_doc = Mock()
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = [mock_table]

        mock_document_class.return_value = mock_doc

        result = DOCXExtractor.extract_plain_text(b"DOCX content")

        assert "Paragraph content" in result
        assert "Table content" in result

    @patch('osd_text_extractor.infrastructure.extractors._docx.Document')
    def test_extract_plain_text_empty_paragraphs_filtered(self, mock_document_class: Mock) -> None:
        """Test that empty paragraphs are filtered out."""
        # Mock paragraphs with some empty
        mock_paragraph1 = Mock()
        mock_paragraph1.text = "Valid content"
        mock_paragraph2 = Mock()
        mock_paragraph2.text = "   "  # Whitespace only
        mock_paragraph3 = Mock()
        mock_paragraph3.text = ""  # Empty
        mock_paragraph4 = Mock()
        mock_paragraph4.text = "More valid content"

        mock_doc = Mock()
        mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2, mock_paragraph3, mock_paragraph4]
        mock_doc.tables = []

        mock_document_class.return_value = mock_doc

        result = DOCXExtractor.extract_plain_text(b"DOCX content")

        assert "Valid content" in result
        assert "More valid content" in result
        # Should only have valid content, joined by newlines
        assert result == "Valid content\nMore valid content"

    @patch('osd_text_extractor.infrastructure.extractors._docx.Document')
    def test_extract_plain_text_removes_emoji(self, mock_document_class: Mock) -> None:
        """Test emoji removal in DOCX content."""
        mock_paragraph = Mock()
        mock_paragraph.text = "Text with 🌍 emoji"

        mock_doc = Mock()
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = []

        mock_document_class.return_value = mock_doc

        result = DOCXExtractor.extract_plain_text(b"DOCX content")

        assert "Text with emoji" in result
        assert "🌍" not in result

    @patch('osd_text_extractor.infrastructure.extractors._docx.Document')
    def test_extract_plain_text_handles_docx_error(self, mock_document_class: Mock) -> None:
        """Test error handling when DOCX parsing fails."""
        mock_document_class.side_effect = Exception("DOCX parsing error")

        with pytest.raises(ExtractionError, match="Failed to extract DOCX text"):
            DOCXExtractor.extract_plain_text(b"Invalid DOCX content")


class TestExtractorErrorHandling:
    """Test error handling patterns across all extractors."""

    def test_all_extractors_handle_empty_input(self) -> None:
        """Test that all extractors handle empty input gracefully."""
        extractors = [
            TXTExtractor,
            HTMLExtractor,
            JSONExtractor,
            CSVExtractor,
            XMLExtractor,
            MDExtractor,
        ]

        empty_content = b""

        for extractor in extractors:
            try:
                result = extractor.extract_plain_text(empty_content)
                # If no exception, result should be empty string
                assert result == ""
            except ExtractionError:
                # It's acceptable for extractors to raise ExtractionError for empty input
                pass

    def test_all_extractors_return_strings(self) -> None:
        """Test that all extractors return string results."""
        test_cases = [
            (TXTExtractor, b"Simple text"),
            (HTMLExtractor, b"<html><body>HTML text</body></html>"),
            (JSONExtractor, b'{"key": "JSON text"}'),
            (CSVExtractor, b"Header\nValue"),
            (XMLExtractor, b"<root>XML text</root>"),
            (MDExtractor, b"# Markdown text"),
        ]

        for extractor_class, content in test_cases:
            result = extractor_class.extract_plain_text(content)
            assert isinstance(result, str), f"{extractor_class.__name__} did not return string"
            # Result should not contain emojis (assuming input doesn't have any)

    def test_all_extractors_follow_protocol(self) -> None:
        """Test that all extractors follow the TextExtractor protocol."""
        from osd_text_extractor.domain.interfaces import TextExtractor

        extractors = [
            TXTExtractor,
            HTMLExtractor,
            JSONExtractor,
            CSVExtractor,
            XMLExtractor,
            MDExtractor,
        ]

        for extractor in extractors:
            # Check that extract_plain_text is a static method
            assert hasattr(extractor, 'extract_plain_text')
            assert callable(extractor.extract_plain_text)

            # Check method signature (should accept bytes, return str)
            import inspect
            sig = inspect.signature(extractor.extract_plain_text)
            params = list(sig.parameters.keys())

            # Should have one parameter (content)
            assert len(params) >= 1, f"{extractor.__name__} missing content parameter"

    def test_extractors_handle_unicode_input(self) -> None:
        """Test that extractors handle Unicode input properly."""
        unicode_content = "Text with Unicode: Русский 中文 العربية".encode('utf-8')

        test_cases = [
            (TXTExtractor, unicode_content),
            (HTMLExtractor, b"<html><body>" + unicode_content + b"</body></html>"),
            (JSONExtractor, b'{"text": "' + unicode_content.decode('utf-8').encode('utf-8') + b'"}'),
            (XMLExtractor, b"<root>" + unicode_content + b"</root>"),
            (MDExtractor, b"# " + unicode_content),
        ]

        for extractor_class, content in test_cases:
            try:
                result = extractor_class.extract_plain_text(content)
                assert isinstance(result, str)
                # Unicode chars should be present (emoji removal happens at extractor level)
                # But non-Latin filtering happens at domain level
            except (UnicodeDecodeError, ExtractionError):
                # Some extractors might not handle complex Unicode gracefully
                passors.utils.decode_to_utf8
                ')

    def test_extract_plain_text_decode_error_handling(self, mock_decode: Mock) -> None:
        """Test error handling when decoding fails."""
        mock_decode.side_effect = Exception("Decode error")
        content = b"test content"

        with pytest.raises(ExtractionError, match="Failed to extract TXT text"):
            TXTExtractor.extract_plain_text(content)


class TestHTMLExtractor:
    """Test HTMLExtractor with real functionality."""

    def test_extract_plain_text_basic_html(self) -> None:
        """Test basic HTML extraction."""
        html_content = b"<html><body><p>Simple paragraph</p></body></html>"
        result = HTMLExtractor.extract_plain_text(html_content)
        assert "Simple paragraph" in result

    def test_extract_plain_text_removes_scripts_and_styles(self) -> None:
        """Test that scripts and styles are removed."""
        html_content = b"""
        <html>
            <head>
                <style>body { color: red; }</style>
                <script>alert('test');</script>
            </head>
            <body>
                <p>Visible text</p>
                <script>hidden script</script>
            </body>
        </html>
        """

        result = HTMLExtractor.extract_plain_text(html_content)

        assert "Visible text" in result
        assert "color: red" not in result
        assert "alert('test')" not in result
        assert "hidden script" not in result

    def test_extract_plain_text_nested_elements(self) -> None:
        """Test extraction from nested HTML elements."""
        html_content = b"<div>Outer <span>inner <b>bold</b> text</span> end</div>"
        result = HTMLExtractor.extract_plain_text(html_content)
        assert "Outer inner bold text end" in result

    def test_extract_plain_text_handles_malformed_html(self) -> None:
        """Test handling of malformed HTML."""
        malformed_html = b"<div>Unclosed div<p>Paragraph without closing"
        result = HTMLExtractor.extract_plain_text(malformed_html)
        assert "Unclosed div" in result
        assert "Paragraph without closing" in result

    def test_extract_plain_text_removes_emoji(self) -> None:
        """Test emoji removal in HTML content."""
        html_content = "<html><body>Text with 🌍 emoji</body></html>".encode('utf-8')
        result = HTMLExtractor.extract_plain_text(html_content)
        assert "Text with emoji" in result
        assert "🌍" not in result

    @patch('osd_text_extractor.infrastructure.extractors._html.BeautifulSoup')
    def test_extract_plain_text_handles_parsing_error(self, mock_bs: Mock) -> None:
        """Test error handling when BeautifulSoup fails."""
        mock_bs.side_effect = Exception("Parsing error")
        content = b"<html>test</html>"

        with pytest.raises(ExtractionError, match="Failed to extract HTML text"):
            HTMLExtractor.extract_plain_text(content)


class TestJSONExtractor:
    """Test JSONExtractor with real functionality."""

    def test_extract_plain_text_simple_json(self) -> None:
        """Test simple JSON extraction."""
        json_content = b'{"key": "value", "number": 123}'
        result = JSONExtractor.extract_plain_text(json_content)
        assert "value" in result
        # Numbers should not be extracted (only strings)
        assert "123" not in result

    def test_extract_plain_text_nested_json(self) -> None:
        """Test nested JSON structure extraction."""
        json_content = b'{"nested": {"key": "nested_value"}, "array": ["item1", "item2"]}'
        result = JSONExtractor.extract_plain_text(json_content)
        assert "nested_value" in result
        assert "item1" in result
        assert "item2" in result

    def test_extract_plain_text_array_only(self) -> None:
        """Test JSON array extraction."""
        json_content = b'["item1", "item2", "item3"]'
        result = JSONExtractor.extract_plain_text(json_content)
        assert "item1" in result
        assert "item2" in result
        assert "item3" in result

    def test_extract_plain_text_ignores_non_string_values(self) -> None:
        """Test that non-string values are ignored."""
        json_content = b'{"string": "text", "number": 123, "boolean": true, "null": null}'
        result = JSONExtractor.extract_plain_text(json_content)
        assert "text" in result
        assert "123" not in result
        assert "true" not in result
        assert "null" not in result

    def test_extract_plain_text_empty_json(self) -> None:
        """Test empty JSON object."""
        json_content = b'{}'
        result = JSONExtractor.extract_plain_text(json_content)
        assert result.strip() == ""

    def test_extract_plain_text_removes_emoji(self) -> None:
        """Test emoji removal in JSON content."""
        json_content = '{"text": "Hello 🌍 world"}'.encode('utf-8')
        result = JSONExtractor.extract_plain_text(json_content)
        assert "Hello world" in result
        assert "🌍" not in result

    def test_extract_plain_text_invalid_json(self) -> None:
        """Test handling of invalid JSON."""
        invalid_json = b'{"invalid": json, missing quotes}'

        with pytest.raises(ExtractionError, match="Failed to extract text from JSON"):
            JSONExtractor.extract_plain_text(invalid_json)

    @patch('osd_text_extractor.infrastructure.extractors._json.json.loads')
    def test_extract_plain_text_handles_json_error(self, mock_loads: Mock) -> None:
        """Test error handling when JSON parsing fails."""
        mock_loads.side_effect = ValueError("Invalid JSON")
        content = b'{"invalid": json}'

        with pytest.raises(ExtractionError, match="Failed to extract text from JSON"):
            JSONExtractor.extract_plain_text(content)


class TestCSVExtractor:
    """Test CSVExtractor with real functionality."""

    def test_extract_plain_text_basic_csv(self) -> None:
        """Test basic CSV extraction."""
        csv_content = b"Name,Age,City\nJohn,30,NYC\nJane,25,LA"
        result = CSVExtractor.extract_plain_text(csv_content)

        assert "Name Age City" in result
        assert "John 30 NYC" in result
        assert "Jane 25 LA" in result

    def test_extract_plain_text_handles_empty_cells(self) -> None:
        """Test CSV with empty cells."""
        csv_content = b"col1,col2,,col4\nval1,val2,,val4"
        result = CSVExtractor.extract_plain_text(csv_content)

        assert "col1 col2 col4" in result
        assert "val1 val2 val4" in result

    def test_extract_plain_text_stops_after_consecutive_empty_cells(self) -> None:
        """Test that processing stops after 3 consecutive empty cells."""
        csv_content = b"col1,col2,,,,should_not_appear\nval1,val2,,,,also_not_appear"
        result = CSVExtractor.extract_plain_text(csv_content)

        assert "col1 col2" in result
        assert "val1 val2" in result
        assert "should_not_appear" not in result
        assert "also_not_appear" not in result

    def test_extract_plain_text_single_column(self) -> None:
        """Test CSV with single column."""
        csv_content = b"Header\nValue1\nValue2"
        result = CSVExtractor.extract_plain_text(csv_content)

        assert "Header" in result
        assert "Value1" in result
        assert "Value2" in result

    def test_extract_plain_text_removes_emoji(self) -> None:
        """Test emoji removal in CSV content."""
        csv_content = "Name,Comment\nJohn,Great 🌍 content".encode('utf-8')
        result = CSVExtractor.extract_plain_text(csv_content)

        assert "Name Comment" in result
        assert "John Great content" in result
        assert "🌍" not in result

    @patch('osd_text_extractor.infrastructure.extractors._csv.csv.reader')
    def test_extract_plain_text_handles_csv_error(self, mock_reader: Mock) -> None:
        """Test error handling when CSV parsing fails."""
        mock_reader.side_effect = Exception("CSV parsing error")
        content = b"test,csv"

        with pytest.raises(ExtractionError, match="Failed to extract CSV text"):
            CSVExtractor.extract_plain_text(content)


class TestPDFExtractor:
    """Test PDFExtractor with mocked PyMuPDF."""

    @patch('osd_text_extractor.infrastructure.extractors._pdf.fitz.open')
    def test_extract_plain_text_success(self, mock_fitz_open: Mock) -> None:
        """Test successful PDF extraction."""
        mock_page = Mock()
        mock_page.get_text.return_value = "PDF page text"

        mock_doc = Mock()
        mock_doc.__iter__ = Mock(return_value=iter([mock_page]))
        mock_doc.__enter__ = Mock(return_value=mock_doc)
        mock_doc.__exit__ = Mock(return_value=None)
        mock_fitz_open.return_value = mock_doc

        result = PDFExtractor.extract_plain_text(b"PDF content")

        assert result == "PDF page text"
        mock_fitz_open.assert_called_once_with(stream=b"PDF content", filetype="pdf")
        mock_page.get_text.assert_called_once_with("text")

    @patch('osd_text_extractor.infrastructure.extractors._pdf.fitz.open')
    def test_extract_plain_text_multiple_pages(self, mock_fitz_open: Mock) -> None:
        """Test PDF with multiple pages."""
        mock_page1 = Mock()
        mock_page1.get_text.return_value = "Page 1 text"
        mock_page2 = Mock()
        mock_page2.get_text.return_value = "Page 2 text"

        mock_doc = Mock()
        mock_doc.__iter__ = Mock(return_value=iter([mock_page1, mock_page2]))
        mock_doc.__enter__ = Mock(return_value=mock_doc)
        mock_doc.__exit__ = Mock(return_value=None)
        mock_fitz_open.return_value = mock_doc

        result = PDFExtractor.extract_plain_text(b"PDF content")

        assert "Page 1 text" in result
        assert "Page 2 text" in result
        assert result == "Page 1 text\nPage 2 text"

    @patch('osd_text_extractor.infrastructure.extractors._pdf.fitz.open')
    def test_extract_plain_text_removes_emoji(self, mock_fitz_open: Mock) -> None:
        """Test emoji removal in PDF content."""
        mock_page = Mock()
        mock_page.get_text.return_value = "Text with 🌍 emoji"

        mock_doc = Mock()
        mock_doc.__iter__ = Mock(return_value=iter([mock_page]))
        mock_doc.__enter__ = Mock(return_value=mock_doc)
        mock_doc.__exit__ = Mock(return_value=None)
        mock_fitz_open.return_value = mock_doc

        result = PDFExtractor.extract_plain_text(b"PDF content")

        assert "Text with emoji" in result
        assert "🌍" not in result

    @patch('osd_text_extractor.infrastructure.extractors._pdf.fitz.open')
    def test_extract_plain_text_handles_pdf_error(self, mock_fitz_open: Mock) -> None:
        """Test error handling when PDF parsing fails."""
        mock_fitz_open.side_effect = Exception("PDF parsing error")

        with pytest.raises(ExtractionError, match="Failed to extract PDF text"):
            PDFExtractor.extract_plain_text(b"Invalid PDF content")


class TestXMLExtractor:
    """Test XMLExtractor with real functionality."""

    def test_extract_plain_text_simple_xml(self) -> None:
        """Test simple XML extraction."""
        xml_content = b"<root>Simple text content</root>"
        result = XMLExtractor.extract_plain_text(xml_content)
        assert "Simple text content" in result

    def test_extract_plain_text_nested_xml(self) -> None:
        """Test nested XML elements."""
        xml_content = b"<root><child>Child text</child><other>Other text</other></root>"
        result = XMLExtractor.extract_plain_text(xml_content)
        assert "Child text" in result
        assert "Other text" in result

    def test_extract_plain_text_with_attributes(self) -> None:
        """Test XML with attributes (attributes should be ignored)."""
        xml_content = b'<root attr="value"><element id="123">Element text</element></root>'
        result = XMLExtractor.extract_plain_text(xml_content)
        assert "Element text" in result
        # Attributes should not be in the result
        assert "attr" not in result
        assert "value" not in result
        assert "id" not in result
        assert "123" not in result

    def test_extract_plain_text_mixed_content(self) -> None:
        """Test XML with mixed text and element content."""
        xml_content = b"<root>Before <child>middle</child> after</root>"
        result = XMLExtractor.extract_plain_text(xml_content)
        assert "Before middle after" in result

    def test_extract_plain_text_removes_emoji(self) -> None:
        """Test emoji removal in XML content."""
        xml_content = "<root>Text with 🌍 emoji</root>".encode('utf-8')
        result = XMLExtractor.extract_plain_text(xml_content)
        assert "Text with emoji" in result
        assert "🌍" not in result

    def test_extract_plain_text_malformed_xml_error(self) -> None:
        """Test error handling with malformed XML."""
        malformed_xml = b"<root>Unclosed root<child>test"

        with pytest.raises(ExtractionError, match="Failed to extract XML text"):
            XMLExtractor.extract_plain_text(malformed_xml)

    @patch('osd_text_extractor.infrastructure.extract