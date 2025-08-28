import re
from string import ascii_letters
from string import digits
from string import punctuation

valid_characters = ascii_letters + digits + punctuation + " \n"
texts = [
    "🌍🚀🎉",  # Only emojis (should be handled by extractors)
    "символы",  # Only Cyrillic
    "中文文本",  # Only Chinese
    "النص العربي",  # Only Arabic
    "      ",  # Only whitespace
]


def _clean(text) -> str:
    text = re.sub(r"[\t\r\f]+", " ", text)
    text = "".join([i for i in text if i in valid_characters])
    text = re.sub(r" +", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


for _text in texts:
    pass
