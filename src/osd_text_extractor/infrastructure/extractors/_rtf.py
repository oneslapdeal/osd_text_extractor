import emoji
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.exceptions import ExtractionError
from osd_text_extractor.infrastructure.extractors.utils import decode_to_utf8
from striprtf.striprtf import rtf_to_text


class RTFExtractor(TextExtractor):
    @staticmethod
    def extract_plain_text(file_content: bytes) -> str:
        try:
            rtf_content = decode_to_utf8(file_content)
            clean_text = rtf_to_text(rtf_content)
            clean_text = _clean_text(clean_text)
            text = clean_text.strip()
            return emoji.replace_emoji(text, replace=" ")
        except Exception as e:
            raise ExtractionError("Failed to extract RTF text") from e


def _clean_text(text: str) -> str:
    text = " ".join(text.split())
    text = text.replace("\x00", "").replace("\uffff", "")
    return text.strip()
