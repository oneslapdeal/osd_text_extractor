import contextlib
from typing import cast

from osd_text_extractor.application.use_cases import ExtractTextUseCase
from osd_text_extractor.infrastructure.di import create_container


def extract_text(content: bytes, content_format: str) -> str:
    """Extracts plain text from multiple document formats.

    :param content: bytes
    :param content_format: str (content format. Ex.: "pdf")
    :return: str (Extracted plain text).
    """
    container = create_container()
    try:
        use_case = cast(ExtractTextUseCase, container.get(ExtractTextUseCase))
        return use_case.execute(content, content_format)
    finally:
        with contextlib.suppress(Exception):
            container.close()
