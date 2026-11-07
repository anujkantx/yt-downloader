"""Download card widget representing a single active or finished download task."""

import re
from collections.abc import Callable

import customtkinter as ctk

from app.core.download_models import DownloadProgress, DownloadTask, TaskStatus
from app.ui.components.progress_bar import CustomProgressBar
from app.ui.theme import (
    ACCENT_HOVER,
    ACCENT_PRIMARY,
    BG_SECONDARY,
    BG_TERTIARY,
    BORDER_COLOR,
    COLOR_DANGER,
    COLOR_INFO,
    COLOR_SUCCESS,
    COLOR_WARNING,
    FONT_BODY_BOLD,
    FONT_CAPTION,
    FONT_SMALL,
    TEXT_MUTED,
    TEXT_PRIMARY,
)

STATUS_COLOR_MAP = {
    TaskStatus.QUEUED: COLOR_WARNING,
    TaskStatus.FETCHING_METADATA: COLOR_INFO,
    TaskStatus.DOWNLOADING: ACCENT_PRIMARY,
    TaskStatus.PROCESSING: COLOR_INFO,
    TaskStatus.COMPLETED: COLOR_SUCCESS,
    TaskStatus.FAILED: COLOR_DANGER,
    TaskStatus.CANCELLED: TEXT_MUTED,
}


