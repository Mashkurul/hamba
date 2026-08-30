# =============================================================
# gui/pages.py - All Feature Pages
# =============================================================
# Each class is one "page" loaded into the content area:
#   DashboardPage, CowsPage, MilkPage, FoodPage,
#   HealthPage, EmployeesPage, ExpensesPage,
#   ReportsPage, AIPage, UsersPage
# =============================================================

import hashlib
import tkinter as tk
from tkinter import messagebox
from datetime import date
import customtkinter as ctk

from database import get_connection
from config   import (COW_STATUS_OPTIONS, GENDER_OPTIONS, FOOD_TYPES,
                      EMPLOYEE_ROLES, ATTENDANCE_STATUS, EXPENSE_CATEGORIES)
from gui.theme   import *
from gui.widgets import (PrimaryButton, DangerButton, SecondaryButton,
                         StyledLabel, StyledEntry, StyledCombo,
                         SectionCard, PageHeader, DataTable,
                         NotificationBar, StatCard, form_row)


def today():
    return str(date.today())


# =============================================================
# Base Page – all pages inherit from this
# =============================================================
class BasePage(ctk.CTkFrame):
    """Common base with notification bar support."""

    def __init__(self, master, user, **kwargs):
        super().__init__(master, fg_color=BG_DARK, corner_radius=0, **kwargs)
        self.user = user
        self.notify = NotificationBar(self)
        self.notify.pack(fill="x", padx=16, pady=(8, 0))

    def ok(self, msg):    self.notify.show(msg, "success")
    def err(self, msg):   self.notify.show(msg, "error")
    def info(self, msg):  self.notify.show(msg, "info")


# =============================================================
# Dashboard Page
# =============================================================
class DashboardPage(BasePage):
    """Overview with stat cards and recent activity."""

    def __init__(self, master, user):
        super().__init__(master, user)
        self._build()

    def _build(self):
        PageHeader(self, "Dashboard", "Welcome to HAMBA Farm Management").pack(
            anchor="w", padx=20, pady=(10, 16)
        )

        # Stats row
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20)

        stats = self._get_stats()

        cards_data = [
            ("Total Cows",     stats["cows"],     "🐄", PRIMARY),
            ("Active Cows",    stats["active"],   "✅", SUCCESS),
            ("Today's Milk",   f"{stats['milk_today']:.1f} L", "🥛", INFO),
            ("Employees",      stats["employees"],"👷", WARNING),
            ("This Month Rev", f"{stats['revenue']:.0f}", "💰", PRIMARY_LIGHT),
            ("Health Events",  stats["health"],   "💉", DANGER),
        ]

        for i, (title, value, icon, color) in enumerate(cards_data):
            card = StatCard(stats_frame, title=title, value=value, icon=icon, color=color)
            card.grid(row=0, column=i, padx=8, pady=4, sticky="ew")
            stats_frame.grid_columnconfigure(i, weight=1)

        # Two-column lower section
        lower = ctk.CTkFrame(self, fg_color="transparent")
        lower.pack(fill="both", expand=True, padx=20, pady=12)
        lower.grid_columnconfigure(0, weight=1)
        lower.grid_columnconfigure(1, weight=1)

        # Recent cows
        left_card = SectionCard(lower)
        left_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(left_card, text="Recent Cows", font=FONT_SUBHEAD,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(12, 4))

        cow_table = DataTable(left_card, [
            ("id", "ID", 40), ("name", "Name", 120),
            ("breed", "Breed", 100), ("status", "Status", 80)
        ])
        cow_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        cow_table.load(stats["recent_cows"])

        # Recent milk
        right_card = SectionCard(lower)
        right_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        ctk.CTkLabel(right_card, text="Recent Milk Records", font=FONT_SUBHEAD,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(12, 4))

        milk_table = DataTable(right_card, [
            ("cow", "Cow", 120), ("date", "Date", 90),
            ("liters", "Liters", 70), ("session", "Session", 80)
        ])
        milk_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        milk_table.load(stats["recent_milk"])

    def _get_stats(self):
        try:
            conn = get_connection()
            c    = conn.cursor()
            m    = today()[:7]  # YYYY-MM

            c.execute("SELECT COUNT(*) as n FROM cows")
            cows = c.fetchone()["n"]

            c.execute("SELECT COUNT(*) as n FROM cows WHERE status='Active'")
            active = c.fetchone()["n"]

            c.execute("SELECT COALESCE(SUM(liters),0) as n FROM milk WHERE date=?", (today(),))
            milk_today = c.fetchone()["n"]

            c.execute("SELECT COUNT(*) as n FROM employees WHERE status='Active'")
            employees = c.fetchone()["n"]

            c.execute(f"SELECT COALESCE(SUM(total_amount),0) as n FROM sales WHERE date LIKE '{m}%'")
            revenue = c.fetchone()["n"]

            c.execute(f"SELECT COUNT(*) as n FROM health WHERE date LIKE '{m}%'")
            health = c.fetchone()["n"]

            c.execute("SELECT id,name,breed,status FROM cows ORDER BY id DESC LIMIT 6")
            recent_cows = [tuple(r) for r in c.fetchall()]

            c.execute("""SELECT c.name, m.date, m.liters, m.session
                         FROM milk m JOIN cows c ON m.cow_id=c.id
                         ORDER BY m.id DESC LIMIT 6""")
            recent_milk = [tuple(r) for r in c.fetchall()]

            conn.close()
            return dict(cows=cows, active=active, milk_today=milk_today,
                        employees=employees, revenue=revenue, health=health,
                        recent_cows=recent_cows, recent_milk=recent_milk)
        except Exception as e:
            return dict(cows=0, active=0, milk_today=0, employees=0,
                        revenue=0, health=0, recent_cows=[], recent_milk=[])


# =============================================================
# Cows Page
# =============================================================
class CowsPage(BasePage):

    def __init__(self, master, user):
        super().__init__(master, user)
        self._build()

    def _build(self):
        PageHeader(self, "Cow Management", "Add, view, edit and delete cow records").pack(
            anchor="w", padx=20, pady=(10, 8)
        )

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=(0, 8))

        PrimaryButton(toolbar, "➕  Add Cow", self._open_add).pack(side="left", padx=(0, 8))

        self.search_var = ctk.StringVar()
        search_entry = StyledEntry(toolbar, "Search by name or ID...", width=220)
        search_entry.pack(side="left", padx=(0, 8))
        search_entry.bind("<KeyRelease>", lambda e: self._search(search_entry.get()))

        SecondaryButton(toolbar, "🔄 Refresh", self._load_data).pack(side="left")

        # Table
        card = SectionCard(self)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.table = DataTable(card, [
            ("id", "ID", 50), ("name", "Name", 120), ("breed", "Breed", 110),
            ("age", "Age", 60), ("weight", "Weight kg", 90),
            ("gender", "Gender", 80), ("color", "Color", 80),
            ("purchase_date", "Purchased", 100), ("status", "Status", 80)
        ])
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        # Action buttons
        action_bar = ctk.CTkFrame(card, fg_color="transparent")
        action_bar.pack(fill="x", padx=10, pady=(0, 10))

        PrimaryButton(action_bar, "✏️ Edit Selected", self._open_edit, width=160).pack(side="left", padx=(0, 8))
        DangerButton(action_bar,  "🗑️ Delete",        self._delete,    width=120).pack(side="left")

        self._all_rows = []
        self._load_data()

    def _load_data(self):
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT id,name,breed,age,weight,gender,color,purchase_date,status FROM cows ORDER BY id DESC")
            rows = [tuple(r) for r in c.fetchall()]
            conn.close()
            self._all_rows = rows
            self.table.load(rows)
        except Exception as e:
            self.err(str(e))

    def _search(self, keyword):
        keyword = keyword.lower()
        filtered = [r for r in self._all_rows
                    if keyword in str(r[0]).lower() or keyword in str(r[1]).lower()]
        self.table.load(filtered)

    def _open_add(self):
        CowFormDialog(self, user=self.user, on_save=self._on_saved)

    def _open_edit(self):
        row = self.table.get_selected()
        if not row:
            self.info("Please select a row to edit.")
            return
        CowFormDialog(self, user=self.user, cow_id=row[0], on_save=self._on_saved)

    def _delete(self):
        row = self.table.get_selected()
        if not row:
            self.info("Please select a row to delete.")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete cow '{row[1]}'?"):
            try:
                conn = get_connection()
                conn.cursor().execute("DELETE FROM cows WHERE id=?", (row[0],))
                conn.commit(); conn.close()
                self.ok(f"Cow '{row[1]}' deleted.")
                self._load_data()
            except Exception as e:
                self.err(str(e))

    def _on_saved(self, msg):
        self.ok(msg)
        self._load_data()


