"""Progress bar widget with metrics (percentage, speed, size, ETA)."""

import customtkinter as ctk

from app.ui.theme import (
    ACCENT_PRIMARY,
    BG_TERTIARY,
    FONT_CAPTION,
    TEXT_MUTED,
    TEXT_SECONDARY,
)


class CustomProgressBar(ctk.CTkFrame):
    """Encapsulates a styled progress bar with live speed, ETA, and size metrics."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            fg_color=BG_TERTIARY,
            progress_color=ACCENT_PRIMARY,
            height=8,
            corner_radius=4,
        )
        self.progress_bar.pack(fill="x", pady=(2, 6))
        self.progress_bar.set(0.0)

        # Metrics row
        self.metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_frame.pack(fill="x")

        self.left_label = ctk.CTkLabel(
            self.metrics_frame,
            text="0% • -- KB/s",
            font=FONT_CAPTION,
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.left_label.pack(side="left")

        self.right_label = ctk.CTkLabel(
            self.metrics_frame,
            text="-- / -- • ETA --:--",
            font=FONT_CAPTION,
            text_color=TEXT_MUTED,
            anchor="e",
        )
        self.right_label.pack(side="right")

    def update_progress(
        self,
        percentage: float,
        speed_str: str = "-- KB/s",
        size_str: str = "--",
        eta_str: str = "--:--",
    ) -> None:
        """Update progress bar fill and text metrics."""
        val = min(1.0, max(0.0, percentage / 100.0))
        self.progress_bar.set(val)
        self.left_label.configure(text=f"{int(percentage)}% • {speed_str}")
        self.right_label.configure(text=f"{size_str} • ETA {eta_str}")

    def set_indeterminate(self, active: bool = True) -> None:
        """Start or stop indeterminate animation (e.g. while processing)."""
        if active:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
            self.left_label.configure(text="Processing media...")
            self.right_label.configure(text="")
        else:
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
