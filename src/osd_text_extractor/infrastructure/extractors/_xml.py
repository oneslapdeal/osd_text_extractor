import xml.etree.ElementTree as et

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
            root = et.fromstring(xml_text)
            return xml_node_to_plain_text(root)
        except Exception as e:
            raise ExtractionError("Failed to extract XML text") from e