class CowFormDialog(ctk.CTkToplevel):
    """Add / Edit cow popup dialog."""

    def __init__(self, parent, user, on_save, cow_id=None):
        super().__init__(parent)
        self.cow_id  = cow_id
        self.on_save = on_save
        self.title("Edit Cow" if cow_id else "Add New Cow")
        self.geometry("500x560")
        self.resizable(False, False)
        self.configure(fg_color=BG_MEDIUM)
        self.grab_set()

        # Center over parent
        self.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        self.geometry(f"500x560+{px+100}+{py+60}")

        self._build()
        if cow_id:
            self._load_existing()

    def _build(self):
        ctk.CTkLabel(self, text="Cow Details", font=FONT_HEADING,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=(0, 12))

        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=24)

        def row(label, widget):
            form_row(f, label, widget)

        self.e_name  = StyledEntry(f, "Cow name", 280)
        self.e_breed = StyledEntry(f, "e.g. Friesian", 280)
        self.e_color = StyledEntry(f, "e.g. Black & White", 280)
        self.e_age   = StyledEntry(f, "Years", 280)
        self.e_weight= StyledEntry(f, "kg", 280)
        self.e_date  = StyledEntry(f, today(), 280)
        self.c_gender= StyledCombo(f, GENDER_OPTIONS, 280)
        self.c_status= StyledCombo(f, COW_STATUS_OPTIONS, 280)

        row("Cow Name *",   self.e_name)
        row("Breed",        self.e_breed)
        row("Color",        self.e_color)
        row("Age (years)",  self.e_age)
        row("Weight (kg)",  self.e_weight)
        row("Purchase Date",self.e_date)
        row("Gender",       self.c_gender)
        row("Status",       self.c_status)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=16)
        PrimaryButton(btn_row, "💾  Save",   self._save,   width=120).pack(side="left", padx=8)
        SecondaryButton(btn_row, "Cancel",   self.destroy, width=100).pack(side="left")

    def _load_existing(self):
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT * FROM cows WHERE id=?", (self.cow_id,))
            cow = c.fetchone()
            conn.close()
            if cow:
                self.e_name.insert(0, cow["name"]   or "")
                self.e_breed.insert(0, cow["breed"]  or "")
                self.e_color.insert(0, cow["color"]  or "")
                self.e_age.insert(0,  str(cow["age"] or ""))
                self.e_weight.insert(0, str(cow["weight"] or ""))
                self.e_date.insert(0, cow["purchase_date"] or "")
                self.c_gender.set(cow["gender"] or GENDER_OPTIONS[0])
                self.c_status.set(cow["status"] or "Active")
        except Exception as e:
            pass

    def _save(self):
        name   = self.e_name.get().strip()
        breed  = self.e_breed.get().strip()
        color  = self.e_color.get().strip()
        gender = self.c_gender.get()
        status = self.c_status.get()
        pdate  = self.e_date.get().strip() or today()

        if not name:
            messagebox.showwarning("Validation", "Cow name is required.")
            return
        try:
            age    = float(self.e_age.get()    or 0)
            weight = float(self.e_weight.get() or 0)
        except ValueError:
            messagebox.showwarning("Validation", "Age and Weight must be numbers.")
            return

        try:
            conn = get_connection()
            c    = conn.cursor()
            if self.cow_id:
                c.execute("""UPDATE cows SET name=?,breed=?,age=?,weight=?,
                             gender=?,color=?,purchase_date=?,status=? WHERE id=?""",
                          (name,breed,age,weight,gender,color,pdate,status,self.cow_id))
                msg = f"Cow '{name}' updated."
            else:
                c.execute("""INSERT INTO cows (name,breed,age,weight,gender,color,purchase_date,status)
                             VALUES (?,?,?,?,?,?,?,?)""",
                          (name,breed,age,weight,gender,color,pdate,status))
                msg = f"Cow '{name}' added."
            conn.commit(); conn.close()
            self.on_save(msg)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# =============================================================
# Milk Page
# =============================================================
class MilkPage(BasePage):

    def __init__(self, master, user):
        super().__init__(master, user)
        self._build()

    def _build(self):
        PageHeader(self, "Milk Management", "Record and track daily milk production").pack(
            anchor="w", padx=20, pady=(10, 8)
        )

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=(0, 8))
        PrimaryButton(toolbar, "➕  Record Milk", self._open_add).pack(side="left", padx=(0, 8))
        SecondaryButton(toolbar, "🔄 Refresh", self._load_data).pack(side="left")

        card = SectionCard(self)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.table = DataTable(card, [
            ("id","ID",50), ("cow","Cow",120), ("date","Date",100),
            ("liters","Liters (L)",90), ("session","Session",90), ("notes","Notes",200)
        ])
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        action_bar = ctk.CTkFrame(card, fg_color="transparent")
        action_bar.pack(fill="x", padx=10, pady=(0, 10))
        DangerButton(action_bar, "🗑️ Delete", self._delete, width=120).pack(side="left")

        self._load_data()

    def _load_data(self):
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("""SELECT m.id, c.name, m.date, m.liters, m.session, COALESCE(m.notes,'')
                         FROM milk m JOIN cows c ON m.cow_id=c.id ORDER BY m.id DESC""")
            self.table.load([tuple(r) for r in c.fetchall()])
            conn.close()
        except Exception as e:
            self.err(str(e))

    def _open_add(self):
        MilkFormDialog(self, on_save=lambda msg: (self.ok(msg), self._load_data()))

    def _delete(self):
        row = self.table.get_selected()
        if not row:
            self.info("Select a row first.")
            return
        if messagebox.askyesno("Confirm", "Delete this milk record?"):
            try:
                conn = get_connection()
                conn.cursor().execute("DELETE FROM milk WHERE id=?", (row[0],))
                conn.commit(); conn.close()
                self.ok("Record deleted.")
                self._load_data()
            except Exception as e:
                self.err(str(e))


class MilkFormDialog(ctk.CTkToplevel):

    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Record Milk Production")
        self.geometry("440x380")
        self.resizable(False, False)
        self.configure(fg_color=BG_MEDIUM)
        self.grab_set()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        self.geometry(f"440x380+{px+120}+{py+80}")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Record Milk", font=FONT_HEADING,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=(0, 12))

        # Load cow list
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT id, name FROM cows WHERE status='Active' ORDER BY name")
            cows = c.fetchall()
            conn.close()
            cow_options = [f"{r['id']} – {r['name']}" for r in cows]
        except:
            cow_options = []

        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=24)

        self.c_cow   = StyledCombo(f, cow_options or ["No active cows"], 280)
        self.e_date  = StyledEntry(f, today(), 280)
        self.e_date.insert(0, today())
        self.e_liters= StyledEntry(f, "e.g. 12.5", 280)
        self.c_session = StyledCombo(f, ["Morning","Afternoon","Evening"], 280)
        self.e_notes = StyledEntry(f, "Optional notes", 280)

        form_row(f, "Cow *",     self.c_cow)
        form_row(f, "Date",      self.e_date)
        form_row(f, "Liters *",  self.e_liters)
        form_row(f, "Session",   self.c_session)
        form_row(f, "Notes",     self.e_notes)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=16)
        PrimaryButton(btn_row, "💾 Save", self._save, width=120).pack(side="left", padx=8)
        SecondaryButton(btn_row, "Cancel", self.destroy, width=100).pack(side="left")

    def _save(self):
        cow_str = self.c_cow.get()
        if "–" not in cow_str:
            messagebox.showwarning("Validation", "Select a cow.")
            return
        cow_id = int(cow_str.split("–")[0].strip())
        dt     = self.e_date.get().strip() or today()
        session= self.c_session.get()
        notes  = self.e_notes.get().strip()
        try:
            liters = float(self.e_liters.get())
            if liters < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Enter a valid number for liters.")
            return
        try:
            conn = get_connection()
            conn.cursor().execute(
                "INSERT INTO milk (cow_id,date,liters,session,notes) VALUES (?,?,?,?,?)",
                (cow_id, dt, liters, session, notes)
            )
            conn.commit(); conn.close()
            self.on_save(f"Recorded {liters}L for cow ID {cow_id}.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# =============================================================
# Food Page
# =============================================================
class FoodPage(BasePage):

    def __init__(self, master, user):
        super().__init__(master, user)
        self._build()

    def _build(self):
        PageHeader(self, "Food Management", "Manage feed stock and daily feeding records").pack(
            anchor="w", padx=20, pady=(10, 8)
        )
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=(0, 8))
        PrimaryButton(toolbar, "➕ Add Feed", self._open_add).pack(side="left", padx=(0, 8))
        SecondaryButton(toolbar, "🔄 Refresh", self._load_data).pack(side="left")

        card = SectionCard(self)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.table = DataTable(card, [
            ("id","ID",50), ("type","Food Type",120), ("qty","Qty (kg)",90),
            ("date","Date",100), ("cow","Cow",100), ("notes","Notes",180)
        ])
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        action_bar = ctk.CTkFrame(card, fg_color="transparent")
        action_bar.pack(fill="x", padx=10, pady=(0, 10))
        DangerButton(action_bar, "🗑️ Delete", self._delete, width=120).pack(side="left")

        self._load_data()

    def _load_data(self):
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("""SELECT f.id, f.food_type, f.quantity_kg, f.date,
                                COALESCE(c.name,'All'), COALESCE(f.notes,'')
                         FROM food f LEFT JOIN cows c ON f.cow_id=c.id
                         ORDER BY f.id DESC""")
            self.table.load([tuple(r) for r in c.fetchall()])
            conn.close()
        except Exception as e:
            self.err(str(e))

    def _open_add(self):
        FoodFormDialog(self, on_save=lambda msg: (self.ok(msg), self._load_data()))

    def _delete(self):
        row = self.table.get_selected()
        if not row:
            self.info("Select a row first.")
            return
        if messagebox.askyesno("Confirm", "Delete this feed record?"):
            try:
                conn = get_connection()
                conn.cursor().execute("DELETE FROM food WHERE id=?", (row[0],))
                conn.commit(); conn.close()
                self.ok("Feed record deleted.")
                self._load_data()
            except Exception as e:
                self.err(str(e))


