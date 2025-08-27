from dishka import Provider, Scope, provide

from osd_text_extractor.application.use_cases import ExtractTextUseCase
from osd_text_extractor.infrastructure.extractors import (
    EXTRACTORS_MAPPING,
    ExtractorFactory,
)


class AppProvider(Provider):
    scope = Scope.APP
    extractors_mapping = provide(lambda: EXTRACTORS_MAPPING)
    extractor_factory = provide(ExtractorFactory)
    extract_text_use_case = provide(ExtractTextUseCase)
