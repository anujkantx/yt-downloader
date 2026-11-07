"""Navigation sidebar for switching between application views."""

from collections.abc import Callable

import customtkinter as ctk

from app.ui.theme import (
    ACCENT_HOVER,
    ACCENT_PRIMARY,
    BG_SECONDARY,
    BG_TERTIARY,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_CAPTION,
    FONT_HEADING,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


class Sidebar(ctk.CTkFrame):
    """Left sidebar with navigation buttons, branding, and status indicators."""

    def __init__(
        self,
        master,
        on_navigate: Callable[[str], None],
        current_page: str = "downloads",
        **kwargs,
    ):
        super().__init__(
            master,
            width=210,
            fg_color=BG_SECONDARY,
            corner_radius=0,
            border_width=0,
            **kwargs,
        )
        self.on_navigate = on_navigate
        self._current_page = current_page
        self._buttons: dict[str, ctk.CTkButton] = {}

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_propagate(False)

        # Branding top
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(20, 24))

        logo_icon = ctk.CTkLabel(
            brand_frame,
            text="⚡",
            font=("Segoe UI", 22),
            text_color=ACCENT_PRIMARY,
        )
        logo_icon.pack(side="left", padx=(0, 8))

        brand_text = ctk.CTkLabel(
            brand_frame,
            text="Video\nDownloader",
            font=FONT_HEADING,
            text_color=TEXT_PRIMARY,
            justify="left",
            anchor="w",
        )
        brand_text.pack(side="left")

        # Nav items
        nav_items = [
            ("downloads", "⬇  Downloads"),
            ("history", "📜  History"),
            ("settings", "⚙  Settings"),
            ("about", "ℹ  About"),
        ]

        for page_id, label in nav_items:
            btn = ctk.CTkButton(
                self,
                text=label,
                font=FONT_BODY_BOLD if page_id == self._current_page else FONT_BODY,
                height=40,
                corner_radius=8,
                anchor="w",
                fg_color=ACCENT_PRIMARY if page_id == self._current_page else "transparent",
                hover_color=ACCENT_HOVER if page_id == self._current_page else BG_TERTIARY,
                text_color="#FFFFFF" if page_id == self._current_page else TEXT_PRIMARY,
                command=lambda pid=page_id: self._handle_click(pid),
            )
            btn.pack(fill="x", padx=12, pady=4)
            self._buttons[page_id] = btn

        # Bottom status info
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=16, pady=16)

        v_label = ctk.CTkLabel(
            bottom_frame,
            text="v1.0.0 • yt-dlp inside",
            font=FONT_CAPTION,
            text_color=TEXT_MUTED,
            anchor="w",
        )
        v_label.pack(fill="x")

    def _handle_click(self, page_id: str) -> None:
        self.set_active_page(page_id)
        self.on_navigate(page_id)

    def set_active_page(self, page_id: str) -> None:
        """Update navigation button highlighting."""
        self._current_page = page_id
        for pid, btn in self._buttons.items():
            if pid == page_id:
                btn.configure(
                    fg_color=ACCENT_PRIMARY,
                    hover_color=ACCENT_HOVER,
                    font=FONT_BODY_BOLD,
                    text_color="#FFFFFF",
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=BG_TERTIARY,
                    font=FONT_BODY,
                    text_color=TEXT_PRIMARY,
                )
