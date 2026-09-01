import calendar as _calendar
import tkinter as tk
from tkinter import ttk
from datetime import date
import customtkinter as ctk
from gui.theme import *
class PrimaryButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, width=140, **kw):
        super().__init__(master, text=text, command=command,
                         width=width, height=BTN_HEIGHT, corner_radius=BTN_CORNER,
                         fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
                         text_color=TEXT_PRIMARY, font=FONT_BTN, **kw)
class DangerButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, width=120, **kw):
        super().__init__(master, text=text, command=command,
                         width=width, height=BTN_HEIGHT, corner_radius=BTN_CORNER,
                         fg_color=DANGER, hover_color=DANGER_HOVER,
                         text_color=TEXT_PRIMARY, font=FONT_BTN, **kw)
class SecondaryButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, width=120, **kw):
        super().__init__(master, text=text, command=command,
                         width=width, height=BTN_HEIGHT, corner_radius=BTN_CORNER,
                         fg_color=BG_LIGHT, hover_color=SIDEBAR_HOVER,
                         text_color=TEXT_PRIMARY, border_color=BORDER,
                         border_width=1, font=FONT_BTN, **kw)
class StyledLabel(ctk.CTkLabel):
    def __init__(self, master, text, font=None, text_color=None, **kw):
        super().__init__(master, text=text,
                         font=font or FONT_BODY,
                         text_color=text_color or TEXT_PRIMARY, **kw)
class StyledEntry(ctk.CTkEntry):
    def __init__(self, master, placeholder="", width=220, show=None, **kw):
        cfg = dict(master=master, placeholder_text=placeholder,
                   width=width, height=INPUT_HEIGHT, corner_radius=INPUT_CORNER,
                   fg_color=INPUT_BG, border_color=BORDER,
                   text_color=TEXT_PRIMARY, placeholder_text_color=TEXT_MUTED,
                   font=FONT_BODY, **kw)
        if show is not None:
            cfg["show"] = show
        super().__init__(**cfg)
class StyledCombo(ctk.CTkComboBox):
    def __init__(self, master, values, width=220, **kw):
        super().__init__(master, values=values,
                         width=width, height=INPUT_HEIGHT, corner_radius=INPUT_CORNER,
                         fg_color=INPUT_BG, border_color=BORDER,
                         text_color=TEXT_PRIMARY,
                         button_color=PRIMARY, button_hover_color=PRIMARY_HOVER,
                         dropdown_fg_color=CARD_BG,
                         dropdown_text_color=TEXT_PRIMARY,
                         dropdown_hover_color=PRIMARY,
                         font=FONT_BODY, **kw)
        if values:
            self.set(values[0])
class DatePicker(ctk.CTkFrame):
    """Text entry (YYYY-MM-DD) + button that opens a calendar popup.
    Keeps the same width as other inputs so it drops into existing
    forms. `entry` is the inner ctk.CTkEntry, so callers can bind
    <KeyRelease> to it for live filtering/validation.
    """
    def __init__(self, master, initial=None, width=300, **kw):
        super().__init__(master, fg_color="transparent",
                         width=width, height=INPUT_HEIGHT, **kw)
        self.pack_propagate(False)
        self._popup = None
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text="YYYY-MM-DD",
            width=width - 48,
            height=INPUT_HEIGHT,
            corner_radius=INPUT_CORNER,
            fg_color=INPUT_BG,
            border_color=BORDER,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            font=FONT_BODY
        )
        self.entry.pack(side="left")
        self._btn = ctk.CTkButton(
            self,
            text="📅",
            width=42,
            height=INPUT_HEIGHT,
            corner_radius=INPUT_CORNER,
            fg_color=INPUT_BG,
            hover_color=SIDEBAR_HOVER,
            text_color=TEXT_MUTED,
            border_color=BORDER,
            border_width=1,
            font=("Segoe UI Emoji", 13),
            command=self._open
        )
        self._btn.pack(side="left", padx=(4, 0))
        if initial:
            self.set(initial)
    def set(self, d):
        if isinstance(d, date):
            d = d.isoformat()
        self.entry.delete(0, "end")
        self.entry.insert(0, str(d))
    def get(self):
        return self.entry.get()
    def _open(self):
        if self._popup is not None and self._popup.winfo_exists():
            self._popup.focus()
            return
        self._popup = CalendarPopup(self, value=self.get())
    def delete(self, a, b=None):
        self.entry.delete(a, b if b is not None else "end")
    def insert(self, i, s):
        self.entry.insert(i, s)
    def focus(self):
        self.entry.focus()
