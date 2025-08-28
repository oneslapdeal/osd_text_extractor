from typing import Protocol


class TextExtractor(Protocol):
    @staticmethod
    def extract_plain_text(content: bytes) -> str: ...
