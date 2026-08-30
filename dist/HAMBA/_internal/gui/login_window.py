# =============================================================
# gui/login_window.py - Login Screen
# =============================================================

import hashlib
import customtkinter as ctk
from gui.theme   import *
from gui.widgets import PasswordEntry
from database    import get_connection


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("HAMBA – Sign In")
        self.geometry("940x600")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)

        self.update_idletasks()
        x = (self.winfo_screenwidth()  // 2) - 470
        y = (self.winfo_screenheight() // 2) - 300
        self.geometry(f"940x600+{x}+{y}")

        self.logged_in_user = None
        self._attempts = 0

        self._build()
        self.bind("<Return>", lambda _: self._login())
        # Focus username field
        self.after(100, self._username.focus)

    # ----------------------------------------------------------
    def _build(self):
        # Two columns: left branding | right form
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ══════════════ LEFT PANEL ══════════════
        left = ctk.CTkFrame(self, fg_color=PRIMARY_DARK, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")

        # Top accent
        ctk.CTkFrame(left, fg_color=PRIMARY, height=4,
                     corner_radius=0).pack(fill="x")

        # Subtle decorative ring behind the logo
        ring = ctk.CTkFrame(left, fg_color="#143324", width=150, height=150,
                            corner_radius=75)
        ring.place(relx=0.5, rely=0.24, anchor="center")

        center = ctk.CTkFrame(left, fg_color="transparent")
        center.place(relx=0.5, rely=0.46, anchor="center")

        ctk.CTkLabel(center, text="🐄",
                     font=("Segoe UI Emoji", 64),
                     text_color=PRIMARY_LIGHT).pack(pady=(0, 10))

        ctk.CTkLabel(center, text="HAMBA",
                     font=("Segoe UI", 38, "bold"),
                     text_color=TEXT_PRIMARY).pack()

        ctk.CTkLabel(center, text="AI Based Cow\nManagement System",
                     font=("Segoe UI", 13),
                     text_color=TEXT_ACCENT,
                     justify="center").pack(pady=(4, 28))

        # Feature list
        features = [
            ("🐄", "Cow Tracking"),
            ("🥛", "Milk Records"),
            ("💉", "Health Monitor"),
            ("🤖", "AI Assistant"),
            ("📊", "Reports & Analytics"),
        ]
        for ico, lbl in features:
            row = ctk.CTkFrame(center, fg_color="#1A3828", corner_radius=20)
            row.pack(fill="x", pady=3, ipady=5)
            ctk.CTkLabel(row, text=f"  {ico}  {lbl}",
                         font=FONT_SMALL, text_color=TEXT_ACCENT).pack()

        ctk.CTkLabel(left, text="v1.0  •  University Project",
                     font=FONT_TINY, text_color=TEXT_MUTED
                     ).place(relx=0.5, rely=0.96, anchor="center")

        # ══════════════ RIGHT PANEL ══════════════
        right = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")

        form = ctk.CTkFrame(right, fg_color="transparent", width=340)
        form.place(relx=0.5, rely=0.5, anchor="center")
        # No pack_propagate(False): let the form grow with its content so
        # the error banner has room to appear.

        # Welcome heading
        ctk.CTkLabel(form, text="Welcome back 👋",
                     font=("Segoe UI", 26, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(form, text="Sign in to your HAMBA account",
                     font=FONT_BODY,
                     text_color=TEXT_SECONDARY).pack(anchor="w", pady=(2, 24))

        # ── Username ──
        ctk.CTkLabel(form, text="Username",
                     font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w")
        self._username = ctk.CTkEntry(
            form, placeholder_text="Enter your username",
            width=340, height=INPUT_HEIGHT, corner_radius=INPUT_CORNER,
            fg_color=INPUT_BG, border_color=BORDER,
            text_color=TEXT_PRIMARY, placeholder_text_color=TEXT_MUTED,
            font=FONT_BODY
        )
        self._username.pack(pady=(4, 14), anchor="w")

        # ── Password with show/hide ──
        ctk.CTkLabel(form, text="Password",
                     font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w")
        self._password = PasswordEntry(form, placeholder="Enter your password",
                                       width=340)
        self._password.pack(pady=(4, 6), anchor="w")

        # ── Error banner (hidden until a login error occurs) ──
        self._err_frame = ctk.CTkFrame(form, fg_color="#4C1414",
                                       corner_radius=8)
        self._err_lbl = ctk.CTkLabel(self._err_frame, text="",
                                     font=FONT_SMALL, text_color=DANGER,
                                     fg_color="transparent")
        self._err_lbl.pack(padx=12, pady=7)
        self._err_frame.pack_forget()   # start hidden

        # ── Login button ──
        ctk.CTkButton(
            form, text="Sign In  →",
            command=self._login,
            width=340, height=46,
            corner_radius=BTN_CORNER,
            fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
            text_color=TEXT_PRIMARY,
            font=("Segoe UI", 13, "bold")
        ).pack(pady=(18, 0))

    # ----------------------------------------------------------
    def _login(self):
        username = self._username.get().strip()
        password = self._password.get().strip()

        # Hide any previous error
        self._err_frame.pack_forget()

        if not username or not password:
            self._show_err("Please enter both username and password.")
            return

        hashed = hashlib.sha256(password.encode()).hexdigest()
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""SELECT id, username, role, full_name, is_active
                           FROM users WHERE username=? AND password=?""",
                        (username, hashed))
            user = cur.fetchone()
            conn.close()

            if user is None:
                self._attempts += 1
                left = max(0, 3 - self._attempts)
                msg  = "Incorrect username or password."
                if left > 0:
                    msg += f"  ({left} attempt{'s' if left > 1 else ''} remaining)"
                self._show_err(msg)
                self._password.delete(0, "end")
                self._shake()
                return

            if user["is_active"] == 0:
                self._show_err("Account deactivated — contact the admin.")
                return

            self.logged_in_user = dict(user)
            self.destroy()

        except Exception as e:
            self._show_err(f"Database error: {e}")

    def _show_err(self, msg):
        self._err_lbl.configure(text=f"  ✕  {msg}")
        self._err_frame.pack(fill="x", pady=(8, 0))

    def _shake(self):
        x, y = self.winfo_x(), self.winfo_y()
        for d in [10, -10, 7, -7, 4, -4, 0]:
            self.geometry(f"+{x+d}+{y}")
            self.update()
            self.after(22)
