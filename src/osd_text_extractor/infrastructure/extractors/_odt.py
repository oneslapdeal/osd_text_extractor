import xml.etree.ElementTree as et
from io import BytesIO
import emoji
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
                root = et.fromstring(xml_text)
                text = xml_node_to_plain_text(root)
                text = emoji.replace_emoji(text, replace='')
                return text
        except Exception as e:
            raise ExtractionError("Failed to extract ODT text") from e
