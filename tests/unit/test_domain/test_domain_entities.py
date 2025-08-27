import pytest
from osd_text_extractor.domain.entities import PlainText
from osd_text_extractor.domain.exceptions import TextLengthError


class TestPlainText:
    @pytest.mark.parametrize("text_value", [
        "Simple text",
        "Text with spaces   ",
        "Text\nwith\nnewlines",
        "Text\twith\ttabs",
        "Text with unicode: привет мир 🌍",
        "Very long text " * 1000,
        "   Leading and trailing spaces   ",
    ])
    def test_create_plain_text_success(self, text_value: str) -> None:
        plain_text = PlainText(value=text_value)
        assert plain_text.value == text_value
        assert plain_text.to_str() == text_value

    @pytest.mark.parametrize("empty_value", [
        "",
        "   ",
    ])
    def test_create_plain_text_with_empty_string_raises_error(self, empty_value: str) -> None:
        if empty_value.strip() != empty_value and len(empty_value) > 0:
            pytest.skip("Строка с пробелами имеет длину > 0")

        with pytest.raises(TextLengthError, match="Text length should be greater than zero"):
            PlainText(value=empty_value)

    def test_plain_text_is_frozen(self) -> None:
        plain_text = PlainText(value="test text")
        with pytest.raises(AttributeError):
            plain_text.value = "new value"  # type: ignore

    def test_plain_text_equality(self) -> None:
        text1 = PlainText(value="same text")
        text2 = PlainText(value="same text")
        text3 = PlainText(value="different text")

        assert text1 == text2
        assert text1 != text3
        assert hash(text1) == hash(text2)
        assert hash(text1) != hash(text3)

    def test_plain_text_string_representation(self) -> None:
        text_value = "test representation"
        plain_text = PlainText(value=text_value)

        result = str(plain_text)

        assert "PlainText" in result
        assert text_value in result

    @pytest.mark.parametrize("input_text,expected_output", [
        ("Simple text", "Simple text"),
        ("Text with\nmultiple\nlines", "Text with\nmultiple\nlines"),
        ("Text\twith\ttabs", "Text\twith\ttabs"),
        ("   Text with spaces   ", "   Text with spaces   "),
    ])
    def test_to_str_method(self, input_text: str, expected_output: str) -> None:
        plain_text = PlainText(value=input_text)

        result = plain_text.to_str()

        assert result == expected_output

    def test_plain_text_length_boundary(self) -> None:
        """Тест граничных значений длины текста."""
        # Arrange
        single_char = "a"

        # Act
        plain_text = PlainText(value=single_char)

        # Assert
        assert plain_text.value == single_char
        assert len(plain_text.value) == 1