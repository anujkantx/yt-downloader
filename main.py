"""Root entry point for Video Downloader desktop application."""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def main() -> int:
    """Validate runtime environment, configure Windows DPI awareness, and run app."""
    if sys.version_info < (3, 11):
        sys.stderr.write("Error: Python 3.11 or newer is required to run Video Downloader.\n")
        return 1

    # Windows High DPI awareness
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    try:
        from app.application import create_app
        app = create_app()
        app.run()
        return 0
    except Exception as e:
        sys.stderr.write(f"Application error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
