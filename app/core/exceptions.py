"""Custom exceptions for downloader engine and task manager."""


class DownloaderError(Exception):
    """Base exception for all downloader errors."""


class DownloadCancelledError(DownloaderError):
    """Raised when a download task was cancelled by the user."""


class MetadataExtractionError(DownloaderError):
    """Raised when media metadata extraction fails."""


class UnsupportedURLError(DownloaderError):
    """Raised when a URL is not recognized or supported by yt-dlp."""


class FFmpegNotFoundError(DownloaderError):
    """Raised when FFmpeg is required for an operation but not available."""


class FileSystemError(DownloaderError):
    """Raised when an output directory or file cannot be written."""


class PostProcessingError(DownloaderError):
    """Raised when audio conversion or stream merging fails."""