class FoodFormDialog(ctk.CTkToplevel):

    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Add Feed Record")
        self.geometry("440x360")
        self.resizable(False, False)
        self.configure(fg_color=BG_MEDIUM)
        self.grab_set()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        self.geometry(f"440x360+{px+120}+{py+80}")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Add Feed Record", font=FONT_HEADING,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=(0, 12))

        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT id, name FROM cows WHERE status='Active' ORDER BY name")
            cows = c.fetchall()
            conn.close()
            cow_options = ["All Cows"] + [f"{r['id']} – {r['name']}" for r in cows]
        except:
            cow_options = ["All Cows"]

        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=24)

        self.c_type  = StyledCombo(f, FOOD_TYPES, 280)
        self.e_qty   = StyledEntry(f, "kg", 280)
        self.e_date  = StyledEntry(f, today(), 280)
        self.e_date.insert(0, today())
        self.c_cow   = StyledCombo(f, cow_options, 280)
        self.e_notes = StyledEntry(f, "Optional", 280)

        form_row(f, "Food Type *", self.c_type)
        form_row(f, "Quantity (kg)*", self.e_qty)
        form_row(f, "Date",  self.e_date)
        form_row(f, "Cow",   self.c_cow)
        form_row(f, "Notes", self.e_notes)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=16)
        PrimaryButton(btn_row, "💾 Save", self._save, width=120).pack(side="left", padx=8)
        SecondaryButton(btn_row, "Cancel", self.destroy, width=100).pack(side="left")

    def _save(self):
        food_type = self.c_type.get()
        dt        = self.e_date.get().strip() or today()
        notes     = self.e_notes.get().strip()
        cow_str   = self.c_cow.get()
        cow_id    = None
        if "–" in cow_str:
            cow_id = int(cow_str.split("–")[0].strip())
        try:
            qty = float(self.e_qty.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Enter a valid quantity.")
            return
        try:
            conn = get_connection()
            conn.cursor().execute(
                "INSERT INTO food (food_type,quantity_kg,date,cow_id,notes) VALUES (?,?,?,?,?)",
                (food_type, qty, dt, cow_id, notes)
            )
            conn.commit(); conn.close()
            self.on_save(f"Added {qty}kg of {food_type}.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# =============================================================
# Health Page
# =============================================================
class HealthPage(BasePage):
    RECORD_TYPES = ["Vaccination", "Disease", "Medicine", "Checkup", "Other"]

    def __init__(self, master, user):
        super().__init__(master, user)
        self._build()

    def _build(self):
        PageHeader(self, "Health & Medicine", "Track vaccinations, diseases and treatments").pack(
            anchor="w", padx=20, pady=(10, 8)
        )
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=(0, 8))
        PrimaryButton(toolbar, "➕ Add Record", self._open_add).pack(side="left", padx=(0, 8))
        SecondaryButton(toolbar, "🔄 Refresh", self._load_data).pack(side="left")

        card = SectionCard(self)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.table = DataTable(card, [
            ("id","ID",50), ("cow","Cow",110), ("date","Date",95),
            ("type","Type",100), ("desc","Description",180),
            ("med","Medicine",110), ("vet","Vet",100), ("cost","Cost",70)
        ])
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        action_bar = ctk.CTkFrame(card, fg_color="transparent")
        action_bar.pack(fill="x", padx=10, pady=(0, 10))
        DangerButton(action_bar, "🗑️ Delete", self._delete, width=120).pack(side="left")
        self._load_data()

    def _load_data(self):
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("""SELECT h.id, c.name, h.date, h.record_type,
                                COALESCE(h.description,''), COALESCE(h.medicine,''),
                                COALESCE(h.vet_name,''), h.cost
                         FROM health h JOIN cows c ON h.cow_id=c.id
                         ORDER BY h.id DESC""")
            self.table.load([tuple(r) for r in c.fetchall()])
            conn.close()
        except Exception as e:
            self.err(str(e))

    def _open_add(self):
        HealthFormDialog(self, on_save=lambda msg: (self.ok(msg), self._load_data()))

    def _delete(self):
        row = self.table.get_selected()
        if not row:
            self.info("Select a record first.")
            return
        if messagebox.askyesno("Confirm", "Delete this health record?"):
            try:
                conn = get_connection()
                conn.cursor().execute("DELETE FROM health WHERE id=?", (row[0],))
                conn.commit(); conn.close()
                self.ok("Record deleted.")
                self._load_data()
            except Exception as e:
                self.err(str(e))


class HealthFormDialog(ctk.CTkToplevel):
    RECORD_TYPES = ["Vaccination","Disease","Medicine","Checkup","Other"]

    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Add Health Record")
        self.geometry("460x420")
        self.resizable(False, False)
        self.configure(fg_color=BG_MEDIUM)
        self.grab_set()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        self.geometry(f"460x420+{px+100}+{py+60}")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Health Record", font=FONT_HEADING,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=(0, 12))

        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT id, name FROM cows WHERE status='Active' ORDER BY name")
            cows = c.fetchall()
            conn.close()
            cow_options = [f"{r['id']} – {r['name']}" for r in cows]
        except:
            cow_options = []

        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=24)

        self.c_cow    = StyledCombo(f, cow_options or ["No cows"], 280)
        self.e_date   = StyledEntry(f, today(), 280)
        self.e_date.insert(0, today())
        self.c_type   = StyledCombo(f, self.RECORD_TYPES, 280)
        self.e_desc   = StyledEntry(f, "Symptoms / description", 280)
        self.e_med    = StyledEntry(f, "Medicine name", 280)
        self.e_vet    = StyledEntry(f, "Vet name", 280)
        self.e_cost   = StyledEntry(f, "0.00", 280)

        form_row(f, "Cow *",        self.c_cow)
        form_row(f, "Date",         self.e_date)
        form_row(f, "Record Type",  self.c_type)
        form_row(f, "Description",  self.e_desc)
        form_row(f, "Medicine",     self.e_med)
        form_row(f, "Vet Name",     self.e_vet)
        form_row(f, "Cost",         self.e_cost)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=16)
        PrimaryButton(btn_row, "💾 Save", self._save, width=120).pack(side="left", padx=8)
        SecondaryButton(btn_row, "Cancel", self.destroy, width=100).pack(side="left")

    def _save(self):
        cow_str = self.c_cow.get()
        if "–" not in cow_str:
            messagebox.showwarning("Validation", "Select a cow.")
            return
        cow_id = int(cow_str.split("–")[0].strip())
        dt     = self.e_date.get().strip() or today()
        rtype  = self.c_type.get()
        desc   = self.e_desc.get().strip()
        med    = self.e_med.get().strip()
        vet    = self.e_vet.get().strip()
        try:
            cost = float(self.e_cost.get() or 0)
        except ValueError:
            cost = 0.0
        try:
            conn = get_connection()
            conn.cursor().execute(
                "INSERT INTO health (cow_id,date,record_type,description,medicine,vet_name,cost) VALUES (?,?,?,?,?,?,?)",
                (cow_id, dt, rtype, desc, med, vet, cost)
            )
            conn.commit(); conn.close()
            self.on_save(f"Health record ({rtype}) saved.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# =============================================================
# Employees Page
# =============================================================
class EmployeesPage(BasePage):

    def __init__(self, master, user):
        super().__init__(master, user)
        self._build()

    def _build(self):
        PageHeader(self, "Employee Management", "Manage staff, attendance and salaries").pack(
            anchor="w", padx=20, pady=(10, 8)
        )

        # Tab-like buttons
        tab_bar = ctk.CTkFrame(self, fg_color="transparent")
        tab_bar.pack(fill="x", padx=20, pady=(0, 8))
        PrimaryButton(tab_bar, "👷 Employees",  self._show_employees, width=140).pack(side="left", padx=(0,6))
        SecondaryButton(tab_bar, "📋 Attendance", self._show_attendance, width=140).pack(side="left", padx=(0,6))
        SecondaryButton(tab_bar, "💵 Salary",    self._show_salary,    width=140).pack(side="left")

        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self._show_employees()

    def _clear(self):
        for w in self.content_area.winfo_children():
            w.destroy()

    def _show_employees(self):
        self._clear()
        toolbar = ctk.CTkFrame(self.content_area, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 8))
        PrimaryButton(toolbar, "➕ Add Employee", self._open_add).pack(side="left", padx=(0, 8))
        SecondaryButton(toolbar, "🔄 Refresh", self._show_employees).pack(side="left")

        card = SectionCard(self.content_area)
        card.pack(fill="both", expand=True)

        self.emp_table = DataTable(card, [
            ("id","ID",50), ("name","Name",140), ("role","Role",110),
            ("phone","Phone",110), ("salary","Salary",90),
            ("joined","Joined",100), ("status","Status",80)
        ])
        self.emp_table.pack(fill="both", expand=True, padx=10, pady=10)

        action_bar = ctk.CTkFrame(card, fg_color="transparent")
        action_bar.pack(fill="x", padx=10, pady=(0, 10))
        DangerButton(action_bar, "🗑️ Delete", self._delete_emp, width=120).pack(side="left")

        self._load_employees()

    def _load_employees(self):
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT id,name,role,phone,salary,join_date,status FROM employees ORDER BY id DESC")
            self.emp_table.load([tuple(r) for r in c.fetchall()])
            conn.close()
        except Exception as e:
            self.err(str(e))

    def _open_add(self):
        EmployeeFormDialog(self, on_save=lambda msg: (self.ok(msg), self._load_employees()))

    def _delete_emp(self):
        row = self.emp_table.get_selected()
        if not row:
            self.info("Select an employee first.")
            return
        if messagebox.askyesno("Confirm", f"Delete '{row[1]}'?"):
            try:
                conn = get_connection()
                conn.cursor().execute("DELETE FROM employees WHERE id=?", (row[0],))
                conn.commit(); conn.close()
                self.ok(f"'{row[1]}' deleted.")
                self._load_employees()
            except Exception as e:
                self.err(str(e))

    def _show_attendance(self):
        self._clear()
        toolbar = ctk.CTkFrame(self.content_area, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 8))
        PrimaryButton(toolbar, "➕ Mark Attendance", self._open_attendance).pack(side="left", padx=(0,8))
        SecondaryButton(toolbar, "🔄 Refresh", self._show_attendance).pack(side="left")

        card = SectionCard(self.content_area)
        card.pack(fill="both", expand=True)

        self.att_table = DataTable(card, [
            ("id","ID",50), ("emp","Employee",150), ("date","Date",100), ("status","Status",100)
        ])
        self.att_table.pack(fill="both", expand=True, padx=10, pady=10)
        self._load_attendance()

    def _load_attendance(self):
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("""SELECT a.id, e.name, a.date, a.status
                         FROM attendance a JOIN employees e ON a.employee_id=e.id
                         ORDER BY a.id DESC""")
            self.att_table.load([tuple(r) for r in c.fetchall()])
            conn.close()
        except Exception as e:
            self.err(str(e))

    def _open_attendance(self):
        AttendanceDialog(self, on_save=lambda msg: (self.ok(msg), self._load_attendance()))

    def _show_salary(self):
        self._clear()
        card = SectionCard(self.content_area)
        card.pack(fill="both", expand=True)
        ctk.CTkLabel(card, text="Salary Summary", font=FONT_SUBHEAD,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(12,4))

        sal_table = DataTable(card, [
            ("id","ID",50), ("name","Name",160), ("role","Role",110),
            ("salary","Salary",100), ("status","Status",80)
        ])
        sal_table.pack(fill="both", expand=True, padx=10, pady=(0, 4))

        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT id,name,role,salary,status FROM employees ORDER BY name")
            rows = [tuple(r) for r in c.fetchall()]
            conn.close()
            sal_table.load(rows)
            total = sum(r[3] for r in rows)
            ctk.CTkLabel(card, text=f"  Total Monthly Payroll:  {total:,.2f}",
                         font=FONT_SUBHEAD, text_color=SUCCESS).pack(anchor="w", padx=14, pady=(4,12))
        except Exception as e:
            self.err(str(e))


