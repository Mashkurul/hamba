# =============================================================
# gui/widgets.py - Reusable Custom Widgets
# =============================================================
# Contains reusable UI components used throughout the app:
#   - StyledButton, DangerButton
#   - StyledEntry, StyledLabel
#   - SectionCard, PageHeader
#   - DataTable (ttk.Treeview wrapper)
#   - FormDialog (popup form base)
#   - StatusBar, NotificationBar
# =============================================================

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from gui.theme import *


# ---------------------------------------------------------
# Primary Action Button
# ---------------------------------------------------------
class PrimaryButton(ctk.CTkButton):
    """Green primary action button."""
    def __init__(self, master, text, command=None, width=140, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=BTN_HEIGHT,
            corner_radius=BTN_CORNER,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color=TEXT_PRIMARY,
            font=FONT_BTN,
            **kwargs
        )


# ---------------------------------------------------------
# Danger / Delete Button
# ---------------------------------------------------------
class DangerButton(ctk.CTkButton):
    """Red button for destructive actions."""
    def __init__(self, master, text, command=None, width=120, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=BTN_HEIGHT,
            corner_radius=BTN_CORNER,
            fg_color=DANGER,
            hover_color=DANGER_HOVER,
            text_color=TEXT_PRIMARY,
            font=FONT_BTN,
            **kwargs
        )


# ---------------------------------------------------------
# Secondary / Outline Button
# ---------------------------------------------------------
class SecondaryButton(ctk.CTkButton):
    """Subtle grey secondary button."""
    def __init__(self, master, text, command=None, width=120, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            width=width,
            height=BTN_HEIGHT,
            corner_radius=BTN_CORNER,
            fg_color=CARD_BG,
            hover_color=BG_LIGHT,
            text_color=TEXT_PRIMARY,
            border_color=BORDER,
            border_width=1,
            font=FONT_BTN,
            **kwargs
        )


# ---------------------------------------------------------
# Styled Label
# ---------------------------------------------------------
class StyledLabel(ctk.CTkLabel):
    """Standard body text label."""
    def __init__(self, master, text, font=None, text_color=None, **kwargs):
        super().__init__(
            master,
            text=text,
            font=font or FONT_BODY,
            text_color=text_color or TEXT_PRIMARY,
            **kwargs
        )


# ---------------------------------------------------------
# Styled Entry (text input)
# ---------------------------------------------------------
class StyledEntry(ctk.CTkEntry):
    """Clean input field."""
    def __init__(self, master, placeholder="", width=220, show=None, **kwargs):
        kw = dict(
            master=master,
            placeholder_text=placeholder,
            width=width,
            height=INPUT_HEIGHT,
            corner_radius=INPUT_CORNER,
            fg_color=INPUT_BG,
            border_color=BORDER,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            font=FONT_BODY,
            **kwargs
        )
        if show is not None:
            kw["show"] = show
        super().__init__(**kw)


# ---------------------------------------------------------
# Styled Combobox (dropdown)
# ---------------------------------------------------------
class StyledCombo(ctk.CTkComboBox):
    """Dropdown selector."""
    def __init__(self, master, values, width=220, **kwargs):
        super().__init__(
            master,
            values=values,
            width=width,
            height=INPUT_HEIGHT,
            corner_radius=INPUT_CORNER,
            fg_color=INPUT_BG,
            border_color=BORDER,
            text_color=TEXT_PRIMARY,
            button_color=PRIMARY,
            button_hover_color=PRIMARY_HOVER,
            dropdown_fg_color=CARD_BG,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_hover_color=PRIMARY,
            font=FONT_BODY,
            **kwargs
        )
        if values:
            self.set(values[0])


# ---------------------------------------------------------
# Section Card (container with rounded bg)
# ---------------------------------------------------------
class SectionCard(ctk.CTkFrame):
    """Rounded dark card for grouping content."""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=CARD_BG,
            corner_radius=CARD_CORNER,
            **kwargs
        )


