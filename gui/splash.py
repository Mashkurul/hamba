import customtkinter as ctk
from gui.theme import *
from config import APP_VERSION
class SplashScreen(ctk.CTkToplevel):
    def __init__(self, on_done, width=460, height=420):
        super().__init__()
        self.on_done = on_done
        self.overrideredirect(True)
        self.geometry(f"{width}x{height}")
        self.configure(fg_color=BG_DARK)
        self.attributes("-alpha", 0.0)
        set_window_icon(self)
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - width)  // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self._build()
        self._steps = None
        self._t = 0
        self._run()
    def _build(self):
        self.ring = ctk.CTkFrame(self, fg_color="#143324", width=170,
                                 height=170, corner_radius=85)
        self.ring.place(relx=0.5, rely=0.38, anchor="center")
        self.logo = ctk.CTkLabel(self, text="🐄", text_color=PRIMARY_LIGHT)
        self.logo.place(relx=0.5, rely=0.38, anchor="center")
        self.title_lbl = ctk.CTkLabel(self, text="HAMBAA",
                                      font=("Segoe UI", 40, "bold"),
                                      text_color=TEXT_PRIMARY)
        self.title_lbl.place(relx=0.5, rely=0.62, anchor="center")
        self.tag = ctk.CTkLabel(self, text="AI Based Cow Management System",
                                font=FONT_BODY, text_color=TEXT_ACCENT)
        self.tag.place(relx=0.5, rely=0.70, anchor="center")
        self.bar = ctk.CTkProgressBar(self, width=240, height=6,
                                      corner_radius=3,
                                      fg_color=BG_LIGHT,
                                      progress_color=PRIMARY)
        self.bar.set(0)
        self.bar.place(relx=0.5, rely=0.82, anchor="center")
        ctk.CTkLabel(self, text=f"Version {APP_VERSION}",
                     font=FONT_TINY, text_color=TEXT_MUTED
                     ).place(relx=0.5, rely=0.93, anchor="center")
        self.title_lbl.place_forget()
        self.tag.place_forget()
        self.bar.place_forget()
    def _run(self):
        self._steps = [
            (0,    self._fade_in),
            (250,  self._logo_spring),
            (850,  self._title_in),
            (1050, self._tag_in),
            (1150, self._bar_fill),
            (2400, self._fade_out),
        ]
        self._t = 0
        self._schedule_next()
    def _schedule_next(self):
        if self._t >= len(self._steps):
            return
        delay, fn = self._steps[self._t]
        self._t += 1
        self.after(delay, lambda: (fn(), self._schedule_next()))
    def _fade_in(self):
        for i in range(1, 11):
            self.after(i * 25, lambda a=i / 10: self.attributes("-alpha", a))
    def _logo_spring(self):
        """Scale the cow from small to big with an overshoot bounce."""
        sizes = [28, 40, 56, 74, 92, 104, 96, 100, 96, 98]
        delays = [0, 30, 30, 30, 30, 40, 40, 40, 40, 40]
        total = 0
        for size, d in zip(sizes, delays):
            total += d
            self.after(total, lambda s=size: self.logo.configure(
                font=("Segoe UI Emoji", s)))
    def _title_in(self):
        self.title_lbl.place(relx=0.5, rely=0.68, anchor="center")
        for i in range(1, 11):
            self.after(i * 18,
                       lambda k=i / 10: self.title_lbl.place(
                           relx=0.5, rely=0.68 + (1 - k) * 0.06,
                           anchor="center"))
    def _tag_in(self):
        self.tag.place(relx=0.5, rely=0.70, anchor="center")
        for i in range(1, 11):
            self.after(i * 18, lambda a=i / 10: self.tag.configure(
                text_color=blend(TEXT_ACCENT, BG_DARK, 1 - a)))
    def _bar_fill(self):
        self.bar.place(relx=0.5, rely=0.82, anchor="center")
        for i in range(1, 21):
            self.after(i * 45, lambda v=i / 20: self.bar.set(v))
    def _fade_out(self):
        for i in range(10, 0, -1):
            self.after((10 - i) * 25,
                       lambda a=i / 10: self.attributes("-alpha", a))
        self.after(300, self._close)
    def _close(self):
        self.destroy()
        cb = self.on_done
        if cb:
            cb()
def blend(c1: str, c2: str, t: float) -> str:
    """Blend hex color c1 toward c2 by t (0..1)."""
    try:
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02X}{g:02X}{b:02X}"
    except Exception:
        return c1
