import csv
from io import StringIO

import emoji
from osd_text_extractor.domain.interfaces import TextExtractor
from osd_text_extractor.infrastructure.exceptions import ExtractionError
from osd_text_extractor.infrastructure.extractors.utils import decode_to_utf8


class CSVExtractor(TextExtractor):
    @staticmethod
    def extract_plain_text(file_content: bytes) -> str:
        try:
            csv_file = StringIO(decode_to_utf8(file_content))
            csv_reader = csv.reader(csv_file, delimiter=",", lineterminator="\n")
            extracted_text = []
            for row in csv_reader:
                row_text = []
                empty_count = 0

                for cell in row:
                    cell = cell.strip()
                    if not cell:
                        empty_count += 1
                        if empty_count >= 3:
                            break
                    else:
                        empty_count = 0
                        row_text.append(cell)
                if row_text:
                    extracted_text.append(" ".join(row_text))
            text = "\n".join(extracted_text)
            return emoji.replace_emoji(text, replace=" ")
        except Exception as e:
            raise ExtractionError("Failed to extract CSV text") from e
