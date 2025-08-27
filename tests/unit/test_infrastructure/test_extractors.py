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
    @pytest.mark.parametrize("input_content,expected_output", [
        (b"Simple text", "Simple text"),
        (b"Text\nwith\nnewlines", "Text\nwith\nnewlines"),
        (b"Text\n\nwith\n\ndouble\nnewlines", "Text\nwith\ndouble\nnewlines"),
        (b"Text\twith\ttabs", "Text with tabs"),
        (b"Text\rwith\rreturns", "Text with returns"),
        (b"Text  with  double  spaces", "Text with double spaces"),
        (b"   Text with leading/trailing spaces   ", "   Text with leading/trailing spaces   "),
    ])
    def test_extract_plain_text_success(
            self, input_content: bytes, expected_output: str
    ) -> None:
        result = TXTExtractor.extract_plain_text(input_content)
        assert result == expected_output

    @pytest.mark.parametrize("encoding_content", [
        ("Тестовый текст", "utf-8"),
        ("Тестовый текст", "utf-16"),
        ("Test text", "iso-8859-1"),
    ])
    def test_extract_plain_text_different_encodings(
            self, encoding_content: tuple[str, str]
    ) -> None:
        text, encoding = encoding_content
        content = text.encode(encoding)
        result = TXTExtractor.extract_plain_text(content)
        assert text in result

    @patch('osd_text_extractor.infrastructure.extractors.utils.decode_to_utf8')
    def test_extract_plain_text_decode_error_handling(self, mock_decode: Mock) -> None:
        mock_decode.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "test error")
        content = b"test content"
        with pytest.raises(ExtractionError, match="Failed to extract TXT text"):
            TXTExtractor.extract_plain_text(content)


class TestHTMLExtractor:
    @pytest.mark.parametrize("html_content,expected_text", [
        (b"<html><body>Simple text</body></html>", "Simple text"),
        (b"<p>Paragraph text</p>", "Paragraph text"),
        (b"<div>Text with <span>nested</span> elements</div>", "Text with nested elements"),
        (b"<h1>Title</h1><p>Content</p>", "Title\n\nContent"),
    ])
    def test_extract_plain_text_success(
            self, html_content: bytes, expected_text: str
    ) -> None:
        result = HTMLExtractor.extract_plain_text(html_content)
        assert expected_text in result

    def test_extract_plain_text_removes_scripts_and_styles(self) -> None:
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

    def test_extract_plain_text_handles_malformed_html(self) -> None:
        malformed_html = b"<div>Unclosed div<p>Paragraph without closing"
        result = HTMLExtractor.extract_plain_text(malformed_html)
        assert "Unclosed div" in result
        assert "Paragraph without closing" in result

    @patch('osd_text_extractor.infrastructure.extractors._html.BeautifulSoup')
    def test_extract_plain_text_handles_parsing_error(self, mock_bs: Mock) -> None:
        mock_bs.side_effect = Exception("Parsing error")
        content = b"<html>test</html>"
        with pytest.raises(ExtractionError, match="Failed to extract HTML text"):
            HTMLExtractor.extract_plain_text(content)


class TestJSONExtractor:
    @pytest.mark.parametrize("json_content,expected_values", [
        (b'{"key": "value"}', ["value"]),
        (b'{"nested": {"key": "nested_value"}}', ["nested_value"]),
        (b'["item1", "item2", "item3"]', ["item1", "item2", "item3"]),
        (b'{"array": ["val1", "val2"]}', ["val1", "val2"]),
        (b'{"mixed": {"str": "text", "arr": ["a", "b"]}}', ["text", "a", "b"]),
    ])
    def test_extract_plain_text_success(
            self, json_content: bytes, expected_values: list[str]
    ) -> None:
        result = JSONExtractor.extract_plain_text(json_content)
        for expected_value in expected_values:
            assert expected_value in result

    def test_extract_plain_text_ignores_non_string_values(self) -> None:
        json_content = b'{"string": "text", "number": 123, "boolean": true, "null": null}'
        result = JSONExtractor.extract_plain_text(json_content)
        assert "text" in result
        assert "123" not in result
        assert "true" not in result
        assert "null" not in result

    def test_extract_plain_text_handles_empty_json(self) -> None:
        json_content = b'{}'
        result = JSONExtractor.extract_plain_text(json_content)
        assert result.strip() == ""

    @patch('osd_text_extractor.infrastructure.extractors._json.json.loads')
    def test_extract_plain_text_handles_json_error(self, mock_loads: Mock) -> None:
        mock_loads.side_effect = ValueError("Invalid JSON")
        content = b'{"invalid": json}'
        with pytest.raises(ExtractionError, match="Failed to extract text from JSON"):
            JSONExtractor.extract_plain_text(content)


