"""Settings view for configuring application preferences, FFmpeg, and defaults."""

from tkinter import filedialog

import customtkinter as ctk

from app.config.defaults import (
    AVAILABLE_FORMATS,
    AVAILABLE_QUALITIES,
)
from app.services.download_service import DownloadService
from app.ui.components.dialogs import ConfirmDialog
from app.ui.components.quality_selector import FORMAT_DISPLAY_MAP, QUALITY_DISPLAY_MAP
from app.ui.theme import (
    ACCENT_HOVER,
    ACCENT_PRIMARY,
    BG_PRIMARY,
    BG_SECONDARY,
    BG_TERTIARY,
    BORDER_COLOR,
    COLOR_DANGER,
    COLOR_SUCCESS,
    COLOR_WARNING,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_CAPTION,
    FONT_SUBHEADING,
    FONT_TITLE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class SettingsPage(ctk.CTkFrame):
    """View allowing users to configure download defaults, paths, and FFmpeg."""

    def __init__(self, master, download_service: DownloadService, **kwargs):
        super().__init__(master, fg_color=BG_PRIMARY, **kwargs)
        self.service = download_service
        self.settings = self.service.settings_manager.current

        self._build_ui()
        self.check_ffmpeg_status()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header Frame
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))

        title = ctk.CTkLabel(
            header,
            text="Settings",
            font=FONT_TITLE,
            text_color=TEXT_PRIMARY,
        )
        title.pack(side="left")

        # Scrollable container for settings sections
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 16))
        self.scroll_frame.columnconfigure(0, weight=1)

        # 1. Section: Download Directory
        dir_card = self._create_card("Default Download Location")
        dir_row = ctk.CTkFrame(dir_card, fg_color="transparent")
        dir_row.pack(fill="x", padx=16, pady=(0, 14))

        self.dir_entry = ctk.CTkEntry(
            dir_row,
            font=FONT_BODY,
            fg_color=BG_TERTIARY,
            border_color=BORDER_COLOR,
        )
        self.dir_entry.insert(0, self.settings.download_dir)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = ctk.CTkButton(
            dir_row,
            text="📁 Browse",
            width=80,
            font=FONT_CAPTION,
            fg_color=BG_TERTIARY,
            hover_color=ACCENT_PRIMARY,
            command=self._browse_dir,
        )
        browse_btn.pack(side="left", padx=(0, 6))

        open_dir_btn = ctk.CTkButton(
            dir_row,
            text="↗ Open",
            width=70,
            font=FONT_CAPTION,
            fg_color=BG_TERTIARY,
            hover_color=ACCENT_PRIMARY,
            command=lambda: self.service.open_containing_folder(self.dir_entry.get().strip()),
        )
        open_dir_btn.pack(side="left")

        # 2. Section: Video Quality & Defaults
        defaults_card = self._create_card("Download Defaults")
        defaults_grid = ctk.CTkFrame(defaults_card, fg_color="transparent")
        defaults_grid.pack(fill="x", padx=16, pady=(0, 14))
        defaults_grid.columnconfigure(0, weight=1)
        defaults_grid.columnconfigure(1, weight=1)

        # Quality
        q_frame = ctk.CTkFrame(defaults_grid, fg_color="transparent")
        q_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkLabel(
            q_frame, text="Default Quality", font=FONT_CAPTION, text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 4))

        q_options = [QUALITY_DISPLAY_MAP.get(q, q) for q in AVAILABLE_QUALITIES]
        self.quality_menu = ctk.CTkOptionMenu(
            q_frame,
            values=q_options,
            font=FONT_BODY,
            fg_color=BG_TERTIARY,
            button_color=ACCENT_PRIMARY,
        )
        self.quality_menu.set(QUALITY_DISPLAY_MAP.get(self.settings.default_quality, "1080p (Full HD)"))
        self.quality_menu.pack(fill="x")

        # Format
        f_frame = ctk.CTkFrame(defaults_grid, fg_color="transparent")
        f_frame.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ctk.CTkLabel(
            f_frame, text="Default Format", font=FONT_CAPTION, text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 4))

        f_options = [FORMAT_DISPLAY_MAP.get(f, f) for f in AVAILABLE_FORMATS]
        self.format_menu = ctk.CTkOptionMenu(
            f_frame,
            values=f_options,
            font=FONT_BODY,
            fg_color=BG_TERTIARY,
            button_color=ACCENT_PRIMARY,
        )
        self.format_menu.set(FORMAT_DISPLAY_MAP.get(self.settings.default_format, "MP4 (Video)"))
        self.format_menu.pack(fill="x")

        # 3. Section: Performance & Concurrency
        perf_card = self._create_card("Concurrency & Appearance")
        perf_grid = ctk.CTkFrame(perf_card, fg_color="transparent")
        perf_grid.pack(fill="x", padx=16, pady=(0, 14))
        perf_grid.columnconfigure(0, weight=1)
        perf_grid.columnconfigure(1, weight=1)

        # Max Concurrent
        c_frame = ctk.CTkFrame(perf_grid, fg_color="transparent")
        c_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.concurrency_label = ctk.CTkLabel(
            c_frame,
            text=f"Max Concurrent Downloads: {self.settings.max_concurrent_downloads}",
            font=FONT_CAPTION,
            text_color=TEXT_SECONDARY,
        )
        self.concurrency_label.pack(anchor="w", pady=(0, 4))

        self.concurrency_slider = ctk.CTkSlider(
            c_frame,
            from_=1,
            to=6,
            number_of_steps=5,
            command=self._on_concurrency_change,
        )
        self.concurrency_slider.set(self.settings.max_concurrent_downloads)
        self.concurrency_slider.pack(fill="x")

        # Theme
        t_frame = ctk.CTkFrame(perf_grid, fg_color="transparent")
        t_frame.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ctk.CTkLabel(
            t_frame, text="Theme (Restart recommended)", font=FONT_CAPTION, text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 4))

        self.theme_menu = ctk.CTkOptionMenu(
            t_frame,
            values=["dark", "light", "system"],
            font=FONT_BODY,
            fg_color=BG_TERTIARY,
            button_color=ACCENT_PRIMARY,
            command=self._on_theme_selected,
        )
        self.theme_menu.set(self.settings.theme)
        self.theme_menu.pack(fill="x")

        # 4. Section: FFmpeg Configuration & Diagnostics
        ffmpeg_card = self._create_card("FFmpeg Configuration")

        ffmpeg_row = ctk.CTkFrame(ffmpeg_card, fg_color="transparent")
        ffmpeg_row.pack(fill="x", padx=16, pady=(0, 8))

        self.ffmpeg_entry = ctk.CTkEntry(
            ffmpeg_row,
            placeholder_text="Leave blank to use system PATH or bundled FFmpeg",
            font=FONT_BODY,
            fg_color=BG_TERTIARY,
            border_color=BORDER_COLOR,
        )
        if self.settings.ffmpeg_path:
            self.ffmpeg_entry.insert(0, self.settings.ffmpeg_path)
        self.ffmpeg_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ffmpeg_browse_btn = ctk.CTkButton(
            ffmpeg_row,
            text="📁 Browse",
            width=80,
            font=FONT_CAPTION,
            fg_color=BG_TERTIARY,
            hover_color=ACCENT_PRIMARY,
            command=self._browse_ffmpeg,
        )
        ffmpeg_browse_btn.pack(side="left", padx=(0, 6))

        test_ffmpeg_btn = ctk.CTkButton(
            ffmpeg_row,
            text="Check Status",
            width=90,
            font=FONT_CAPTION,
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            command=self.check_ffmpeg_status,
        )
        test_ffmpeg_btn.pack(side="left")

        # FFmpeg status readout
        self.ffmpeg_status_label = ctk.CTkLabel(
            ffmpeg_card,
            text="Checking FFmpeg...",
            font=FONT_CAPTION,
            text_color=TEXT_MUTED,
            wraplength=600,
            justify="left",
            anchor="w",
        )
        self.ffmpeg_status_label.pack(fill="x", padx=16, pady=(0, 14))

        # 5. Section: Filename Template & Toggles
        advanced_card = self._create_card("Filename & Preferences")

        tmpl_frame = ctk.CTkFrame(advanced_card, fg_color="transparent")
        tmpl_frame.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(
            tmpl_frame,
            text="Filename Template",
            font=FONT_CAPTION,
            text_color=TEXT_SECONDARY,
        ).pack(anchor="w", pady=(0, 4))

        self.template_entry = ctk.CTkEntry(
            tmpl_frame,
            font=FONT_BODY,
            fg_color=BG_TERTIARY,
            border_color=BORDER_COLOR,
        )
        self.template_entry.insert(0, self.settings.filename_template)
        self.template_entry.pack(fill="x")

        ctk.CTkLabel(
            tmpl_frame,
            text="Standard template: %(title).200s [%(id)s].%(ext)s (prevents long filename or collision errors)",
            font=FONT_CAPTION,
            text_color=TEXT_MUTED,
        ).pack(anchor="w", pady=(2, 0))

        # Checkboxes
        toggles_frame = ctk.CTkFrame(advanced_card, fg_color="transparent")
        toggles_frame.pack(fill="x", padx=16, pady=(0, 14))

        self.auto_open_var = ctk.BooleanVar(value=self.settings.auto_open_folder)
        self.auto_open_cb = ctk.CTkCheckBox(
            toggles_frame,
            text="Automatically open destination folder when a download finishes",
            variable=self.auto_open_var,
            font=FONT_BODY,
        )
        self.auto_open_cb.pack(anchor="w", pady=(0, 8))

        self.embed_meta_var = ctk.BooleanVar(value=self.settings.embed_metadata)
        self.embed_meta_cb = ctk.CTkCheckBox(
            toggles_frame,
            text="Embed video metadata and chapter markers (requires FFmpeg)",
            variable=self.embed_meta_var,
            font=FONT_BODY,
        )
        self.embed_meta_cb.pack(anchor="w")

        # Bottom Buttons Row: Save & Reset
        action_bar = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        action_bar.pack(fill="x", pady=(10, 20))

        self.save_feedback_label = ctk.CTkLabel(
            action_bar,
            text="",
            font=FONT_BODY_BOLD,
            text_color=COLOR_SUCCESS,
        )
        self.save_feedback_label.pack(side="left")

        reset_btn = ctk.CTkButton(
            action_bar,
            text="Reset to Defaults",
            font=FONT_CAPTION,
            width=120,
            height=34,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER_COLOR,
            hover_color=COLOR_DANGER,
            command=self._confirm_reset,
        )
        reset_btn.pack(side="right", padx=(10, 0))

        save_btn = ctk.CTkButton(
            action_bar,
            text="💾 Save Settings",
            font=FONT_BODY_BOLD,
            width=130,
            height=34,
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            command=self.save_settings,
        )
        save_btn.pack(side="right")

    def _create_card(self, title: str) -> ctk.CTkFrame:
        """Create a styled card container with title."""
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=BG_SECONDARY,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        card.pack(fill="x", pady=8)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=FONT_SUBHEADING,
            text_color=TEXT_PRIMARY,
        )
        title_label.pack(anchor="w", padx=16, pady=(12, 10))
        return card

    def _browse_dir(self) -> None:
        chosen = filedialog.askdirectory(
            title="Select Default Download Directory",
            initialdir=self.dir_entry.get().strip() or None,
        )
        if chosen:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, chosen)

    def _browse_ffmpeg(self) -> None:
        chosen = filedialog.askopenfilename(
            title="Locate ffmpeg.exe",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")],
        )
        if chosen:
            self.ffmpeg_entry.delete(0, "end")
            self.ffmpeg_entry.insert(0, chosen)
            self.check_ffmpeg_status()

    def check_ffmpeg_status(self) -> None:
        """Run FFmpeg inspection and display user-friendly results."""
        custom_path = self.ffmpeg_entry.get().strip()
        self.service.ffmpeg_service.set_configured_path(custom_path)
        is_avail, message = self.service.ffmpeg_service.get_status_info()

        if is_avail:
            self.ffmpeg_status_label.configure(
                text=f"✓ {message}",
                text_color=COLOR_SUCCESS,
            )
        else:
            self.ffmpeg_status_label.configure(
                text=f"⚠ {message}",
                text_color=COLOR_WARNING,
            )

    def _on_concurrency_change(self, value: float) -> None:
        int_val = int(value)
        self.concurrency_label.configure(text=f"Max Concurrent Downloads: {int_val}")

    def _on_theme_selected(self, theme: str) -> None:
        ctk.set_appearance_mode(theme)

    def save_settings(self) -> None:
        """Collect form values, validate, and persist."""
        # Map display names back to values
        q_disp = self.quality_menu.get()
        f_disp = self.format_menu.get()

        selected_q = "1080p"
        for k, v in QUALITY_DISPLAY_MAP.items():
            if v == q_disp:
                selected_q = k
                break

        selected_f = "mp4"
        for k, v in FORMAT_DISPLAY_MAP.items():
            if v == f_disp:
                selected_f = k
                break

        updated = self.service.settings_manager.update(
            download_dir=self.dir_entry.get().strip(),
            default_quality=selected_q,
            default_format=selected_f,
            max_concurrent_downloads=int(self.concurrency_slider.get()),
            theme=self.theme_menu.get(),
            ffmpeg_path=self.ffmpeg_entry.get().strip(),
            filename_template=self.template_entry.get().strip(),
            auto_open_folder=self.auto_open_var.get(),
            embed_metadata=self.embed_meta_var.get(),
        )
        self.settings = updated

        self.save_feedback_label.configure(text="✓ Settings saved successfully!")
        self.after(3000, lambda: self.save_feedback_label.configure(text=""))
        self.check_ffmpeg_status()

    def _confirm_reset(self) -> None:
        def do_reset():
            self.settings = self.service.settings_manager.reset_to_defaults()
            # Update UI fields
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, self.settings.download_dir)
            self.quality_menu.set(QUALITY_DISPLAY_MAP.get(self.settings.default_quality, "1080p"))
            self.format_menu.set(FORMAT_DISPLAY_MAP.get(self.settings.default_format, "mp4"))
            self.concurrency_slider.set(self.settings.max_concurrent_downloads)
            self.concurrency_label.configure(text=f"Max Concurrent Downloads: {self.settings.max_concurrent_downloads}")
            self.theme_menu.set(self.settings.theme)
            self.ffmpeg_entry.delete(0, "end")
            self.template_entry.delete(0, "end")
            self.template_entry.insert(0, self.settings.filename_template)
            self.auto_open_var.set(self.settings.auto_open_folder)
            self.embed_meta_var.set(self.settings.embed_metadata)
            self.check_ffmpeg_status()
            self.save_feedback_label.configure(text="Reset to default settings.")
            self.after(3000, lambda: self.save_feedback_label.configure(text=""))

        ConfirmDialog(
            self.winfo_toplevel(),
            title="Reset Settings",
            message="Are you sure you want to revert all settings to their initial default values?",
            on_confirm=do_reset,
            confirm_label="Reset",
            is_destructive=True,
        )
