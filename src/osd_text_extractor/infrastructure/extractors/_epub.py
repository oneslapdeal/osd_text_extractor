import emoji
import fitz
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.exceptions import ExtractionError


class EPUBExtractor(TextExtractor):
    @staticmethod
    def extract_plain_text(file_content: bytes) -> str:
        try:
            full_text = []
            with fitz.open(stream=file_content, filetype="epub") as doc:
                for page in doc:
                    text = page.get_text("text")
                    full_text.append(text)
            text = "\n".join(full_text)
            return emoji.replace_emoji(text, replace=" ")
        except Exception as e:
            raise ExtractionError("Failed to extract EPUB text") from e
