"""Design language, typography, and color tokens for CustomTkinter."""

import customtkinter as ctk

# Color Palette (Ultra-Modern Obsidian & Electric Indigo theme)
BG_PRIMARY = ("#F8FAFC", "#0B0F19")        # slate-50 / rich midnight obsidian
BG_SECONDARY = ("#FFFFFF", "#131B2E")      # pure white / elevated card surface
BG_TERTIARY = ("#F1F5F9", "#1A243B")       # slate-100 / input & chip background
BG_CARD_HOVER = ("#F8FAFC", "#1E2A45")     # subtle hover card state
BORDER_COLOR = ("#E2E8F0", "#24324F")      # crisp modern border
BORDER_FOCUS = ("#6366F1", "#818CF8")      # focus border ring

# Accent Colors
ACCENT_PRIMARY = ("#4F46E5", "#6366F1")    # Electric Indigo
ACCENT_HOVER = ("#4338CA", "#4F46E5")      # Deep Indigo Hover
ACCENT_PURPLE = ("#7C3AED", "#8B5CF6")     # Modern Violet
ACCENT_PURPLE_HOVER = ("#6D28D9", "#7C3AED")
ACCENT_CYAN = ("#0284C7", "#38BDF8")       # Cyan highlight

# Semantic Colors
COLOR_SUCCESS = ("#059669", "#10B981")     # Emerald green
COLOR_DANGER = ("#DC2626", "#F43F5E")      # Rose red
COLOR_WARNING = ("#D97706", "#F59E0B")     # Amber gold
COLOR_INFO = ("#2563EB", "#38BDF8")        # Sky blue

# Text Colors
TEXT_PRIMARY = ("#0F172A", "#F8FAFC")      # dark slate / crisp bright white
TEXT_SECONDARY = ("#475569", "#94A3B8")    # muted slate
TEXT_MUTED = ("#64748B", "#64748B")        # subtle hint text

# Typography
FONT_FAMILY = "Segoe UI"


def get_font(size: int = 13, weight: str = "normal") -> ctk.CTkFont:
    """Return consistent Segoe UI CTkFont instance."""
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


FONT_HERO = ("Segoe UI", 22, "bold")
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_HEADING = ("Segoe UI", 15, "bold")
FONT_SUBHEADING = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 13, "normal")
FONT_BODY_BOLD = ("Segoe UI", 13, "bold")
FONT_CAPTION = ("Segoe UI", 11, "normal")
FONT_SMALL = ("Segoe UI", 10, "normal")
FONT_MONO = ("Consolas", 12, "normal")
