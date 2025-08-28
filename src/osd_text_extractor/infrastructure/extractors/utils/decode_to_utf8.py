def decode_to_utf8(file_content: bytes) -> str:
    # Try UTF-8 first with replacement for invalid bytes
    try:
        return file_content.decode("utf-8", errors="replace")
    except UnicodeDecodeError:
        pass

    # Try other encodings if needed
    encodings = ["iso-8859-1", "windows-1251"]
    for encoding in encodings:
        try:
            return file_content.decode(encoding)
        except UnicodeDecodeError:
            continue

    # Final fallback: UTF-8 with replacement
    return file_content.decode("utf-8", errors="replace")