class CalendarPopup(ctk.CTkToplevel):
    """Small month-view calendar. Pick a day → writes YYYY-MM-DD back."""
    def __init__(self, picker, value=None):
        super().__init__(picker)
        self.picker = picker
        self.title("Select Date")
        self.configure(fg_color=BG_MEDIUM)
        self.resizable(False, False)
        self.grab_set()
        today = date.today()
        self._sel = None
        if value:
            try:
                self._sel = date.fromisoformat(str(value).strip())
            except ValueError:
                self._sel = None
        self.year, self.month = (self._sel.year, self._sel.month) if self._sel \
            else (today.year, today.month)
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=10, pady=(10, 4))
        ctk.CTkButton(head, text="‹", width=34, height=30,
                      corner_radius=6, fg_color=BG_LIGHT,
                      hover_color=SIDEBAR_HOVER, text_color=TEXT_PRIMARY,
                      font=("Segoe UI", 14, "bold"),
                      command=lambda: self._shift(-1)).pack(side="left")
        self._lbl = ctk.CTkLabel(head, text="", font=FONT_HEADING,
                                 text_color=TEXT_PRIMARY)
        self._lbl.pack(side="left", expand=True)
        ctk.CTkButton(head, text="›", width=34, height=30,
                      corner_radius=6, fg_color=BG_LIGHT,
                      hover_color=SIDEBAR_HOVER, text_color=TEXT_PRIMARY,
                      font=("Segoe UI", 14, "bold"),
                      command=lambda: self._shift(1)).pack(side="left")
        self._day_names = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        names = ctk.CTkFrame(self, fg_color="transparent")
        names.pack(fill="x", padx=10)
        for i, n in enumerate(self._day_names):
            ctk.CTkLabel(names, text=n, font=FONT_TINY,
                         text_color=TEXT_MUTED).grid(
                row=0, column=i, padx=1, pady=1, sticky="ew")
            names.grid_columnconfigure(i, weight=1)
        self._grid = ctk.CTkFrame(self, fg_color="transparent")
        self._grid.pack(fill="x", padx=10, pady=(2, 10))
        self._build()
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.pack(fill="x", padx=10, pady=(0, 10))
        SecondaryButton(foot, "Today", lambda: self._pick(today), width=80).pack(
            side="left", padx=(0, 8))
        SecondaryButton(foot, "Cancel", self.destroy, width=80).pack(side="left")
        self._center_over()
    def _build(self):
        for w in self._grid.winfo_children():
            w.destroy()
        self._lbl.configure(
            text=f"{_calendar.month_name[self.month]} {self.year}")
        first = date(self.year, self.month, 1)
        start_col = first.weekday()
        days = _calendar.monthrange(self.year, self.month)[1]
        today = date.today()
        for i in range(6 * 7):
            day_num = i - start_col + 1
            r, c = divmod(i, 7)
            if not (1 <= day_num <= days):
                ctk.CTkLabel(self._grid, text="", width=36, height=30,
                             fg_color="transparent").grid(
                    row=r, column=c, padx=1, pady=1)
                continue
            d = date(self.year, self.month, day_num)
            is_today = d == today
            is_sel = self._sel is not None and d == self._sel
            fg = PRIMARY if is_today else TEXT_PRIMARY
            bg = CARD_BG if is_today else ("transparent" if c % 2 == 0 else BG_LIGHT)
            btn = ctk.CTkButton(
                self._grid, text=str(day_num), width=36, height=30,
                corner_radius=6, fg_color=bg, hover_color=PRIMARY_HOVER,
                text_color=fg, font=("Segoe UI", 11),
                command=lambda dd=d: self._pick(dd))
            btn.grid(row=r, column=c, padx=1, pady=1)
    def _shift(self, delta):
        m = self.month + delta
        y = self.year
        if m < 1:
            m, y = 12, y - 1
        elif m > 12:
            m, y = 1, y + 1
        self.month, self.year = m, y
        self._build()
    def _pick(self, d):
        self.picker.set(d)
        self.destroy()
    def _center_over(self):
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        p = self.picker
        px = p.winfo_rootx() + (p.winfo_width() - w) // 2
        py = p.winfo_rooty() + (p.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{max(px, 0)}+{max(py, 0)}")
class PasswordEntry(ctk.CTkFrame):
    """
    Password input with a show/hide eye button.
    Can be used exactly like a normal entry field.
    """
    def __init__(self, master, placeholder="Enter password", width=300, **kw):
        super().__init__(master, fg_color="transparent",
                         width=width, height=INPUT_HEIGHT, **kw)
        self.pack_propagate(False)
        self._shown = False
        self._entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            show="●",
            width=width - 48,
            height=INPUT_HEIGHT,
            corner_radius=INPUT_CORNER,
            fg_color=INPUT_BG,
            border_color=BORDER,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            font=FONT_BODY
        )
        self._entry.pack(side="left")
        self._eye_btn = ctk.CTkButton(
            self,
            text="👁",
            width=42,
            height=INPUT_HEIGHT,
            corner_radius=INPUT_CORNER,
            fg_color=INPUT_BG,
            hover_color=SIDEBAR_HOVER,
            text_color=TEXT_MUTED,
            border_color=BORDER,
            border_width=1,
            font=("Segoe UI Emoji", 14),
            command=self._toggle
        )
        self._eye_btn.pack(side="left", padx=(4, 0))
    def _toggle(self):
        self._shown = not self._shown
        if self._shown:
            self._entry.configure(show="")
            self._eye_btn.configure(text="🙈", text_color=PRIMARY_LIGHT)
        else:
            self._entry.configure(show="●")
            self._eye_btn.configure(text="👁", text_color=TEXT_MUTED)
    def get(self):               return self._entry.get()
    def delete(self, a, b=None): self._entry.delete(a, b) if b else self._entry.delete(a, "end")
    def insert(self, i, s):      self._entry.insert(i, s)
    def focus(self):             self._entry.focus()
