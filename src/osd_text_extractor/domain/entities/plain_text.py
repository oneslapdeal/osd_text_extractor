from dataclasses import dataclass

from osd_text_extractor.domain.exceptions import TextLengthError


@dataclass(frozen=True)
class PlainText:
    value: str

    def __post_init__(self):
        if len(self.value) <= 0:
            raise TextLengthError("Text length should be greater than zero")

    def _clean(self) -> str:
        return self.value

    def to_str(self) -> str:
        cleaned_value = self._clean()
        return cleaned_value
