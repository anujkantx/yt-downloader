"""Tests for URL and filename validators."""

from app.utils.validators import (
    extract_urls,
    is_valid_url,
    sanitize_filename,
    validate_output_directory,
)


def test_is_valid_url():
    assert is_valid_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert is_valid_url("http://example.com/video.mp4")
    assert is_valid_url("https://vimeo.com/123456")

    assert not is_valid_url("")
    assert not is_valid_url("   ")
    assert not is_valid_url("not a url")
    assert not is_valid_url("ftp://example.com/file")
    assert not is_valid_url("javascript:alert(1)")


def test_extract_urls():
    text = """
    https://www.youtube.com/watch?v=one
    not_a_url
    https://www.youtube.com/watch?v=two
    https://www.youtube.com/watch?v=one   # duplicate

    https://vimeo.com/999
    """
    urls = extract_urls(text)
    assert len(urls) == 3
    assert urls[0] == "https://www.youtube.com/watch?v=one"
    assert urls[1] == "https://www.youtube.com/watch?v=two"
    assert urls[2] == "https://vimeo.com/999"


def test_sanitize_filename_forbidden_chars():
    raw = 'My: Cool / Video * Title? "<Special>|'
    sanitized = sanitize_filename(raw)
    assert ":" not in sanitized
    assert "/" not in sanitized
    assert "*" not in sanitized
    assert "?" not in sanitized
    assert '"' not in sanitized
    assert "<" not in sanitized
    assert ">" not in sanitized
    assert "|" not in sanitized


def test_sanitize_filename_reserved_device_names():
    assert sanitize_filename("CON.mp4") == "CON_file.mp4"
    assert sanitize_filename("aux.mkv") == "aux_file.mkv"
    assert sanitize_filename("NUL") == "NUL_file"
    assert sanitize_filename("com1.mp4") == "com1_file.mp4"


def test_sanitize_filename_trailing_periods_and_spaces():
    assert sanitize_filename("Video Title... ") == "Video Title"
    assert sanitize_filename("...video...mp4") == "video.mp4" or sanitize_filename("...video...mp4").endswith(".mp4")


def test_sanitize_filename_max_length():
    long_title = "A" * 300 + ".mp4"
    sanitized = sanitize_filename(long_title)
    assert len(sanitized) <= 200
    assert sanitized.endswith(".mp4")


def test_validate_output_directory(tmp_path):
    valid_dir = tmp_path / "downloads"
    is_valid, err = validate_output_directory(valid_dir)
    assert is_valid
    assert valid_dir.exists()
    assert err == ""
