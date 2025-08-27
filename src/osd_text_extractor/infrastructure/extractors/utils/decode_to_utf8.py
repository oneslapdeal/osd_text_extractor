def decode_to_utf8(file_content: bytes) -> str:
    encodings = ["utf-8", "utf-16", "windows-1251", "iso-8859-1"]
    for encoding in encodings:
        try:
            return file_content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return file_content.decode("utf-8", errors="replace")
