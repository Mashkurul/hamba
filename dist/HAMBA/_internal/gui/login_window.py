# =============================================================
# gui/login_window.py - Login Screen
# =============================================================
# The first window users see. Has:
#   - App logo/title
#   - Username & Password fields
#   - Login button
#   - Role badge shown after login
# =============================================================

import hashlib
import tkinter as tk
import customtkinter as ctk
from gui.theme import *
from database import get_connection


class LoginWindow(ctk.CTk):
    """
    The login window. On success, destroys itself and
    passes the logged-in user dict back to the caller.
    """

    def __init__(self):
        super().__init__()

        # Window setup
        self.title("HAMBA – Login")
        self.geometry("480x580")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)

        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  // 2) - (480 // 2)
        y = (self.winfo_screenheight() // 2) - (580 // 2)
        self.geometry(f"480x580+{x}+{y}")

        # Result – set by successful login
        self.logged_in_user = None

        self._build_ui()

        # Allow pressing Enter to submit
        self.bind("<Return>", lambda e: self._do_login())

    # ---------------------------------------------------------
    # Build UI
    # ---------------------------------------------------------
    def _build_ui(self):

        # ── Top green accent bar ──
        ctk.CTkFrame(
            self, fg_color=PRIMARY, height=6
        ).pack(fill="x")

        # ── Logo / Title area ──
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(pady=(40, 10))

        ctk.CTkLabel(
            logo_frame,
            text="🐄",
            font=("Segoe UI Emoji", 52),
            text_color=PRIMARY_LIGHT
        ).pack()

        ctk.CTkLabel(
            logo_frame,
            text="HAMBA",
            font=("Segoe UI", 32, "bold"),
            text_color=TEXT_PRIMARY
        ).pack()

        ctk.CTkLabel(
            logo_frame,
            text="AI Based Cow Management System",
            font=FONT_SMALL,
            text_color=TEXT_MUTED
        ).pack()

        # ── Login Card ──
        card = ctk.CTkFrame(
            self,
            fg_color=CARD_BG,
            corner_radius=CARD_CORNER,
            width=380
        )
        card.pack(padx=50, pady=20, fill="x")
        card.pack_propagate(False)
        card.configure(height=260)

        ctk.CTkLabel(
            card,
            text="Sign In",
            font=FONT_HEADING,
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            card,
            text="Enter your credentials to continue",
            font=FONT_SMALL,
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # Username
        ctk.CTkLabel(
            card, text="Username",
            font=FONT_SMALL, text_color=TEXT_SECONDARY
        ).pack(anchor="w", padx=24)

        self.username_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter username",
            width=332,
            height=INPUT_HEIGHT,
            corner_radius=INPUT_CORNER,
            fg_color=INPUT_BG,
            border_color=BORDER,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            font=FONT_BODY
        )
        self.username_entry.pack(padx=24, pady=(4, 12))

        # Password
        ctk.CTkLabel(
            card, text="Password",
            font=FONT_SMALL, text_color=TEXT_SECONDARY
        ).pack(anchor="w", padx=24)

        self.password_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter password",
            show="●",
            width=332,
            height=INPUT_HEIGHT,
            corner_radius=INPUT_CORNER,
            fg_color=INPUT_BG,
            border_color=BORDER,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            font=FONT_BODY
        )
        self.password_entry.pack(padx=24, pady=(4, 20))

        # ── Error message label ──
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            font=FONT_SMALL,
            text_color=DANGER,
            fg_color="transparent"
        )
        self.error_label.pack(pady=(0, 4))

        # ── Login Button ──
        ctk.CTkButton(
            self,
            text="Sign In  →",
            command=self._do_login,
            width=380,
            height=44,
            corner_radius=BTN_CORNER,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color=TEXT_PRIMARY,
            font=("Segoe UI", 13, "bold")
        ).pack(padx=50)

        # ── Default credentials hint ──
        ctk.CTkLabel(
            self,
            text="Default: admin / admin123",
            font=FONT_SMALL,
            text_color=TEXT_MUTED
        ).pack(pady=(12, 0))

    # ---------------------------------------------------------
    # Login Logic
    # ---------------------------------------------------------
    def _do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self._show_error("Please enter username and password.")
            return

        hashed = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, role, full_name, is_active
                FROM users
                WHERE username = ? AND password = ?
            """, (username, hashed))
            user = cursor.fetchone()
            conn.close()

            if user is None:
                self._show_error("Invalid username or password.")
                self.password_entry.delete(0, "end")
                return

            if user["is_active"] == 0:
                self._show_error("Account deactivated. Contact admin.")
                return

            # Success – store user and close window
            self.logged_in_user = dict(user)
            self.destroy()

        except Exception as e:
            self._show_error(f"Error: {e}")

    def _show_error(self, msg: str):
        """Display an error message below the form."""
        self.error_label.configure(text=f"⚠  {msg}")
        # Shake the window slightly for feedback
        x, y = self.winfo_x(), self.winfo_y()
        for dx in [6, -6, 5, -5, 3, -3, 0]:
            self.geometry(f"+{x+dx}+{y}")
            self.update()
            self.after(30)
