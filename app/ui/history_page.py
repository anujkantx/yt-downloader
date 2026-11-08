"""Download history view displaying past tasks with search and file operations."""

from datetime import datetime

import customtkinter as ctk

from app.core.download_models import format_bytes
from app.database.repository import DownloadRecord
from app.services.download_service import DownloadService
from app.ui.components.dialogs import ConfirmDialog
from app.ui.theme import (
    ACCENT_HOVER,
    ACCENT_PRIMARY,
    BG_PRIMARY,
    BG_SECONDARY,
    BG_TERTIARY,
    BORDER_COLOR,
    COLOR_DANGER,
    COLOR_SUCCESS,
    FONT_BODY_BOLD,
    FONT_CAPTION,
    FONT_HEADING,
    FONT_SMALL,
    FONT_SUBHEADING,
    FONT_TITLE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from app.utils.logging_config import get_logger

logger = get_logger("history_page")


class HistoryPage(ctk.CTkFrame):
    """View displaying persistent SQLite download history."""

    def __init__(self, master, download_service: DownloadService, **kwargs):
        super().__init__(master, fg_color=BG_PRIMARY, **kwargs)
        self.service = download_service
        self._records: list[DownloadRecord] = []

        self._build_ui()
        self.refresh_history()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header Frame
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 12))

        title_label = ctk.CTkLabel(
            header,
            text="Download History",
            font=FONT_TITLE,
            text_color=TEXT_PRIMARY,
        )
        title_label.pack(side="left")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")

        refresh_btn = ctk.CTkButton(
            actions,
            text="Refresh",
            font=FONT_CAPTION,
            width=75,
            height=30,
            fg_color=BG_TERTIARY,
            hover_color=ACCENT_PRIMARY,
            command=self.refresh_history,
        )
        refresh_btn.pack(side="left", padx=(0, 8))

        clear_btn = ctk.CTkButton(
            actions,
            text="Clear History",
            font=FONT_CAPTION,
            width=95,
            height=30,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER_COLOR,
            hover_color=COLOR_DANGER,
            command=self._confirm_clear_all,
        )
        clear_btn.pack(side="left")

        # Scrollable list for history records
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 16))
        self.scroll_frame.columnconfigure(0, weight=1)

        # Empty state container
        self.empty_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        empty_icon = ctk.CTkLabel(
            self.empty_frame, text="History Empty", font=FONT_HEADING, text_color=TEXT_MUTED
        )
        empty_icon.pack(pady=(40, 4))
        ctk.CTkLabel(
            self.empty_frame,
            text="No download history yet",
            font=FONT_SUBHEADING,
            text_color=TEXT_MUTED,
        ).pack()

    def refresh_history(self) -> None:
        """Fetch and render history records from database."""
        # Clear existing items
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self._records = self.service.get_history(limit=150)

        if not self._records:
            self.empty_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            self.empty_frame.pack(fill="both", expand=True, pady=40)
            ctk.CTkLabel(
                self.empty_frame, text="History Empty", font=FONT_HEADING, text_color=TEXT_MUTED
            ).pack(pady=(0, 6))
            ctk.CTkLabel(
                self.empty_frame,
                text="No download history found",
                font=FONT_SUBHEADING,
                text_color=TEXT_MUTED,
            ).pack()
            return

        for record in self._records:
            self._create_record_row(record)

    def _create_record_row(self, record: DownloadRecord) -> None:
        """Create a rounded card row for a history record."""
        row_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=BG_SECONDARY,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        row_card.pack(fill="x", pady=5)
        row_card.columnconfigure(0, weight=1)

        # Content container
        content = ctk.CTkFrame(row_card, fg_color="transparent")
        content.pack(fill="x", padx=16, pady=12)
        content.columnconfigure(0, weight=1)

        # Top row: Title + Status
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x")

        title = ctk.CTkLabel(
            top_row,
            text=record.title or record.source_url,
            font=FONT_BODY_BOLD,
            text_color=TEXT_PRIMARY,
            anchor="w",
            wraplength=480,
        )
        title.pack(side="left", fill="x", expand=True)

        status_color = (
            COLOR_SUCCESS
            if record.status == "completed"
            else COLOR_DANGER
            if record.status == "failed"
            else TEXT_MUTED
        )
        status_label = ctk.CTkLabel(
            top_row,
            text=record.status.upper(),
            font=FONT_SMALL,
            corner_radius=4,
            fg_color=status_color,
            text_color="#FFFFFF",
            padx=6,
            pady=2,
        )
        status_label.pack(side="right")

        # Details Row: Date, Quality, Format, File Size
        details_row = ctk.CTkFrame(content, fg_color="transparent")
        details_row.pack(fill="x", pady=(4, 6))

        date_str = ""
        if record.created_at:
            try:
                dt = datetime.fromisoformat(record.created_at)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                date_str = record.created_at[:16]

        size_str = format_bytes(record.file_size) if record.file_size else ""
        meta_parts = [
            part for part in [
                date_str,
                f"Quality: {record.selected_quality}",
                f"Format: {record.selected_format}",
                size_str,
                f"By: {record.uploader}" if record.uploader else "",
            ] if part
        ]

        details_label = ctk.CTkLabel(
            details_row,
            text=" • ".join(meta_parts),
            font=FONT_CAPTION,
            text_color=TEXT_MUTED,
            anchor="w",
        )
        details_label.pack(side="left")

        # Path / Error row
        if record.status == "completed" and record.output_path:
            path_label = ctk.CTkLabel(
                content,
                text=f"File: {record.output_path}",
                font=FONT_CAPTION,
                text_color=TEXT_SECONDARY,
                anchor="w",
                wraplength=500,
            )
            path_label.pack(fill="x", pady=(0, 6))
        elif record.status == "failed" and record.error_message:
            err_label = ctk.CTkLabel(
                content,
                text=f"Error: {record.error_message}",
                font=FONT_CAPTION,
                text_color=COLOR_DANGER,
                anchor="w",
                wraplength=500,
            )
            err_label.pack(fill="x", pady=(0, 6))

        # Action Buttons Row
        actions_row = ctk.CTkFrame(content, fg_color="transparent")
        actions_row.pack(fill="x")

        # Copy URL
        copy_btn = ctk.CTkButton(
            actions_row,
            text="Copy URL",
            font=FONT_CAPTION,
            width=70,
            height=24,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER_COLOR,
            hover_color=BG_TERTIARY,
            command=lambda u=record.source_url: self._copy_to_clipboard(u),
        )
        copy_btn.pack(side="left", padx=(0, 6))

        # Open File (if completed and exists)
        if record.status == "completed" and record.output_path:
            open_btn = ctk.CTkButton(
                actions_row,
                text="Play / Open",
                font=FONT_CAPTION,
                width=80,
                height=24,
                fg_color=BG_TERTIARY,
                hover_color=ACCENT_PRIMARY,
                command=lambda p=record.output_path: self.service.open_file(p),
            )
            open_btn.pack(side="left", padx=(0, 6))

            folder_btn = ctk.CTkButton(
                actions_row,
                text="Open Folder",
                font=FONT_CAPTION,
                width=80,
                height=24,
                fg_color=BG_TERTIARY,
                hover_color=ACCENT_PRIMARY,
                command=lambda p=record.output_path: self.service.open_containing_folder(p),
            )
            folder_btn.pack(side="left", padx=(0, 6))

        # Retry (if failed)
        if record.status == "failed":
            retry_btn = ctk.CTkButton(
                actions_row,
                text="Retry",
                font=FONT_CAPTION,
                width=65,
                height=24,
                fg_color=ACCENT_PRIMARY,
                hover_color=ACCENT_HOVER,
                command=lambda rec=record: self._retry_record(rec),
            )
            retry_btn.pack(side="left", padx=(0, 6))

        # Delete Entry (does not delete file on disk unless user specifies)
        delete_btn = ctk.CTkButton(
            actions_row,
            text="Remove",
            font=FONT_CAPTION,
            width=65,
            height=24,
            fg_color="transparent",
            hover_color=COLOR_DANGER,
            text_color=TEXT_MUTED,
            command=lambda r_id=record.id: self._confirm_delete_record(r_id),
        )
        delete_btn.pack(side="right")

    def _copy_to_clipboard(self, text: str) -> None:
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
        except Exception:
            pass

    def _retry_record(self, record: DownloadRecord) -> None:
        self.service.enqueue_downloads(
            urls=[record.source_url],
            quality=record.selected_quality,
            format_choice=record.selected_format,
        )

    def _confirm_delete_record(self, record_id: int | None) -> None:
        if not record_id:
            return

        def do_delete():
            self.service.delete_history_record(record_id, delete_file=False)
            self.refresh_history()

        ConfirmDialog(
            self.winfo_toplevel(),
            title="Delete History Entry",
            message="Are you sure you want to remove this record from history? (The downloaded video file on disk will NOT be deleted).",
            on_confirm=do_delete,
            confirm_label="Remove",
            is_destructive=True,
        )

    def _confirm_clear_all(self) -> None:
        def do_clear():
            self.service.clear_all_history(delete_files=False)
            self.refresh_history()

        ConfirmDialog(
            self.winfo_toplevel(),
            title="Clear All History",
            message="Are you sure you want to clear your entire download history? (Your files on disk will NOT be deleted).",
            on_confirm=do_clear,
            confirm_label="Clear All",
            is_destructive=True,
        )
