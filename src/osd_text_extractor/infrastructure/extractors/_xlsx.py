from io import BytesIO

import emoji
from openpyxl import load_workbook
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.exceptions import ExtractionError


class XLSXExtractor(TextExtractor):
    @staticmethod
    def extract_plain_text(file_content: bytes) -> str:
        try:
            with BytesIO(file_content) as buffer:
                workbook = load_workbook(buffer, read_only=True, data_only=True)
                all_text = []
                for sheet in workbook:
                    for row in sheet.rows:
                        row_text = []
                        empty_count = 0
                        for cell in row:
                            cell_text = (
                                str(cell.value).strip()
                                if cell.value is not None
                                else ""
                            )
                            if not cell_text:
                                empty_count += 1
                                if empty_count >= 3:
                                    break
                            else:
                                empty_count = 0
                                row_text.append(cell_text)
                        if row_text:
                            all_text.append(" ".join(row_text))
                workbook.close()
                text = "\n".join(all_text)
                return emoji.replace_emoji(text, replace=" ")
        except Exception as e:
            raise ExtractionError("Failed to extract XLSX text") from e