class DownloadCard(ctk.CTkFrame):
    """Card widget displaying task progress, metadata, status badge, and controls."""

    def __init__(
        self,
        master,
        task: DownloadTask,
        on_cancel: Callable[[str], None] | None = None,
        on_retry: Callable[[str], None] | None = None,
        on_remove: Callable[[str], None] | None = None,
        on_open_file: Callable[[str], None] | None = None,
        on_open_folder: Callable[[str], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=BG_SECONDARY, corner_radius=12, border_width=1, border_color=BORDER_COLOR, **kwargs)
        self.task = task
        self.on_cancel = on_cancel
        self.on_retry = on_retry
        self.on_remove = on_remove
        self.on_open_file = on_open_file
        self.on_open_folder = on_open_folder

        self._thumbnail_image: ctk.CTkImage | None = None

        self._build_ui()
        self.update_task_state(task)

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)

        # Left: Thumbnail / placeholder
        self.thumb_label = ctk.CTkLabel(
            self,
            text="🎬",
            width=96,
            height=64,
            corner_radius=8,
            fg_color=BG_TERTIARY,
            font=("Segoe UI", 24),
        )
        self.thumb_label.grid(row=0, column=0, rowspan=2, padx=(14, 12), pady=12, sticky="n")

        # Right / Center: Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=0, column=1, padx=(0, 14), pady=(12, 4), sticky="nsew")
        content.columnconfigure(0, weight=1)

        # Title and Badge Row
        header_row = ctk.CTkFrame(content, fg_color="transparent")
        header_row.pack(fill="x")

        self.title_label = ctk.CTkLabel(
            header_row,
            text=self.task.metadata.title if self.task.metadata else self.task.url,
            font=FONT_BODY_BOLD,
            text_color=TEXT_PRIMARY,
            anchor="w",
            wraplength=480,
        )
        self.title_label.pack(side="left", fill="x", expand=True)

        self.status_badge = ctk.CTkLabel(
            header_row,
            text=self.task.status.display_name,
            font=FONT_SMALL,
            corner_radius=6,
            fg_color=STATUS_COLOR_MAP.get(self.task.status, TEXT_MUTED),
            text_color="#FFFFFF",
            padx=8,
            pady=2,
        )
        self.status_badge.pack(side="right", padx=(8, 0))

        # Channel & Quality info
        meta_row = ctk.CTkFrame(content, fg_color="transparent")
        meta_row.pack(fill="x", pady=(2, 6))

        uploader = self.task.metadata.uploader if self.task.metadata else "Pending"
        duration = f" • {self.task.metadata.duration_str}" if self.task.metadata else ""
        self.meta_label = ctk.CTkLabel(
            meta_row,
            text=f"{uploader}{duration} • {self.task.quality.upper()} ({self.task.format.upper()})",
            font=FONT_CAPTION,
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.meta_label.pack(side="left")

        # Progress bar
        self.progress_bar = CustomProgressBar(content)
        self.progress_bar.pack(fill="x", pady=(0, 4))

        # Error label (hidden by default)
        self.error_label = ctk.CTkLabel(
            content,
            text="",
            font=FONT_CAPTION,
            text_color=COLOR_DANGER,
            anchor="w",
            wraplength=480,
        )

        # Action Buttons Row
        self.actions_row = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_row.grid(row=1, column=1, padx=(0, 14), pady=(0, 10), sticky="ew")

        # Create action buttons
        self.cancel_btn = ctk.CTkButton(
            self.actions_row,
            text="Cancel",
            font=FONT_CAPTION,
            width=65,
            height=26,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER_COLOR,
            hover_color=COLOR_DANGER,
            command=self._on_cancel_click,
        )

        self.retry_btn = ctk.CTkButton(
            self.actions_row,
            text="Retry",
            font=FONT_CAPTION,
            width=65,
            height=26,
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            command=self._on_retry_click,
        )

        self.open_file_btn = ctk.CTkButton(
            self.actions_row,
            text="Open File",
            font=FONT_CAPTION,
            width=75,
            height=26,
            fg_color=BG_TERTIARY,
            hover_color=ACCENT_PRIMARY,
            command=self._on_open_file_click,
        )

        self.open_folder_btn = ctk.CTkButton(
            self.actions_row,
            text="Open Folder",
            font=FONT_CAPTION,
            width=85,
            height=26,
            fg_color=BG_TERTIARY,
            hover_color=ACCENT_PRIMARY,
            command=self._on_open_folder_click,
        )

        self.remove_btn = ctk.CTkButton(
            self.actions_row,
            text="Dismiss",
            font=FONT_CAPTION,
            width=65,
            height=26,
            fg_color="transparent",
            hover_color=BG_TERTIARY,
            text_color=TEXT_MUTED,
            command=self._on_remove_click,
        )

    def update_task_state(self, task: DownloadTask) -> None:
        """Refresh card visuals based on task status."""
        self.task = task

        # Title
        if task.metadata and task.metadata.title:
            self.title_label.configure(text=task.metadata.title)
        else:
            self.title_label.configure(text=task.url)

        # Meta label
        uploader = task.metadata.uploader if task.metadata else "Pending"
        duration = f" • {task.metadata.duration_str}" if task.metadata else ""
        self.meta_label.configure(
            text=f"{uploader}{duration} • {task.quality.upper()} ({task.format.upper()})"
        )

        # Status Badge
        badge_text = task.status.display_name
        badge_color = STATUS_COLOR_MAP.get(task.status, TEXT_MUTED)
        self.status_badge.configure(text=badge_text, fg_color=badge_color)

        # Progress
        if task.status == TaskStatus.PROCESSING:
            self.progress_bar.set_indeterminate(True)
        else:
            self.progress_bar.set_indeterminate(False)
            self.progress_bar.update_progress(
                percentage=task.progress.percentage,
                speed_str=task.progress.speed_str,
                size_str=task.progress.size_str,
                eta_str=task.progress.eta_str,
            )

        # Error display
        if task.status == TaskStatus.FAILED and task.error_message:
            clean_err = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", task.error_message)
            clean_err = re.sub(r"\[0;31m.*?\[0m", "", clean_err)
            clean_err = re.sub(r"^ERROR:\s*", "", clean_err).strip()
            self.error_label.configure(text=f"Error: {clean_err}")
            self.error_label.pack(fill="x", pady=(2, 4))
        else:
            self.error_label.pack_forget()

        # Update action buttons
        self._update_buttons()

    def update_progress(self, progress: DownloadProgress) -> None:
        """Update live progress metrics."""
        self.task.progress = progress
        if self.task.status == TaskStatus.DOWNLOADING:
            self.progress_bar.update_progress(
                percentage=progress.percentage,
                speed_str=progress.speed_str,
                size_str=progress.size_str,
                eta_str=progress.eta_str,
            )

    def _update_buttons(self) -> None:
        # Hide all first
        for btn in (self.cancel_btn, self.retry_btn, self.open_file_btn, self.open_folder_btn, self.remove_btn):
            btn.pack_forget()

        if self.task.status.is_active:
            self.cancel_btn.pack(side="right")
        elif self.task.status == TaskStatus.COMPLETED:
            self.remove_btn.pack(side="right", padx=(6, 0))
            self.open_folder_btn.pack(side="right", padx=(6, 0))
            self.open_file_btn.pack(side="right")
        elif self.task.status in (TaskStatus.FAILED, TaskStatus.CANCELLED):
            self.remove_btn.pack(side="right", padx=(6, 0))
            self.retry_btn.pack(side="right")

    def _on_cancel_click(self) -> None:
        if self.on_cancel:
            self.on_cancel(self.task.task_id)

    def _on_retry_click(self) -> None:
        if self.on_retry:
            self.on_retry(self.task.task_id)

    def _on_remove_click(self) -> None:
        if self.on_remove:
            self.on_remove(self.task.task_id)

    def _on_open_file_click(self) -> None:
        if self.on_open_file and self.task.output_file_path:
            self.on_open_file(self.task.output_file_path)

    def _on_open_folder_click(self) -> None:
        if self.on_open_folder:
            target = self.task.output_file_path or self.task.output_dir
            self.on_open_folder(target)
