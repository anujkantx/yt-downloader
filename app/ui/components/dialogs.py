"""Modern modal dialogs for notifications and confirmations."""

from collections.abc import Callable

import customtkinter as ctk

from app.ui.theme import (
    ACCENT_HOVER,
    ACCENT_PRIMARY,
    BG_PRIMARY,
    BG_SECONDARY,
    COLOR_DANGER,
    COLOR_WARNING,
    FONT_BODY,
    FONT_HEADING,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class BaseModalDialog(ctk.CTkToplevel):
    """Base class for centered modal dialogs."""

    def __init__(self, parent: ctk.CTk, title: str, width: int = 420, height: int = 220):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(fg_color=BG_PRIMARY)

        # Center on parent
        self.update_idletasks()
        try:
            parent_x = parent.winfo_x()
            parent_y = parent.winfo_y()
            parent_w = parent.winfo_width()
            parent_h = parent.winfo_height()
            pos_x = parent_x + (parent_w - width) // 2
            pos_y = parent_y + (parent_h - height) // 2
            self.geometry(f"+{max(0, pos_x)}+{max(0, pos_y)}")
        except Exception:
            pass

        self.transient(parent)
        self.grab_set()
        self.focus_set()


class ConfirmDialog(BaseModalDialog):
    """Modern confirmation dialog with optional destructive styling."""

    def __init__(
        self,
        parent: ctk.CTk,
        title: str,
        message: str,
        on_confirm: Callable[[], None],
        on_cancel: Callable[[], None] | None = None,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
        is_destructive: bool = False,
    ):
        super().__init__(parent, title, width=440, height=200)
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel

        # Container frame
        container = ctk.CTkFrame(self, fg_color=BG_SECONDARY, corner_radius=12)
        container.pack(fill="both", expand=True, padx=16, pady=16)

        # Title
        title_label = ctk.CTkLabel(
            container,
            text=title,
            font=FONT_HEADING,
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        title_label.pack(fill="x", padx=20, pady=(16, 8))

        # Message
        msg_label = ctk.CTkLabel(
            container,
            text=message,
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            wraplength=380,
            justify="left",
            anchor="w",
        )
        msg_label.pack(fill="both", expand=True, padx=20, pady=4)

        # Buttons row
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(12, 16))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text=cancel_label,
            font=FONT_BODY,
            fg_color="transparent",
            border_width=1,
            border_color="#475569",
            text_color=TEXT_PRIMARY,
            hover_color="#334155",
            width=90,
            command=self._cancel,
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        confirm_btn = ctk.CTkButton(
            btn_frame,
            text=confirm_label,
            font=FONT_BODY,
            fg_color=COLOR_DANGER if is_destructive else ACCENT_PRIMARY,
            hover_color="#B91C1C" if is_destructive else ACCENT_HOVER,
            text_color="#FFFFFF",
            width=100,
            command=self._confirm,
        )
        confirm_btn.pack(side="right")

    def _confirm(self) -> None:
        self.destroy()
        self._on_confirm()

    def _cancel(self) -> None:
        self.destroy()
        if self._on_cancel:
            self._on_cancel()


class MessageDialog(BaseModalDialog):
    """Informational or alert modal dialog."""

    def __init__(
        self,
        parent: ctk.CTk,
        title: str,
        message: str,
        dialog_type: str = "info",
    ):
        super().__init__(parent, title, width=440, height=200)

        container = ctk.CTkFrame(self, fg_color=BG_SECONDARY, corner_radius=12)
        container.pack(fill="both", expand=True, padx=16, pady=16)

        header_color = TEXT_PRIMARY
        if dialog_type == "error":
            header_color = COLOR_DANGER
        elif dialog_type == "warning":
            header_color = COLOR_WARNING

        title_label = ctk.CTkLabel(
            container,
            text=title,
            font=FONT_HEADING,
            text_color=header_color,
            anchor="w",
        )
        title_label.pack(fill="x", padx=20, pady=(16, 8))

        msg_label = ctk.CTkLabel(
            container,
            text=message,
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            wraplength=380,
            justify="left",
            anchor="w",
        )
        msg_label.pack(fill="both", expand=True, padx=20, pady=4)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(12, 16))

        ok_btn = ctk.CTkButton(
            btn_frame,
            text="OK",
            font=FONT_BODY,
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            width=90,
            command=self.destroy,
        )
        ok_btn.pack(side="right")