class SectionCard(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=CARD_BG,
                         corner_radius=CARD_CORNER,
                         border_width=1, border_color=CARD_BORDER, **kw)
class PageHeader(ctk.CTkFrame):
    def __init__(self, master, title, subtitle="", **kw):
        super().__init__(master, fg_color="transparent", **kw)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(anchor="w", fill="x")
        ctk.CTkFrame(row, fg_color=PRIMARY, width=4, height=46,
                     corner_radius=2).pack(side="left", padx=(0, 12))
        col = ctk.CTkFrame(row, fg_color="transparent")
        col.pack(side="left")
        ctk.CTkLabel(col, text=title, font=FONT_TITLE,
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(col, text=subtitle, font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).pack(anchor="w")
def form_row(parent, label, widget, pady=7):
    """Label + input on one row. Returns the input widget.
    `widget` may be a widget instance or a callable(row) that creates it.
    Widgets must live INSIDE the row (created with the row as parent) so
    customtkinter draws them correctly — reparenting with pack(in_=row)
    breaks CTkEntry/CTkComboBox rendering.
    """
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=8, pady=pady)
    ctk.CTkLabel(row, text=label, font=FONT_SMALL,
                 text_color=TEXT_SECONDARY, width=130, anchor="w").pack(side="left")
    if callable(widget):
        widget = widget(row)
    widget.pack(side="left", padx=(6, 0))
    return widget
