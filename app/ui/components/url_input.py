"""URL input component with multi-line support, validation, and paste/clear actions."""

from collections.abc import Callable

import customtkinter as ctk

from app.ui.theme import (
    ACCENT_HOVER,
    ACCENT_PRIMARY,
    BG_SECONDARY,
    BG_TERTIARY,
    BORDER_COLOR,
    COLOR_DANGER,
    COLOR_SUCCESS,
    FONT_BODY,
    FONT_CAPTION,
    FONT_SUBHEADING,
    TEXT_MUTED,
    TEXT_PRIMARY,
)
from app.utils.validators import extract_urls


class URLInputComponent(ctk.CTkFrame):
    """Component for pasting and validating one or more video URLs."""

    def __init__(
        self,
        master,
        on_urls_changed: Callable[[list[str]], None] | None = None,
        on_fetch_preview: Callable[[str], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=BG_SECONDARY, corner_radius=12, border_width=1, border_color=BORDER_COLOR, **kwargs)
        self.on_urls_changed = on_urls_changed
        self.on_fetch_preview = on_fetch_preview
        self._last_single_preview_url: str | None = None

        # Header row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 6))

        title = ctk.CTkLabel(
            header,
            text="Video URLs",
            font=FONT_SUBHEADING,
            text_color=TEXT_PRIMARY,
        )
        title.pack(side="left")

        actions_frame = ctk.CTkFrame(header, fg_color="transparent")
        actions_frame.pack(side="right")

        paste_btn = ctk.CTkButton(
            actions_frame,
            text="Paste",
            width=65,
            height=28,
            font=FONT_CAPTION,
            fg_color=BG_TERTIARY,
            hover_color=ACCENT_PRIMARY,
            text_color=TEXT_PRIMARY,
            command=self.paste_from_clipboard,
        )
        paste_btn.pack(side="left", padx=(0, 6))

        clear_btn = ctk.CTkButton(
            actions_frame,
            text="Clear",
            width=60,
            height=28,
            font=FONT_CAPTION,
            fg_color=BG_TERTIARY,
            hover_color=COLOR_DANGER,
            text_color=TEXT_PRIMARY,
            command=self.clear_text,
        )
        clear_btn.pack(side="left")

        # Multi-line text box for URLs
        self.text_box = ctk.CTkTextbox(
            self,
            height=75,
            corner_radius=8,
            border_width=1,
            border_color=BORDER_COLOR,
            fg_color=BG_TERTIARY,
            text_color=TEXT_PRIMARY,
            font=FONT_BODY,
            wrap="word",
        )
        self.text_box.pack(fill="x", padx=16, pady=(0, 6))
        self.text_box.bind("<KeyRelease>", self._on_text_change)

        # Status / Feedback row
        feedback_frame = ctk.CTkFrame(self, fg_color="transparent")
        feedback_frame.pack(fill="x", padx=16, pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            feedback_frame,
            text="Enter one or more video URLs (one per line)",
            font=FONT_CAPTION,
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.status_label.pack(side="left", fill="x", expand=True)

        self.preview_btn = ctk.CTkButton(
            feedback_frame,
            text="Fetch Info",
            width=85,
            height=26,
            font=FONT_CAPTION,
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            command=self._trigger_preview,
            state="disabled",
        )
        self.preview_btn.pack(side="right")

    def get_urls(self) -> list[str]:
        raw_text = self.text_box.get("1.0", "end")
        return extract_urls(raw_text)

    def _on_text_change(self, event=None) -> None:
        urls = self.get_urls()
        raw = self.text_box.get("1.0", "end").strip()

        if not raw:
            self.status_label.configure(
                text="Enter one or more video URLs (one per line)",
                text_color=TEXT_MUTED,
            )
            self.preview_btn.configure(state="disabled")
            self._last_single_preview_url = None
        elif urls:
            count_str = f"{len(urls)} valid URL{'s' if len(urls) > 1 else ''} ready to download"
            self.status_label.configure(text=count_str, text_color=COLOR_SUCCESS)
            self.preview_btn.configure(state="normal" if len(urls) == 1 else "disabled")
            # Auto-preview single URL if not previewed yet
            if len(urls) == 1 and urls[0] != self._last_single_preview_url:
                self._last_single_preview_url = urls[0]
                self._trigger_preview()
        else:
            self.status_label.configure(
                text="No valid HTTP/HTTPS URLs detected",
                text_color=COLOR_DANGER,
            )
            self.preview_btn.configure(state="disabled")
            self._last_single_preview_url = None

        if self.on_urls_changed:
            self.on_urls_changed(urls)

    def paste_from_clipboard(self) -> None:
        try:
            clipboard_text = self.clipboard_get()
            if clipboard_text:
                current_text = self.text_box.get("1.0", "end").strip()
                if current_text:
                    self.text_box.insert("end", f"\n{clipboard_text}")
                else:
                    self.text_box.delete("1.0", "end")
                    self.text_box.insert("1.0", clipboard_text)
                self._on_text_change()
        except Exception:
            pass

    def clear_text(self) -> None:
        self.text_box.delete("1.0", "end")
        self._on_text_change()

    def _trigger_preview(self) -> None:
        urls = self.get_urls()
        if urls and self.on_fetch_preview:
            self.on_fetch_preview(urls[0])
