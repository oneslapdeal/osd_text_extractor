# OSD Text Extractor

A Python library for extracting plain text from various document formats for LLM and NLP purposes.

## Features

- **Multi-format support**: Extract text from PDF, DOCX, XLSX, HTML, XML, JSON, Markdown, RTF, CSV, EPUB, FB2, ODS, ODT, and TXT files
- **Clean output**: Automatically removes non-Latin characters, normalizes whitespace, and filters out formatting artifacts
- **LLM-ready**: Produces clean, plain text optimized for language model processing
- **Robust error handling**: Comprehensive exception handling with detailed error messages
- **Memory efficient**: Handles large files with appropriate size limits and safeguards
- **Type safe**: Full type hints and mypy compliance

## Installation

```bash
pip install osd-text-extractor
```

## Quick Start

```python
from osd_text_extractor import extract_text

# Extract text from a file
with open("document.pdf", "rb") as f:
    content = f.read()

text = extract_text(content, "pdf")
print(text)
```

## Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| PDF | `.pdf` | Portable Document Format |
| DOCX | `.docx` | Microsoft Word documents |
| XLSX | `.xlsx` | Microsoft Excel spreadsheets |
| HTML | `.html`, `.htm` | Web pages |
| XML | `.xml` | XML documents |
| JSON | `.json` | JSON data files |
| Markdown | `.md` | Markdown documents |
| RTF | `.rtf` | Rich Text Format |
| CSV | `.csv` | Comma-separated values |
| TXT | `.txt` | Plain text files |
| EPUB | `.epub` | Electronic books |
| FB2 | `.fb2` | FictionBook format |
| ODS | `.ods` | OpenDocument Spreadsheet |
| ODT | `.odt` | OpenDocument Text |

## Usage Examples

### Basic Text Extraction

```python
from osd_text_extractor import extract_text

# PDF extraction
with open("report.pdf", "rb") as f:
    pdf_text = extract_text(f.read(), "pdf")

# HTML extraction
html_content = b"<html><body><h1>Title</h1><p>Content</p></body></html>"
html_text = extract_text(html_content, "html")

# JSON extraction
json_content = b'{"title": "Document", "content": "Text content"}'
json_text = extract_text(json_content, "json")
```

### Working with Different File Types

```python
import os
from osd_text_extractor import extract_text

def extract_from_file(file_path):
    # Get file extension
    _, ext = os.path.splitext(file_path)
    format_name = ext[1:].lower()  # Remove dot and lowercase

    # Read file content
    with open(file_path, "rb") as f:
        content = f.read()

    # Extract text
    try:
        text = extract_text(content, format_name)
        return text
    except Exception as e:
        print(f"Failed to extract text from {file_path}: {e}")
        return None

# Usage
text = extract_from_file("document.docx")
if text:
    print(f"Extracted {len(text)} characters")
```

### Batch Processing

```python
import os
from pathlib import Path
from osd_text_extractor import extract_text

def process_directory(directory_path, output_file):
    supported_extensions = {'.pdf', '.docx', '.xlsx', '.html', '.xml',
                          '.json', '.md', '.rtf', '.csv', '.txt',
                          '.epub', '.fb2', '.ods', '.odt'}

    results = []

    for file_path in Path(directory_path).rglob('*'):
        if file_path.suffix.lower() in supported_extensions:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()

                format_name = file_path.suffix[1:].lower()
                text = extract_text(content, format_name)

                results.append({
                    'file': str(file_path),
                    'text': text,
                    'length': len(text)
                })
                print(f"✓ Processed {file_path}")

            except Exception as e:
                print(f"✗ Failed {file_path}: {e}")

    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"=== {result['file']} ===\n")
            f.write(f"{result['text']}\n\n")

    print(f"Processed {len(results)} files, saved to {output_file}")

# Usage
process_directory("./documents", "extracted_texts.txt")
```

## Text Cleaning

The library automatically cleans extracted text:

- **Character filtering**: Removes non-Latin characters (Cyrillic, Chinese, Arabic, emojis, etc.)
- **Whitespace normalization**: Collapses multiple spaces, tabs, and line breaks
- **Artifact removal**: Strips HTML tags, markdown syntax, and formatting codes
- **Emoji removal**: Filters out emoji characters

### Example of text cleaning:

```python
# Input text with mixed content
raw_text = "English text Русский 中文 with symbols @#$% and emojis 🌍"

# After extraction and cleaning
cleaned_text = "English text with symbols and emojis"
```

## Error Handling

The library provides specific exceptions for different error scenarios:

```python
from osd_text_extractor import extract_text
from osd_text_extractor.application.exceptions import UnsupportedFormatError
from osd_text_extractor.domain.exceptions import TextLengthError
from osd_text_extractor.infrastructure.exceptions import ExtractionError

try:
    text = extract_text(content, format_name)
except UnsupportedFormatError:
    print("File format not supported")
except TextLengthError:
    print("No valid text content found")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Security Features

The library includes several security protections:

- **Size limits**: Prevents processing of excessively large files
- **XML bomb protection**: Guards against malicious XML with excessive nesting or entity expansion
- **Memory safeguards**: Limits memory usage during processing
- **Input validation**: Validates file formats and content structure

## Performance Considerations

- **Memory usage**: Files are processed in memory, consider available RAM for large files
- **Processing speed**: Varies by format complexity (TXT > HTML > PDF > DOCX)
- **Concurrent processing**: Library is thread-safe for concurrent usage

## Dependencies

Core dependencies:
- `beautifulsoup4` - HTML/XML parsing
- `lxml` - XML processing
- `pymupdf` - PDF processing
- `python-docx` - DOCX processing
- `openpyxl` - XLSX processing
- `striprtf` - RTF processing
- `odfpy` - ODS/ODT processing
- `emoji` - Emoji handling
- `dishka` - Dependency injection

## Development

### Setting up development environment

```bash
# Clone repository
git clone https://github.com/OneSlap/osd-text-extractor.git
cd osd-text-extractor

# Install UV (package manager)
pip install uv

# Install dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Run type checking
uv run mypy src/
```

### Running tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/osd_text_extractor --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_domain/test_domain_entities.py

# Run integration tests only
uv run pytest tests/integration/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`uv run pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Changelog

### v0.1.0
- Initial release
- Support for 14 document formats
- Clean architecture with dependency injection
- Comprehensive test suite
- Type safety with mypy
- Security protections for XML processing

## Support

- **Issues**: [GitHub Issues](https://github.com/OneSlap/osd-text-extractor/issues)
- **Documentation**: [GitHub README](https://github.com/OneSlap/osd-text-extractor#readme)
- **Source Code**: [GitHub Repository](https://github.com/OneSlap/osd-text-extractor)

## Roadmap

- [ ] Add support for PowerPoint (PPTX) files
- [ ] Implement streaming processing for very large files
- [ ] Add OCR support for image-based PDFs
- [ ] Improve text structure preservation
- [ ] Add configuration options for text cleaning
- [ ] Performance optimizations for batch processing
