import fitz
import emoji
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.exceptions import ExtractionError


class FB2Extractor(TextExtractor):
    @staticmethod
    def extract_plain_text(file_content: bytes) -> str:
        try:
            extracted_pages = []
            with fitz.open(stream=file_content, filetype="fb2") as doc:
                for page in doc:
                    text = page.get_text("text")
                    extracted_pages.append(text)
            text = "\n".join(extracted_pages)
            text = emoji.replace_emoji(text, replace='')
            return text
        except Exception as e:
            raise ExtractionError("Failed to extract FB2 text") from e
