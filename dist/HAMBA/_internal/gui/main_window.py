# =============================================================
# gui/main_window.py - Main Application Window
# =============================================================
# The main shell after login:
#   - Left sidebar with navigation buttons
#   - Top header bar with user info & logout
#   - Right content area where pages are loaded
# =============================================================

import tkinter as tk
import customtkinter as ctk
from gui.theme import *
from gui import pages


class MainWindow(ctk.CTk):
    """
    The main application window after login.
    Manages navigation between all feature pages.
    """

    def __init__(self, user: dict):
        super().__init__()

        self.current_user = user
        self.role         = user["role"]

        # Window config
        self.title("HAMBA – AI Based Cow Management System")
        self.geometry("1200x720")
        self.minsize(900, 600)
        self.configure(fg_color=BG_DARK)

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth()  // 2) - (1200 // 2)
        y = (self.winfo_screenheight() // 2) - (720 // 2)
        self.geometry(f"1200x720+{x}+{y}")

        self._active_btn   = None
        self._current_page = None

        self._build_layout()
        self._build_sidebar()
        self._build_header()

        # Load dashboard on startup
        self._navigate("Dashboard")

    # ---------------------------------------------------------
    # Layout skeleton: sidebar | main_area (header + content)
    # ---------------------------------------------------------
    def _build_layout(self):
        # Sidebar (fixed left)
        self.sidebar = ctk.CTkFrame(
            self,
            width=SIDEBAR_WIDTH,
            fg_color=SIDEBAR_BG,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Right area
        self.right_area = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self.right_area.pack(side="left", fill="both", expand=True)

        # Header bar (top of right area)
        self.header = ctk.CTkFrame(
            self.right_area,
            height=HEADER_HEIGHT,
            fg_color=BG_MEDIUM,
            corner_radius=0
        )
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        # Content area (fills remaining space)
        self.content = ctk.CTkFrame(
            self.right_area,
            fg_color=BG_DARK,
            corner_radius=0
        )
        self.content.pack(fill="both", expand=True)

    # ---------------------------------------------------------
    # Sidebar
    # ---------------------------------------------------------
    def _build_sidebar(self):

        # App logo / title
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=80)
        logo_frame.pack(fill="x", pady=(0, 4))
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(
            logo_frame,
            text="🐄  HAMBA",
            font=("Segoe UI", 18, "bold"),
            text_color=TEXT_PRIMARY
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Thin separator
        ctk.CTkFrame(self.sidebar, fg_color=PRIMARY_LIGHT, height=1).pack(fill="x", padx=12)

        # ── Navigation items ──
        # Define nav: (label, page_name, icon, allowed_roles)
        nav_items = [
            ("Dashboard",   "Dashboard",   "📊", ["admin", "worker", "salesman"]),
            ("Cows",        "Cows",        "🐄", ["admin", "worker"]),
            ("Milk",        "Milk",        "🥛", ["admin", "worker", "salesman"]),
            ("Food",        "Food",        "🌾", ["admin", "worker"]),
            ("Health",      "Health",      "💉", ["admin", "worker"]),
            ("Employees",   "Employees",   "👷", ["admin"]),
            ("Expenses",    "Expenses",    "💰", ["admin", "salesman"]),
            ("Reports",     "Reports",     "📄", ["admin", "salesman"]),
            ("AI Assistant","AI",          "🤖", ["admin", "worker", "salesman"]),
        ]

        # Admin-only user management
        if self.role == "admin":
            nav_items.append(("Users",  "Users",  "🔐", ["admin"]))

        self._nav_buttons = {}

        ctk.CTkLabel(
            self.sidebar,
            text="NAVIGATION",
            font=("Segoe UI", 9, "bold"),
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=18, pady=(10, 4))

        for label, page, icon, roles in nav_items:
            if self.role not in roles:
                continue

            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                command=lambda p=page: self._navigate(p),
                width=SIDEBAR_WIDTH - 20,
                height=40,
                corner_radius=8,
                fg_color="transparent",
                hover_color=PRIMARY,
                text_color=TEXT_PRIMARY,
                font=FONT_SIDEBAR
            )
            btn.pack(padx=10, pady=2)
            self._nav_buttons[page] = btn

        # Bottom: user info + logout
        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=10, pady=12)

        ctk.CTkFrame(self.sidebar, fg_color=PRIMARY_LIGHT, height=1).pack(
            side="bottom", fill="x", padx=12, pady=(0, 4)
        )

        role_colors = {"admin": WARNING, "worker": PRIMARY_LIGHT, "salesman": INFO}
        badge_color = role_colors.get(self.role, TEXT_MUTED)

        ctk.CTkLabel(
            bottom,
            text=f"  👤 {self.current_user.get('full_name') or self.current_user['username']}",
            font=FONT_SMALL,
            text_color=TEXT_PRIMARY,
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            bottom,
            text=f"     {self.role.upper()}",
            font=("Segoe UI", 9, "bold"),
            text_color=badge_color,
            anchor="w"
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            bottom,
            text="  🚪  Logout",
            anchor="w",
            command=self._logout,
            height=36,
            corner_radius=8,
            fg_color=DANGER,
            hover_color=DANGER_HOVER,
            text_color=TEXT_PRIMARY,
            font=FONT_SIDEBAR
        ).pack(fill="x")

    # ---------------------------------------------------------
    # Header Bar
    # ---------------------------------------------------------
    def _build_header(self):
        self._page_title_label = ctk.CTkLabel(
            self.header,
            text="Dashboard",
            font=FONT_HEADING,
            text_color=TEXT_PRIMARY
        )
        self._page_title_label.pack(side="left", padx=20)

        # Right side: version
        ctk.CTkLabel(
            self.header,
            text="HAMBA v1.0  |  University Project",
            font=FONT_SMALL,
            text_color=TEXT_MUTED
        ).pack(side="right", padx=20)

    # ---------------------------------------------------------
    # Navigation: switch page
    # ---------------------------------------------------------
    def _navigate(self, page_name: str):
        """Destroy current page and load the new one."""

        # Highlight active sidebar button
        if self._active_btn:
            self._active_btn.configure(fg_color="transparent")
        btn = self._nav_buttons.get(page_name)
        if btn:
            btn.configure(fg_color=PRIMARY)
            self._active_btn = btn

        # Update header title
        self._page_title_label.configure(text=page_name)

        # Destroy current page content
        for widget in self.content.winfo_children():
            widget.destroy()

        # Map page name → class
        page_map = {
            "Dashboard": pages.DashboardPage,
            "Cows":      pages.CowsPage,
            "Milk":      pages.MilkPage,
            "Food":      pages.FoodPage,
            "Health":    pages.HealthPage,
            "Employees": pages.EmployeesPage,
            "Expenses":  pages.ExpensesPage,
            "Reports":   pages.ReportsPage,
            "AI":        pages.AIPage,
            "Users":     pages.UsersPage,
        }

        PageClass = page_map.get(page_name)
        if PageClass:
            self._current_page = PageClass(self.content, self.current_user)
            self._current_page.pack(fill="both", expand=True)

    # ---------------------------------------------------------
    # Logout
    # ---------------------------------------------------------
    def _logout(self):
        """Close main window – app will show login again."""
        self.destroy()
