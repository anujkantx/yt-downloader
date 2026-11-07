"""Filesystem utilities for safe Windows file and folder operations."""

import os
import subprocess
from pathlib import Path

from app.utils.logging_config import get_logger

logger = get_logger("file_service")


class FileService:
    """Provides safe platform-aware filesystem and explorer operations."""

    @staticmethod
    def open_file(file_path: Path | str) -> bool:
        """Open a file with the default associated application."""
        p = Path(file_path).resolve()
        if not p.exists() or not p.is_file():
            logger.warning("File does not exist: %s", p)
            return False

        try:
            if os.name == "nt":
                os.startfile(str(p))
            else:
                subprocess.Popen(["xdg-open", str(p)])
            return True
        except Exception as e:
            logger.error("Failed to open file '%s': %s", p, e)
            return False

    @staticmethod
    def open_containing_folder(file_path: Path | str) -> bool:
        """Open Windows Explorer and select the specified file."""
        p = Path(file_path).resolve()
        if not p.exists():
            # If the file doesn't exist, try opening parent folder
            if p.parent.exists():
                return FileService.open_directory(p.parent)
            logger.warning("Neither file nor parent folder exists: %s", p)
            return False

        try:
            if os.name == "nt":
                subprocess.run(
                    ["explorer.exe", f"/select,{p!s}"],
                    check=False,
                )
            else:
                subprocess.Popen(["xdg-open", str(p.parent)])
            return True
        except Exception as e:
            logger.error("Failed to reveal file '%s': %s", p, e)
            return False

    @staticmethod
    def open_directory(dir_path: Path | str) -> bool:
        """Open a directory in Windows Explorer."""
        p = Path(dir_path).resolve()
        if not p.exists() or not p.is_dir():
            logger.warning("Directory does not exist: %s", p)
            return False

        try:
            if os.name == "nt":
                os.startfile(str(p))
            else:
                subprocess.Popen(["xdg-open", str(p)])
            return True
        except Exception as e:
            logger.error("Failed to open directory '%s': %s", p, e)
            return False

    @staticmethod
    def get_unique_filepath(target_path: Path | str) -> Path:
        """If target exists, generate non-colliding file name e.g. 'video (1).mp4'."""
        p = Path(target_path).resolve()
        if not p.exists():
            return p

        stem = p.stem
        suffix = p.suffix
        parent = p.parent

        counter = 1
        while True:
            candidate = parent / f"{stem} ({counter}){suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    @staticmethod
    def delete_file_safely(file_path: Path | str) -> bool:
        """Delete file if it exists."""
        try:
            p = Path(file_path).resolve()
            if p.is_file():
                p.unlink()
                logger.info("Deleted file: %s", p)
                return True
            return False
        except Exception as e:
            logger.error("Failed to delete file '%s': %s", file_path, e)
            return False

    @staticmethod
    def get_file_size(file_path: Path | str) -> int | None:
        """Return file size in bytes if file exists."""
        try:
            p = Path(file_path).resolve()
            if p.is_file():
                return p.stat().st_size
        except Exception:
            pass
        return None
