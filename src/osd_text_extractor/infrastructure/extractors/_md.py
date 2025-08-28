import re

import emoji
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.exceptions import ExtractionError
from osd_text_extractor.infrastructure.extractors.utils import decode_to_utf8


class MDExtractor(TextExtractor):
    @staticmethod
    def extract_plain_text(file_content: bytes) -> str:
        try:
            text = decode_to_utf8(file_content)
            # Remove code blocks (both triple backticks and single backticks)
            text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
            text = re.sub(r"`[^`]+`", "", text)
            # Remove headers (1-6 # symbols, followed by optional whitespace and text)
            text = re.sub(r"^[ \t]*#{1,6}[ \t]*.*?$", "", text, flags=re.MULTILINE)
            # Remove bold and italic markers
            text = re.sub(r"\*\*?(.*?)\*\*?", r"\1", text)
            text = re.sub(r"__(.*?)__", r"\1", text)
            # Remove links and images, keeping only the link/image text
            text = re.sub(r"\[([^\]]*)\]\([^\)]*\)", r"\1", text)
            text = re.sub(r"!\[([^\]]*)\]\([^\)]*\)", r"\1", text)
            # Remove list markers (bullets and numbered lists)
            text = re.sub(r"^[ \t]*[-*+][ \t]+", "", text, flags=re.MULTILINE)
            text = re.sub(r"^[ \t]*\d+\.[ \t]+", "", text, flags=re.MULTILINE)
            # Remove blockquotes
            text = re.sub(r"^[ \t]*>[ \t]*", "", text, flags=re.MULTILINE)
            # Remove horizontal rules
            text = re.sub(r"^[ \t]*-{3,}[ \t]*$", "", text, flags=re.MULTILINE)
            text = re.sub(r"^[ \t]*\*{3,}[ \t]*$", "", text, flags=re.MULTILINE)
            # Normalize whitespace: multiple spaces to single space
            text = re.sub(r"[ \t]+", " ", text)
            # Normalize newlines: multiple newlines to single newline
            text = re.sub(r"\n\s*\n", "\n", text)
            # Remove emojis
            text = emoji.replace_emoji(text.strip(), replace=" ")
            return text.strip()
        except Exception as e:
            raise ExtractionError("Failed to extract MD text") from e
