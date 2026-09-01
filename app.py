import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import customtkinter as ctk
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
from database       import initialize_database
from gui.splash       import SplashScreen
from gui.login_window import LoginWindow
from gui.main_window  import MainWindow
def run():
    """Main application loop."""
    initialize_database()
    app = ctk.CTk()
    app.withdraw()
    def start_login():
        app.destroy()
        while True:
            login_win = LoginWindow()
            login_win.mainloop()
            user = login_win.logged_in_user
            if user is None:
                break
            main_win = MainWindow(user)
            main_win.mainloop()
    SplashScreen(on_done=start_login)
    app.mainloop()
if __name__ == "__main__":
    run()
