from osd_text_extractor.application.use_cases import ExtractTextUseCase
from osd_text_extractor.infrastructure.di import create_container


def extract_text(content: bytes, content_format: str) -> str:
    container = create_container()
    try:
        use_case = container.get(ExtractTextUseCase)
        return use_case.execute(content, content_format)
    finally:
        container.close()
