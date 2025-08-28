import emoji
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.exceptions import ExtractionError
from osd_text_extractor.infrastructure.extractors.utils import decode_to_utf8


class TXTExtractor(TextExtractor):
    @staticmethod
    def extract_plain_text(file_content: bytes) -> str:
        try:
            text = decode_to_utf8(file_content)
            return emoji.replace_emoji(text, replace=" ")
        except Exception as e:
            raise ExtractionError("Failed to extract TXT text") from e
