import xml.etree.ElementTree as et
from io import BytesIO
import emoji
from odf.opendocument import load
from xml.etree.ElementTree import ParseError

from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.exceptions import ExtractionError
from osd_text_extractor.infrastructure.extractors.utils import (
    decode_to_utf8,
    xml_node_to_plain_text,
)


class ODTExtractor(TextExtractor):
    @staticmethod
    def extract_plain_text(file_content: bytes) -> str:
        try:
            if len(file_content) > 50 * 1024 * 1024:
                raise ExtractionError("ODT file too large for processing")

            with BytesIO(file_content) as buffer:
                doc = load(buffer)
                xml_text = decode_to_utf8(doc.xml())

                if len(xml_text) > 100 * 1024 * 1024:
                    raise ExtractionError("ODT content too large after decompression")

                root = et.fromstring(xml_text)

                max_depth = 100
                if _get_max_depth(root) > max_depth:
                    raise ExtractionError("ODT structure too deeply nested")

                text = xml_node_to_plain_text(root)
                text = emoji.replace_emoji(text, replace='')
                return text
        except ParseError as e:
            raise ExtractionError(f"Invalid ODT XML format: {str(e)}") from e
        except Exception as e:
            raise ExtractionError("Failed to extract ODT text") from e


def _get_max_depth(element, current_depth=0):
    if not element:
        return current_depth

    max_child_depth = current_depth
    for child in element:
        child_depth = _get_max_depth(child, current_depth + 1)
        max_child_depth = max(max_child_depth, child_depth)

    return max_child_depth