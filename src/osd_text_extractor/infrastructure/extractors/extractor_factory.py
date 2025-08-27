from osd_text_extractor.application.exceptions import UnsupportedFormatError
from osd_text_extractor.domain.interfaces import TextExtractor


class ExtractorFactory:
    def __init__(self, extractor_mapping: dict[str, type[TextExtractor]]):
        self.extractor_mapping = extractor_mapping

    def get_extractor(self, content_format: str) -> type[TextExtractor]:
        extractor_class = self.extractor_mapping.get(content_format.lower())
        if not extractor_class:
            raise UnsupportedFormatError(f"Unsupported format: {content_format}")
        return extractor_class
