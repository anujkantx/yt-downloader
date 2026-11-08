"""Navigation sidebar for switching between application views."""

from collections.abc import Callable

import customtkinter as ctk
from PIL import Image

from app.ui.theme import (
    ACCENT_HOVER,
    ACCENT_PRIMARY,
    BG_SECONDARY,
    BG_TERTIARY,
    BORDER_COLOR,
    COLOR_SUCCESS,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_CAPTION,
    FONT_HEADING,
    FONT_SMALL,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from app.utils.paths import get_assets_dir


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
            width=220,
            fg_color=BG_SECONDARY,
            corner_radius=0,
            border_width=1,
            border_color=BORDER_COLOR,
            **kwargs,
        )
        self.on_navigate = on_navigate
        self._current_page = current_page
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._logo_image: ctk.CTkImage | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_propagate(False)

        # Branding top
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(22, 20))

        # Modern Emblem using official logo
        logo_path = get_assets_dir() / "icons" / "logo.png"
        if logo_path.exists():
            try:
                pil_logo = Image.open(logo_path)
                self._logo_image = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(38, 38))
            except Exception:
                pass

        if self._logo_image:
            emblem = ctk.CTkLabel(
                brand_frame,
                text="",
                image=self._logo_image,
                width=38,
                height=38,
            )
        else:
            emblem = ctk.CTkLabel(
                brand_frame,
                text="A",
                width=38,
                height=38,
                corner_radius=10,
                fg_color=ACCENT_PRIMARY,
                text_color="#FFFFFF",
                font=("Segoe UI", 16, "bold"),
            )
        emblem.pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_box.pack(side="left", fill="both", expand=True)

        brand_text = ctk.CTkLabel(
            title_box,
            text="yt-downloader",
            font=FONT_HEADING,
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        brand_text.pack(fill="x")

        badge_text = ctk.CTkLabel(
            title_box,
            text="OPEN SOURCE • v1.0",
            font=FONT_SMALL,
            text_color=TEXT_MUTED,
            anchor="w",
        )
        badge_text.pack(fill="x")

        # Subtle separator
        sep = ctk.CTkFrame(self, height=1, fg_color=BORDER_COLOR)
        sep.pack(fill="x", padx=16, pady=(0, 16))

        # Nav items without emojis
        nav_items = [
            ("downloads", "Downloads"),
            ("history", "History"),
            ("settings", "Settings"),
            ("about", "About"),
        ]

        for page_id, label in nav_items:
            btn = ctk.CTkButton(
                self,
                text=label,
                font=FONT_BODY_BOLD if page_id == self._current_page else FONT_BODY,
                height=42,
                corner_radius=10,
                anchor="w",
                fg_color=ACCENT_PRIMARY if page_id == self._current_page else "transparent",
                hover_color=ACCENT_HOVER if page_id == self._current_page else BG_TERTIARY,
                text_color="#FFFFFF" if page_id == self._current_page else TEXT_PRIMARY,
                command=lambda pid=page_id: self._handle_click(pid),
            )
            btn.pack(fill="x", padx=12, pady=3)
            self._buttons[page_id] = btn

        # Bottom status card
        bottom_card = ctk.CTkFrame(
            self,
            fg_color=BG_TERTIARY,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        bottom_card.pack(side="bottom", fill="x", padx=12, pady=16)

        status_row = ctk.CTkFrame(bottom_card, fg_color="transparent")
        status_row.pack(fill="x", padx=12, pady=10)

        dot_label = ctk.CTkLabel(
            status_row,
            text="●",
            font=("Segoe UI", 12),
            text_color=COLOR_SUCCESS,
        )
        dot_label.pack(side="left", padx=(0, 6))

        engine_label = ctk.CTkLabel(
            status_row,
            text="Engine Active",
            font=FONT_CAPTION,
            text_color=TEXT_SECONDARY,
        )
        engine_label.pack(side="left")

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
