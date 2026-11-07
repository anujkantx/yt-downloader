"""FFmpeg detection, verification, and location resolution service."""

import os
import shutil
import subprocess
from pathlib import Path

from app.utils.logging_config import get_logger
from app.utils.paths import get_assets_dir, get_base_dir

logger = get_logger("ffmpeg_service")


class FFmpegService:
    """Detects, inspects, and validates FFmpeg installations."""

    def __init__(self, configured_path: str = ""):
        self.configured_path = configured_path.strip()
        self._cached_path: str | None = None
        self._cached_version: str | None = None

    def get_ffmpeg_path(self) -> str | None:
        """
        Resolve the absolute path or directory to FFmpeg executable.
        Priority:
          1. User-configured custom path (if valid)
          2. Bundled FFmpeg (in assets/bin or application base dir)
          3. System PATH
        """
        # 1. Configured path
        if self.configured_path:
            p = Path(self.configured_path)
            if p.is_file() and p.name.lower().startswith("ffmpeg"):
                return str(p)
            elif p.is_dir():
                candidate = p / "ffmpeg.exe" if os.name == "nt" else p / "ffmpeg"
                if candidate.is_file():
                    return str(candidate)

        # 2. Bundled in assets/bin or base dir
        bundled_candidates = [
            get_assets_dir() / "bin" / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg"),
            get_base_dir() / "bin" / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg"),
            get_base_dir() / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg"),
        ]
        for candidate in bundled_candidates:
            if candidate.is_file():
                return str(candidate)

        # 3. System PATH
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            return system_ffmpeg

        # 4. Windows-specific standard package manager and installation paths
        if os.name == "nt":
            local_app_data = os.environ.get("LOCALAPPDATA", "")
            user_profile = os.environ.get("USERPROFILE", "")
            windows_candidates = [
                Path(local_app_data) / "Microsoft" / "WinGet" / "Links" / "ffmpeg.exe",
                Path("C:/ffmpeg/bin/ffmpeg.exe"),
                Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
                Path("C:/ProgramData/chocolatey/bin/ffmpeg.exe"),
                Path(user_profile) / "scoop" / "shims" / "ffmpeg.exe",
            ]
            for candidate in windows_candidates:
                if candidate.is_file():
                    return str(candidate)

            # Check WinGet Packages directory
            winget_pkgs = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
            if winget_pkgs.exists():
                try:
                    for ffmpeg_found in winget_pkgs.glob("**/ffmpeg.exe"):
                        if ffmpeg_found.is_file():
                            return str(ffmpeg_found)
                except Exception:
                    pass

            # Check Windows Registry User/System PATH (refreshes without terminal restart)
            try:
                import winreg
                for root_key, subkey in [
                    (winreg.HKEY_CURRENT_USER, r"Environment"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                ]:
                    try:
                        with winreg.OpenKey(root_key, subkey) as key:
                            reg_path, _ = winreg.QueryValueEx(key, "Path")
                            for folder in reg_path.split(";"):
                                f_path = Path(folder.strip()) / "ffmpeg.exe"
                                if f_path.is_file():
                                    return str(f_path)
                    except Exception:
                        pass
            except Exception:
                pass

        return None

    def is_available(self) -> bool:
        """Check if a valid working FFmpeg executable is found."""
        path = self.get_ffmpeg_path()
        if not path:
            return False
        return self._verify_executable(path)

    def _verify_executable(self, path: str) -> bool:
        """Execute ffmpeg -version to verify functionality."""
        try:
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            res = subprocess.run(
                [path, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
                startupinfo=startupinfo,
            )
            if res.returncode == 0:
                first_line = res.stdout.splitlines()[0] if res.stdout else "FFmpeg detected"
                self._cached_version = first_line
                return True
            return False
        except Exception as e:
            logger.debug("Verification failed for FFmpeg at %s: %s", path, e)
            return False

    def get_status_info(self) -> tuple[bool, str]:
        """
        Return (is_available, status_message).
        Provides clear user-facing explanation when FFmpeg is missing.
        """
        path = self.get_ffmpeg_path()
        if path and self._verify_executable(path):
            version_str = self._cached_version or "Detected"
            return True, f"Available: {version_str} ({path})"

        return False, (
            "FFmpeg not found. Downloading without FFmpeg is supported for pre-merged streams, "
            "but 1080p+ separate video/audio merging and MP3 conversion require FFmpeg."
        )

    def set_configured_path(self, path: str) -> None:
        """Update configured path and clear caches."""
        self.configured_path = path.strip()
        self._cached_path = None
        self._cached_version = None