# ---------------------------------------------------------
# Page Header (title + subtitle)
# ---------------------------------------------------------
class PageHeader(ctk.CTkFrame):
    """Top area showing current page title."""
    def __init__(self, master, title, subtitle="", **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )
        ctk.CTkLabel(
            self, text=title,
            font=FONT_TITLE,
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(
                self, text=subtitle,
                font=FONT_SMALL,
                text_color=TEXT_MUTED
            ).pack(anchor="w")


# ---------------------------------------------------------
# Data Table using ttk.Treeview
# ---------------------------------------------------------
class DataTable(tk.Frame):
    """
    A scrollable table widget using ttk.Treeview.
    Supports column headers, striped rows, and row selection.
    """

    def __init__(self, master, columns: list, **kwargs):
        """
        columns: list of (column_id, display_name, width) tuples
        Example: [("id","ID",50), ("name","Name",150)]
        """
        super().__init__(master, bg=CARD_BG, **kwargs)

        # Style the treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Hamba.Treeview",
            background=TABLE_ODD,
            foreground=TEXT_PRIMARY,
            fieldbackground=TABLE_ODD,
            rowheight=32,
            font=FONT_TABLE,
            borderwidth=0,
        )
        style.configure(
            "Hamba.Treeview.Heading",
            background=TABLE_HEADER,
            foreground=TEXT_PRIMARY,
            font=FONT_TABLE_H,
            relief="flat",
            padding=(8, 6),
        )
        style.map(
            "Hamba.Treeview",
            background=[("selected", PRIMARY)],
            foreground=[("selected", TEXT_PRIMARY)],
        )
        style.map("Hamba.Treeview.Heading", relief=[("active", "flat")])

        # Build column id list
        col_ids   = [c[0] for c in columns]
        col_names = {c[0]: c[1] for c in columns}
        col_widths = {c[0]: c[2] for c in columns}

        # Create Treeview
        self.tree = ttk.Treeview(
            self,
            columns=col_ids,
            show="headings",
            style="Hamba.Treeview",
            selectmode="browse",
        )

        # Configure columns
        for col in columns:
            cid, cname, cwidth = col
            self.tree.heading(cid, text=cname)
            self.tree.column(cid, width=cwidth, minwidth=40, anchor="center")

        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Tag for alternating row colors
        self.tree.tag_configure("odd",  background=TABLE_ODD)
        self.tree.tag_configure("even", background=TABLE_EVEN)

    def load(self, rows: list):
        """
        Clear and reload table with new data.
        rows: list of tuples/lists matching column order.
        """
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert new rows with alternating colors
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=row, tags=(tag,))

    def get_selected(self):
        """Returns the values of the currently selected row, or None."""
        selected = self.tree.selection()
        if selected:
            return self.tree.item(selected[0])["values"]
        return None

    def bind_select(self, callback):
        """Bind a callback when a row is clicked."""
        self.tree.bind("<<TreeviewSelect>>", callback)


# ---------------------------------------------------------
# Notification Banner (success / error / info)
# ---------------------------------------------------------
class NotificationBar(ctk.CTkFrame):
    """
    A colored banner for showing success/error messages.
    Automatically hides after a timeout.
    """

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            height=0,
            **kwargs
        )
        self._label = ctk.CTkLabel(
            self, text="", font=FONT_BODY,
            text_color=TEXT_PRIMARY,
            corner_radius=6,
            fg_color="transparent"
        )
        self._label.pack(fill="x", padx=8, pady=4)
        self._after_id = None

    def show(self, message: str, kind: str = "success"):
        """
        Display a notification.
        kind: "success" | "error" | "info" | "warning"
        """
        colors = {
            "success": SUCCESS,
            "error":   DANGER,
            "info":    INFO,
            "warning": WARNING,
        }
        bg = colors.get(kind, SUCCESS)
        self.configure(fg_color=bg, height=36)
        self._label.configure(text=f"  {message}", fg_color=bg)
        self.pack(fill="x", padx=16, pady=(4, 0))

        # Auto-hide after 3 seconds
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(3500, self.hide)

    def hide(self):
        self.configure(fg_color="transparent", height=0)
        self._label.configure(text="")
        self.pack_forget()


# ---------------------------------------------------------
# Form Row helper (label + widget side by side)
# ---------------------------------------------------------
def form_row(parent, label_text, widget, pady=6):
    """Packs a label and its input widget as a horizontal row."""
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=pady)
    ctk.CTkLabel(
        row, text=label_text,
        font=FONT_BODY,
        text_color=TEXT_SECONDARY,
        width=140,
        anchor="w"
    ).pack(side="left")
    widget.pack(side="left", padx=(8, 0))
    return row


# ---------------------------------------------------------
# Stat Card (dashboard summary box)
# ---------------------------------------------------------
class StatCard(ctk.CTkFrame):
    """
    A small card showing a metric with label and value.
    Used on the dashboard.
    """
    def __init__(self, master, title, value, icon="", color=PRIMARY, **kwargs):
        super().__init__(
            master,
            fg_color=CARD_BG,
            corner_radius=CARD_CORNER,
            **kwargs
        )
        # Top colored bar
        ctk.CTkFrame(
            self, fg_color=color, height=4, corner_radius=2
        ).pack(fill="x", padx=0, pady=(0, 8))

        ctk.CTkLabel(
            self, text=f"{icon}  {title}" if icon else title,
            font=FONT_SMALL,
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=14)

        self.value_label = ctk.CTkLabel(
            self, text=str(value),
            font=("Segoe UI", 24, "bold"),
            text_color=TEXT_PRIMARY
        )
        self.value_label.pack(anchor="w", padx=14, pady=(2, 10))

    def update_value(self, value):
        """Update the displayed metric value."""
        self.value_label.configure(text=str(value))
