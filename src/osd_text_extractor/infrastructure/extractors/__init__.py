from ._csv import CSVExtractor
from ._docx import DOCXExtractor
from ._epub import EPUBExtractor
from ._fb2 import FB2Extractor
from ._html import HTMLExtractor
from ._json import JSONExtractor
from ._md import MDExtractor
from ._ods import ODSExtractor
from ._odt import ODTExtractor
from ._pdf import PDFExtractor
from ._rtf import RTFExtractor
from ._txt import TXTExtractor
from ._xlsx import XLSXExtractor
from ._xml import XMLExtractor
from .extractor_factory import ExtractorFactory

EXTRACTORS_MAPPING = {
    "csv": CSVExtractor,
    "docx": DOCXExtractor,
    "epub": EPUBExtractor,
    "fb2": FB2Extractor,
    "html": HTMLExtractor,
    "json": JSONExtractor,
    "md": MDExtractor,
    "ods": ODSExtractor,
    "odt": ODTExtractor,
    "pdf": PDFExtractor,
    "rtf": RTFExtractor,
    "txt": TXTExtractor,
    "xlsx": XLSXExtractor,
    "xml": XMLExtractor,
}
__all__ = [
    "CSVExtractor",
    "DOCXExtractor",
    "EPUBExtractor",
    "FB2Extractor",
    "HTMLExtractor",
    "JSONExtractor",
    "MDExtractor",
    "ODSExtractor",
    "ODTExtractor",
    "PDFExtractor",
    "RTFExtractor",
    "TXTExtractor",
    "XLSXExtractor",
    "XMLExtractor",
    "ExtractorFactory",
    "EXTRACTORS_MAPPING",
]
