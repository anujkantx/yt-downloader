"""FFmpeg detection, verification, auto-download, and location resolution service."""

import os
import shutil
import subprocess
import urllib.request
import zipfile
from collections.abc import Callable
from pathlib import Path

from app.utils.logging_config import get_logger
from app.utils.paths import get_assets_dir, get_base_dir, get_bin_dir

logger = get_logger("ffmpeg_service")

# Candidate download URLs for static Windows builds
FFMPEG_DOWNLOAD_URLS = [
    # Lightweight static build (~52MB, fast and reliable)
    "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v6.1/ffmpeg-6.1-win-64.zip",
    # Official Gyan essentials release (~109MB fallback)
    "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
]


class FFmpegService:
    """Detects, inspects, validates, and downloads FFmpeg installations."""

    def __init__(self, configured_path: str = ""):
        self.configured_path = configured_path.strip()
        self._cached_path: str | None = None
        self._cached_version: str | None = None

    def get_ffmpeg_path(self) -> str | None:
        """
        Resolve the absolute path or directory to FFmpeg executable.
        Priority:
          1. User-configured custom path (if valid)
          2. Local user bin (LocalAppData) or bundled FFmpeg (assets/bin or application base dir)
          3. System PATH
          4. Windows package managers (WinGet, Chocolatey, Scoop, Registry)
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

        # 2. Local bin or bundled in assets/bin or base dir
        bundled_candidates = [
            get_bin_dir() / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg"),
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

    def download_ffmpeg(
        self,
        target_dir: Path | str | None = None,
        progress_callback: Callable[[int, str], None] | None = None,
    ) -> str:
        """
        Download static FFmpeg executable directly and place it in the target or local bin directory.

        :param target_dir: Directory where ffmpeg.exe will be saved (defaults to LocalAppData bin).
        :param progress_callback: Callback taking (percentage: int, message: str).
        :return: Absolute path string to the installed ffmpeg executable.
        """
        dest_dir = Path(target_dir) if target_dir else get_bin_dir()
        dest_dir.mkdir(parents=True, exist_ok=True)
        exe_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
        final_exe = dest_dir / exe_name

        def _notify(pct: int, msg: str) -> None:
            if progress_callback:
                try:
                    progress_callback(pct, msg)
                except Exception:
                    pass

        _notify(0, "Connecting to download server...")

        last_error: Exception | None = None
        for url in FFMPEG_DOWNLOAD_URLS:
            tmp_zip = dest_dir / f"ffmpeg_download_{os.getpid()}.zip"
            try:
                logger.info("Attempting FFmpeg download from %s", url)
                _notify(5, "Downloading static FFmpeg package...")

                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) yt-downloader/1.0"},
                )
                with urllib.request.urlopen(req, timeout=30) as response, open(tmp_zip, "wb") as out_file:
                    total_size = int(response.headers.get("Content-Length", 0))
                    downloaded = 0
                    chunk_size = 128 * 1024  # 128 KB chunks

                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            pct = 5 + int((downloaded / total_size) * 80)
                            downloaded_mb = downloaded / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)
                            _notify(
                                min(pct, 85),
                                f"Downloading FFmpeg... {downloaded_mb:.1f} MB / {total_mb:.1f} MB ({pct}%)",
                            )
                        else:
                            downloaded_mb = downloaded / (1024 * 1024)
                            _notify(50, f"Downloading FFmpeg... {downloaded_mb:.1f} MB")

                _notify(88, "Extracting FFmpeg executable...")
                extracted = False
                with zipfile.ZipFile(tmp_zip, "r") as zf:
                    for member in zf.namelist():
                        member_path = Path(member)
                        # Look for ffmpeg.exe or ffmpeg
                        if member_path.name.lower() in ("ffmpeg.exe", "ffmpeg"):
                            with zf.open(member) as source, open(final_exe, "wb") as target:
                                shutil.copyfileobj(source, target)
                            extracted = True
                        elif member_path.name.lower() in ("ffprobe.exe", "ffprobe"):
                            probe_path = dest_dir / member_path.name
                            with zf.open(member) as source, open(probe_path, "wb") as target:
                                shutil.copyfileobj(source, target)

                if not extracted:
                    raise RuntimeError("Could not locate ffmpeg binary inside the downloaded package.")

                # Set executable permission on Unix-like platforms
                if os.name != "nt":
                    final_exe.chmod(0o755)

                _notify(95, "Verifying FFmpeg installation...")
                self._cached_path = None
                self._cached_version = None
                if not self._verify_executable(str(final_exe)):
                    raise RuntimeError("Downloaded FFmpeg executable verification failed.")

                self.configured_path = str(final_exe)
                _notify(100, "FFmpeg installed successfully!")
                logger.info("FFmpeg successfully downloaded and installed to %s", final_exe)
                return str(final_exe)

            except Exception as e:
                logger.warning("Download from %s failed: %s", url, e)
                last_error = e
            finally:
                if tmp_zip.exists():
                    try:
                        tmp_zip.unlink(missing_ok=True)
                    except Exception:
                        pass

        raise RuntimeError(f"Failed to auto-download FFmpeg from all sources: {last_error}")


if __name__ == "__main__":
    import sys

    svc = FFmpegService()
    if "--download" in sys.argv:
        print("Starting FFmpeg download to LocalAppData bin...")

        def _print_progress(pct: int, msg: str) -> None:
            print(f"[{pct}%] {msg}")

        path = svc.download_ffmpeg(progress_callback=_print_progress)
        print(f"\nSuccess! FFmpeg installed at: {path}")
    elif "--download-assets" in sys.argv:
        print("Starting FFmpeg download to assets/bin...")

        def _print_progress(pct: int, msg: str) -> None:
            print(f"[{pct}%] {msg}")

        target = get_assets_dir() / "bin"
        path = svc.download_ffmpeg(target_dir=target, progress_callback=_print_progress)
        print(f"\nSuccess! FFmpeg installed at: {path}")
    else:
        avail, status = svc.get_status_info()
        print("Available:", avail)
        print("Status:", status)
