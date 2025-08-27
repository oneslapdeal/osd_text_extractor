from typing import Protocol

from osd_text_extractor.domain.interfaces import TextExtractor


class ExtractorFactory(Protocol):
    def get_extractor(self) -> type[TextExtractor]: ...
