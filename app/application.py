"""Application bootstrap and top-level lifecycle controller."""

import logging

from app.config.settings import SettingsManager
from app.database.database import Database
from app.services.download_service import DownloadService
from app.ui.main_window import MainWindow
from app.utils.logging_config import get_logger, setup_logging
from app.utils.paths import ensure_app_dirs

logger = get_logger("application")


class VideoDownloaderApp:
    """Coordinates lifecycle, configuration, database, and GUI mainloop."""

    def __init__(self):
        # 1. Initialize core directories and rotating logs
        ensure_app_dirs()
        setup_logging(level=logging.INFO)
        logger.info("Starting Video Downloader Application...")

        # 2. Initialize configuration & database
        self.settings_manager = SettingsManager()
        self.database = Database()

        # 3. Initialize application service layer
        self.download_service = DownloadService(
            settings_manager=self.settings_manager,
            database=self.database,
        )

        # 4. Initialize UI
        self.main_window = MainWindow(download_service=self.download_service)

    def run(self) -> None:
        """Start the graphical application event loop."""
        try:
            self.main_window.mainloop()
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received. Exiting...")
            self.main_window._force_shutdown()
        except Exception as e:
            logger.critical("Fatal application error: %s", e, exc_info=True)
            raise


def create_app() -> VideoDownloaderApp:
    """Factory function for application instance."""
    return VideoDownloaderApp()
