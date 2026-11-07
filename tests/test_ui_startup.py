"""Smoke test for application and GUI startup."""

from app.application import VideoDownloaderApp


def test_application_initialization():
    """Verify that the full application, service layers, and Tkinter UI initialize cleanly."""
    app = VideoDownloaderApp()
    assert app.main_window is not None
    assert app.download_service is not None
    assert app.settings_manager is not None
    assert app.database is not None

    # Verify pages
    assert "downloads" in app.main_window.pages
    assert "history" in app.main_window.pages
    assert "settings" in app.main_window.pages
    assert "about" in app.main_window.pages

    # Shutdown cleanly
    app.main_window._force_shutdown()
