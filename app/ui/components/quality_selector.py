"""Quality and format selector component."""

from collections.abc import Callable

import customtkinter as ctk

from app.config.defaults import AVAILABLE_FORMATS, AVAILABLE_QUALITIES
from app.ui.theme import (
    ACCENT_PRIMARY,
    BG_SECONDARY,
    BG_TERTIARY,
    BORDER_COLOR,
    FONT_BODY,
    FONT_CAPTION,
    FONT_SUBHEADING,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

QUALITY_DISPLAY_MAP = {
    "best": "Best Available",
    "2160p": "2160p (4K UHD)",
    "1440p": "1440p (2K QHD)",
    "1080p": "1080p (Full HD)",
    "720p": "720p (HD)",
    "480p": "480p (SD)",
    "360p": "360p (Low)",
    "audio": "Audio Only",
}

FORMAT_DISPLAY_MAP = {
    "mp4": "MP4 (Video)",
    "mkv": "MKV (Video)",
    "mp3": "MP3 (Audio)",
    "m4a": "M4A (Audio)",
    "best": "Original / Best",
}


class QualityFormatSelector(ctk.CTkFrame):
    """Component for selecting download resolution and output container format."""

    def __init__(
        self,
        master,
        default_quality: str = "1080p",
        default_format: str = "mp4",
        on_change: Callable[[str, str], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=BG_SECONDARY, corner_radius=12, border_width=1, border_color=BORDER_COLOR, **kwargs)
        self.on_change = on_change

        self._quality_val = default_quality
        self._format_val = default_format

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(12, 8))

        title = ctk.CTkLabel(
            header_frame,
            text="Download Options",
            font=FONT_SUBHEADING,
            text_color=TEXT_PRIMARY,
        )
        title.pack(side="left")

        # Selectors grid
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(fill="x", padx=16, pady=(0, 12))
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)

        # Quality column
        q_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        q_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(
            q_frame,
            text="Video Quality / Max Resolution",
            font=FONT_CAPTION,
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        quality_options = [QUALITY_DISPLAY_MAP.get(q, q) for q in AVAILABLE_QUALITIES]
        initial_q_display = QUALITY_DISPLAY_MAP.get(default_quality, "1080p (Full HD)")

        self.quality_menu = ctk.CTkOptionMenu(
            q_frame,
            values=quality_options,
            command=self._on_quality_selected,
            font=FONT_BODY,
            fg_color=BG_TERTIARY,
            button_color=ACCENT_PRIMARY,
            text_color=TEXT_PRIMARY,
        )
        self.quality_menu.set(initial_q_display)
        self.quality_menu.pack(fill="x")

        # Format column
        f_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        f_frame.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ctk.CTkLabel(
            f_frame,
            text="Output Container Format",
            font=FONT_CAPTION,
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        format_options = [FORMAT_DISPLAY_MAP.get(f, f) for f in AVAILABLE_FORMATS]
        initial_f_display = FORMAT_DISPLAY_MAP.get(default_format, "MP4 (Video)")

        self.format_menu = ctk.CTkOptionMenu(
            f_frame,
            values=format_options,
            command=self._on_format_selected,
            font=FONT_BODY,
            fg_color=BG_TERTIARY,
            button_color=ACCENT_PRIMARY,
            text_color=TEXT_PRIMARY,
        )
        self.format_menu.set(initial_f_display)
        self.format_menu.pack(fill="x")

        # Helper info notice
        self.note_label = ctk.CTkLabel(
            self,
            text="Note: Resolutions above 720p or audio conversions require FFmpeg to merge/transcode streams.",
            font=FONT_CAPTION,
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.note_label.pack(fill="x", padx=16, pady=(0, 10))

    def _on_quality_selected(self, choice: str) -> None:
        # Map display name back to key
        for key, disp in QUALITY_DISPLAY_MAP.items():
            if disp == choice:
                self._quality_val = key
                break

        # If audio only selected, auto-select audio format if current is video
        if self._quality_val == "audio" and self._format_val in ("mp4", "mkv"):
            self._format_val = "mp3"
            self.format_menu.set(FORMAT_DISPLAY_MAP["mp3"])

        self._trigger_change()

    def _on_format_selected(self, choice: str) -> None:
        for key, disp in FORMAT_DISPLAY_MAP.items():
            if disp == choice:
                self._format_val = key
                break

        # If MP3 or M4A selected, auto-select audio quality
        if self._format_val in ("mp3", "m4a"):
            self._quality_val = "audio"
            self.quality_menu.set(QUALITY_DISPLAY_MAP["audio"])

        self._trigger_change()

    def _trigger_change(self) -> None:
        if self.on_change:
            self.on_change(self._quality_val, self._format_val)

    def get_selection(self) -> tuple[str, str]:
        """Return (quality_key, format_key)."""
        return self._quality_val, self._format_val

    def set_available_resolutions(self, resolutions: list[str]) -> None:
        """Update notice with source's highest detected resolution."""
        if resolutions:
            highest = resolutions[0]
            self.note_label.configure(
                text=f"Source stream max detected resolution: {highest}. Selected quality caps at maximum available."
            )
        else:
            self.note_label.configure(
                text="Note: Resolutions above 720p or audio conversions require FFmpeg to merge/transcode streams."
            )
