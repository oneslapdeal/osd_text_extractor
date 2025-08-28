import json
from typing import Any

import emoji
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.exceptions import ExtractionError
from osd_text_extractor.infrastructure.extractors.utils import decode_to_utf8


class JSONExtractor(TextExtractor):
    @staticmethod
    def extract_plain_text(file_content: bytes) -> str:
        try:
            json_data = json.loads(decode_to_utf8(file_content))
            extracted_values = _recursive_extract(json_data)
            text = " ".join(extracted_values).strip()
            return emoji.replace_emoji(text, replace=" ")
        except Exception as e:
            raise ExtractionError("Failed to extract JSON text") from e


def _recursive_extract(obj: Any) -> list[str]:
    result = []
    if isinstance(obj, str):
        result.append(obj)
    elif isinstance(obj, dict):
        for value in obj.values():
            result.extend(_recursive_extract(value))
    elif isinstance(obj, list | tuple):
        for item in obj:
            result.extend(_recursive_extract(item))
    return result
