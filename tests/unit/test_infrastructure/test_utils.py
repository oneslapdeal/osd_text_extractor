import xml.etree.ElementTree as ET
import pytest
from osd_text_extractor.infrastructure.extractors.utils import (
    decode_to_utf8,
    xml_node_to_plain_text,
)


class TestDecodeToUTF8:
    @pytest.mark.parametrize("text,encoding", [
        ("Simple text", "utf-8"),
        ("Русский текст", "utf-8"),
        ("English text", "ascii"),
        ("Тест", "utf-16"),
        ("Test", "iso-8859-1"),
        ("Тестовый текст", "windows-1251"),
    ])
    def test_decode_success(self, text: str, encoding: str) -> None:
        try:
            content = text.encode(encoding)
        except UnicodeEncodeError:
            pytest.skip(f"Cannot encode '{text}' with {encoding}")
        result = decode_to_utf8(content)

        assert isinstance(result, str)
        if encoding in ("utf-8", "ascii"):
            assert result == text

    def test_decode_invalid_bytes_with_fallback(self) -> None:
        invalid_content = b"\xff\xfe\invalid_bytes\x00"
        result = decode_to_utf8(invalid_content)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_decode_empty_content(self) -> None:
        content = b""
        result = decode_to_utf8(content)
        assert result == ""

    def test_decode_tries_multiple_encodings(self) -> None:
        content = "Тест".encode("windows-1251")
        result = decode_to_utf8(content)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_decode_utf8_bom(self) -> None:
        text = "Test with BOM"
        content = b"\xef\xbb\xbf" + text.encode("utf-8")
        result = decode_to_utf8(content)
        assert "Test with BOM" in result

    def test_decode_mixed_bytes(self) -> None:
        content = b"ASCII text \x80\x81\x82 more text"
        result = decode_to_utf8(content)
        assert isinstance(result, str)
        assert "ASCII text" in result
        assert "more text" in result


class TestXMLNodeToPlainText:
    def test_simple_text_node(self) -> None:
        xml = "<root>Simple text</root>"
        root = ET.fromstring(xml)
        result = xml_node_to_plain_text(root)
        assert result == "Simple text"

    def test_nested_nodes(self) -> None:
        xml = "<root>Parent <child>child text</child> after</root>"
        root = ET.fromstring(xml)
        result = xml_node_to_plain_text(root)
        assert "Parent" in result
        assert "child text" in result
        assert "after" in result

    def test_multiple_children(self) -> None:
        xml = """
        <root>
            <child1>First child</child1>
            <child2>Second child</child2>
            <child3>Third child</child3>
        </root>
        """
        root = ET.fromstring(xml)
        result = xml_node_to_plain_text(root)
        assert "First child" in result
        assert "Second child" in result
        assert "Third child" in result

    def test_empty_node(self) -> None:
        xml = "<root></root>"
        root = ET.fromstring(xml)
        result = xml_node_to_plain_text(root)
        assert result == ""

    def test_node_with_only_whitespace(self) -> None:
        xml = "<root>   </root>"
        root = ET.fromstring(xml)
        result = xml_node_to_plain_text(root)
        assert result == ""

    def test_deeply_nested_nodes(self) -> None:
        xml = """
        <root>
            <level1>
                <level2>
                    <level3>Deep text</level3>
                </level2>
            </level1>
        </root>
        """
        root = ET.fromstring(xml)
        result = xml_node_to_plain_text(root)
        assert "Deep text" in result

    def test_mixed_content(self) -> None:
        xml = "<root>Before <em>emphasized</em> middle <strong>strong</strong> after</root>"
        root = ET.fromstring(xml)
        result = xml_node_to_plain_text(root)
        assert "Before" in result
        assert "emphasized" in result
        assert "middle" in result
        assert "strong" in result
        assert "after" in result

    def test_node_with_attributes(self) -> None:
        xml = '<root><element attr="value">Text content</element></root>'
        root = ET.fromstring(xml)
        result = xml_node_to_plain_text(root)
        assert "Text content" in result
        assert "attr" not in result
        assert "value" not in result

    def test_self_closing_tags(self) -> None:
        xml = "<root>Before <br/> after</root>"
        root = ET.fromstring(xml)
        result = xml_node_to_plain_text(root)
        assert "Before" in result
        assert "after" in result

    def test_cdata_sections(self) -> None:
        xml = "<root><![CDATA[CDATA content]]></root>"
        root = ET.fromstring(xml)
        result = xml_node_to_plain_text(root)
        assert "CDATA content" in result

    def test_unicode_content(self) -> None:
        xml = "<root>Unicode: 你好 🌍 Русский</root>"
        root = ET.fromstring(xml)
        result = xml_node_to_plain_text(root)
        assert "Unicode:" in result
        assert "你好" in result
        assert "🌍" in result
        assert "Русский" in result

    def test_performance_large_xml(self) -> None:
        xml_parts = ["<root>"]
        for i in range(100):
            xml_parts.append(f"<item{i}>Content {i}</item{i}>")
        xml_parts.append("</root>")
        xml = "".join(xml_parts)
        root = ET.fromstring(xml)
        result = xml_node_to_plain_text(root)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Content 0" in result
        assert "Content 99" in result