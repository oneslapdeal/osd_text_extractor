import xml.etree.ElementTree as ET
from io import BytesIO

from odf.opendocument import load

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
            with BytesIO(file_content) as buffer:
                xml_text = decode_to_utf8(load(buffer).xml())
                root = ET.fromstring(xml_text)
                return xml_node_to_plain_text(root).replace("\n\n", "\n")
        except Exception as e:
            raise ExtractionError("Failed to extract ODT text") from e