class EmployeeFormDialog(ctk.CTkToplevel):

    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Add Employee")
        self.geometry("440x380")
        self.resizable(False, False)
        self.configure(fg_color=BG_MEDIUM)
        self.grab_set()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        self.geometry(f"440x380+{px+120}+{py+60}")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Employee Details", font=FONT_HEADING,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=(0, 12))
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=24)

        self.e_name   = StyledEntry(f, "Full name", 280)
        self.c_role   = StyledCombo(f, EMPLOYEE_ROLES, 280)
        self.e_phone  = StyledEntry(f, "Phone number", 280)
        self.e_salary = StyledEntry(f, "Monthly salary", 280)
        self.e_date   = StyledEntry(f, today(), 280)
        self.e_date.insert(0, today())

        form_row(f, "Full Name *", self.e_name)
        form_row(f, "Role",        self.c_role)
        form_row(f, "Phone",       self.e_phone)
        form_row(f, "Salary",      self.e_salary)
        form_row(f, "Join Date",   self.e_date)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=16)
        PrimaryButton(btn_row, "💾 Save", self._save, width=120).pack(side="left", padx=8)
        SecondaryButton(btn_row, "Cancel", self.destroy, width=100).pack(side="left")

    def _save(self):
        name  = self.e_name.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Name is required.")
            return
        role  = self.c_role.get()
        phone = self.e_phone.get().strip()
        jdate = self.e_date.get().strip() or today()
        try:
            salary = float(self.e_salary.get() or 0)
        except ValueError:
            salary = 0.0
        try:
            conn = get_connection()
            conn.cursor().execute(
                "INSERT INTO employees (name,role,phone,salary,join_date,status) VALUES (?,?,?,?,?,'Active')",
                (name, role, phone, salary, jdate)
            )
            conn.commit(); conn.close()
            self.on_save(f"Employee '{name}' added.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


class AttendanceDialog(ctk.CTkToplevel):

    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Mark Attendance")
        self.geometry("400x280")
        self.resizable(False, False)
        self.configure(fg_color=BG_MEDIUM)
        self.grab_set()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        self.geometry(f"400x280+{px+150}+{py+100}")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Mark Attendance", font=FONT_HEADING,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=(0, 12))

        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT id, name FROM employees WHERE status='Active' ORDER BY name")
            emps = c.fetchall()
            conn.close()
            emp_options = [f"{r['id']} – {r['name']}" for r in emps]
        except:
            emp_options = []

        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=24)

        self.c_emp    = StyledCombo(f, emp_options or ["No employees"], 280)
        self.e_date   = StyledEntry(f, today(), 280)
        self.e_date.insert(0, today())
        self.c_status = StyledCombo(f, ATTENDANCE_STATUS, 280)

        form_row(f, "Employee *", self.c_emp)
        form_row(f, "Date",       self.e_date)
        form_row(f, "Status",     self.c_status)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=16)
        PrimaryButton(btn_row, "💾 Save", self._save, width=120).pack(side="left", padx=8)
        SecondaryButton(btn_row, "Cancel", self.destroy, width=100).pack(side="left")

    def _save(self):
        emp_str = self.c_emp.get()
        if "–" not in emp_str:
            messagebox.showwarning("Validation", "Select an employee.")
            return
        emp_id = int(emp_str.split("–")[0].strip())
        dt     = self.e_date.get().strip() or today()
        status = self.c_status.get()
        try:
            conn = get_connection()
            conn.cursor().execute(
                "INSERT INTO attendance (employee_id, date, status) VALUES (?,?,?)",
                (emp_id, dt, status)
            )
            conn.commit(); conn.close()
            self.on_save(f"Attendance marked: {status} on {dt}.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# =============================================================
# Expenses Page
# =============================================================
class ExpensesPage(BasePage):

    def __init__(self, master, user):
        super().__init__(master, user)
        self._build()

    def _build(self):
        PageHeader(self, "Expense & Sales", "Track farm expenses and milk sales").pack(
            anchor="w", padx=20, pady=(10, 8)
        )
        tab_bar = ctk.CTkFrame(self, fg_color="transparent")
        tab_bar.pack(fill="x", padx=20, pady=(0, 8))
        PrimaryButton(tab_bar, "💸 Expenses", self._show_expenses, width=140).pack(side="left", padx=(0,6))
        SecondaryButton(tab_bar, "🛒 Sales",   self._show_sales,   width=140).pack(side="left", padx=(0,6))
        SecondaryButton(tab_bar, "📊 Profit",  self._show_profit,  width=140).pack(side="left")

        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self._show_expenses()

    def _clear(self):
        for w in self.content_area.winfo_children():
            w.destroy()

    def _show_expenses(self):
        self._clear()
        toolbar = ctk.CTkFrame(self.content_area, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 8))
        PrimaryButton(toolbar, "➕ Add Expense", self._open_expense).pack(side="left", padx=(0,8))
        SecondaryButton(toolbar, "🔄 Refresh", self._show_expenses).pack(side="left")

        card = SectionCard(self.content_area)
        card.pack(fill="both", expand=True)

        self.exp_table = DataTable(card, [
            ("id","ID",50), ("date","Date",100), ("cat","Category",110),
            ("amount","Amount",90), ("desc","Description",220)
        ])
        self.exp_table.pack(fill="both", expand=True, padx=10, pady=10)

        action_bar = ctk.CTkFrame(card, fg_color="transparent")
        action_bar.pack(fill="x", padx=10, pady=(0,10))
        DangerButton(action_bar, "🗑️ Delete", self._delete_exp, width=120).pack(side="left")

        self._load_expenses()

    def _load_expenses(self):
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT id,date,category,amount,COALESCE(description,'') FROM expenses ORDER BY id DESC")
            rows = [tuple(r) for r in c.fetchall()]
            conn.close()
            self.exp_table.load(rows)
        except Exception as e:
            self.err(str(e))

    def _open_expense(self):
        ExpenseFormDialog(self, on_save=lambda msg: (self.ok(msg), self._load_expenses()))

    def _delete_exp(self):
        row = self.exp_table.get_selected()
        if not row:
            self.info("Select a row first.")
            return
        if messagebox.askyesno("Confirm", "Delete this expense?"):
            try:
                conn = get_connection()
                conn.cursor().execute("DELETE FROM expenses WHERE id=?", (row[0],))
                conn.commit(); conn.close()
                self.ok("Expense deleted.")
                self._load_expenses()
            except Exception as e:
                self.err(str(e))

    def _show_sales(self):
        self._clear()
        toolbar = ctk.CTkFrame(self.content_area, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 8))
        PrimaryButton(toolbar, "➕ Record Sale", self._open_sale).pack(side="left", padx=(0,8))
        SecondaryButton(toolbar, "🔄 Refresh", self._show_sales).pack(side="left")

        card = SectionCard(self.content_area)
        card.pack(fill="both", expand=True)

        self.sale_table = DataTable(card, [
            ("id","ID",50), ("date","Date",100), ("liters","Liters",80),
            ("price","Price/L",80), ("total","Total",90), ("buyer","Buyer",130), ("notes","Notes",150)
        ])
        self.sale_table.pack(fill="both", expand=True, padx=10, pady=10)
        self._load_sales()

    def _load_sales(self):
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT id,date,liters_sold,price_per_liter,total_amount,COALESCE(buyer_name,''),COALESCE(notes,'') FROM sales ORDER BY id DESC")
            self.sale_table.load([tuple(r) for r in c.fetchall()])
            conn.close()
        except Exception as e:
            self.err(str(e))

    def _open_sale(self):
        SaleFormDialog(self, on_save=lambda msg: (self.ok(msg), self._load_sales()))

    def _show_profit(self):
        self._clear()
        card = SectionCard(self.content_area)
        card.pack(fill="both", expand=True)
        ctk.CTkLabel(card, text="Profit Calculator", font=FONT_SUBHEAD,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(14, 4))

        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(row1, text="Start Date:", font=FONT_BODY, text_color=TEXT_SECONDARY, width=100).pack(side="left")
        self.p_start = StyledEntry(row1, "YYYY-MM-DD", 180)
        self.p_start.pack(side="left", padx=8)
        ctk.CTkLabel(row1, text="End Date:", font=FONT_BODY, text_color=TEXT_SECONDARY, width=80).pack(side="left")
        self.p_end = StyledEntry(row1, "YYYY-MM-DD", 180)
        self.p_end.pack(side="left", padx=8)
        PrimaryButton(row1, "Calculate", self._calc_profit, width=120).pack(side="left", padx=8)

        self.profit_result = ctk.CTkLabel(card, text="", font=("Segoe UI", 18, "bold"),
                                          text_color=SUCCESS)
        self.profit_result.pack(pady=16)

    def _calc_profit(self):
        start = self.p_start.get().strip()
        end   = self.p_end.get().strip()
        if not start or not end:
            self.err("Enter both dates.")
            return
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT COALESCE(SUM(total_amount),0) FROM sales WHERE date BETWEEN ? AND ?", (start, end))
            revenue = c.fetchone()[0]
            c.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date BETWEEN ? AND ?", (start, end))
            expenses = c.fetchone()[0]
            conn.close()
            profit = revenue - expenses
            sign   = "+" if profit >= 0 else ""
            color  = SUCCESS if profit >= 0 else DANGER
            self.profit_result.configure(
                text=f"Revenue: {revenue:,.2f}   Expenses: {expenses:,.2f}   Net: {sign}{profit:,.2f}",
                text_color=color
            )
        except Exception as e:
            self.err(str(e))


