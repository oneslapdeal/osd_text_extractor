from dishka import provide
from dishka import Provider
from dishka import Scope
from osd_text_extractor.application.use_cases import ExtractTextUseCase
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.extractors import ExtractorFactory
from osd_text_extractor.infrastructure.extractors import EXTRACTORS_MAPPING


class AppProvider(Provider):
    scope = Scope.APP

    @provide
    def get_extractors_mapping(self) -> dict[str, type[TextExtractor]]:
        return EXTRACTORS_MAPPING

    extractor_factory = provide(ExtractorFactory)
    extract_text_use_case = provide(ExtractTextUseCase)