def divider(parent, padx=16, pady=8):
    ctk.CTkFrame(parent, fg_color=DIVIDER, height=1).pack(
        fill="x", padx=padx, pady=pady)
class DataTable(tk.Frame):
    def __init__(self, master, columns: list, **kw):
        super().__init__(master, bg=CARD_BG, **kw)
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("H.Treeview",
                    background=TABLE_ODD, foreground=TEXT_PRIMARY,
                    fieldbackground=TABLE_ODD, rowheight=34,
                    font=FONT_TABLE, borderwidth=0)
        s.configure("H.Treeview.Heading",
                    background=TABLE_HEADER, foreground=TEXT_ACCENT,
                    font=FONT_TABLE_H, relief="flat", padding=(10, 8))
        s.map("H.Treeview",
              background=[("selected", TABLE_SELECT)],
              foreground=[("selected", TABLE_SEL_FG)])
        s.map("H.Treeview.Heading", relief=[("active", "flat")])
        s.configure("H.Vertical.TScrollbar",
                    troughcolor=TABLE_HEADER, background=BORDER,
                    bordercolor=TABLE_HEADER, arrowcolor=TEXT_MUTED)
        s.configure("H.Horizontal.TScrollbar",
                    troughcolor=TABLE_HEADER, background=BORDER,
                    bordercolor=TABLE_HEADER, arrowcolor=TEXT_MUTED)
        self.tree = ttk.Treeview(self, columns=[c[0] for c in columns],
                                 show="headings", style="H.Treeview",
                                 selectmode="browse")
        self._col_count = len(columns)
        for cid, cname, cw in columns:
            self.tree.heading(cid, text=cname)
            self.tree.column(cid, width=cw, minwidth=30, anchor="center")
        vsb = ttk.Scrollbar(self, orient="vertical",   command=self.tree.yview,
                            style="H.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview,
                            style="H.Horizontal.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0,  column=1, sticky="ns")
        hsb.grid(row=1,  column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tree.tag_configure("odd",  background=TABLE_ODD)
        self.tree.tag_configure("even", background=TABLE_EVEN)
        self.tree.tag_configure("hover", background=STAT_HOVER)
        self._hover_item = None
        self.tree.bind("<Motion>", self._on_motion)
    def _on_motion(self, event):
        item = self.tree.identify_row(event.y)
        if item != self._hover_item:
            if self._hover_item:
                tags = self.tree.item(self._hover_item, "tags")
                idx = int(self.tree.index(self._hover_item))
                zebra = ("even" if idx % 2 == 0 else "odd")
                self.tree.item(self._hover_item, tags=(zebra,))
            self._hover_item = item
            if item:
                self.tree.item(item, tags=("hover",))
    def load(self, rows):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self._hover_item = None
        if not rows:
            empty = [""] * self._col_count
            empty[1] = "No records found"
            self.tree.insert("", "end", values=empty)
            return
        for i, r in enumerate(rows):
            self.tree.insert("", "end", values=r,
                             tags=("even" if i % 2 == 0 else "odd",))
    def get_selected(self):
        sel = self.tree.selection()
        return self.tree.item(sel[0])["values"] if sel else None
    def bind_select(self, cb):
        self.tree.bind("<<TreeviewSelect>>", cb)
class NotificationBar(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color="transparent", height=0, **kw)
        self._lbl = ctk.CTkLabel(self, text="", font=FONT_SMALL,
                                 text_color=TEXT_PRIMARY, fg_color="transparent")
        self._lbl.pack(fill="x", padx=14, pady=6)
        self._after = None
    def show(self, msg, kind="success"):
        fg  = {  "success": SUCCESS, "error": DANGER,
                 "info":    INFO,    "warning": WARNING  }.get(kind, SUCCESS)
        bg  = {  "success": SUCCESS_BG, "error": "#4C1414",
                 "info":    INFO_BG,    "warning": WARNING_BG }.get(kind, SUCCESS_BG)
        ico = {"success": "✓", "error": "✕", "info": "ℹ", "warning": "⚠"}.get(kind, "•")
        self.configure(fg_color=bg, corner_radius=8, height=36)
        self._lbl.configure(text=f"  {ico}  {msg}", text_color=fg, fg_color=bg)
        self.pack(fill="x", padx=20, pady=(6, 0))
        if self._after:
            self.after_cancel(self._after)
        self._after = self.after(3500, self.hide)
    def hide(self):
        self.configure(fg_color="transparent", height=0)
        self._lbl.configure(text="")
        self.pack_forget()
class StatCard(ctk.CTkFrame):
    def __init__(self, master, title, value, icon="", color=PRIMARY, **kw):
        super().__init__(master, fg_color=CARD_BG, corner_radius=CARD_CORNER,
                         border_width=1, border_color=CARD_BORDER, **kw)
        self._color = color
        self._stripe = ctk.CTkFrame(self, fg_color=color, width=4,
                                    corner_radius=4)
        self._stripe.pack(side="left", fill="y", pady=0)
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(side="left", padx=12, pady=14, fill="both", expand=True)
        ctk.CTkLabel(body, text=icon, font=("Segoe UI Emoji", 20),
                     text_color=color).pack(anchor="w")
        self._val = ctk.CTkLabel(body, text=str(value),
                                 font=("Segoe UI", 22, "bold"),
                                 text_color=TEXT_PRIMARY)
        self._val.pack(anchor="w")
        ctk.CTkLabel(body, text=title, font=FONT_TINY,
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        self._hovered = False
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    def _on_enter(self, _):
        self._hovered = True
        self.configure(fg_color=STAT_HOVER, border_color=color_alpha(self._color))
        self._stripe.configure(fg_color=self._color)
    def _on_leave(self, _):
        self._hovered = False
        self.configure(fg_color=CARD_BG, border_color=CARD_BORDER)
    def update_value(self, v):
        self._val.configure(text=str(v))
class BaseDialog(ctk.CTkToplevel):
    """
    Consistent popup base: dark background, title bar,
    centered over parent.
    """
    def __init__(self, parent, title, width=480, height=520):
        super().__init__(parent)
        self.title(title)
        self.configure(fg_color=BG_MEDIUM)
        self.grab_set()
        self.btn_row = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_row.pack(side="bottom", fill="x", padx=24, pady=14)
        bar = ctk.CTkFrame(self, fg_color=PRIMARY_DARK,
                           height=48, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        ctk.CTkFrame(bar, fg_color=PRIMARY, width=4,
                     corner_radius=0).pack(side="left", fill="y")
        ctk.CTkLabel(bar, text=f"  {title}", font=FONT_HEADING,
                     text_color=TEXT_PRIMARY).pack(side="left", padx=8)
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=24, pady=(12, 0))
        self._width, self._height = width, height
        self.after(10, self._finalize_layout)
    def _finalize_layout(self):
        """Size the window to fit its content and center over parent."""
        self.update_idletasks()
        req_w = max(self._width, self.winfo_reqwidth())
        req_h = max(self._height, self.winfo_reqheight())
        parent = self.master
        px = parent.winfo_rootx() + (parent.winfo_width()  - req_w) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - req_h) // 2
        self.geometry(f"{req_w}x{req_h}+{max(px,0)}+{max(py,0)}")
    def add_buttons(self, save_cmd, cancel_cmd=None):
        PrimaryButton(self.btn_row, "💾  Save",
                      save_cmd, width=120).pack(side="left", padx=(0, 8))
        SecondaryButton(self.btn_row, "Cancel",
                        cancel_cmd or self.destroy, width=100).pack(side="left")
    def add_field(self, label, factory, **kw):
        """Add a labelled form field inside the dialog body.
        `factory` is a callable(row) that creates the input widget with the
        row as its parent — required so customtkinter draws it correctly.
        Returns the created widget.
        """
        return form_row(self.body, label, factory, **kw)