class ExpenseFormDialog(ctk.CTkToplevel):

    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Add Expense")
        self.geometry("420x320")
        self.resizable(False, False)
        self.configure(fg_color=BG_MEDIUM)
        self.grab_set()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        self.geometry(f"420x320+{px+130}+{py+80}")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Add Expense", font=FONT_HEADING,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=(0, 12))
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=24)

        self.e_date  = StyledEntry(f, today(), 280)
        self.e_date.insert(0, today())
        self.c_cat   = StyledCombo(f, EXPENSE_CATEGORIES, 280)
        self.e_amount= StyledEntry(f, "Amount", 280)
        self.e_desc  = StyledEntry(f, "Description", 280)

        form_row(f, "Date *",       self.e_date)
        form_row(f, "Category *",   self.c_cat)
        form_row(f, "Amount *",     self.e_amount)
        form_row(f, "Description",  self.e_desc)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=16)
        PrimaryButton(btn_row, "💾 Save", self._save, width=120).pack(side="left", padx=8)
        SecondaryButton(btn_row, "Cancel", self.destroy, width=100).pack(side="left")

    def _save(self):
        dt   = self.e_date.get().strip() or today()
        cat  = self.c_cat.get()
        desc = self.e_desc.get().strip()
        try:
            amount = float(self.e_amount.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Enter a valid amount.")
            return
        try:
            conn = get_connection()
            conn.cursor().execute(
                "INSERT INTO expenses (date,category,amount,description) VALUES (?,?,?,?)",
                (dt, cat, amount, desc)
            )
            conn.commit(); conn.close()
            self.on_save(f"Expense {cat} {amount:.2f} saved.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


class SaleFormDialog(ctk.CTkToplevel):

    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Record Milk Sale")
        self.geometry("420x360")
        self.resizable(False, False)
        self.configure(fg_color=BG_MEDIUM)
        self.grab_set()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        self.geometry(f"420x360+{px+130}+{py+60}")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Record Milk Sale", font=FONT_HEADING,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=(0, 12))
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=24)

        self.e_date   = StyledEntry(f, today(), 280)
        self.e_date.insert(0, today())
        self.e_liters = StyledEntry(f, "Liters sold", 280)
        self.e_price  = StyledEntry(f, "Price per liter", 280)
        self.e_buyer  = StyledEntry(f, "Buyer name", 280)
        self.e_notes  = StyledEntry(f, "Notes", 280)

        form_row(f, "Date *",        self.e_date)
        form_row(f, "Liters *",      self.e_liters)
        form_row(f, "Price/Liter *", self.e_price)
        form_row(f, "Buyer",         self.e_buyer)
        form_row(f, "Notes",         self.e_notes)

        self.total_label = ctk.CTkLabel(f, text="Total: –", font=FONT_SUBHEAD,
                                        text_color=SUCCESS)
        self.total_label.pack(anchor="w", padx=0, pady=(8,0))

        self.e_liters.bind("<KeyRelease>", self._update_total)
        self.e_price.bind("<KeyRelease>",  self._update_total)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=12)
        PrimaryButton(btn_row, "💾 Save", self._save, width=120).pack(side="left", padx=8)
        SecondaryButton(btn_row, "Cancel", self.destroy, width=100).pack(side="left")

    def _update_total(self, *_):
        try:
            l = float(self.e_liters.get())
            p = float(self.e_price.get())
            self.total_label.configure(text=f"Total: {l*p:,.2f}")
        except:
            self.total_label.configure(text="Total: –")

    def _save(self):
        dt    = self.e_date.get().strip() or today()
        buyer = self.e_buyer.get().strip()
        notes = self.e_notes.get().strip()
        try:
            liters = float(self.e_liters.get())
            price  = float(self.e_price.get())
            if liters <= 0 or price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Enter valid liters and price.")
            return
        total = liters * price
        try:
            conn = get_connection()
            conn.cursor().execute(
                "INSERT INTO sales (date,liters_sold,price_per_liter,total_amount,buyer_name,notes) VALUES (?,?,?,?,?,?)",
                (dt, liters, price, total, buyer, notes)
            )
            conn.commit(); conn.close()
            self.on_save(f"Sale recorded: {liters}L = {total:.2f}")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# =============================================================
