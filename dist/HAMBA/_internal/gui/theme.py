# =============================================================
# gui/theme.py - Color Theme & Style Constants
# =============================================================

import os
import sys

# ── Color Palette ──
PRIMARY        = "#40916C"
PRIMARY_HOVER  = "#2D6A4F"
PRIMARY_LIGHT  = "#74C69D"
PRIMARY_DARK   = "#1B4332"
ACCENT         = "#52B788"

BG_DARK        = "#0F1923"
BG_MEDIUM      = "#162032"
BG_LIGHT       = "#1E2D40"
SIDEBAR_BG     = "#0D1520"
SIDEBAR_HOVER  = "#1A2840"
SIDEBAR_ACTIVE = "#183352"

CARD_BG        = "#162032"
CARD_BORDER    = "#1E2D40"
INPUT_BG       = "#1E2D40"
BORDER         = "#2A3F58"
DIVIDER        = "#1E2D40"

TEXT_PRIMARY   = "#F0F4F8"
TEXT_SECONDARY = "#8FA8C8"
TEXT_MUTED     = "#4A6080"
TEXT_ACCENT    = "#6EE7B7"

DANGER         = "#EF4444"
DANGER_HOVER   = "#DC2626"
WARNING        = "#F59E0B"
WARNING_BG     = "#2D1A00"
SUCCESS        = "#10B981"
SUCCESS_BG     = "#052E1C"
INFO           = "#3B82F6"
INFO_BG        = "#0F1E40"

TABLE_ODD      = "#162032"
TABLE_EVEN     = "#1A2840"
TABLE_HEADER   = "#0D1520"
TABLE_SELECT   = "#183352"
TABLE_SEL_FG   = "#6EE7B7"

# ── Fonts ──
FONT_TITLE   = ("Segoe UI", 22, "bold")
FONT_HEADING = ("Segoe UI", 15, "bold")
FONT_SUBHEAD = ("Segoe UI", 12, "bold")
FONT_BODY    = ("Segoe UI", 11)
FONT_SMALL   = ("Segoe UI", 10)
FONT_TINY    = ("Segoe UI", 9)
FONT_SIDEBAR = ("Segoe UI", 11, "bold")
FONT_BTN     = ("Segoe UI", 11, "bold")
FONT_TABLE   = ("Segoe UI", 10)
FONT_TABLE_H = ("Segoe UI", 10, "bold")
FONT_MONO    = ("Consolas", 11)

# ── Sizes ──
SIDEBAR_WIDTH = 240
HEADER_HEIGHT = 56
BTN_HEIGHT    = 36
BTN_CORNER    = 8
INPUT_HEIGHT  = 38
INPUT_CORNER  = 8
CARD_CORNER   = 12
PADDING       = 20

# ── Shadows / depth ──
CARD_SHADOW   = "#0A1018"
STAT_HOVER    = "#1A2B40"


# ── Helpers ──
def color_alpha(hex_color: str, alpha: float = 0.35) -> str:
    """
    Blend a hex color toward the page background by 'alpha' (0..1).
    Returns a hex string usable as a soft border/tint.
    """
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
    except (ValueError, IndexError):
        return hex_color
    br, bg, bb = 0x0F, 0x19, 0x23  # BG_DARK
    nr = int(r * (1 - alpha) + br * alpha)
    ng = int(g * (1 - alpha) + bg * alpha)
    nb = int(b * (1 - alpha) + bb * alpha)
    return f"#{nr:02X}{ng:02X}{nb:02X}"


def app_icon_path() -> str:
    """Resolve the HAMBA icon path, works in source and PyInstaller builds."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, "assets", "hamba.ico")


def set_window_icon(window) -> None:
    """Set the cow icon on a window's titlebar/taskbar (Windows)."""
    try:
        import tkinter as tk
        from PIL import Image, ImageTk
        path = app_icon_path()
        if os.path.exists(path):
            img = Image.open(path)
            # Windows titlebar wants a small icon
            photo = ImageTk.PhotoImage(img.resize((32, 32)))
            window.iconphoto(False, photo)
            # Keep a reference so it isn't garbage-collected
            window._icon_ref = photo
    except Exception:
        pass
