"""Downloads view handling URL entry, metadata preview, options, and live tasks."""

import threading
from tkinter import filedialog

import customtkinter as ctk

from app.core.download_events import DownloadEvent, EventType
from app.core.download_models import VideoMetadata
from app.services.download_service import DownloadService
from app.ui.components.quality_selector import QualityFormatSelector
from app.ui.components.url_input import URLInputComponent
from app.ui.download_card import DownloadCard
from app.ui.theme import (
    ACCENT_HOVER,
    ACCENT_PRIMARY,
    BG_PRIMARY,
    BG_SECONDARY,
    BG_TERTIARY,
    BORDER_COLOR,
    COLOR_DANGER,
    COLOR_INFO,
    COLOR_SUCCESS,
    COLOR_WARNING,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_CAPTION,
    FONT_HEADING,
    FONT_SUBHEADING,
    FONT_TITLE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from app.utils.logging_config import get_logger

logger = get_logger("downloads_page")


class DownloadsPage(ctk.CTkFrame):
    """Main view for creating downloads and monitoring active/recent download tasks."""

    def __init__(self, master, download_service: DownloadService, **kwargs):
        super().__init__(master, fg_color=BG_PRIMARY, **kwargs)
        self.service = download_service
        self._cards: dict[str, DownloadCard] = {}
        self._cached_metadata: dict[str, VideoMetadata] = {}
        self._download_dir = self.service.settings_manager.current.download_dir

        self._build_ui()
        self._subscribe_events()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Top section: Input Form (non-scrolling or clean pinned area)
        top_container = ctk.CTkFrame(self, fg_color="transparent")
        top_container.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))

        # Title
        title_label = ctk.CTkLabel(
            top_container,
            text="Video Downloader",
            font=FONT_TITLE,
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        title_label.pack(fill="x", pady=(0, 12))

        # 1. URL Input Component
        self.url_component = URLInputComponent(
            top_container,
            on_urls_changed=self._on_urls_changed,
            on_fetch_preview=self._fetch_preview,
        )
        self.url_component.pack(fill="x", pady=(0, 10))

        # Metadata Preview Frame (collapsed by default)
        self.preview_frame = ctk.CTkFrame(
            top_container,
            fg_color=BG_SECONDARY,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        self._build_preview_ui()

        # 2. Quality and Format Selector
        current_settings = self.service.settings_manager.current
        self.selector = QualityFormatSelector(
            top_container,
            default_quality=current_settings.default_quality,
            default_format=current_settings.default_format,
        )
        self.selector.pack(fill="x", pady=(0, 10))

        # FFmpeg warning and 1-click install banner (shown if FFmpeg is not found)
        self.ffmpeg_banner = ctk.CTkFrame(
            top_container,
            fg_color=BG_SECONDARY,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        self.ffmpeg_banner_inner = ctk.CTkFrame(self.ffmpeg_banner, fg_color="transparent")
        self.ffmpeg_banner_inner.pack(fill="x", padx=12, pady=8)

        self.ffmpeg_banner_label = ctk.CTkLabel(
            self.ffmpeg_banner_inner,
            text="💡 FFmpeg is missing: 1080p+, 4K streams & MP3 conversion require FFmpeg.",
            font=FONT_CAPTION,
            text_color=COLOR_WARNING,
            anchor="w",
        )
        self.ffmpeg_banner_label.pack(side="left", fill="x", expand=True)

        self.ffmpeg_banner_btn = ctk.CTkButton(
            self.ffmpeg_banner_inner,
            text="⚡ 1-Click Install",
            width=120,
            height=28,
            font=FONT_CAPTION,
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            command=self._start_inline_ffmpeg_download,
        )
        self.ffmpeg_banner_btn.pack(side="right", padx=(8, 0))

        if not self.service.ffmpeg_service.is_available():
            self.ffmpeg_banner.pack(fill="x", pady=(0, 10))

        # 3. Download Location and Download Button Row
        bottom_bar = ctk.CTkFrame(
            top_container,
            fg_color=BG_SECONDARY,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        bottom_bar.pack(fill="x", pady=(0, 6))

        loc_frame = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        loc_frame.pack(side="left", fill="x", expand=True, padx=16, pady=12)

        ctk.CTkLabel(
            loc_frame,
            text="Save to Directory:",
            font=FONT_CAPTION,
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).pack(fill="x")

        loc_action_row = ctk.CTkFrame(loc_frame, fg_color="transparent")
        loc_action_row.pack(fill="x", pady=(2, 0))

        self.dir_label = ctk.CTkLabel(
            loc_action_row,
            text=str(self._download_dir),
            font=FONT_BODY,
            text_color=TEXT_PRIMARY,
            anchor="w",
            wraplength=380,
        )
        self.dir_label.pack(side="left", fill="x", expand=True)

        browse_btn = ctk.CTkButton(
            loc_action_row,
            text="📁 Browse",
            font=FONT_CAPTION,
            width=75,
            height=28,
            fg_color=BG_TERTIARY,
            hover_color=ACCENT_PRIMARY,
            command=self._browse_directory,
        )
        browse_btn.pack(side="left", padx=(6, 4))

        open_dir_btn = ctk.CTkButton(
            loc_action_row,
            text="↗ Open",
            font=FONT_CAPTION,
            width=65,
            height=28,
            fg_color=BG_TERTIARY,
            hover_color=ACCENT_PRIMARY,
            command=lambda: self.service.open_containing_folder(self._download_dir),
        )
        open_dir_btn.pack(side="left")

        # Download Button
        self.download_btn = ctk.CTkButton(
            bottom_bar,
            text="🚀 Start Download",
            font=FONT_SUBHEADING,
            width=175,
            height=44,
            corner_radius=10,
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            command=self._start_download,
            state="disabled",
        )
        self.download_btn.pack(side="right", padx=16, pady=12)

        # Bottom section: Active & Recent Tasks
        tasks_section = ctk.CTkFrame(self, fg_color="transparent")
        tasks_section.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 16))
        tasks_section.rowconfigure(1, weight=1)
        tasks_section.columnconfigure(0, weight=1)

        tasks_header = ctk.CTkFrame(tasks_section, fg_color="transparent")
        tasks_header.grid(row=0, column=0, sticky="ew", pady=(4, 8))

        self.tasks_title = ctk.CTkLabel(
            tasks_header,
            text="Active Downloads",
            font=FONT_HEADING,
            text_color=TEXT_PRIMARY,
        )
        self.tasks_title.pack(side="left")

        self.clear_finished_btn = ctk.CTkButton(
            tasks_header,
            text="Clear Finished",
            font=FONT_CAPTION,
            width=90,
            height=26,
            fg_color="transparent",
            hover_color=BG_TERTIARY,
            text_color=TEXT_MUTED,
            command=self._clear_finished_tasks,
        )
        self.clear_finished_btn.pack(side="right")

        # Scrollable area for cards
        self.scroll_frame = ctk.CTkScrollableFrame(
            tasks_section,
            fg_color="transparent",
            corner_radius=0,
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.columnconfigure(0, weight=1)

        # Empty State
        self.empty_state_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.empty_state_frame.pack(fill="both", expand=True, pady=40)

        empty_icon = ctk.CTkLabel(
            self.empty_state_frame,
            text="📥",
            font=("Segoe UI", 48),
            text_color=TEXT_MUTED,
        )
        empty_icon.pack()

        empty_text = ctk.CTkLabel(
            self.empty_state_frame,
            text="No active downloads",
            font=FONT_SUBHEADING,
            text_color=TEXT_MUTED,
        )
        empty_text.pack(pady=(8, 2))

        empty_sub = ctk.CTkLabel(
            self.empty_state_frame,
            text="Paste a video URL above and click Start Download.",
            font=FONT_CAPTION,
            text_color=TEXT_MUTED,
        )
        empty_sub.pack()

    def _build_preview_ui(self) -> None:
        """Create metadata preview layout."""
        self.preview_frame.columnconfigure(1, weight=1)

        self.preview_thumb = ctk.CTkLabel(
            self.preview_frame,
            text="🎬",
            width=100,
            height=65,
            corner_radius=8,
            fg_color=BG_TERTIARY,
            font=("Segoe UI", 24),
        )
        self.preview_thumb.grid(row=0, column=0, padx=12, pady=10)

        info_box = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        info_box.grid(row=0, column=1, sticky="w", padx=(0, 12), pady=10)

        self.preview_title = ctk.CTkLabel(
            info_box,
            text="",
            font=FONT_BODY_BOLD,
            text_color=TEXT_PRIMARY,
            anchor="w",
            wraplength=460,
        )
        self.preview_title.pack(fill="x")

        self.preview_details = ctk.CTkLabel(
            info_box,
            text="",
            font=FONT_CAPTION,
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.preview_details.pack(fill="x", pady=(2, 0))

    def _subscribe_events(self) -> None:
        self.service.event_bus.subscribe(EventType.TASK_ADDED, self._on_task_added)
        self.service.event_bus.subscribe(EventType.STATUS_CHANGED, self._on_task_updated)
        self.service.event_bus.subscribe(EventType.PROGRESS_UPDATED, self._on_progress_updated)
        self.service.event_bus.subscribe(EventType.TASK_COMPLETED, self._on_task_updated)
        self.service.event_bus.subscribe(EventType.TASK_FAILED, self._on_task_updated)
        self.service.event_bus.subscribe(EventType.TASK_CANCELLED, self._on_task_updated)
        self.service.event_bus.subscribe(EventType.QUEUE_UPDATED, self._on_queue_updated)

    def _on_urls_changed(self, urls: list[str]) -> None:
        if urls:
            self.download_btn.configure(
                state="normal",
                text=f"⬇ Download ({len(urls)})" if len(urls) > 1 else "⬇ Start Download",
            )
        else:
            self.download_btn.configure(state="disabled", text="⬇ Start Download")
            self.preview_frame.pack_forget()

    def _fetch_preview(self, url: str) -> None:
        """Initiate asynchronous metadata inspection."""
        self.url_component.status_label.configure(
            text="Fetching video metadata...", text_color=COLOR_INFO
        )

        def on_success(meta: VideoMetadata):
            # Must update on Tkinter main thread
            self.after(0, lambda: self._show_preview(url, meta))

        def on_error(err_msg: str):
            self.after(
                0,
                lambda: self.url_component.status_label.configure(
                    text=f"Metadata notice: {err_msg[:60]}", text_color=COLOR_DANGER
                ),
            )

        self.service.fetch_metadata(url, on_success, on_error)

    def _show_preview(self, url: str, meta: VideoMetadata) -> None:
        self._cached_metadata[url] = meta
        self.preview_title.configure(text=meta.title)
        self.preview_details.configure(
            text=f"Channel: {meta.uploader} • Duration: {meta.duration_str}"
        )
        self.selector.set_available_resolutions(meta.available_resolutions)

        # Show preview frame right below url input
        self.preview_frame.pack(fill="x", pady=(0, 10), after=self.url_component)
        self.url_component.status_label.configure(
            text=f"✓ Video ready: {meta.title[:45]}...", text_color=COLOR_SUCCESS
        )

    def _browse_directory(self) -> None:
        selected = filedialog.askdirectory(
            title="Select Download Directory",
            initialdir=self._download_dir,
        )
        if selected:
            self._download_dir = selected
            self.dir_label.configure(text=selected)
            # Update settings persistence
            self.service.settings_manager.update(download_dir=selected)

    def _start_download(self) -> None:
        urls = self.url_component.get_urls()
        if not urls:
            return

        quality, fmt = self.selector.get_selection()
        # Enqueue via service
        self.service.enqueue_downloads(
            urls=urls,
            quality=quality,
            format_choice=fmt,
            output_dir=self._download_dir,
            metadata_map=self._cached_metadata,
        )

        # Clear input field and preview after submission
        self.url_component.clear_text()
        self.preview_frame.pack_forget()

    # Event Handlers for Task Lifecycle
    def _on_task_added(self, event: DownloadEvent) -> None:
        if not event.task:
            return
        self.empty_state_frame.pack_forget()

        # Create new Card
        card = DownloadCard(
            self.scroll_frame,
            task=event.task,
            on_cancel=self.service.cancel_task,
            on_retry=self.service.retry_task,
            on_remove=self._remove_card,
            on_open_file=self.service.open_file,
            on_open_folder=self.service.open_containing_folder,
        )
        card.pack(fill="x", pady=6)
        self._cards[event.task_id] = card
        self._update_tasks_title()

    def _on_task_updated(self, event: DownloadEvent) -> None:
        card = self._cards.get(event.task_id)
        if card and event.task:
            card.update_task_state(event.task)
        self._update_tasks_title()

    def _on_progress_updated(self, event: DownloadEvent) -> None:
        card = self._cards.get(event.task_id)
        if card and event.progress:
            card.update_progress(event.progress)

    def _on_queue_updated(self, event: DownloadEvent) -> None:
        # Check if tasks were removed
        current_manager_tasks = {t.task_id for t in self.service.download_manager.get_all_tasks()}
        removed_ids = [tid for tid in self._cards if tid not in current_manager_tasks]
        for tid in removed_ids:
            card = self._cards.pop(tid, None)
            if card:
                card.destroy()

        if not self._cards:
            self.empty_state_frame.pack(fill="both", expand=True, pady=40)
        self._update_tasks_title()

    def _remove_card(self, task_id: str) -> None:
        self.service.remove_task(task_id)
        card = self._cards.pop(task_id, None)
        if card:
            card.destroy()
        if not self._cards:
            self.empty_state_frame.pack(fill="both", expand=True, pady=40)
        self._update_tasks_title()

    def _clear_finished_tasks(self) -> None:
        self.service.clear_completed_tasks()

    def _update_tasks_title(self) -> None:
        count = len(self._cards)
        active_count = self.service.download_manager.get_active_count()
        if count == 0:
            self.tasks_title.configure(text="Active Downloads")
        elif active_count > 0:
            self.tasks_title.configure(text=f"Active Downloads ({active_count} running)")
        else:
            self.tasks_title.configure(text=f"Downloads ({count})")

    def _start_inline_ffmpeg_download(self) -> None:
        """Start background FFmpeg download directly from the main view."""
        self.ffmpeg_banner_btn.configure(state="disabled", text="Installing...")
        self.ffmpeg_banner_label.configure(
            text="Downloading and setting up FFmpeg in the background...",
            text_color=TEXT_PRIMARY,
        )

        def _worker():
            def _progress(pct: int, msg: str) -> None:
                self.after(0, lambda: self.ffmpeg_banner_label.configure(text=f"FFmpeg: {msg}"))

            try:
                path = self.service.ffmpeg_service.download_ffmpeg(progress_callback=_progress)
                self.service.settings_manager.current.ffmpeg_path = path
                self.service.settings_manager.save(self.service.settings_manager.current)
                self.service.ffmpeg_service.set_configured_path(path)
                self.after(0, self._on_inline_ffmpeg_success)
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda msg=err_msg: self._on_inline_ffmpeg_error(msg))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_inline_ffmpeg_success(self) -> None:
        self.ffmpeg_banner_label.configure(
            text="✓ FFmpeg installed successfully! 1080p+ and MP3 audio conversion are now active.",
            text_color=COLOR_SUCCESS,
        )
        self.ffmpeg_banner_btn.pack_forget()
        self.after(3500, self.ffmpeg_banner.pack_forget)

    def _on_inline_ffmpeg_error(self, err_msg: str) -> None:
        self.ffmpeg_banner_label.configure(
            text=f"FFmpeg download failed: {err_msg}",
            text_color=COLOR_DANGER,
        )
        self.ffmpeg_banner_btn.configure(state="normal", text="⚡ Retry Install")