# Reports Page
# =============================================================
class ReportsPage(BasePage):

    def __init__(self, master, user):
        super().__init__(master, user)
        self._build()

    def _build(self):
        PageHeader(self, "Reports", "Generate daily, monthly, and summary reports").pack(
            anchor="w", padx=20, pady=(10, 8)
        )

        # Controls row
        ctrl = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=10)
        ctrl.pack(fill="x", padx=20, pady=(0, 8))

        inner = ctk.CTkFrame(ctrl, fg_color="transparent")
        inner.pack(padx=16, pady=12, fill="x")

        ctk.CTkLabel(inner, text="Report Type:", font=FONT_BODY,
                     text_color=TEXT_SECONDARY).pack(side="left")
        self.report_type = StyledCombo(inner, [
            "Daily Report", "Monthly Report",
            "Milk Production", "Expense Report"
        ], width=200)
        self.report_type.pack(side="left", padx=8)

        ctk.CTkLabel(inner, text="From:", font=FONT_BODY,
                     text_color=TEXT_SECONDARY).pack(side="left", padx=(16,4))
        self.r_start = StyledEntry(inner, "YYYY-MM-DD", 130)
        self.r_start.pack(side="left")

        ctk.CTkLabel(inner, text="To:", font=FONT_BODY,
                     text_color=TEXT_SECONDARY).pack(side="left", padx=(8,4))
        self.r_end = StyledEntry(inner, "YYYY-MM-DD", 130)
        self.r_end.pack(side="left")

        PrimaryButton(inner, "📊 Generate", self._generate, width=130).pack(side="left", padx=12)

        # Output area
        out_card = SectionCard(self)
        out_card.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.output = ctk.CTkTextbox(
            out_card,
            fg_color=INPUT_BG,
            text_color=TEXT_PRIMARY,
            font=("Courier New", 11),
            border_color=BORDER,
            border_width=1,
            corner_radius=6
        )
        self.output.pack(fill="both", expand=True, padx=10, pady=10)
        self.output.configure(state="disabled")

    def _write(self, text):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", text)
        self.output.configure(state="disabled")

    def _generate(self):
        rtype  = self.report_type.get()
        start  = self.r_start.get().strip()
        end    = self.r_end.get().strip()

        if "Daily" in rtype:
            dt = start or today()
            self._write(self._daily_report(dt))
        elif "Monthly" in rtype:
            month = start[:7] if start else today()[:7]
            self._write(self._monthly_report(month))
        elif "Milk" in rtype:
            if not start or not end:
                self.err("Enter start and end dates.")
                return
            self._write(self._milk_report(start, end))
        elif "Expense" in rtype:
            if not start or not end:
                self.err("Enter start and end dates.")
                return
            self._write(self._expense_report(start, end))

    def _daily_report(self, dt):
        try:
            conn = get_connection()
            c    = conn.cursor()
            lines = [f"{'='*55}", f"  DAILY REPORT  –  {dt}", f"{'='*55}\n"]

            c.execute("""SELECT c.name, m.liters, m.session FROM milk m
                         JOIN cows c ON m.cow_id=c.id WHERE m.date=?""", (dt,))
            milk = c.fetchall()
            total_milk = sum(r[1] for r in milk)
            lines.append("[ MILK PRODUCTION ]")
            for r in milk:
                lines.append(f"  {r[0]:<18} {r[2]:<12} {r[1]} L")
            lines.append(f"  Total: {total_milk:.2f} L\n")

            c.execute("SELECT category, amount, description FROM expenses WHERE date=?", (dt,))
            expenses = c.fetchall()
            total_exp = sum(r[1] for r in expenses)
            lines.append("[ EXPENSES ]")
            for r in expenses:
                lines.append(f"  {r[0]:<18} {r[1]:>10.2f}  {r[2]}")
            lines.append(f"  Total: {total_exp:.2f}\n")

            c.execute("SELECT liters_sold, price_per_liter, total_amount, buyer_name FROM sales WHERE date=?", (dt,))
            sales = c.fetchall()
            total_sales = sum(r[2] for r in sales)
            lines.append("[ SALES ]")
            for r in sales:
                lines.append(f"  {r[3] or 'N/A':<18} {r[0]}L × {r[1]} = {r[2]:.2f}")
            lines.append(f"  Total: {total_sales:.2f}\n")

            net = total_sales - total_exp
            sign = "+" if net >= 0 else ""
            lines.append(f"{'─'*55}")
            lines.append(f"  Net Profit / Loss: {sign}{net:.2f}")

            conn.close()
            return "\n".join(lines)
        except Exception as e:
            return f"Error: {e}"

    def _monthly_report(self, month):
        start = f"{month}-01"; end = f"{month}-31"
        try:
            conn = get_connection()
            c    = conn.cursor()
            lines = [f"{'='*55}", f"  MONTHLY REPORT  –  {month}", f"{'='*55}\n"]

            c.execute("SELECT COUNT(*) FROM cows WHERE status='Active'")
            lines.append(f"  Active Cows     : {c.fetchone()[0]}")

            c.execute("SELECT COALESCE(SUM(liters),0), COUNT(*) FROM milk WHERE date BETWEEN ? AND ?", (start,end))
            r = c.fetchone(); lines.append(f"  Milk Produced   : {r[0]:.2f} L  ({r[1]} sessions)")

            c.execute("SELECT COALESCE(SUM(total_amount),0), COALESCE(SUM(liters_sold),0) FROM sales WHERE date BETWEEN ? AND ?", (start,end))
            r = c.fetchone(); rev = r[0]; liters_sold = r[1]
            lines.append(f"  Milk Sold       : {liters_sold:.2f} L")
            lines.append(f"  Total Revenue   : {rev:.2f}")

            c.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date BETWEEN ? AND ?", (start,end))
            exp = c.fetchone()[0]
            lines.append(f"  Total Expenses  : {exp:.2f}")

            c.execute("SELECT COUNT(*) FROM health WHERE date BETWEEN ? AND ?", (start,end))
            lines.append(f"  Health Events   : {c.fetchone()[0]}")

            net  = rev - exp
            sign = "+" if net >= 0 else ""
            lines.append(f"\n{'─'*55}")
            lines.append(f"  Net Profit/Loss : {sign}{net:.2f}")

            conn.close()
            return "\n".join(lines)
        except Exception as e:
            return f"Error: {e}"

    def _milk_report(self, start, end):
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("""SELECT c.name, SUM(m.liters), COUNT(*) FROM milk m
                         JOIN cows c ON m.cow_id=c.id
                         WHERE m.date BETWEEN ? AND ?
                         GROUP BY m.cow_id ORDER BY SUM(m.liters) DESC""", (start,end))
            rows = c.fetchall()
            conn.close()
            lines = [f"{'='*55}", f"  MILK PRODUCTION  –  {start} to {end}", f"{'='*55}",
                     f"  {'Cow':<22} {'Sessions':>10} {'Total (L)':>12}", "─"*55]
            grand = 0.0
            for r in rows:
                lines.append(f"  {r[0]:<22} {r[2]:>10} {r[1]:>12.2f}")
                grand += r[1]
            lines.append("─"*55)
            lines.append(f"  {'GRAND TOTAL':<22} {'':>10} {grand:>12.2f} L")
            return "\n".join(lines)
        except Exception as e:
            return f"Error: {e}"

    def _expense_report(self, start, end):
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("""SELECT category, SUM(amount), COUNT(*) FROM expenses
                         WHERE date BETWEEN ? AND ?
                         GROUP BY category ORDER BY SUM(amount) DESC""", (start,end))
            rows = c.fetchall()
            conn.close()
            lines = [f"{'='*55}", f"  EXPENSE REPORT  –  {start} to {end}", f"{'='*55}",
                     f"  {'Category':<18} {'Count':>8} {'Amount':>14}", "─"*55]
            total = 0.0
            for r in rows:
                lines.append(f"  {r[0]:<18} {r[2]:>8} {r[1]:>14.2f}")
                total += r[1]
            lines.append("─"*55)
            lines.append(f"  {'TOTAL':<18} {'':>8} {total:>14.2f}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error: {e}"


# =============================================================
# AI Assistant Page
# =============================================================
class AIPage(BasePage):

    def __init__(self, master, user):
        super().__init__(master, user)
        self._build()

    def _build(self):
        PageHeader(self, "AI Assistant", "Rule-based smart analysis for your farm").pack(
            anchor="w", padx=20, pady=(10, 8)
        )

        # Button row
        btn_row = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=10)
        btn_row.pack(fill="x", padx=20, pady=(0, 8))
        inner = ctk.CTkFrame(btn_row, fg_color="transparent")
        inner.pack(padx=12, pady=10)

        PrimaryButton(inner,   "🥛 Milk Analysis",    self._milk_analysis,   width=150).pack(side="left", padx=6)
        SecondaryButton(inner, "⚖️  Weight Check",     self._weight_check,    width=140).pack(side="left", padx=6)
        SecondaryButton(inner, "💉 Health Events",    self._health_events,   width=140).pack(side="left", padx=6)
        SecondaryButton(inner, "🔬 Symptom Checker",  self._symptom_checker, width=150).pack(side="left", padx=6)
        SecondaryButton(inner, "💡 Farm Tips",        self._farm_tips,       width=120).pack(side="left", padx=6)

        # Output card
        out_card = SectionCard(self)
        out_card.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        ctk.CTkLabel(out_card, text="🤖 AI Suggestions", font=FONT_SUBHEAD,
                     text_color=PRIMARY_LIGHT).pack(anchor="w", padx=14, pady=(12,4))

        self.output = ctk.CTkTextbox(
            out_card,
            fg_color=INPUT_BG,
            text_color=TEXT_PRIMARY,
            font=("Segoe UI", 11),
            border_color=BORDER,
            border_width=1,
            corner_radius=6
        )
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.output.configure(state="disabled")

        # Symptom input area (hidden by default)
        self.symptom_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=8)
        self.sym_entry = StyledEntry(self.symptom_frame, "Type symptoms here (e.g. fever, cough)...", width=400)
        self.sym_entry.pack(side="left", padx=12, pady=10)
        PrimaryButton(self.symptom_frame, "Analyze", self._run_symptom, width=100).pack(side="left", padx=8, pady=10)

        self._write("Click any button above to get AI-powered suggestions.\n\nHAMBA AI analyzes your farm data and provides smart recommendations based on rules and patterns.")

    def _write(self, text):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", text)
        self.output.configure(state="disabled")

    def _milk_analysis(self):
        self.symptom_frame.pack_forget()
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT AVG(liters) FROM milk WHERE date >= date('now', '-3 days')")
            recent = c.fetchone()[0] or 0.0
            c.execute("SELECT AVG(liters) FROM milk WHERE date >= date('now','-10 days') AND date < date('now','-3 days')")
            prev   = c.fetchone()[0] or 0.0
            conn.close()

            lines = ["🥛 MILK PRODUCTION ANALYSIS\n" + "─"*50]
            lines.append(f"  Recent avg  (last 3 days) : {recent:.2f} L/session")
            lines.append(f"  Previous avg (last 7 days): {prev:.2f} L/session\n")

            if prev > 0 and recent < prev * 0.85:
                drop = ((prev - recent) / prev) * 100
                lines.append(f"  ⚠ ALERT: Production dropped by {drop:.1f}%!\n")
                lines.append("  RECOMMENDATIONS:")
                lines.append("  1. Increase protein-rich feed (concentrate, soy)")
                lines.append("  2. Ensure cows have unlimited clean water")
                lines.append("  3. Check for signs of illness or stress")
                lines.append("  4. Review milking schedule consistency")
                lines.append("  5. Consult a veterinarian if drop persists")
            elif recent == 0:
                lines.append("  ℹ Not enough data. Record more milk entries.")
            else:
                lines.append("  ✅ Milk production is STABLE.")
                lines.append("  Keep maintaining the current feeding & milking schedule.")

            self._write("\n".join(lines))
        except Exception as e:
            self._write(f"Error: {e}")

    def _weight_check(self):
        self.symptom_frame.pack_forget()
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT id, name, weight, breed FROM cows WHERE status='Active'")
            cows = c.fetchall()
            conn.close()

            lines = ["⚖️  COW WEIGHT ANALYSIS\n" + "─"*50]
            if not cows:
                lines.append("  No active cows found.")
                self._write("\n".join(lines)); return

            underweight = [r for r in cows if r[2] < 300]
            healthy     = [r for r in cows if r[2] >= 300]
            lines.append(f"  Total Active Cows    : {len(cows)}")
            lines.append(f"  Healthy (≥300kg)     : {len(healthy)}")
            lines.append(f"  Underweight (<300kg) : {len(underweight)}\n")

            if underweight:
                lines.append("  UNDERWEIGHT COWS:")
                for r in underweight:
                    lines.append(f"  → {r[1]:<18} {r[2]} kg  (ID:{r[0]})")
                lines.append("\n  ⚠ RECOMMENDATIONS:")
                lines.append("  1. Increase daily hay and concentrate rations")
                lines.append("  2. Add mineral & vitamin supplements")
                lines.append("  3. Check for parasites or underlying illness")
                lines.append("  4. Monitor weight every 2 weeks")
            else:
                lines.append("  ✅ All cows are at a HEALTHY weight. Great job!")

            self._write("\n".join(lines))
        except Exception as e:
            self._write(f"Error: {e}")

    def _health_events(self):
        self.symptom_frame.pack_forget()
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("""SELECT h.record_type, c.name, h.date, h.description
                         FROM health h JOIN cows c ON h.cow_id=c.id
                         WHERE h.date >= date('now','-7 days') ORDER BY h.date DESC""")
            records = c.fetchall()
            conn.close()

            lines = ["💉 HEALTH EVENT ANALYSIS (Last 7 Days)\n" + "─"*50]
            lines.append(f"  Events found: {len(records)}\n")

            if not records:
                lines.append("  ✅ No health events this week. Farm looks healthy!")
                lines.append("  Reminder: Schedule routine vaccinations if due.")
                self._write("\n".join(lines)); return

            for r in records:
                lines.append(f"  [{r[0]}] {r[1]:<18} {r[2]}  –  {r[3] or 'N/A'}")

            diseases = [r for r in records if r[0] == "Disease"]
            if len(diseases) >= 3:
                lines.append(f"\n  🚨 OUTBREAK ALERT: {len(diseases)} disease cases!")
                lines.append("  → Isolate affected cows IMMEDIATELY")
                lines.append("  → Contact veterinarian urgently")
                lines.append("  → Disinfect barn and water sources")
            else:
                lines.append("\n  Monitor affected cows closely.")
                lines.append("  Consult a vet if symptoms worsen.")

            self._write("\n".join(lines))
        except Exception as e:
            self._write(f"Error: {e}")

    def _symptom_checker(self):
        self.symptom_frame.pack(fill="x", padx=20, pady=(0, 8))
        self.sym_entry.delete(0, "end")
        self._write("Enter symptoms in the box below and click Analyze.\n\nExamples: fever, cough, not eating, limping, diarrhea")

    def _run_symptom(self):
        symptoms = self.sym_entry.get().strip().lower()
        if not symptoms:
            self.err("Please enter symptoms.")
            return

        results = []
        if "fever" in symptoms:
            results.append("🌡 FEVER: Contact a veterinarian immediately.\n   Isolate the cow and monitor temperature every 2 hours.")
        if "cough" in symptoms:
            results.append("😮‍💨 COUGH: Isolate the affected cow from the herd.\n   Schedule a medical check-up as soon as possible.")
        if "diarrhea" in symptoms or "loose stool" in symptoms:
            results.append("💧 DIARRHEA: Ensure clean water, reduce concentrate.\n   Consult vet if it persists beyond 24 hours.")
        if "limping" in symptoms or "lame" in symptoms:
            results.append("🦶 LAMENESS: Check hooves for injury or infection.\n   Limit movement and apply hoof treatment.")
        if "not eating" in symptoms or "loss of appetite" in symptoms:
            results.append("🍽 APPETITE LOSS: Check for fever or dental issues.\n   Offer fresh green feed. Vet consult if >2 days.")
        if not results:
            results.append("✅ No specific issues detected.\n   Monitor closely and consult a vet if condition worsens.")

        lines = [f"🔬 SYMPTOM ANALYSIS: '{symptoms}'\n" + "─"*50]
        for r in results:
            lines.append(f"\n  {r}")
        self._write("\n".join(lines))

    def _farm_tips(self):
        self.symptom_frame.pack_forget()
        tips = [
            ("🕐", "Feed cows at the same time every day – routine reduces stress."),
            ("💧", "Ensure every cow has access to clean, fresh water at all times."),
            ("🧹", "Clean barn floors daily to prevent hoof disease and infection."),
            ("💉", "Vaccinate cows regularly – consult your vet for a schedule."),
            ("📋", "Record milk production daily to detect drops early."),
            ("⚖️ ", "Weigh cows monthly to monitor nutrition and growth."),
            ("🔴", "Separate sick cows immediately to prevent disease spreading."),
            ("🌬", "Ensure proper barn ventilation to prevent respiratory issues."),
            ("🦶", "Check and trim hooves every 2–3 months."),
            ("😌", "A stress-free environment leads to higher milk production."),
        ]
        lines = ["💡 GENERAL FARM TIPS\n" + "─"*50]
        for i, (icon, tip) in enumerate(tips, 1):
            lines.append(f"  {i:>2}. {icon}  {tip}")
        self._write("\n".join(lines))


