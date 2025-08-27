import re

from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.exceptions import ExtractionError
from osd_text_extractor.infrastructure.extractors.utils import decode_to_utf8


class MDExtractor(TextExtractor):
    @staticmethod
    def extract_plain_text(file_content: bytes) -> str:
        try:
            text = decode_to_utf8(file_content)
            text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
            text = re.sub(r"`[^`]+`", "", text)
            text = re.sub(r"^#{1,6}\s*.*$", "", text, flags=re.MULTILINE)
            text = re.sub(r"\*\*?(.*?)\*\*?", r"\1", text)
            text = re.sub(r"__(.*?)__", r"\1", text)
            text = re.sub(r"\[([^\]]*)\]\([^\)]*\)", r"\1", text)
            text = re.sub(r"!\[([^\]]*)\]\([^\)]*\)", r"\1", text)
            text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
            text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
            text = re.sub(r"^\s*>\s*", "", text, flags=re.MULTILINE)
            text = re.sub(r"^-{3,}\s*$", "", text, flags=re.MULTILINE)
            text = re.sub(r"^\*{3,}\s*$", "", text, flags=re.MULTILINE)
            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"\n\s*\n", "\n", text)
            return text.strip()
        except Exception as e:
            raise ExtractionError("Failed to extract MD text") from e
