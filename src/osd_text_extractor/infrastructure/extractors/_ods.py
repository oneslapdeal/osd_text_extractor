from io import BytesIO

import emoji
from odf.opendocument import load
from odf.table import Table
from odf.table import TableCell
from odf.table import TableRow
from odf.text import P
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.exceptions import ExtractionError


class ODSExtractor(TextExtractor):
    @staticmethod
    def extract_plain_text(file_content: bytes) -> str:
        try:
            with BytesIO(file_content) as buffer:
                doc = load(buffer)
                all_text = []
                for table in doc.spreadsheet.getElementsByType(Table):
                    for row in table.getElementsByType(TableRow):
                        row_text = []
                        empty_count = 0
                        for cell in row.getElementsByType(TableCell):
                            cell_text = ""
                            for p in cell.getElementsByType(P):
                                if p:
                                    cell_text += str(p)
                            cell_text = cell_text.strip()
                            if not cell_text:
                                empty_count += 1
                                if empty_count >= 3:
                                    break
                            else:
                                empty_count = 0
                                row_text.append(cell_text)
                        if row_text:
                            all_text.append(" ".join(row_text))
                text = "\n".join(all_text)
                return emoji.replace_emoji(text, replace=" ")
        except Exception as e:
            raise ExtractionError("Failed to extract ODS text") from e