# =============================================================
# Users Page (Admin Only)
# =============================================================
class UsersPage(BasePage):

    def __init__(self, master, user):
        super().__init__(master, user)
        if user["role"] != "admin":
            StyledLabel(self, "Access Denied", text_color=DANGER).pack(pady=40)
            return
        self._build()

    def _build(self):
        PageHeader(self, "User Management", "Create and manage system user accounts (Admin only)").pack(
            anchor="w", padx=20, pady=(10, 8)
        )
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=(0, 8))
        PrimaryButton(toolbar, "➕ Create User", self._open_create).pack(side="left", padx=(0,8))
        SecondaryButton(toolbar, "🔄 Refresh", self._load_data).pack(side="left")

        card = SectionCard(self)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.table = DataTable(card, [
            ("id","ID",50), ("username","Username",130), ("name","Full Name",160),
            ("role","Role",100), ("active","Active",70), ("created_by","Created By",120)
        ])
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        action_bar = ctk.CTkFrame(card, fg_color="transparent")
        action_bar.pack(fill="x", padx=10, pady=(0,10))
        PrimaryButton(action_bar, "✅ Activate",   self._activate,    width=120).pack(side="left", padx=(0,8))
        DangerButton(action_bar,  "🚫 Deactivate", self._deactivate,  width=130).pack(side="left")

        self._load_data()

    def _load_data(self):
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT id,username,full_name,role,is_active,created_by FROM users ORDER BY id")
            rows = [(r[0], r[1], r[2] or "", r[3], "Yes" if r[4] else "No", r[5]) for r in c.fetchall()]
            conn.close()
            self.table.load(rows)
        except Exception as e:
            self.err(str(e))

    def _open_create(self):
        CreateUserDialog(self, current_user=self.user,
                         on_save=lambda msg: (self.ok(msg), self._load_data()))

    def _deactivate(self):
        row = self.table.get_selected()
        if not row:
            self.info("Select a user first.")
            return
        if row[0] == self.user["id"]:
            self.err("You cannot deactivate your own account.")
            return
        if messagebox.askyesno("Confirm", f"Deactivate user '{row[1]}'?"):
            try:
                conn = get_connection()
                conn.cursor().execute("UPDATE users SET is_active=0 WHERE id=?", (row[0],))
                conn.commit(); conn.close()
                self.ok(f"User '{row[1]}' deactivated.")
                self._load_data()
            except Exception as e:
                self.err(str(e))

    def _activate(self):
        row = self.table.get_selected()
        if not row:
            self.info("Select a user first.")
            return
        try:
            conn = get_connection()
            conn.cursor().execute("UPDATE users SET is_active=1 WHERE id=?", (row[0],))
            conn.commit(); conn.close()
            self.ok(f"User '{row[1]}' activated.")
            self._load_data()
        except Exception as e:
            self.err(str(e))


