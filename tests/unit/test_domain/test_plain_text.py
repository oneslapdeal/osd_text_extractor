import pytest

from osd_text_extractor.domain.entities import PlainText
from osd_text_extractor.domain.exceptions import TextLengthError


class TestPlainText:
    def test_create_plain_text_with_valid_text(self) -> None:
        """Test creating PlainText with normal text."""
        text_value = "Simple text with valid characters"
        plain_text = PlainText(value=text_value)
        assert plain_text.value == text_value

    def test_create_plain_text_with_empty_string_raises_error(self) -> None:
        """Test that empty string raises error during creation."""
        with pytest.raises(
            TextLengthError, match="Text length should be greater than zero"
        ):
            PlainText(value="")

    def test_create_plain_text_with_whitespace_only_raises_error(self) -> None:
        """Test that whitespace-only string raises error during creation."""
        with pytest.raises(
            TextLengthError, match="Text length should be greater than zero"
        ):
            PlainText(value="   ")

        with pytest.raises(
            TextLengthError, match="Text length should be greater than zero"
        ):
            PlainText(value="\n\n\t  ")

    def test_to_str_with_latin_text_success(self) -> None:
        """Test to_str() with text that should pass cleaning."""
        text_value = "Simple Latin text 123"
        plain_text = PlainText(value=text_value)
        result = plain_text.to_str()
        assert result == text_value

    def test_to_str_removes_non_latin_characters(self) -> None:
        """Test that to_str() removes non-Latin characters."""
        # Input has Cyrillic, Chinese, Arabic, symbols
        text_value = "Latin text Русский 中文 العربية @#$%^&*()"
        plain_text = PlainText(value=text_value)
        result = plain_text.to_str()
        # Only Latin chars, digits, and spaces should remain
        assert result == "Latin text @#$%^&*()"

    def test_to_str_normalizes_whitespace(self) -> None:
        """Test that to_str() normalizes whitespace correctly."""
        text_value = "Text   with\t\tmultiple\n\n\nspaces"
        plain_text = PlainText(value=text_value)
        result = plain_text.to_str()
        assert result == "Text with multiple\nspaces"

    def test_to_str_preserves_newlines(self) -> None:
        """Test that to_str() preserves single newlines."""
        text_value = "Line one\nLine two\nLine three"
        plain_text = PlainText(value=text_value)
        result = plain_text.to_str()
        assert result == "Line one\nLine two\nLine three"

    def test_to_str_collapses_multiple_newlines(self) -> None:
        """Test that multiple newlines are collapsed to single."""
        text_value = "Line one\n\n\nLine two"
        plain_text = PlainText(value=text_value)
        result = plain_text.to_str()
        assert result == "Line one\nLine two"

    def test_to_str_strips_leading_trailing_whitespace(self) -> None:
        """Test that leading/trailing whitespace is stripped."""
        text_value = "   Content with spaces   "
        plain_text = PlainText(value=text_value)
        result = plain_text.to_str()
        assert result == "Content with spaces"

    def test_to_str_with_only_non_latin_raises_error(self) -> None:
        """Test that text with only non-Latin chars raises error after cleaning."""
        # Only non-Latin characters
        text_value = "Русский 中文 العربية 🌍"
        plain_text = PlainText(value=text_value)
        with pytest.raises(
            TextLengthError, match="Text length should be greater than zero"
        ):
            plain_text.to_str()

    def test_to_str_preserves_digits(self) -> None:
        """Test that digits are preserved during cleaning."""
        text_value = "Text with numbers 12345 and letters"
        plain_text = PlainText(value=text_value)
        result = plain_text.to_str()
        assert result == "Text with numbers 12345 and letters"

    def test_plain_text_is_frozen(self) -> None:
        """Test that PlainText is immutable."""
        plain_text = PlainText(value="test text")
        with pytest.raises(AttributeError):
            plain_text.value = "new value"  # type: ignore

    def test_plain_text_equality(self) -> None:
        """Test PlainText equality comparison."""
        text1 = PlainText(value="same text")
        text2 = PlainText(value="same text")
        text3 = PlainText(value="different text")

        assert text1 == text2
        assert text1 != text3
        assert hash(text1) == hash(text2)
        assert hash(text1) != hash(text3)

    def test_plain_text_string_representation(self) -> None:
        """Test PlainText string representation."""
        text_value = "test representation"
        plain_text = PlainText(value=text_value)
        result = str(plain_text)
        assert "PlainText" in result
        assert text_value in result

    @pytest.mark.parametrize(
        ("input_text", "expected_output"),
        [
            ("Simple text", "Simple text"),
            ("Text123", "Text123"),
            ("Multiple   spaces", "Multiple spaces"),
            ("Text\nwith\nnewlines", "Text\nwith\nnewlines"),
            ("UPPERCASE lowercase", "UPPERCASE lowercase"),
        ],
    )
    def test_to_str_parametrized_valid_cases(
        self, input_text: str, expected_output: str
    ) -> None:
        """Test to_str() with various valid inputs."""
        plain_text = PlainText(value=input_text)
        result = plain_text.to_str()
        assert result == expected_output

    @pytest.mark.parametrize(
        "invalid_input",
        [
            "🌍🚀🎉",  # Only emojis (should be handled by extractors)
            "символы",  # Only Cyrillic
            "中文文本",  # Only Chinese
            "النص العربي",  # Only Arabic
        ],
    )
    def test_to_str_parametrized_invalid_cases(self, invalid_input: str) -> None:
        """Test to_str() with inputs that become empty after cleaning."""
        plain_text = PlainText(value=invalid_input)
        with pytest.raises(TextLengthError):
            plain_text.to_str()

    def test_mixed_content_cleaning(self) -> None:
        """Test cleaning mixed Latin and non-Latin content."""
        text_value = "Hello мир! 123 test@email.com 🌍"
        plain_text = PlainText(value=text_value)
        result = plain_text.to_str()
        assert result == "Hello ! 123 test@email.com"

    def test_performance_with_large_text(self) -> None:
        """Test performance with large text input."""
        large_text = "Valid text content " * 1000  # ~19KB
        plain_text = PlainText(value=large_text)
        result = plain_text.to_str()
        assert len(result) > 0
        assert "Valid text content" in result

    def test_edge_case_single_character(self) -> None:
        """Test with single character inputs."""
        # Valid single char
        plain_text = PlainText(value="a")
        assert plain_text.to_str() == "a"

        # Invalid single char
        plain_text_invalid = PlainText(value="ф")
        with pytest.raises(TextLengthError):
            plain_text_invalid.to_str()

    def test_clean_method_internal_consistency(self) -> None:
        """Test that _clean() method works consistently."""
        plain_text = PlainText(value="Test   content\n\nwith\tstuff")
        result1 = plain_text.to_str()
        result2 = plain_text.to_str()
        assert result1 == result2
        assert result1 == "Test content\nwith stuff"
