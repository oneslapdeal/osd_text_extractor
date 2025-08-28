import re
from dataclasses import dataclass
from string import ascii_letters
from string import digits
from string import punctuation

from osd_text_extractor.domain.exceptions import TextLengthError

valid_characters = ascii_letters + digits + punctuation + " \n"


@dataclass(frozen=True)
class PlainText:
    value: str

    def __post_init__(self) -> None:
        if len(self.value.strip()) <= 0:
            raise TextLengthError("Text length should be greater than zero")

    def _clean(self) -> str:
        text = self.value
        text = re.sub(r"[\t\r\f]+", " ", text)
        text = "".join([i for i in text if i in valid_characters])
        text = re.sub(r" +", " ", text)
        text = re.sub(r"\n+", "\n", text)
        return text.strip()

    def to_str(self) -> str:
        cleaned_value = self._clean()
        if len(cleaned_value) <= 0:
            raise TextLengthError("Text length should be greater than zero")
        return cleaned_value
