from typing import Any


def xml_node_to_plain_text(node: Any) -> str:
    text_parts: list[str] = []
    if node.text and node.text.strip():
        text_parts.append(node.text.strip())
    for child in node:
        text_parts.append(xml_node_to_plain_text(child))

        if child.tail and child.tail.strip():
            text_parts.append(child.tail.strip())
    return " ".join(text_parts) if text_parts else ""