class TestCSVExtractor:
    @pytest.mark.parametrize("csv_content,expected_lines", [
        (b"col1,col2,col3\nval1,val2,val3", ["col1 col2 col3", "val1 val2 val3"]),
        (b"header\nvalue", ["header", "value"]),
        (b"a,b,c\n1,2,3\nx,y,z", ["a b c", "1 2 3", "x y z"]),
    ])
    def test_extract_plain_text_success(
            self, csv_content: bytes, expected_lines: list[str]
    ) -> None:
        result = CSVExtractor.extract_plain_text(csv_content)
        for expected_line in expected_lines:
            assert expected_line in result

    def test_extract_plain_text_handles_empty_cells(self) -> None:
        csv_content = b"col1,,col3\nval1,,val3"
        result = CSVExtractor.extract_plain_text(csv_content)
        assert "col1 col3" in result
        assert "val1 val3" in result

    def test_extract_plain_text_stops_after_consecutive_empty_cells(self) -> None:
        csv_content = b"col1,col2,,,,should_not_appear\nval1,val2,,,,also_not_appear"
        result = CSVExtractor.extract_plain_text(csv_content)
        assert "col1 col2" in result
        assert "val1 val2" in result
        assert "should_not_appear" not in result
        assert "also_not_appear" not in result

    @patch('osd_text_extractor.infrastructure.extractors._csv.csv.reader')
    def test_extract_plain_text_handles_csv_error(self, mock_reader: Mock) -> None:
        mock_reader.side_effect = Exception("CSV parsing error")
        content = b"test,csv"
        with pytest.raises(ExtractionError, match="Failed to extract CSV text"):
            CSVExtractor.extract_plain_text(content)


class TestPDFExtractor:
    @patch('osd_text_extractor.infrastructure.extractors._pdf.fitz.open')
    def test_extract_plain_text_success(self, mock_fitz_open: Mock) -> None:
        mock_page = Mock()
        mock_page.get_text.return_value = "PDF page text"
        mock_doc = Mock()
        mock_doc.__iter__ = Mock(return_value=iter([mock_page]))
        mock_doc.__enter__ = Mock(return_value=mock_doc)
        mock_doc.__exit__ = Mock(return_value=None)
        mock_fitz_open.return_value = mock_doc
        result = PDFExtractor.extract_plain_text(b"PDF content")
        assert result == "PDF page text"
        mock_fitz_open.assert_called_once()
        mock_page.get_text.assert_called_once_with("text")

    @patch('osd_text_extractor.infrastructure.extractors._pdf.fitz.open')
    def test_extract_plain_text_multiple_pages(self, mock_fitz_open: Mock) -> None:
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
    def test_extract_plain_text_handles_pdf_error(self, mock_fitz_open: Mock) -> None:
        mock_fitz_open.side_effect = Exception("PDF parsing error")
        with pytest.raises(ExtractionError, match="Failed to extract PDF text"):
            PDFExtractor.extract_plain_text(b"Invalid PDF content")


