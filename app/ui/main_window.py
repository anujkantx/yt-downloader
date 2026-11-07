"""Main application window, layout container, event dispatcher, and lifecycle manager."""

import customtkinter as ctk

from app.services.download_service import DownloadService
from app.ui.about_page import AboutPage
from app.ui.components.dialogs import ConfirmDialog
from app.ui.downloads_page import DownloadsPage
from app.ui.history_page import HistoryPage
from app.ui.settings_page import SettingsPage
from app.ui.sidebar import Sidebar
from app.ui.theme import BG_PRIMARY
from app.utils.logging_config import get_logger
from app.utils.paths import get_assets_dir

logger = get_logger("main_window")


class MainWindow(ctk.CTk):
    """Primary application window handling view routing, event polling, and shutdown."""

    def __init__(self, download_service: DownloadService):
        super().__init__()
        self.service = download_service
        self.settings = self.service.settings_manager.current

        # Window configuration
        self.title("Video Downloader")
        self.geometry("1060x720")
        self.minsize(920, 600)
        self.configure(fg_color=BG_PRIMARY)

        # Apply saved theme mode
        ctk.set_appearance_mode(self.settings.theme)
        ctk.set_default_color_theme("blue")

        # Set window icon
        self._set_window_icon()

        # Build primary container layout
        self._build_layout()

        # Handle window close protocol
        self.protocol("WM_DELETE_WINDOW", self.on_close_requested)

        # Start periodic event pump for thread-safe UI updates
        self._is_running = True
        self.after(50, self._poll_events)

    def _set_window_icon(self) -> None:
        """Load and set application window and taskbar icon."""
        try:
            ico_path = get_assets_dir() / "icons" / "app_icon.ico"
            if ico_path.exists():
                self.iconbitmap(str(ico_path))
        except Exception as e:
            logger.debug("Could not set window icon: %s", e)

    def _build_layout(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Left Sidebar
        self.sidebar = Sidebar(self, on_navigate=self.show_page, current_page="downloads")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Right Content View Area
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.columnconfigure(0, weight=1)
        self.content_area.rowconfigure(0, weight=1)

        # Instantiate View Pages
        self.pages: dict[str, ctk.CTkFrame] = {
            "downloads": DownloadsPage(self.content_area, self.service),
            "history": HistoryPage(self.content_area, self.service),
            "settings": SettingsPage(self.content_area, self.service),
            "about": AboutPage(self.content_area, self.service),
        }

        # Show initial page
        self.show_page("downloads")

    def show_page(self, page_id: str) -> None:
        """Switch active page in the content area."""
        target_page = self.pages.get(page_id)
        if not target_page:
            return

        # Hide all pages
        for page in self.pages.values():
            page.grid_forget()

        # Show target page
        target_page.grid(row=0, column=0, sticky="nsew")

        # If switching to history, trigger data refresh
        if page_id == "history" and isinstance(target_page, HistoryPage):
            target_page.refresh_history()

    def _poll_events(self) -> None:
        """Periodic event loop processing queued events from background worker threads."""
        if not self._is_running:
            return

        try:
            self.service.event_bus.process_pending_events(max_events=40)
        except Exception as e:
            logger.error("Error during event dispatch: %s", e)

        # Schedule next iteration
        self.after(50, self._poll_events)

    def on_close_requested(self) -> None:
        """Handle application close safely with active download confirmation."""
        active_count = self.service.download_manager.get_active_count()

        if active_count > 0:
            msg = (
                f"There {'is' if active_count == 1 else 'are'} {active_count} active "
                f"download{' task' if active_count == 1 else ' tasks'} in progress.\n\n"
                "Closing the application will cancel ongoing downloads. Are you sure you want to exit?"
            )
            ConfirmDialog(
                self,
                title="Active Downloads in Progress",
                message=msg,
                on_confirm=self._force_shutdown,
                confirm_label="Exit Application",
                is_destructive=True,
            )
        else:
            self._force_shutdown()

    def _force_shutdown(self) -> None:
        """Execute graceful shutdown sequence and destroy window."""
        logger.info("Application shutdown initiated...")
        self._is_running = False

        try:
            self.service.shutdown(wait=False)
        except Exception as e:
            logger.error("Error shutting down services: %s", e)

        try:
            self.destroy()
        except Exception:
            pass
        logger.info("Application closed.")
