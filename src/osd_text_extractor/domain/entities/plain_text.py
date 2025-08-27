from dataclasses import dataclass
import re
from osd_text_extractor.domain.exceptions import TextLengthError


@dataclass(frozen=True)
class PlainText:
    value: str

    def __post_init__(self):
        if len(self.value) <= 0:
            raise TextLengthError("Text length should be greater than zero")

    def _clean(self) -> str:
        text = self.value
        text = re.sub(r'[^a-zA-Z0-9\s\n]', '', text)

        text = re.sub(r'[\t\r\f]+', ' ', text)
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()
        return text

    def to_str(self) -> str:
        cleaned_value = self._clean()
        if len(cleaned_value) == 0:
            raise TextLengthError("Text length should be greater than zero")
        return cleaned_value