class CreateUserDialog(ctk.CTkToplevel):

    def __init__(self, parent, current_user, on_save):
        super().__init__(parent)
        self.current_user = current_user
        self.on_save      = on_save
        self.title("Create New User")
        self.geometry("440x380")
        self.resizable(False, False)
        self.configure(fg_color=BG_MEDIUM)
        self.grab_set()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        self.geometry(f"440x380+{px+120}+{py+80}")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Create User Account", font=FONT_HEADING,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(self, text="Admin can create Worker and Salesman accounts only.",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w", padx=24)
        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=(8, 12))

        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=24)

        self.e_username = StyledEntry(f, "Username", 280)
        self.e_fullname = StyledEntry(f, "Full name", 280)
        self.c_role     = StyledCombo(f, ["worker", "salesman"], 280)
        self.e_password = StyledEntry(f, "Password (min 4 chars)", 280, show="●")
        self.e_confirm  = StyledEntry(f, "Confirm password", 280, show="●")

        form_row(f, "Username *",  self.e_username)
        form_row(f, "Full Name",   self.e_fullname)
        form_row(f, "Role *",      self.c_role)
        form_row(f, "Password *",  self.e_password)
        form_row(f, "Confirm *",   self.e_confirm)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=16)
        PrimaryButton(btn_row, "💾 Create", self._save, width=120).pack(side="left", padx=8)
        SecondaryButton(btn_row, "Cancel", self.destroy, width=100).pack(side="left")

    def _save(self):
        username = self.e_username.get().strip()
        fullname = self.e_fullname.get().strip()
        role     = self.c_role.get()
        password = self.e_password.get()
        confirm  = self.e_confirm.get()

        if not username:
            messagebox.showwarning("Validation", "Username is required.")
            return
        if len(password) < 4:
            messagebox.showwarning("Validation", "Password must be at least 4 characters.")
            return
        if password != confirm:
            messagebox.showwarning("Validation", "Passwords do not match.")
            return

        hashed = hashlib.sha256(password.encode()).hexdigest()
        try:
            conn = get_connection()
            c    = conn.cursor()
            c.execute("SELECT id FROM users WHERE username=?", (username,))
            if c.fetchone():
                messagebox.showwarning("Validation", f"Username '{username}' already exists.")
                conn.close()
                return
            c.execute("""INSERT INTO users (username,password,role,full_name,created_by)
                         VALUES (?,?,?,?,?)""",
                      (username, hashed, role, fullname, self.current_user["username"]))
            conn.commit(); conn.close()
            self.on_save(f"User '{username}' ({role}) created successfully.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