class TestXMLExtractor:
    @pytest.mark.parametrize("xml_content,expected_text", [
        (b"<root>Simple text</root>", "Simple text"),
        (b"<root><child>Child text</child></root>", "Child text"),
        (b"<root>Text <child>with</child> nested</root>", "Text with nested"),
    ])
    def test_extract_plain_text_success(
            self, xml_content: bytes, expected_text: str
    ) -> None:
        result = XMLExtractor.extract_plain_text(xml_content)
        assert expected_text in result

    def test_extract_plain_text_handles_malformed_xml(self) -> None:
        malformed_xml = b"<root>Unclosed root<child>test"
        with pytest.raises(ExtractionError, match="Failed to extract XML text"):
            XMLExtractor.extract_plain_text(malformed_xml)

    @patch('osd_text_extractor.infrastructure.extractors._xml.et.fromstring')
    def test_extract_plain_text_handles_parsing_error(self, mock_fromstring: Mock) -> None:
        mock_fromstring.side_effect = Exception("XML parsing error")
        content = b"<root>test</root>"
        with pytest.raises(ExtractionError, match="Failed to extract XML text"):
            XMLExtractor.extract_plain_text(content)


class TestMDExtractor:
    @pytest.mark.parametrize("md_content,expected_clean", [
        (b"# Header\nParagraph text", "Paragraph text"),
        (b"**Bold text**", "Bold text"),
        (b"*Italic text*", "Italic text"),
        (b"[Link text](http://example.com)", "Link text"),
        (b"![Alt text](image.jpg)", "Alt text"),
        (b"```python\ncode block\n```\nNormal text", "Normal text"),
        (b"`inline code`\nNormal text", "Normal text"),
    ])
    def test_extract_plain_text_removes_markdown(
            self, md_content: bytes, expected_clean: str
    ) -> None:
        result = MDExtractor.extract_plain_text(md_content)
        assert expected_clean in result
        assert "#" not in result or "# " not in result
        assert "**" not in result
        assert "__" not in result
        assert "```" not in result

    def test_extract_plain_text_handles_lists(self) -> None:
        md_content = b"- Item 1\n- Item 2\n1. Numbered item"
        result = MDExtractor.extract_plain_text(md_content)
        assert "Item 1" in result
        assert "Item 2" in result
        assert "Numbered item" in result
        assert "- " not in result
        assert "1. " not in result

    @patch('osd_text_extractor.infrastructure.extractors.utils.decode_to_utf8')
    def test_extract_plain_text_handles_decode_error(self, mock_decode: Mock) -> None:
        mock_decode.side_effect = Exception("Decode error")
        content = b"# Test markdown"
        with pytest.raises(ExtractionError, match="Failed to extract MD text"):
            MDExtractor.extract_plain_text(content)


class TestDOCXExtractor:
    @patch('osd_text_extractor.infrastructure.extractors._docx.Document')
    def test_extract_plain_text_success(self, mock_document_class: Mock) -> None:

        mock_paragraph = Mock()
        mock_paragraph.text = "Paragraph text"

        mock_doc = Mock()
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = []

        mock_document_class.return_value = mock_doc
        result = DOCXExtractor.extract_plain_text(b"DOCX content")
        assert "Paragraph text" in result
        mock_document_class.assert_called_once()

    @patch('osd_text_extractor.infrastructure.extractors._docx.Document')
    def test_extract_plain_text_with_tables(self, mock_document_class: Mock) -> None:
        mock_cell = Mock()
        mock_cell.text = "Cell text"
        mock_row = Mock()
        mock_row.cells = [mock_cell]
        mock_table = Mock()
        mock_table.rows = [mock_row]

        mock_doc = Mock()
        mock_doc.paragraphs = []
        mock_doc.tables = [mock_table]

        mock_document_class.return_value = mock_doc
        result = DOCXExtractor.extract_plain_text(b"DOCX content")
        assert "Cell text" in result

    @patch('osd_text_extractor.infrastructure.extractors._docx.Document')
    def test_extract_plain_text_handles_docx_error(self, mock_document_class: Mock) -> None:
        mock_document_class.side_effect = Exception("DOCX parsing error")
        with pytest.raises(ExtractionError, match="Failed to extract DOCX text"):
            DOCXExtractor.extract_plain_text(b"Invalid DOCX content")