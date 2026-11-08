"""About and system information view."""

import sys

import customtkinter as ctk
import yt_dlp
from PIL import Image

from app.services.download_service import DownloadService
from app.ui.theme import (
    ACCENT_PRIMARY,
    BG_PRIMARY,
    BG_SECONDARY,
    BORDER_COLOR,
    FONT_BODY,
    FONT_CAPTION,
    FONT_SUBHEADING,
    FONT_TITLE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from app.utils.paths import get_assets_dir


class AboutPage(ctk.CTkFrame):
    """View displaying application version, technical environment, and legal notices."""

    def __init__(self, master, download_service: DownloadService, **kwargs):
        super().__init__(master, fg_color=BG_PRIMARY, **kwargs)
        self.service = download_service
        self._build_ui()

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(
            self,
            fg_color=BG_SECONDARY,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        container.pack(fill="both", expand=True, padx=40, pady=30)

        # Header branding
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))

        logo_path = get_assets_dir() / "icons" / "logo.png"
        self._about_logo = None
        if logo_path.exists():
            try:
                pil_logo = Image.open(logo_path)
                self._about_logo = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(54, 54))
            except Exception:
                pass

        if self._about_logo:
            logo = ctk.CTkLabel(
                header,
                text="",
                image=self._about_logo,
                width=54,
                height=54,
            )
        else:
            logo = ctk.CTkLabel(
                header,
                text="A",
                font=("Segoe UI", 32, "bold"),
                text_color=ACCENT_PRIMARY,
            )
        logo.pack(side="left", padx=(0, 16))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="Video Downloader Desktop",
            font=FONT_TITLE,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Version 1.0.0 • High-Performance Media Downloader for Windows",
            font=FONT_CAPTION,
            text_color=TEXT_MUTED,
        ).pack(anchor="w")

        # Technical environment card
        env_card = ctk.CTkFrame(container, fg_color=BG_PRIMARY, corner_radius=10)
        env_card.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkLabel(
            env_card,
            text="Technical Environment",
            font=FONT_SUBHEADING,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(12, 6))

        is_avail, ffmpeg_info = self.service.ffmpeg_service.get_status_info()
        ffmpeg_line = ffmpeg_info[:80] + "..." if len(ffmpeg_info) > 80 else ffmpeg_info

        env_details = [
            f"• Core Engine: yt-dlp {yt_dlp.version.__version__}",
            f"• Python Runtime: {sys.version.split()[0]}",
            f"• FFmpeg Integration: {ffmpeg_line}",
            "• Database Engine: SQLite 3",
            "• Graphical Framework: CustomTkinter 6.0",
        ]

        for detail in env_details:
            ctk.CTkLabel(
                env_card,
                text=detail,
                font=FONT_BODY,
                text_color=TEXT_SECONDARY,
            ).pack(anchor="w", padx=16, pady=2)

        ctk.CTkFrame(env_card, height=8, fg_color="transparent").pack()

        # Responsible usage statement
        legal_card = ctk.CTkFrame(container, fg_color=BG_PRIMARY, corner_radius=10)
        legal_card.pack(fill="both", expand=True, padx=30, pady=(0, 24))

        ctk.CTkLabel(
            legal_card,
            text="Legal & Responsible Usage",
            font=FONT_SUBHEADING,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(12, 6))

        legal_text = (
            "This application is designed for personal archival, educational, and content creation workflows. "
            "Please respect copyright laws, intellectual property rights, and platform terms of service. "
            "This software does not bypass digital rights management (DRM) or access unauthorized restricted streams."
        )

        ctk.CTkLabel(
            legal_card,
            text=legal_text,
            font=FONT_BODY,
            text_color=TEXT_MUTED,
            wraplength=650,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 12))
