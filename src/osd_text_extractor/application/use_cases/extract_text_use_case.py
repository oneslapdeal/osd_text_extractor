from osd_text_extractor.domain.entities import PlainText
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.extractors import ExtractorFactory


class ExtractTextUseCase:
    def __init__(self, extractor_factory: ExtractorFactory):
        self.extractor_factory = extractor_factory

    def execute(self, content: bytes, content_format: str) -> str:
        extractor: TextExtractor = self.extractor_factory.get_extractor(content_format)
        plain_text = PlainText(value=extractor.extract_plain_text(content))
        return plain_text.to_str()
