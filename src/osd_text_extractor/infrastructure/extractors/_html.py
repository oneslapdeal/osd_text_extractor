import re
import emoji
from bs4 import BeautifulSoup

from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.exceptions import ExtractionError


class HTMLExtractor(TextExtractor):
    @staticmethod
    def extract_plain_text(file_content: bytes) -> str:
        try:
            html_content = file_content.decode("utf-8")
            soup = BeautifulSoup(html_content, "lxml")
            for element in soup(["script", "style", "meta", "link", "noscript", "svg"]):
                element.decompose()
            text = soup.get_text("\n", strip=True)
            text = re.sub(r"(\n\s*){2,}", "\n\n", text)
            text = re.sub(r"[ \t]{2,}", " ", text)
            text = emoji.replace_emoji(text.strip(), replace='')
            return text
        except Exception as e:
            raise ExtractionError("Failed to extract HTML text") from e
