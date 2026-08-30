# =============================================================
# app.py - GUI Application Entry Point
# =============================================================
# Run this file to launch the HAMBA desktop GUI:
#   python app.py
#
# Flow:
#   1. Initialize database
#   2. Show login window
#   3. On success → show main window
#   4. On logout → return to login
# =============================================================

import sys
import os

# Make sure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk


# Set appearance before creating any windows
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

from database       import initialize_database
from gui.splash       import SplashScreen
from gui.login_window import LoginWindow
from gui.main_window  import MainWindow


def run():
    """Main application loop."""

    # Step 1: Initialize database (creates tables + default admin)
    initialize_database()

    # Step 2: Animated splash screen
    app = ctk.CTk()
    app.withdraw()          # hidden root while the splash plays

    def start_login():
        app.destroy()
        # Step 3: Login → Main loop (returns to login after logout)
        while True:
            login_win = LoginWindow()
            login_win.mainloop()

            user = login_win.logged_in_user
            if user is None:
                # User closed login window without logging in
                break

            main_win = MainWindow(user)
            main_win.mainloop()
            # If main window was closed (logout), loop back to login

    SplashScreen(on_done=start_login)
    app.mainloop()


if __name__ == "__main__":
    run()
