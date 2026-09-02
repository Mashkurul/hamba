import customtkinter as ctk
from datetime import datetime
from gui.theme import *
from gui import pages, new_pages
class MainWindow(ctk.CTk):
    def __init__(self, user: dict):
        super().__init__()
        self.current_user = user
        self.role         = user["role"]
        self._active_btn  = None
        self.title("HAMBAA – AI Based Cow Management System")
        self.geometry("1300x780")
        self.minsize(980, 640)
        self.configure(fg_color=BG_DARK)
        set_window_icon(self)
        self.update_idletasks()
        x = (self.winfo_screenwidth()  // 2) - 650
        y = (self.winfo_screenheight() // 2) - 390
        self.geometry(f"1300x780+{x}+{y}")
        self._build_layout()
        self._build_sidebar()
        self._build_header()
        if self.role == "watchman":
            self._navigate("Incidents")
        elif self.role == "cleaner":
            self._navigate("Cleaning")
        else:
            self._navigate("Dashboard")
    def _build_layout(self):
        self.sidebar = ctk.CTkFrame(self, width=SIDEBAR_WIDTH,
                                    fg_color=SIDEBAR_BG, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        right = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        right.pack(side="left", fill="both", expand=True)
        self.topbar = ctk.CTkFrame(right, height=HEADER_HEIGHT,
                                   fg_color=BG_MEDIUM, corner_radius=0)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)
        ctk.CTkFrame(right, fg_color=DIVIDER, height=1,
                     corner_radius=0).pack(fill="x")
        self.content = ctk.CTkFrame(right, fg_color=BG_DARK, corner_radius=0)
        self.content.pack(fill="both", expand=True)
    def _build_sidebar(self):
        logo = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=68)
        logo.pack(fill="x")
        logo.pack_propagate(False)
        ctk.CTkFrame(logo, fg_color=PRIMARY, width=3,
                     corner_radius=0).pack(side="left", fill="y")
        inner = ctk.CTkFrame(logo, fg_color="transparent")
        inner.pack(side="left", padx=12, fill="both", expand=True)
        inner.pack_propagate(False)
        ctk.CTkLabel(inner, text="🐄  HAMBAA",
                     font=("Segoe UI", 16, "bold"),
                     text_color=TEXT_PRIMARY, anchor="w"
                     ).place(relx=0, rely=0.38, anchor="w")
        ctk.CTkLabel(inner, text="Farm Management",
                     font=FONT_TINY, text_color=TEXT_MUTED, anchor="w"
                     ).place(relx=0, rely=0.70, anchor="w")
        ctk.CTkFrame(self.sidebar, fg_color=DIVIDER, height=1).pack(fill="x")
        nav = [
            ("Dashboard",    "Dashboard",  "📊", ["admin","worker","salesman","farm_owner"]),
            ("Cows",         "Cows",       "🐄", ["admin","worker","farm_owner","watchman","cleaner"]),
            ("Milk",         "Milk",       "🥛", ["admin","worker","salesman","farm_owner"]),
            ("Food",         "Food",       "🌾", ["admin","worker","farm_owner"]),
            ("Health",       "Health",     "💉", ["admin","worker","farm_owner"]),
            ("Employees",    "Employees",  "👷", ["admin","farm_owner"]),
            ("Expenses",     "Expenses",   "💰", ["admin","salesman","farm_owner"]),
            ("Reports",      "Reports",    "📄", ["admin","salesman","farm_owner"]),
            ("AI Assistant", "AI",         "🤖", ["admin","worker","salesman","farm_owner"]),
            ("Incidents",    "Incidents",  "🚨", ["admin","watchman","farm_owner"]),
            ("Cleaning",     "Cleaning",   "🧹", ["admin","cleaner","farm_owner"]),
            ("Notifications","Notifs",     "🔔", ["admin","worker","salesman","watchman","cleaner","farm_owner"]),
        ]
        if self.role == "admin":
            nav.append(("Users", "Users", "🔐", ["admin"]))
        self._nav_btns = {}
        ctk.CTkLabel(self.sidebar, text="  MENU", font=("Segoe UI",9,"bold"),
                     text_color=TEXT_MUTED, anchor="w"
                     ).pack(fill="x", padx=12, pady=(14,4))
        for label, page, icon, roles in nav:
            if self.role not in roles:
                continue
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"    {icon}  {label}",
                anchor="w",
                command=lambda p=page: self._navigate(p),
                width=SIDEBAR_WIDTH - 20,
                height=42, corner_radius=10,
                fg_color="transparent",
                hover_color=SIDEBAR_HOVER,
                text_color=TEXT_SECONDARY,
                font=FONT_SIDEBAR
            )
            btn.pack(padx=10, pady=2)
            self._nav_btns[page] = btn
        ctk.CTkFrame(self.sidebar, fg_color=DIVIDER,
                     height=1).pack(side="bottom", fill="x")
        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=10, pady=10)
        badge_map = {"admin":    ("#F59E0B","#2D1A00"),
                     "worker":   ("#10B981","#052E1C"),
                     "salesman": ("#3B82F6","#0F1E40")}
        fg_c, bg_c = badge_map.get(self.role, (TEXT_MUTED, CARD_BG))
        ctk.CTkButton(
            bottom, text="  🚪  Sign Out", anchor="w",
            command=self._logout, height=36, corner_radius=8,
            fg_color=DANGER, hover_color=DANGER_HOVER,
            text_color=TEXT_PRIMARY, font=FONT_SIDEBAR
        ).pack(fill="x", pady=(0, 8))
        card = ctk.CTkFrame(bottom, fg_color=CARD_BG,
                            corner_radius=10,
                            border_color=CARD_BORDER, border_width=1)
        card.pack(fill="x")
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(padx=10, pady=8, fill="x")
        av = ctk.CTkFrame(row, fg_color=bg_c, width=34, height=34,
                          corner_radius=17)
        av.pack(side="left")
        av.pack_propagate(False)
        initials = (self.current_user.get("full_name") or
                    self.current_user["username"])[:1].upper()
        ctk.CTkLabel(av, text=initials, font=("Segoe UI",13,"bold"),
                     text_color=fg_c).place(relx=.5, rely=.5, anchor="center")
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", padx=8, fill="both", expand=True)
        name = (self.current_user.get("full_name") or
                self.current_user["username"])[:18]
        ctk.CTkLabel(info, text=name, font=("Segoe UI",10,"bold"),
                     text_color=TEXT_PRIMARY, anchor="w").pack(anchor="w")
        badge = ctk.CTkFrame(info, fg_color=bg_c, corner_radius=10)
        badge.pack(anchor="w")
        ctk.CTkLabel(badge, text=f"  {self.role.upper()}  ",
                     font=FONT_TINY, text_color=fg_c).pack()
    def _build_header(self):
        left = ctk.CTkFrame(self.topbar, fg_color="transparent")
        left.pack(side="left", fill="y", padx=20)
        ctk.CTkLabel(left, text="HAMBAA", font=("Segoe UI", 10, "bold"),
                     text_color=TEXT_ACCENT).pack(side="left")
        ctk.CTkLabel(left, text="  /  ", font=FONT_TINY,
                     text_color=TEXT_MUTED).pack(side="left")
        self._breadcrumb = ctk.CTkLabel(left, text="Dashboard",
                                        font=("Segoe UI",11,"bold"),
                                        text_color=TEXT_PRIMARY)
        self._breadcrumb.pack(side="left")
        right = ctk.CTkFrame(self.topbar, fg_color="transparent")
        right.pack(side="right", fill="y", padx=20)
        self._clock = ctk.CTkLabel(right, text="",
                                   font=FONT_SMALL, text_color=TEXT_MUTED)
        self._clock.pack(side="left")
        self._tick()
    def _tick(self):
        self._clock.configure(
            text=datetime.now().strftime("  %a %d %b  %H:%M"))
        self.after(30000, self._tick)
    def _navigate(self, page_name: str):
        if self._active_btn:
            self._active_btn.configure(fg_color="transparent",
                                       text_color=TEXT_SECONDARY)
            if hasattr(self._active_btn, "_accent"):
                self._active_btn._accent.place_forget()
        btn = self._nav_btns.get(page_name)
        if btn:
            btn.configure(fg_color=SIDEBAR_ACTIVE, text_color=TEXT_ACCENT)
            accent = ctk.CTkFrame(btn, fg_color=PRIMARY, width=4,
                                  height=22, corner_radius=2)
            accent.place(x=6, rely=0.5, anchor="w")
            btn._accent = accent
            self._active_btn = btn
        if hasattr(self, "_breadcrumb"):
            self._breadcrumb.configure(text=page_name)
        for w in self.content.winfo_children():
            w.destroy()
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
            "Incidents": new_pages.IncidentsPage,
            "Cleaning":  new_pages.CleaningPage,
            "Notifs":    new_pages.NotificationsPage,
        }
        if self.role == "farm_owner" and page_name == "Dashboard":
            cls = new_pages.OwnerDashboardPage
        else:
            cls = page_map.get(page_name)
        if cls:
            cls(self.content, self.current_user).pack(fill="both", expand=True)
    def _logout(self):
        self.destroy()
