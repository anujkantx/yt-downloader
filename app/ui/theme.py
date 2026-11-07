"""Design language, typography, and color tokens for CustomTkinter."""

import customtkinter as ctk

# Color Palette (Slate & Indigo/Purple theme)
BG_PRIMARY = ("#F1F5F9", "#0F172A")        # slate-100 / slate-900
BG_SECONDARY = ("#FFFFFF", "#1E293B")      # white / slate-800
BG_TERTIARY = ("#E2E8F0", "#334155")       # slate-200 / slate-700
BORDER_COLOR = ("#CBD5E1", "#334155")

# Accent Colors
ACCENT_PRIMARY = ("#4F46E5", "#6366F1")    # Indigo
ACCENT_HOVER = ("#4338CA", "#4F46E5")
ACCENT_PURPLE = ("#7C3AED", "#8B5CF6")
ACCENT_PURPLE_HOVER = ("#6D28D9", "#7C3AED")

# Semantic Colors
COLOR_SUCCESS = ("#059669", "#10B981")     # Emerald
COLOR_DANGER = ("#DC2626", "#EF4444")      # Red
COLOR_WARNING = ("#D97706", "#F59E0B")     # Amber
COLOR_INFO = ("#2563EB", "#3B82F6")        # Blue

# Text Colors
TEXT_PRIMARY = ("#0F172A", "#F8FAFC")
TEXT_SECONDARY = ("#475569", "#94A3B8")
TEXT_MUTED = ("#64748B", "#64748B")

# Typography
FONT_FAMILY = "Segoe UI"


def get_font(size: int = 13, weight: str = "normal") -> ctk.CTkFont:
    """Return consistent Segoe UI CTkFont instance."""
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_HEADING = ("Segoe UI", 16, "bold")
FONT_SUBHEADING = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 13, "normal")
FONT_BODY_BOLD = ("Segoe UI", 13, "bold")
FONT_CAPTION = ("Segoe UI", 11, "normal")
FONT_SMALL = ("Segoe UI", 10, "normal")
