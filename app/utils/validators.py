"""Validation and sanitization utilities for URLs, filenames, and paths."""

import os
import re
from pathlib import Path
from urllib.parse import urlparse

# Windows forbidden characters in filenames: < > : " / \ | ? * and control chars (0-31)
FORBIDDEN_CHARS_PATTERN = re.compile(r'[\<\>\:"/\\\|\?\*\x00-\x1f]')

# Windows reserved device names
RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}

# Maximum filename length (Windows safe)
MAX_FILENAME_LENGTH = 200


def is_valid_url(url: str) -> bool:
    """Check if the provided string is a valid HTTP/HTTPS URL."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    try:
        parsed = urlparse(url)
        return parsed.scheme.lower() in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def extract_urls(text: str) -> list[str]:
    """
    Extract, trim, and validate unique URLs from multi-line or whitespace-separated text.
    Rejects empty lines, invalid schemes, and duplicates while preserving order.
    """
    if not text:
        return []

    lines = text.splitlines()
    cleaned_urls: list[str] = []
    seen = set()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Check if line contains space-separated tokens or is a single url
        tokens = stripped.split()
        for token in tokens:
            token = token.strip()
            if is_valid_url(token) and token not in seen:
                seen.add(token)
                cleaned_urls.append(token)

    return cleaned_urls


def sanitize_filename(name: str, fallback: str = "video") -> str:
    """
    Sanitize a string to be a safe Windows filename.
    Removes invalid characters, strips leading/trailing spaces and periods,
    replaces reserved device names, and enforces max length.
    """
    if not name or not isinstance(name, str):
        return fallback

    # Replace forbidden characters with underscore or strip
    cleaned = FORBIDDEN_CHARS_PATTERN.sub("_", name)

    # Replace consecutive spaces or underscores
    cleaned = re.sub(r"[\s_]+", " ", cleaned).strip()

    # Windows files cannot end in a period or space
    cleaned = cleaned.rstrip(". ")

    if not cleaned:
        cleaned = fallback

    # Split stem and extension if present
    base_name = cleaned
    ext = ""
    if "." in cleaned:
        parts = cleaned.rsplit(".", 1)
        # Only treat as extension if short (<= 10 chars)
        if len(parts[1]) <= 10 and not any(c in parts[1] for c in " /\\"):
            base_name, ext = parts[0], f".{parts[1]}"

    # Check for reserved Windows device names (case-insensitive)
    if base_name.upper() in RESERVED_NAMES:
        base_name = f"{base_name}_file"

    # Enforce maximum length
    max_stem_len = MAX_FILENAME_LENGTH - len(ext)
    max_stem_len = max(max_stem_len, 10)
    base_name = base_name[:max_stem_len].rstrip(". ")

    return f"{base_name}{ext}" if ext else base_name


def validate_output_directory(path: Path | str) -> tuple[bool, str]:
    """
    Validate that an output directory exists or can be created, and is writable.
    Returns (is_valid, error_message).
    """
    try:
        p = Path(path).resolve()
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
        if not os.access(p, os.W_OK):
            return False, f"Directory is not writable: {p}"
        return True, ""
    except Exception as e:
        return False, f"Invalid directory path: {e}"
