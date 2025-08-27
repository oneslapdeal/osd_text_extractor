import xml.etree.ElementTree as et
import emoji
from xml.etree.ElementTree import ParseError
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.exceptions import ExtractionError
from osd_text_extractor.infrastructure.extractors.utils import (
    decode_to_utf8,
    xml_node_to_plain_text,
)


class XMLExtractor(TextExtractor):
    @staticmethod
    def extract_plain_text(file_content: bytes) -> str:
        try:
            xml_text = decode_to_utf8(file_content)

            if len(xml_text) > 10 * 1024 * 1024:
                raise ExtractionError("XML file too large for processing")

            root = et.fromstring(xml_text)

            max_depth = 50
            if _get_max_depth(root) > max_depth:
                raise ExtractionError("XML structure too deeply nested")

            text = xml_node_to_plain_text(root)
            text = emoji.replace_emoji(text, replace='')
            return text
        except ParseError as e:
            raise ExtractionError(f"Invalid XML format: {str(e)}") from e
        except Exception as e:
            raise ExtractionError("Failed to extract XML text") from e


def _get_max_depth(element, current_depth=0):
    if not element:
        return current_depth

    max_child_depth = current_depth
    for child in element:
        child_depth = _get_max_depth(child, current_depth + 1)
        max_child_depth = max(max_child_depth, child_depth)

    return max_child_depth