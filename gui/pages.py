# =============================================================
# gui/pages.py  –  All Feature Pages (complete rewrite)
# =============================================================

import hashlib, tkinter as tk
from tkinter  import messagebox
from datetime import date
import customtkinter as ctk

from database import get_connection
from config   import (COW_STATUS_OPTIONS, GENDER_OPTIONS, FOOD_TYPES,
                      EMPLOYEE_ROLES, ATTENDANCE_STATUS, EXPENSE_CATEGORIES)
from gui.theme   import *
from gui.widgets import (PrimaryButton, DangerButton, SecondaryButton,
                         StyledLabel, StyledEntry, StyledCombo,
                         PasswordEntry, SectionCard, PageHeader,
                         DataTable, NotificationBar, StatCard,
                         BaseDialog, DatePicker, form_row, divider)


def today(): return str(date.today())


def cow_filter_options(include_all=True):
    """List of 'All Cows' + 'ID – Name' entries for cow filter dropdowns."""
    try:
        c = get_connection().execute(
            "SELECT id,name FROM cows ORDER BY name")
        cows = [f"{r[0]} – {r[1]}" for r in c.fetchall()]
        c.connection.close()
    except Exception:
        cows = []
    return (["All Cows"] if include_all else []) + cows


def selected_cow_id(combo):
    """Return cow id from a 'ID – Name' combo value, or None for 'All Cows'."""
    s = combo.get() if combo else "All Cows"
    if "–" not in s:
        return None
    try:
        return int(s.split("–")[0].strip())
    except ValueError:
        return None


def valid_date(s):
    """Return a normalized 'YYYY-MM-DD' string if s is a real date, else None."""
    try:
        return date.fromisoformat(str(s).strip()).isoformat()
    except ValueError:
        return None


def get_date_or_warn(entry, label):
    """Validate a date entry; warn on impossible dates. Returns str or None."""
    raw = entry.get().strip()
    if not raw:
        return today()
    d = valid_date(raw)
    if d is None:
        messagebox.showwarning("Invalid Date",
                               f"{label}: '{raw}' is not a valid date.\n"
                               "Use the 📅 calendar or format YYYY-MM-DD.")
        return None
    return d


# ── Helper: dialog heading ────────────────────────────────────
def dlg_sep(parent): divider(parent, padx=0, pady=8)


# =============================================================
#  BASE PAGE
# =============================================================
class BasePage(ctk.CTkFrame):
    def __init__(self, master, user, **kw):
        super().__init__(master, fg_color=BG_DARK, corner_radius=0, **kw)
        self.user   = user
        self.notify = NotificationBar(self)

    def ok(self, m):   self.notify.show(m, "success")
    def err(self, m):  self.notify.show(m, "error")
    def info(self, m): self.notify.show(m, "info")

    def _header(self, title, sub=""):
        PageHeader(self, title, sub).pack(anchor="w", padx=24, pady=(18,10))
        # Notification bar is packed only when a notification is shown
        self.notify.pack_forget()

    def _toolbar(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=(0,8))
        return f

    def _card(self):
        c = SectionCard(self)
        c.pack(fill="both", expand=True, padx=20, pady=(0,16))
        return c

    def _action_bar(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=10, pady=(0,10))
        return f


# =============================================================
#  DASHBOARD
# =============================================================
class DashboardPage(BasePage):
    def __init__(self, master, user):
        super().__init__(master, user)
        self._header("Dashboard", "Farm overview at a glance")
        stats = self._stats()

        # ── Stat cards ──
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.pack(fill="x", padx=20, pady=(0,12))
        for i,(t,v,ic,col) in enumerate([
            ("Total Cows",    stats["cows"],                 "🐄", PRIMARY),
            ("Active Cows",   stats["active"],               "✅", SUCCESS),
            ("Today's Milk",  f"{stats['milk_today']:.1f} L","🥛", INFO),
            ("Employees",     stats["employees"],            "👷", WARNING),
            ("Month Revenue", f"{stats['revenue']:,.0f}",    "💰", ACCENT),
            ("Health Events", stats["health"],               "💉", DANGER),
        ]):
            StatCard(sf, t, v, ic, col).grid(
                row=0, column=i, padx=6, pady=4, sticky="ew", ipady=4)
            sf.grid_columnconfigure(i, weight=1)

        # ── Two tables ──
        lower = ctk.CTkFrame(self, fg_color="transparent")
        lower.pack(fill="both", expand=True, padx=20, pady=(0,16))
        lower.grid_columnconfigure(0, weight=1)
        lower.grid_columnconfigure(1, weight=1)
        lower.grid_rowconfigure(0, weight=1)

        def half(col, title, badge):
            c = SectionCard(lower)
            c.grid(row=0, column=col, padx=(0,8) if col==0 else (8,0), sticky="nsew")
            h = ctk.CTkFrame(c, fg_color="transparent")
            h.pack(fill="x", padx=14, pady=(12,4))
            ctk.CTkLabel(h, text=title, font=FONT_SUBHEAD,
                         text_color=TEXT_PRIMARY).pack(side="left")
            ctk.CTkLabel(h, text=badge, font=FONT_TINY,
                         text_color=TEXT_MUTED).pack(side="right")
            divider(c, padx=14, pady=0)
            return c

        lc = half(0, "Recent Cows",    f"Total: {stats['cows']}")
        rc = half(1, "Milk Records",   f"Today: {stats['milk_today']:.1f} L")

        t1 = DataTable(lc, [("id","ID",45),("name","Name",130),
                             ("breed","Breed",110),("status","Status",80)])
        t1.pack(fill="both", expand=True, padx=10, pady=(6,10))
        t1.load(stats["recent_cows"])

        t2 = DataTable(rc, [("cow","Cow",130),("date","Date",95),
                             ("liters","Liters",75),("session","Session",85)])
        t2.pack(fill="both", expand=True, padx=10, pady=(6,10))
        t2.load(stats["recent_milk"])

    def _stats(self):
        try:
            conn=get_connection(); c=conn.cursor(); m=today()[:7]
            def q(sql,*a): c.execute(sql,a); return c.fetchone()
            cows   = q("SELECT COUNT(*) FROM cows")[0]
            active = q("SELECT COUNT(*) FROM cows WHERE status='Active'")[0]
            milk_t = q("SELECT COALESCE(SUM(liters),0) FROM milk WHERE date=?",today())[0]
            emps   = q("SELECT COUNT(*) FROM employees WHERE status='Active'")[0]
            rev    = q(f"SELECT COALESCE(SUM(total_amount),0) FROM sales WHERE date LIKE '{m}%'")[0]
            health = q(f"SELECT COUNT(*) FROM health WHERE date LIKE '{m}%'")[0]
            c.execute("SELECT id,name,breed,status FROM cows ORDER BY id DESC LIMIT 6")
            rc = [tuple(r) for r in c.fetchall()]
            c.execute("""SELECT c.name,m.date,m.liters,m.session
                         FROM milk m JOIN cows c ON m.cow_id=c.id
                         ORDER BY m.id DESC LIMIT 6""")
            rm = [tuple(r) for r in c.fetchall()]
            conn.close()
            return dict(cows=cows,active=active,milk_today=milk_t,
                        employees=emps,revenue=rev,health=health,
                        recent_cows=rc,recent_milk=rm)
        except:
            return dict(cows=0,active=0,milk_today=0,employees=0,
                        revenue=0,health=0,recent_cows=[],recent_milk=[])


# =============================================================
#  COWS
# =============================================================
class CowsPage(BasePage):
    def __init__(self, master, user):
        super().__init__(master, user)
        self._header("Cow Management", "Add, view, update and delete cow records")
        read_only = user["role"] in ("watchman", "cleaner")
        tb = self._toolbar()
        if not read_only:
            PrimaryButton(tb, "➕  Add Cow",    self._add).pack(side="left", padx=(0,8))
        SecondaryButton(tb,"🔄 Refresh",    self._load).pack(side="left", padx=(0,8))
        self._search_e = StyledEntry(tb, "Search name / ID / breed…", 200)
        self._search_e.pack(side="left")
        self._search_e.bind("<KeyRelease>", lambda _: self._apply_filters())
        self.c_status_f = StyledCombo(tb, ["All Statuses"] + COW_STATUS_OPTIONS, 130)
        self.c_status_f.pack(side="left", padx=(8,0))
        self.c_status_f.bind("<<ComboboxSelected>>", lambda _: self._apply_filters())
        self.c_gender_f = StyledCombo(tb, ["All Genders"] + GENDER_OPTIONS, 120)
        self.c_gender_f.pack(side="left", padx=(8,0))
        self.c_gender_f.bind("<<ComboboxSelected>>", lambda _: self._apply_filters())

        card = self._card()
        self.tbl = DataTable(card,[
            ("id","ID",50),("name","Name",120),("breed","Breed",110),
            ("age","Age",60),("weight","Weight kg",90),
            ("gender","Gender",80),("color","Color",80),
            ("pd","Purchased",100),("status","Status",80)])
        self.tbl.pack(fill="both", expand=True, padx=10, pady=10)

        if not read_only:
            ab = self._action_bar(card)
            PrimaryButton(ab, "✏️ Edit",   self._edit,   width=130).pack(side="left", padx=(0,8))
            DangerButton(ab,  "🗑️ Delete", self._delete, width=110).pack(side="left")
        else:
            StyledLabel(card, "🔒  Read-only view for your role.",
                        font=FONT_SMALL, text_color=TEXT_MUTED).pack(
                anchor="w", padx=14, pady=(0, 10))

        self._rows = []
        self._load()

    def _load(self):
        try:
            c = get_connection().execute(
                "SELECT id,name,breed,age,weight,gender,color,purchase_date,status FROM cows ORDER BY id DESC")
            self._rows = [tuple(r) for r in c.fetchall()]
            c.connection.close()
            self._apply_filters()
        except Exception as e: self.err(str(e))

    def _apply_filters(self):
        kw = self._search_e.get().lower()
        st = self.c_status_f.get()
        gd = self.c_gender_f.get()
        rows = self._rows
        if st != "All Statuses":
            rows = [r for r in rows if r[8] == st]
        if gd != "All Genders":
            rows = [r for r in rows if r[5] == gd]
        if kw:
            rows = [r for r in rows
                    if any(kw in str(v).lower()
                           for v in (r[0], r[1], r[2], r[6]))]  # id, name, breed, color
        self.tbl.load(rows)

    def _add(self):    CowDialog(self, on_save=lambda m:(self.ok(m), self._load()))
    def _edit(self):
        r = self.tbl.get_selected()
        if not r: self.info("Select a row to edit."); return
        CowDialog(self, cow_id=r[0], on_save=lambda m:(self.ok(m), self._load()))

    def _delete(self):
        r = self.tbl.get_selected()
        if not r: self.info("Select a row to delete."); return
        if messagebox.askyesno("Delete", f"Delete cow '{r[1]}'?"):
            try:
                conn=get_connection(); conn.execute("DELETE FROM cows WHERE id=?",(r[0],))
                conn.commit(); conn.close(); self.ok(f"Cow '{r[1]}' deleted."); self._load()
            except Exception as e: self.err(str(e))


class CowDialog(BaseDialog):
    def __init__(self, parent, on_save, cow_id=None):
        super().__init__(parent, "Edit Cow" if cow_id else "Add Cow", 500, 540)
        self.cow_id  = cow_id
        self.on_save = on_save

        def E(ph): return lambda row: StyledEntry(row, ph, 300)
        def C(v):  return lambda row: StyledCombo(row, v, 300)

        self.e_name   = self.add_field("Cow Name *", E("Cow name"))
        self.e_breed  = self.add_field("Breed",      E("e.g. Friesian"))
        self.e_color  = self.add_field("Color",      E("e.g. Black & White"))
        self.e_age    = self.add_field("Age (yrs)",  E("Years"))
        self.e_weight = self.add_field("Weight (kg)",E("kg"))
        self.e_date   = self.add_field("Purchase Date", lambda row: DatePicker(row, today()))
        self.c_gender = self.add_field("Gender",     C(GENDER_OPTIONS))
        self.c_status = self.add_field("Status",     C(COW_STATUS_OPTIONS))

        self.add_buttons(self._save)

        if cow_id:
            try:
                conn=get_connection(); c=conn.cursor()
                c.execute("SELECT * FROM cows WHERE id=?",(cow_id,))
                row=c.fetchone(); conn.close()
                if row:
                    for e,k in [(self.e_name,"name"),(self.e_breed,"breed"),
                                (self.e_color,"color")]:
                        e.delete(0,"end"); e.insert(0,row[k] or "")
                    self.e_date.set(row["purchase_date"] or today())
                    self.e_age.delete(0,"end");    self.e_age.insert(0,str(row["age"] or ""))
                    self.e_weight.delete(0,"end"); self.e_weight.insert(0,str(row["weight"] or ""))
                    self.c_gender.set(row["gender"] or GENDER_OPTIONS[0])
                    self.c_status.set(row["status"] or "Active")
            except: pass

    def _save(self):
        name = self.e_name.get().strip()
        if not name: messagebox.showwarning("","Name is required."); return
        try:
            age    = float(self.e_age.get()    or 0)
            weight = float(self.e_weight.get() or 0)
        except ValueError: messagebox.showwarning("","Age/Weight must be numbers."); return
        breed  = self.e_breed.get().strip()
        color  = self.e_color.get().strip()
        gender = self.c_gender.get()
        status = self.c_status.get()
        pdate  = get_date_or_warn(self.e_date, "Purchase date")
        if pdate is None: return
        try:
            conn=get_connection(); c=conn.cursor()
            if self.cow_id:
                c.execute("""UPDATE cows SET name=?,breed=?,age=?,weight=?,
                             gender=?,color=?,purchase_date=?,status=? WHERE id=?""",
                          (name,breed,age,weight,gender,color,pdate,status,self.cow_id))
                msg=f"Cow '{name}' updated."
            else:
                c.execute("""INSERT INTO cows (name,breed,age,weight,gender,color,purchase_date,status)
                             VALUES (?,?,?,?,?,?,?,?)""",
                          (name,breed,age,weight,gender,color,pdate,status))
                msg=f"Cow '{name}' added."
            conn.commit(); conn.close()
            self.on_save(msg); self.destroy()
        except Exception as e: messagebox.showerror("Error",str(e))


# =============================================================
#  MILK
# =============================================================
class MilkPage(BasePage):
    def __init__(self, master, user):
        super().__init__(master, user)
        self._header("Milk Management","Record and track daily milk production")
        tb = self._toolbar()
        PrimaryButton(tb,"➕  Record Milk",self._add).pack(side="left",padx=(0,8))
        SecondaryButton(tb,"🔄 Refresh",   self._load).pack(side="left")
        self.c_cow_f = StyledCombo(tb, cow_filter_options(), 160)
        self.c_cow_f.pack(side="left", padx=(8,0))
        self.c_cow_f.bind("<<ComboboxSelected>>", lambda _: self._apply_filters())
        self._search_e = StyledEntry(tb, "Search cow / notes…", 180)
        self._search_e.pack(side="left", padx=(8,0))
        self._search_e.bind("<KeyRelease>", lambda _: self._apply_filters())

        card = self._card()
        self.tbl = DataTable(card,[
            ("id","ID",50),("cow","Cow",120),("date","Date",100),
            ("liters","Liters L",85),("session","Session",90),("notes","Notes",200)])
        self.tbl.pack(fill="both",expand=True,padx=10,pady=10)
        ab = self._action_bar(card)
        DangerButton(ab,"🗑️ Delete",self._delete,width=110).pack(side="left")
        self._load()

    def _load(self):
        try:
            c=get_connection().execute(
                """SELECT m.cow_id, m.id,c.name,m.date,m.liters,m.session,COALESCE(m.notes,'')
                   FROM milk m JOIN cows c ON m.cow_id=c.id ORDER BY m.id DESC""")
            self._rows = [tuple(r) for r in c.fetchall()]   # (cow_id, id, name, date, ...)
            c.connection.close()
            self._apply_filters()
        except Exception as e: self.err(str(e))

    def _apply_filters(self):
        rows = self._rows
        cow_id = selected_cow_id(self.c_cow_f)
        if cow_id is not None:
            rows = [r for r in rows if r[0] == cow_id]
        kw = self._search_e.get().lower()
        if kw:
            rows = [r for r in rows
                    if any(kw in str(v).lower() for v in (r[2], r[6]))]  # cow name, notes
        self.tbl.load([r[1:] for r in rows])

    def _add(self): MilkDialog(self, on_save=lambda m:(self.ok(m),self._load()))
    def _delete(self):
        r=self.tbl.get_selected()
        if not r: self.info("Select a row."); return
        if messagebox.askyesno("Delete","Delete this milk record?"):
            try:
                conn=get_connection(); conn.execute("DELETE FROM milk WHERE id=?",(r[0],))
                conn.commit(); conn.close(); self.ok("Record deleted."); self._load()
            except Exception as e: self.err(str(e))


class MilkDialog(BaseDialog):
    def __init__(self, parent, on_save):
        super().__init__(parent,"Record Milk Production",440,380)
        self.on_save = on_save
        try:
            c=get_connection().execute(
                "SELECT id,name FROM cows WHERE status='Active' ORDER BY name")
            cows=[f"{r[0]} – {r[1]}" for r in c.fetchall()]
            c.connection.close()
        except: cows=[]
        def E(ph): return lambda row: StyledEntry(row, ph, 300)
        def C(v):  return lambda row: StyledCombo(row, v, 300)
        self.c_cow    = self.add_field("Cow *",     C(cows or ["No active cows"]))
        self.e_date   = self.add_field("Date",      lambda row: DatePicker(row, today()))
        self.e_liters = self.add_field("Liters *",  E("e.g. 12.5"))
        self.c_sess   = self.add_field("Session",   C(["Morning","Afternoon","Evening"]))
        self.e_notes  = self.add_field("Notes",     E("Optional"))
        self.add_buttons(self._save)

    def _save(self):
        s=self.c_cow.get()
        if "–" not in s: messagebox.showwarning("","Select a cow."); return
        cow_id=int(s.split("–")[0].strip())
        try: liters=float(self.e_liters.get()); assert liters>=0
        except: messagebox.showwarning("","Enter valid liters."); return
        dt = get_date_or_warn(self.e_date, "Date")
        if dt is None: return
        try:
            conn=get_connection()
            conn.execute("INSERT INTO milk (cow_id,date,liters,session,notes) VALUES(?,?,?,?,?)",
                         (cow_id,dt,liters,self.c_sess.get(),self.e_notes.get().strip()))
            conn.commit(); conn.close()
            self.on_save(f"Recorded {liters}L."); self.destroy()
        except Exception as e: messagebox.showerror("Error",str(e))


# =============================================================
#  FOOD
# =============================================================
class FoodPage(BasePage):
    def __init__(self, master, user):
        super().__init__(master, user)
        self._header("Food Management","Manage feed stock and daily feeding")
        tb=self._toolbar()
        PrimaryButton(tb,"➕  Add Feed",self._add).pack(side="left",padx=(0,8))
        SecondaryButton(tb,"🔄 Refresh",self._load).pack(side="left")
        self.c_cow_f = StyledCombo(tb, cow_filter_options(), 160)
        self.c_cow_f.pack(side="left", padx=(8,0))
        self.c_cow_f.bind("<<ComboboxSelected>>", lambda _: self._apply_filters())
        self._search_e = StyledEntry(tb, "Search food type / cow / notes…", 200)
        self._search_e.pack(side="left", padx=(8,0))
        self._search_e.bind("<KeyRelease>", lambda _: self._apply_filters())

        card=self._card()
        self.tbl=DataTable(card,[
            ("id","ID",50),("type","Food Type",120),("qty","Qty kg",85),
            ("date","Date",100),("cow","Cow",100),("notes","Notes",180)])
        self.tbl.pack(fill="both",expand=True,padx=10,pady=10)
        ab=self._action_bar(card)
        DangerButton(ab,"🗑️ Delete",self._delete,width=110).pack(side="left")
        self._load()

    def _load(self):
        try:
            c=get_connection().execute(
                """SELECT f.id,f.food_type,f.quantity_kg,f.date,
                          COALESCE(c.name,'All'),COALESCE(f.notes,''),f.cow_id
                   FROM food f LEFT JOIN cows c ON f.cow_id=c.id ORDER BY f.id DESC""")
            self._rows = [tuple(r) for r in c.fetchall()]
            c.connection.close()
            self._apply_filters()
        except Exception as e: self.err(str(e))

    def _apply_filters(self):
        rows = self._rows
        cow_id = selected_cow_id(self.c_cow_f)
        if cow_id is not None:
            rows = [r for r in rows if r[6] == cow_id]
        kw = self._search_e.get().lower()
        if kw:
            rows = [r for r in rows
                    if any(kw in str(v).lower() for v in (r[1], r[4], r[5]))]  # type, cow, notes
        self.tbl.load([r[:5] for r in rows])

    def _add(self): FoodDialog(self, on_save=lambda m:(self.ok(m),self._load()))
    def _delete(self):
        r=self.tbl.get_selected()
        if not r: self.info("Select a row."); return
        if messagebox.askyesno("Delete","Delete this feed record?"):
            try:
                conn=get_connection(); conn.execute("DELETE FROM food WHERE id=?",(r[0],))
                conn.commit(); conn.close(); self.ok("Record deleted."); self._load()
            except Exception as e: self.err(str(e))


class FoodDialog(BaseDialog):
    def __init__(self, parent, on_save):
        super().__init__(parent,"Add Feed Record",440,360)
        self.on_save=on_save
        try:
            c=get_connection().execute(
                "SELECT id,name FROM cows WHERE status='Active' ORDER BY name")
            cows=["All Cows"]+[f"{r[0]} – {r[1]}" for r in c.fetchall()]
            c.connection.close()
        except: cows=["All Cows"]
        def E(ph): return lambda row: StyledEntry(row, ph, 300)
        def C(v):  return lambda row: StyledCombo(row, v, 300)
        self.c_type  = self.add_field("Food Type *",    C(FOOD_TYPES))
        self.e_qty   = self.add_field("Quantity (kg) *",E("kg"))
        self.e_date  = self.add_field("Date",           lambda row: DatePicker(row, today()))
        self.c_cow   = self.add_field("Cow",            C(cows))
        self.e_notes = self.add_field("Notes",          E("Optional"))
        self.add_buttons(self._save)

    def _save(self):
        try: qty=float(self.e_qty.get()); assert qty>0
        except: messagebox.showwarning("","Enter valid quantity."); return
        cow_str=self.c_cow.get()
        cow_id=int(cow_str.split("–")[0].strip()) if "–" in cow_str else None
        dt = get_date_or_warn(self.e_date, "Date")
        if dt is None: return
        try:
            conn=get_connection()
            conn.execute("INSERT INTO food (food_type,quantity_kg,date,cow_id,notes) VALUES(?,?,?,?,?)",
                         (self.c_type.get(),qty,dt,cow_id,self.e_notes.get().strip()))
            conn.commit(); conn.close()
            self.on_save(f"Added {qty}kg of {self.c_type.get()}."); self.destroy()
        except Exception as e: messagebox.showerror("Error",str(e))


# =============================================================
#  HEALTH
# =============================================================
HEALTH_TYPES = ["Vaccination","Disease","Medicine","Checkup","Other"]

class HealthPage(BasePage):
    def __init__(self, master, user):
        super().__init__(master, user)
        self._header("Health & Medicine","Track vaccinations, diseases and treatments")
        tb=self._toolbar()
        PrimaryButton(tb,"➕  Add Record",self._add).pack(side="left",padx=(0,8))
        SecondaryButton(tb,"🔄 Refresh",self._load).pack(side="left")
        self.c_cow_f = StyledCombo(tb, cow_filter_options(), 160)
        self.c_cow_f.pack(side="left", padx=(8,0))
        self.c_cow_f.bind("<<ComboboxSelected>>", lambda _: self._apply_filters())
        self.c_type_f = StyledCombo(tb, ["All Types"] + HEALTH_TYPES, 130)
        self.c_type_f.pack(side="left", padx=(8,0))
        self.c_type_f.bind("<<ComboboxSelected>>", lambda _: self._apply_filters())
        self._search_e = StyledEntry(tb, "Search description / med / vet…", 190)
        self._search_e.pack(side="left", padx=(8,0))
        self._search_e.bind("<KeyRelease>", lambda _: self._apply_filters())

        card=self._card()
        self.tbl=DataTable(card,[
            ("id","ID",50),("cow","Cow",110),("date","Date",95),
            ("type","Type",100),("desc","Description",175),
            ("med","Medicine",110),("vet","Vet",95),("cost","Cost",70)])
        self.tbl.pack(fill="both",expand=True,padx=10,pady=10)
        ab=self._action_bar(card)
        DangerButton(ab,"🗑️ Delete",self._delete,width=110).pack(side="left")
        self._load()

    def _load(self):
        try:
            c=get_connection().execute(
                """SELECT h.id,c.name,h.date,h.record_type,
                          COALESCE(h.description,''),COALESCE(h.medicine,''),
                          COALESCE(h.vet_name,''),h.cost,h.cow_id
                   FROM health h JOIN cows c ON h.cow_id=c.id ORDER BY h.id DESC""")
            self._rows = [tuple(r) for r in c.fetchall()]
            c.connection.close()
            self._apply_filters()
        except Exception as e: self.err(str(e))

    def _apply_filters(self):
        rows = self._rows
        cow_id = selected_cow_id(self.c_cow_f)
        if cow_id is not None:
            rows = [r for r in rows if r[8] == cow_id]
        typ = self.c_type_f.get()
        if typ != "All Types":
            rows = [r for r in rows if r[3] == typ]
        kw = self._search_e.get().lower()
        if kw:
            rows = [r for r in rows
                    if any(kw in str(v).lower() for v in (r[1], r[4], r[5], r[6]))]  # cow, desc, med, vet
        self.tbl.load([r[:8] for r in rows])

    def _add(self): HealthDialog(self, on_save=lambda m:(self.ok(m),self._load()))
    def _delete(self):
        r=self.tbl.get_selected()
        if not r: self.info("Select a row."); return
        if messagebox.askyesno("Delete","Delete this health record?"):
            try:
                conn=get_connection(); conn.execute("DELETE FROM health WHERE id=?",(r[0],))
                conn.commit(); conn.close(); self.ok("Record deleted."); self._load()
            except Exception as e: self.err(str(e))


class HealthDialog(BaseDialog):
    def __init__(self, parent, on_save):
        super().__init__(parent,"Add Health Record",460,440)
        self.on_save=on_save
        try:
            c=get_connection().execute(
                "SELECT id,name FROM cows WHERE status='Active' ORDER BY name")
            cows=[f"{r[0]} – {r[1]}" for r in c.fetchall()]
            c.connection.close()
        except: cows=[]
        def E(ph): return lambda row: StyledEntry(row, ph, 300)
        def C(v):  return lambda row: StyledCombo(row, v, 300)
        self.c_cow  = self.add_field("Cow *",        C(cows or ["No cows"]))
        self.e_date = self.add_field("Date",         lambda row: DatePicker(row, today()))
        self.c_type = self.add_field("Record Type",  C(HEALTH_TYPES))
        self.e_desc = self.add_field("Description",  E("Symptoms / description"))
        self.e_med  = self.add_field("Medicine",     E("Medicine name"))
        self.e_vet  = self.add_field("Vet Name",     E("Vet name"))
        self.e_cost = self.add_field("Cost",         E("0.00"))
        self.add_buttons(self._save)

    def _save(self):
        s=self.c_cow.get()
        if "–" not in s: messagebox.showwarning("","Select a cow."); return
        cow_id=int(s.split("–")[0].strip())
        try: cost=float(self.e_cost.get() or 0)
        except: cost=0.0
        dt = get_date_or_warn(self.e_date, "Date")
        if dt is None: return
        try:
            conn=get_connection()
            conn.execute(
                "INSERT INTO health (cow_id,date,record_type,description,medicine,vet_name,cost) VALUES(?,?,?,?,?,?,?)",
                (cow_id,dt,self.c_type.get(),
                 self.e_desc.get().strip(),self.e_med.get().strip(),
                 self.e_vet.get().strip(),cost))
            conn.commit(); conn.close()
            self.on_save(f"Health record saved."); self.destroy()
        except Exception as e: messagebox.showerror("Error",str(e))


# =============================================================
#  EMPLOYEES
# =============================================================
class EmployeesPage(BasePage):
    def __init__(self, master, user):
        super().__init__(master, user)
        self._header("Employee Management","Staff, attendance and salaries")

        tabs = ctk.CTkFrame(self, fg_color="transparent")
        tabs.pack(fill="x", padx=20, pady=(0,8))
        self._tab_btns = {}
        for lbl in ["Employees","Attendance","Salary"]:
            b = ctk.CTkButton(tabs, text=lbl, width=130, height=34,
                              corner_radius=8, fg_color=BG_LIGHT,
                              hover_color=SIDEBAR_HOVER,
                              text_color=TEXT_SECONDARY, font=FONT_BTN,
                              command=lambda l=lbl: self._tab(l))
            b.pack(side="left", padx=(0,6))
            self._tab_btns[lbl] = b

        self._area = ctk.CTkFrame(self, fg_color="transparent")
        self._area.pack(fill="both", expand=True, padx=20, pady=(0,16))
        self._tab("Employees")

    def _tab(self, name):
        for k,b in self._tab_btns.items():
            b.configure(fg_color=PRIMARY if k==name else BG_LIGHT,
                        text_color=TEXT_PRIMARY if k==name else TEXT_SECONDARY)
        for w in self._area.winfo_children(): w.destroy()
        {"Employees": self._emp_tab,
         "Attendance": self._att_tab,
         "Salary": self._sal_tab}[name]()

    # ── Employees tab ──
    def _emp_tab(self):
        tb = ctk.CTkFrame(self._area, fg_color="transparent")
        tb.pack(fill="x", pady=(0,8))
        PrimaryButton(tb,"➕ Add Employee",self._add_emp).pack(side="left",padx=(0,8))
        SecondaryButton(tb,"🔄 Refresh",self._emp_tab).pack(side="left")

        card = SectionCard(self._area)
        card.pack(fill="both", expand=True)
        self._etbl = DataTable(card,[
            ("id","ID",50),("name","Name",140),("role","Role",110),
            ("phone","Phone",110),("salary","Salary",90),
            ("joined","Joined",100),("status","Status",80)])
        self._etbl.pack(fill="both",expand=True,padx=10,pady=10)
        ab = ctk.CTkFrame(card,fg_color="transparent")
        ab.pack(fill="x",padx=10,pady=(0,10))
        DangerButton(ab,"🗑️ Delete",self._del_emp,width=110).pack(side="left")

        try:
            c=get_connection().execute(
                "SELECT id,name,role,phone,salary,join_date,status FROM employees ORDER BY id DESC")
            self._etbl.load([tuple(r) for r in c.fetchall()])
            c.connection.close()
        except Exception as e: self.err(str(e))

    def _add_emp(self): EmpDialog(self, on_save=lambda m:(self.ok(m),self._emp_tab()))
    def _del_emp(self):
        r=self._etbl.get_selected()
        if not r: self.info("Select a row."); return
        if messagebox.askyesno("Delete",f"Delete '{r[1]}'?"):
            try:
                conn=get_connection(); conn.execute("DELETE FROM employees WHERE id=?",(r[0],))
                conn.commit(); conn.close(); self.ok(f"'{r[1]}' deleted."); self._emp_tab()
            except Exception as e: self.err(str(e))

    # ── Attendance tab ──
    def _att_tab(self):
        tb = ctk.CTkFrame(self._area,fg_color="transparent")
        tb.pack(fill="x",pady=(0,8))
        PrimaryButton(tb,"➕ Mark Attendance",self._add_att).pack(side="left",padx=(0,8))
        SecondaryButton(tb,"🔄 Refresh",self._att_tab).pack(side="left")

        card=SectionCard(self._area); card.pack(fill="both",expand=True)
        self._atbl=DataTable(card,[
            ("id","ID",50),("emp","Employee",150),("date","Date",100),("status","Status",100)])
        self._atbl.pack(fill="both",expand=True,padx=10,pady=10)
        try:
            c=get_connection().execute(
                """SELECT a.id,e.name,a.date,a.status
                   FROM attendance a JOIN employees e ON a.employee_id=e.id
                   ORDER BY a.id DESC""")
            self._atbl.load([tuple(r) for r in c.fetchall()])
            c.connection.close()
        except Exception as e: self.err(str(e))

    def _add_att(self): AttDialog(self, on_save=lambda m:(self.ok(m),self._att_tab()))

    # ── Salary tab ──
    def _sal_tab(self):
        card=SectionCard(self._area); card.pack(fill="both",expand=True)
        ctk.CTkLabel(card,text="Salary Summary",font=FONT_SUBHEAD,
                     text_color=TEXT_PRIMARY).pack(anchor="w",padx=14,pady=(12,4))
        divider(card,padx=14,pady=0)
        tbl=DataTable(card,[("id","ID",50),("name","Name",160),
                             ("role","Role",110),("salary","Salary",100),("status","Status",80)])
        tbl.pack(fill="both",expand=True,padx=10,pady=(6,4))
        try:
            c=get_connection().execute(
                "SELECT id,name,role,salary,status FROM employees ORDER BY name")
            rows=[tuple(r) for r in c.fetchall()]
            c.connection.close()
            tbl.load(rows)
            total=sum(r[3] for r in rows)
            ctk.CTkLabel(card,text=f"  Total Monthly Payroll:  {total:,.2f}",
                         font=FONT_SUBHEAD,text_color=SUCCESS
                         ).pack(anchor="w",padx=14,pady=(4,12))
        except Exception as e: self.err(str(e))


class EmpDialog(BaseDialog):
    def __init__(self, parent, on_save):
        super().__init__(parent,"Add Employee",440,390)
        self.on_save=on_save
        def E(ph): return lambda row: StyledEntry(row, ph, 300)
        def C(v):  return lambda row: StyledCombo(row, v, 300)
        self.e_name   = self.add_field("Full Name *", E("Full name"))
        self.c_role   = self.add_field("Role",        C(EMPLOYEE_ROLES))
        self.e_phone  = self.add_field("Phone",       E("Phone number"))
        self.e_salary = self.add_field("Salary",      E("Monthly salary"))
        self.e_date   = self.add_field("Join Date",   lambda row: DatePicker(row, today()))
        self.add_buttons(self._save)

    def _save(self):
        name=self.e_name.get().strip()
        if not name: messagebox.showwarning("","Name is required."); return
        try: salary=float(self.e_salary.get() or 0)
        except: salary=0.0
        dt = get_date_or_warn(self.e_date, "Join date")
        if dt is None: return
        try:
            conn=get_connection()
            conn.execute("INSERT INTO employees (name,role,phone,salary,join_date,status) VALUES(?,?,?,?,?,'Active')",
                         (name,self.c_role.get(),self.e_phone.get().strip(),
                          salary,dt))
            conn.commit(); conn.close()
            self.on_save(f"Employee '{name}' added."); self.destroy()
        except Exception as e: messagebox.showerror("Error",str(e))


class AttDialog(BaseDialog):
    def __init__(self, parent, on_save):
        super().__init__(parent,"Mark Attendance",420,290)
        self.on_save=on_save
        try:
            c=get_connection().execute(
                "SELECT id,name FROM employees WHERE status='Active' ORDER BY name")
            emps=[f"{r[0]} – {r[1]}" for r in c.fetchall()]
            c.connection.close()
        except: emps=[]
        def E(ph): return lambda row: StyledEntry(row, ph, 300)
        def C(v):  return lambda row: StyledCombo(row, v, 300)
        self.c_emp   = self.add_field("Employee *", C(emps or ["No employees"]))
        self.e_date  = self.add_field("Date",       lambda row: DatePicker(row, today()))
        self.c_stat  = self.add_field("Status",     C(ATTENDANCE_STATUS))
        self.add_buttons(self._save)

    def _save(self):
        s=self.c_emp.get()
        if "–" not in s: messagebox.showwarning("","Select an employee."); return
        emp_id=int(s.split("–")[0].strip())
        dt = get_date_or_warn(self.e_date, "Date")
        if dt is None: return
        try:
            conn=get_connection()
            conn.execute("INSERT INTO attendance (employee_id,date,status) VALUES(?,?,?)",
                         (emp_id,dt,self.c_stat.get()))
            conn.commit(); conn.close()
            self.on_save(f"Attendance marked: {self.c_stat.get()} on {dt}."); self.destroy()
        except Exception as e: messagebox.showerror("Error",str(e))


# =============================================================
#  EXPENSES & SALES
# =============================================================
class ExpensesPage(BasePage):
    def __init__(self, master, user):
        super().__init__(master, user)
        self._header("Expense & Sales","Track farm expenses and milk sales")

        tabs=ctk.CTkFrame(self,fg_color="transparent")
        tabs.pack(fill="x",padx=20,pady=(0,8))
        self._tbns={}
        for lbl in ["Expenses","Sales","Profit"]:
            b=ctk.CTkButton(tabs,text=lbl,width=120,height=34,corner_radius=8,
                            fg_color=BG_LIGHT,hover_color=SIDEBAR_HOVER,
                            text_color=TEXT_SECONDARY,font=FONT_BTN,
                            command=lambda l=lbl:self._tab(l))
            b.pack(side="left",padx=(0,6))
            self._tbns[lbl]=b

        self._area=ctk.CTkFrame(self,fg_color="transparent")
        self._area.pack(fill="both",expand=True,padx=20,pady=(0,16))
        self._tab("Expenses")

    def _tab(self,name):
        for k,b in self._tbns.items():
            b.configure(fg_color=PRIMARY if k==name else BG_LIGHT,
                        text_color=TEXT_PRIMARY if k==name else TEXT_SECONDARY)
        for w in self._area.winfo_children(): w.destroy()
        {"Expenses":self._exp_tab,"Sales":self._sal_tab,"Profit":self._profit_tab}[name]()

    # ── Expenses ──
    def _exp_tab(self):
        tb=ctk.CTkFrame(self._area,fg_color="transparent")
        tb.pack(fill="x",pady=(0,8))
        PrimaryButton(tb,"➕ Add Expense",self._add_exp).pack(side="left",padx=(0,8))
        SecondaryButton(tb,"🔄 Refresh",self._exp_tab).pack(side="left")
        card=SectionCard(self._area); card.pack(fill="both",expand=True)
        self._exptbl=DataTable(card,[
            ("id","ID",50),("date","Date",100),("cat","Category",110),
            ("amount","Amount",90),("desc","Description",220)])
        self._exptbl.pack(fill="both",expand=True,padx=10,pady=10)
        ab=ctk.CTkFrame(card,fg_color="transparent"); ab.pack(fill="x",padx=10,pady=(0,10))
        DangerButton(ab,"🗑️ Delete",self._del_exp,width=110).pack(side="left")
        try:
            c=get_connection().execute(
                "SELECT id,date,category,amount,COALESCE(description,'') FROM expenses ORDER BY id DESC")
            self._exptbl.load([tuple(r) for r in c.fetchall()])
            c.connection.close()
        except Exception as e: self.err(str(e))

    def _add_exp(self): ExpDialog(self,on_save=lambda m:(self.ok(m),self._exp_tab()))
    def _del_exp(self):
        r=self._exptbl.get_selected()
        if not r: self.info("Select a row."); return
        if messagebox.askyesno("Delete","Delete this expense?"):
            try:
                conn=get_connection(); conn.execute("DELETE FROM expenses WHERE id=?",(r[0],))
                conn.commit(); conn.close(); self.ok("Deleted."); self._exp_tab()
            except Exception as e: self.err(str(e))

    # ── Sales ──
    def _sal_tab(self):
        tb=ctk.CTkFrame(self._area,fg_color="transparent")
        tb.pack(fill="x",pady=(0,8))
        PrimaryButton(tb,"➕ Record Sale",self._add_sale).pack(side="left",padx=(0,8))
        SecondaryButton(tb,"🔄 Refresh",self._sal_tab).pack(side="left")
        card=SectionCard(self._area); card.pack(fill="both",expand=True)
        self._sltbl=DataTable(card,[
            ("id","ID",50),("date","Date",100),("liters","Liters",80),
            ("price","Price/L",80),("total","Total",90),("buyer","Buyer",130),("notes","Notes",130)])
        self._sltbl.pack(fill="both",expand=True,padx=10,pady=10)
        try:
            c=get_connection().execute(
                "SELECT id,date,liters_sold,price_per_liter,total_amount,COALESCE(buyer_name,''),COALESCE(notes,'') FROM sales ORDER BY id DESC")
            self._sltbl.load([tuple(r) for r in c.fetchall()])
            c.connection.close()
        except Exception as e: self.err(str(e))

    def _add_sale(self): SaleDialog(self,on_save=lambda m:(self.ok(m),self._sal_tab()))

    # ── Profit ──
    def _profit_tab(self):
        card=SectionCard(self._area); card.pack(fill="both",expand=True)
        ctk.CTkLabel(card,text="Profit Calculator",font=FONT_SUBHEAD,
                     text_color=TEXT_PRIMARY).pack(anchor="w",padx=16,pady=(14,4))
        divider(card,padx=16,pady=0)

        row=ctk.CTkFrame(card,fg_color="transparent")
        row.pack(fill="x",padx=16,pady=14)
        ctk.CTkLabel(row,text="Start:",font=FONT_SMALL,
                     text_color=TEXT_SECONDARY,width=50).pack(side="left")
        self._ps=DatePicker(row,width=170); self._ps.pack(side="left",padx=(4,14))
        ctk.CTkLabel(row,text="End:",font=FONT_SMALL,
                     text_color=TEXT_SECONDARY,width=40).pack(side="left")
        self._pe=DatePicker(row,width=170); self._pe.pack(side="left",padx=(4,14))
        PrimaryButton(row,"Calculate",self._calc,width=120).pack(side="left")

        self._pres=ctk.CTkLabel(card,text="",
                                font=("Segoe UI",18,"bold"),text_color=SUCCESS)
        self._pres.pack(pady=16)

    def _calc(self):
        s=get_date_or_warn(self._ps,"Start date"); 
        e=get_date_or_warn(self._pe,"End date")
        if s is None or e is None: return
        if not s or not e: self.err("Enter both dates."); return
        try:
            conn=get_connection(); c=conn.cursor()
            c.execute("SELECT COALESCE(SUM(total_amount),0) FROM sales WHERE date BETWEEN ? AND ?",(s,e))
            rev=c.fetchone()[0]
            c.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date BETWEEN ? AND ?",(s,e))
            exp=c.fetchone()[0]; conn.close()
            net=rev-exp; sign="+" if net>=0 else ""
            self._pres.configure(
                text=f"Revenue: {rev:,.2f}   |   Expenses: {exp:,.2f}   |   Net: {sign}{net:,.2f}",
                text_color=SUCCESS if net>=0 else DANGER)
        except Exception as e: self.err(str(e))


class ExpDialog(BaseDialog):
    def __init__(self,parent,on_save):
        super().__init__(parent,"Add Expense",430,330)
        self.on_save=on_save
        def E(ph): return lambda row: StyledEntry(row, ph, 300)
        def C(v):  return lambda row: StyledCombo(row, v, 300)
        self.e_date  = self.add_field("Date *",       lambda row: DatePicker(row, today()))
        self.c_cat   = self.add_field("Category *",   C(EXPENSE_CATEGORIES))
        self.e_amt   = self.add_field("Amount *",     E("Amount"))
        self.e_desc  = self.add_field("Description",  E("Description"))
        self.add_buttons(self._save)

    def _save(self):
        try: amt=float(self.e_amt.get()); assert amt>0
        except: messagebox.showwarning("","Enter valid amount."); return
        dt = get_date_or_warn(self.e_date, "Date")
        if dt is None: return
        try:
            conn=get_connection()
            conn.execute("INSERT INTO expenses (date,category,amount,description) VALUES(?,?,?,?)",
                         (dt,self.c_cat.get(),
                          amt,self.e_desc.get().strip()))
            conn.commit(); conn.close()
            self.on_save(f"Expense {self.c_cat.get()} {amt:.2f} saved."); self.destroy()
        except Exception as e: messagebox.showerror("Error",str(e))


class SaleDialog(BaseDialog):
    def __init__(self,parent,on_save):
        super().__init__(parent,"Record Milk Sale",440,380)
        self.on_save=on_save
        def E(ph): return lambda row: StyledEntry(row, ph, 300)
        self.e_date   = self.add_field("Date *",        lambda row: DatePicker(row, today()))
        self.e_liters = self.add_field("Liters *",      E("Liters sold"))
        self.e_price  = self.add_field("Price/Liter *", E("Price per liter"))
        self.e_buyer  = self.add_field("Buyer",         E("Buyer name"))
        self.e_notes  = self.add_field("Notes",         E("Notes"))
        self._tlbl    = ctk.CTkLabel(self.body,text="Total: –",
                                     font=FONT_SUBHEAD,text_color=SUCCESS)
        self._tlbl.pack(anchor="w",padx=8,pady=(4,0))
        self.e_liters.bind("<KeyRelease>",self._upd)
        self.e_price.bind("<KeyRelease>",self._upd)
        self.add_buttons(self._save)

    def _upd(self,*_):
        try: self._tlbl.configure(text=f"Total: {float(self.e_liters.get())*float(self.e_price.get()):,.2f}")
        except: self._tlbl.configure(text="Total: –")

    def _save(self):
        try:
            liters=float(self.e_liters.get()); price=float(self.e_price.get())
            assert liters>0 and price>0
        except: messagebox.showwarning("","Enter valid liters and price."); return
        total=liters*price
        dt = get_date_or_warn(self.e_date, "Date")
        if dt is None: return
        try:
            conn=get_connection()
            conn.execute("INSERT INTO sales (date,liters_sold,price_per_liter,total_amount,buyer_name,notes) VALUES(?,?,?,?,?,?)",
                         (dt,liters,price,total,
                          self.e_buyer.get().strip(),self.e_notes.get().strip()))
            conn.commit(); conn.close()
            self.on_save(f"Sale recorded: {liters}L = {total:,.2f}"); self.destroy()
        except Exception as e: messagebox.showerror("Error",str(e))


# =============================================================
#  REPORTS
# =============================================================
class ReportsPage(BasePage):
    def __init__(self, master, user):
        super().__init__(master, user)
        self._header("Reports","Generate farm reports")

        ctrl=ctk.CTkFrame(self,fg_color=CARD_BG,corner_radius=10,
                          border_color=CARD_BORDER,border_width=1)
        ctrl.pack(fill="x",padx=20,pady=(0,8))
        row=ctk.CTkFrame(ctrl,fg_color="transparent")
        row.pack(padx=16,pady=12,fill="x")

        ctk.CTkLabel(row,text="Type:",font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(side="left")
        self._rtype=StyledCombo(row,["Daily Report","Monthly Report",
                                     "Milk Production","Expense Report"],width=170)
        self._rtype.pack(side="left",padx=(6,12))
        ctk.CTkLabel(row,text="Cow:",font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(side="left")
        self._rcow=StyledCombo(row, cow_filter_options(), 140)
        self._rcow.pack(side="left",padx=(6,12))
        ctk.CTkLabel(row,text="From:",font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(side="left")
        self._rs=DatePicker(row,width=140); self._rs.pack(side="left",padx=(4,10))
        ctk.CTkLabel(row,text="To:",font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(side="left")
        self._re=DatePicker(row,width=140); self._re.pack(side="left",padx=(4,10))
        PrimaryButton(row,"📊 Generate",self._gen,width=120).pack(side="left")

        card=SectionCard(self)
        card.pack(fill="both",expand=True,padx=20,pady=(0,16))
        self._out=ctk.CTkTextbox(card,fg_color=INPUT_BG,text_color=TEXT_PRIMARY,
                                 font=FONT_MONO,border_color=BORDER,
                                 border_width=1,corner_radius=8)
        self._out.pack(fill="both",expand=True,padx=10,pady=10)
        self._out.configure(state="disabled")
        self._write("Select a report type, enter dates, then click Generate.")

    def _write(self,txt):
        self._out.configure(state="normal")
        self._out.delete("1.0","end")
        self._out.insert("end",txt)
        self._out.configure(state="disabled")

    def _gen(self):
        rt=self._rtype.get()
        s=get_date_or_warn(self._rs,"From date"); 
        e=get_date_or_warn(self._re,"To date")
        if s is None or e is None: return
        cow_id = selected_cow_id(self._rcow)
        if "Daily"    in rt: self._write(self._daily(s or today()))
        elif "Monthly" in rt: self._write(self._monthly((s or today())[:7]))
        elif "Milk"    in rt:
            if not s or not e: self.err("Enter start and end dates."); return
            self._write(self._milk(s,e,cow_id))
        elif "Expense" in rt:
            if not s or not e: self.err("Enter start and end dates."); return
            self._write(self._expense(s,e))

    def _daily(self,dt):
        try:
            conn=get_connection(); c=conn.cursor()
            L=[f"{'='*58}","  DAILY REPORT  –  "+dt,f"{'='*58}",""]
            c.execute("""SELECT c.name,m.liters,m.session FROM milk m
                         JOIN cows c ON m.cow_id=c.id WHERE m.date=?""",(dt,))
            rows=c.fetchall(); tm=sum(r[1] for r in rows)
            L+=["[ MILK PRODUCTION ]"]+[f"  {r[0]:<18}{r[2]:<12}{r[1]} L" for r in rows]+[f"  Total: {tm:.2f} L",""]
            c.execute("SELECT category,amount,COALESCE(description,'') FROM expenses WHERE date=?",(dt,))
            rows=c.fetchall(); te=sum(r[1] for r in rows)
            L+=["[ EXPENSES ]"]+[f"  {r[0]:<18}{r[1]:>10.2f}  {r[2]}" for r in rows]+[f"  Total: {te:.2f}",""]
            c.execute("SELECT liters_sold,price_per_liter,total_amount,COALESCE(buyer_name,'N/A') FROM sales WHERE date=?",(dt,))
            rows=c.fetchall(); ts=sum(r[2] for r in rows)
            L+=["[ SALES ]"]+[f"  {r[3]:<18}{r[0]}L × {r[1]} = {r[2]:.2f}" for r in rows]+[f"  Total: {ts:.2f}",""]
            net=ts-te; sign="+" if net>=0 else ""
            L+=[f"{'─'*58}",f"  Net Profit / Loss: {sign}{net:.2f}"]
            conn.close(); return "\n".join(L)
        except Exception as e: return f"Error: {e}"

    def _monthly(self,m):
        s=f"{m}-01"; e=f"{m}-31"
        try:
            conn=get_connection(); c=conn.cursor()
            L=[f"{'='*58}","  MONTHLY REPORT  –  "+m,f"{'='*58}",""]
            c.execute("SELECT COUNT(*) FROM cows WHERE status='Active'")
            L.append(f"  Active Cows     : {c.fetchone()[0]}")
            c.execute("SELECT COALESCE(SUM(liters),0),COUNT(*) FROM milk WHERE date BETWEEN ? AND ?",(s,e))
            r=c.fetchone(); L.append(f"  Milk Produced   : {r[0]:.2f} L  ({r[1]} sessions)")
            c.execute("SELECT COALESCE(SUM(total_amount),0),COALESCE(SUM(liters_sold),0) FROM sales WHERE date BETWEEN ? AND ?",(s,e))
            r=c.fetchone(); rev=r[0]; L+=[f"  Milk Sold       : {r[1]:.2f} L",f"  Total Revenue   : {rev:,.2f}"]
            c.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date BETWEEN ? AND ?",(s,e))
            exp=c.fetchone()[0]; L.append(f"  Total Expenses  : {exp:,.2f}")
            c.execute("SELECT COUNT(*) FROM health WHERE date BETWEEN ? AND ?",(s,e))
            L+=[f"  Health Events   : {c.fetchone()[0]}","",f"{'─'*58}"]
            net=rev-exp; sign="+" if net>=0 else ""
            L.append(f"  Net Profit/Loss : {sign}{net:,.2f}")
            conn.close(); return "\n".join(L)
        except Exception as e: return f"Error: {e}"

    def _milk(self,s,e,cow_id=None):
        try:
            conn=get_connection(); c=conn.cursor()
            if cow_id is None:
                c.execute("""SELECT c.name,SUM(m.liters),COUNT(*) FROM milk m
                             JOIN cows c ON m.cow_id=c.id WHERE m.date BETWEEN ? AND ?
                             GROUP BY m.cow_id ORDER BY SUM(m.liters) DESC""",(s,e))
            else:
                c.execute("""SELECT c.name,SUM(m.liters),COUNT(*) FROM milk m
                             JOIN cows c ON m.cow_id=c.id WHERE m.date BETWEEN ? AND ?
                             AND m.cow_id=? GROUP BY m.cow_id""",(s,e,cow_id))
            rows=c.fetchall(); conn.close()
            scope = "ALL COWS" if cow_id is None else "SINGLE COW"
            L=[f"{'='*58}",f"  MILK PRODUCTION  –  {s} to {e}  [{scope}]",f"{'='*58}",
               f"  {'Cow':<22}{'Sessions':>10}{'Total (L)':>12}","─"*58]
            gt=0
            for r in rows: L.append(f"  {r[0]:<22}{r[2]:>10}{r[1]:>12.2f}"); gt+=r[1]
            L+=["─"*58,f"  {'GRAND TOTAL':<22}{'':>10}{gt:>12.2f} L"]
            return "\n".join(L)
        except Exception as e: return f"Error: {e}"

    def _expense(self,s,e):
        try:
            conn=get_connection(); c=conn.cursor()
            c.execute("""SELECT category,SUM(amount),COUNT(*) FROM expenses
                         WHERE date BETWEEN ? AND ? GROUP BY category
                         ORDER BY SUM(amount) DESC""",(s,e))
            rows=c.fetchall(); conn.close()
            L=[f"{'='*58}",f"  EXPENSE REPORT  –  {s} to {e}",f"{'='*58}",
               f"  {'Category':<18}{'Count':>8}{'Total':>14}","─"*58]
            gt=0
            for r in rows: L.append(f"  {r[0]:<18}{r[2]:>8}{r[1]:>14.2f}"); gt+=r[1]
            L+=["─"*58,f"  {'TOTAL':<18}{'':>8}{gt:>14.2f}"]
            return "\n".join(L)
        except Exception as e: return f"Error: {e}"


# =============================================================
#  AI ASSISTANT
# =============================================================
class AIPage(BasePage):
    def __init__(self, master, user):
        super().__init__(master, user)
        self._header("AI Assistant","Smart rule-based farm analysis")

        # Button row
        br=ctk.CTkFrame(self,fg_color=CARD_BG,corner_radius=10,
                        border_color=CARD_BORDER,border_width=1)
        br.pack(fill="x",padx=20,pady=(0,8))
        inner=ctk.CTkFrame(br,fg_color="transparent")
        inner.pack(padx=12,pady=10)
        for txt,cmd,typ in [
            ("🥛 Milk Analysis",   self._milk_analysis,   "primary"),
            ("⚖️  Weight Check",   self._weight_check,    "secondary"),
            ("💉 Health Events",   self._health_events,   "secondary"),
            ("🔬 Symptom Checker", self._symptom_toggle,  "secondary"),
            ("💡 Farm Tips",       self._farm_tips,       "secondary"),
        ]:
            (PrimaryButton if typ=="primary" else SecondaryButton)(
                inner, txt, cmd, width=148
            ).pack(side="left", padx=4)

        # Symptom input bar (hidden initially)
        self._sym_bar = ctk.CTkFrame(self, fg_color=CARD_BG,
                                     corner_radius=8,
                                     border_color=CARD_BORDER, border_width=1)
        self._sym_e = StyledEntry(self._sym_bar,
                                  "Type symptoms e.g. fever, cough, not eating…", 440)
        self._sym_e.pack(side="left", padx=12, pady=10)
        PrimaryButton(self._sym_bar,"Analyze",self._run_sym,width=110).pack(
            side="left", padx=(0,12), pady=10)

        # Output area
        card=SectionCard(self)
        card.pack(fill="both",expand=True,padx=20,pady=(0,16))
        ctk.CTkLabel(card,text="🤖  AI Suggestions",font=FONT_SUBHEAD,
                     text_color=TEXT_ACCENT).pack(anchor="w",padx=14,pady=(12,4))
        divider(card,padx=14,pady=0)
        self._out=ctk.CTkTextbox(card,fg_color=INPUT_BG,text_color=TEXT_PRIMARY,
                                 font=("Segoe UI",11),border_color=BORDER,
                                 border_width=1,corner_radius=8)
        self._out.pack(fill="both",expand=True,padx=10,pady=(6,10))
        self._out.configure(state="disabled")
        self._write("Click any button above to run an AI analysis on your farm data.")

    def _write(self,txt):
        self._out.configure(state="normal")
        self._out.delete("1.0","end")
        self._out.insert("end",txt)
        self._out.configure(state="disabled")

    def _sym_bar_hide(self): self._sym_bar.pack_forget()

    def _milk_analysis(self):
        self._sym_bar_hide()
        try:
            conn=get_connection(); c=conn.cursor()
            c.execute("SELECT AVG(liters) FROM milk WHERE date>=date('now','-3 days')")
            recent=c.fetchone()[0] or 0
            c.execute("SELECT AVG(liters) FROM milk WHERE date>=date('now','-10 days') AND date<date('now','-3 days')")
            prev=c.fetchone()[0] or 0; conn.close()
            L=["🥛  MILK PRODUCTION ANALYSIS\n"+"─"*54,
               f"  Recent avg  (last 3 days) : {recent:.2f} L/session",
               f"  Previous avg (last 7 days): {prev:.2f} L/session",""]
            if prev>0 and recent<prev*0.85:
                drop=((prev-recent)/prev)*100
                L+=[f"  ⚠  Production dropped by {drop:.1f}%!","",
                    "  RECOMMENDATIONS:","  1. Increase protein-rich feed (concentrate, soy)",
                    "  2. Ensure unlimited clean water supply",
                    "  3. Check for signs of illness or stress",
                    "  4. Review milking schedule consistency",
                    "  5. Consult a veterinarian if drop persists"]
            elif recent==0 and prev==0:
                L+=["  ℹ  Not enough data. Please record more milk entries."]
            else:
                L+=["  ✅  Milk production is STABLE.",
                    "  Keep maintaining the current feeding & milking schedule."]
            self._write("\n".join(L))
        except Exception as e: self._write(f"Error: {e}")

    def _weight_check(self):
        self._sym_bar_hide()
        try:
            conn=get_connection(); c=conn.cursor()
            c.execute("SELECT id,name,weight FROM cows WHERE status='Active'")
            cows=c.fetchall(); conn.close()
            uw=[r for r in cows if r[2]<300]
            L=["⚖️   COW WEIGHT ANALYSIS\n"+"─"*54,
               f"  Total active  : {len(cows)}",
               f"  Healthy (≥300kg) : {len(cows)-len(uw)}",
               f"  Underweight (<300kg) : {len(uw)}",""]
            if uw:
                L+=["  UNDERWEIGHT COWS:"]+[f"  → {r[1]:<18} {r[2]} kg  (ID:{r[0]})" for r in uw]+["",
                   "  ⚠  RECOMMENDATIONS:",
                   "  1. Increase daily hay and concentrate rations",
                   "  2. Add mineral & vitamin supplements",
                   "  3. Check for parasites or underlying illness",
                   "  4. Monitor weight every 2 weeks"]
            else:
                L+=["  ✅  All cows are at a healthy weight!"]
            self._write("\n".join(L))
        except Exception as e: self._write(f"Error: {e}")

    def _health_events(self):
        self._sym_bar_hide()
        try:
            conn=get_connection(); c=conn.cursor()
            c.execute("""SELECT h.record_type,c.name,h.date,COALESCE(h.description,'')
                         FROM health h JOIN cows c ON h.cow_id=c.id
                         WHERE h.date>=date('now','-7 days') ORDER BY h.date DESC""")
            rows=c.fetchall(); conn.close()
            L=["💉  HEALTH EVENT ANALYSIS  (Last 7 Days)\n"+"─"*54,
               f"  Events found: {len(rows)}",""]
            if not rows:
                L+=["  ✅  No health events this week!",
                    "  Reminder: schedule routine vaccinations if due."]
            else:
                L+=[f"  [{r[0]}] {r[1]:<18} {r[2]}  –  {r[3]}" for r in rows]
                dc=sum(1 for r in rows if r[0]=="Disease")
                if dc>=3:
                    L+=["",f"  🚨  OUTBREAK ALERT: {dc} disease cases!",
                       "  → Isolate affected cows IMMEDIATELY",
                       "  → Contact veterinarian urgently",
                       "  → Disinfect barn and water sources"]
                else:
                    L+=["","  Monitor affected cows closely.",
                       "  Consult a vet if symptoms worsen."]
            self._write("\n".join(L))
        except Exception as e: self._write(f"Error: {e}")

    def _symptom_toggle(self):
        self._sym_bar.pack(fill="x",padx=20,pady=(0,8),before=self._out.master)
        self._sym_e.delete(0,"end"); self._sym_e.focus()
        self._write("Type symptoms below and click Analyze.\n\nExamples: fever, cough, not eating, limping, diarrhea")

    def _run_sym(self):
        sym=self._sym_e.get().strip().lower()
        if not sym: self.err("Please enter symptoms."); return
        res=[]
        if "fever" in sym:   res.append("🌡  FEVER: Contact vet immediately. Isolate cow, monitor temp every 2h.")
        if "cough" in sym:   res.append("😮  COUGH: Isolate from herd. Schedule medical check-up ASAP.")
        if "diarrhea" in sym or "loose stool" in sym:
            res.append("💧  DIARRHEA: Ensure clean water. Reduce concentrate feed. Vet if >24h.")
        if "limping" in sym or "lame" in sym:
            res.append("🦶  LAMENESS: Check hooves for injury. Limit movement. Apply hoof treatment.")
        if "not eating" in sym or "loss of appetite" in sym:
            res.append("🍽  APPETITE LOSS: Check for fever/dental issues. Offer fresh green feed. Vet if >2 days.")
        if not res:
            res=["✅  No specific issues detected. Monitor closely and consult vet if worsens."]
        L=[f"🔬  SYMPTOM ANALYSIS: '{sym}'\n"+"─"*54,""]
        for r in res: L+=[f"  {r}",""]
        self._write("\n".join(L))

    def _farm_tips(self):
        self._sym_bar_hide()
        tips=[("🕐","Feed cows at the same time every day to maintain routine."),
              ("💧","Ensure every cow has clean, fresh water at all times."),
              ("🧹","Clean barn floors daily to prevent hoof disease."),
              ("💉","Vaccinate cows regularly per your vet's schedule."),
              ("📋","Record milk production daily to detect drops early."),
              ("⚖️ ","Weigh cows monthly to monitor nutrition and growth."),
              ("🔴","Separate sick cows immediately to prevent spreading."),
              ("🌬","Ensure proper barn ventilation for respiratory health."),
              ("🦶","Check and trim hooves every 2–3 months."),
              ("😌","Stress-free cows produce significantly more milk.")]
        L=["💡  GENERAL FARM TIPS\n"+"─"*54]
        for i,(ic,t) in enumerate(tips,1): L.append(f"  {i:>2}. {ic}  {t}")
        self._write("\n".join(L))


# =============================================================
#  USERS  (Admin only)
# =============================================================
class UsersPage(BasePage):
    def __init__(self, master, user):
        super().__init__(master, user)
        if user["role"] != "admin":
            self._header("Access Denied")
            StyledLabel(self,"⛔  You do not have permission to view this page.",
                        text_color=DANGER).pack(pady=40)
            return
        self._header("User Management","Create and manage system accounts")
        tb=self._toolbar()
        PrimaryButton(tb,"➕  Create User",self._create).pack(side="left",padx=(0,8))
        SecondaryButton(tb,"🔄 Refresh",   self._load).pack(side="left")

        card=self._card()
        self.tbl=DataTable(card,[
            ("id","ID",50),("user","Username",130),("name","Full Name",160),
            ("role","Role",100),("active","Active",70),("by","Created By",120)])
        self.tbl.pack(fill="both",expand=True,padx=10,pady=10)

        ab=self._action_bar(card)
        PrimaryButton(ab,"✅ Activate",   self._activate,   width=120).pack(side="left",padx=(0,8))
        DangerButton(ab, "🚫 Deactivate", self._deactivate, width=130).pack(side="left")
        self._load()

    def _load(self):
        try:
            c=get_connection().execute(
                "SELECT id,username,full_name,role,is_active,created_by FROM users ORDER BY id")
            self.tbl.load([(r[0],r[1],r[2] or "",r[3],"Yes" if r[4] else "No",r[5])
                           for r in c.fetchall()])
            c.connection.close()
        except Exception as e: self.err(str(e))

    def _create(self):
        CreateUserDialog(self, current_user=self.user,
                         on_save=lambda m:(self.ok(m),self._load()))

    def _deactivate(self):
        r=self.tbl.get_selected()
        if not r: self.info("Select a user."); return
        if r[0]==self.user["id"]: self.err("Cannot deactivate yourself."); return
        if messagebox.askyesno("Deactivate",f"Deactivate '{r[1]}'?"):
            try:
                conn=get_connection()
                conn.execute("UPDATE users SET is_active=0 WHERE id=?",(r[0],))
                conn.commit(); conn.close(); self.ok(f"'{r[1]}' deactivated."); self._load()
            except Exception as e: self.err(str(e))

    def _activate(self):
        r=self.tbl.get_selected()
        if not r: self.info("Select a user."); return
        try:
            conn=get_connection()
            conn.execute("UPDATE users SET is_active=1 WHERE id=?",(r[0],))
            conn.commit(); conn.close(); self.ok(f"'{r[1]}' activated."); self._load()
        except Exception as e: self.err(str(e))


class CreateUserDialog(BaseDialog):
    def __init__(self, parent, current_user, on_save):
        super().__init__(parent,"Create User Account",460,440)
        self.current_user = current_user
        self.on_save      = on_save

        ctk.CTkLabel(self.body,
                     text="Admin can create Worker, Salesman, Watchman,\n"
                          "Cleaner and Farm Owner accounts.",
                     font=FONT_TINY, text_color=TEXT_MUTED
                     ).pack(anchor="w", pady=(0,8))

        def E(ph): return lambda row: StyledEntry(row, ph, 300)
        def C(v):  return lambda row: StyledCombo(row, v, 300)
        def P(ph): return lambda row: PasswordEntry(row, ph, width=300)

        self.e_user = self.add_field("Username *", E("Username"))
        self.e_name = self.add_field("Full Name",  E("Full name"))
        self.c_role = self.add_field("Role *",
                                     C(["worker","salesman","watchman",
                                        "cleaner","farm_owner"]))
        self.e_pass = self.add_field("Password *", P("Password (min 4 chars)"))
        self.e_conf = self.add_field("Confirm *",  P("Confirm password"))

        self.add_buttons(self._save)

    def _save(self):
        username = self.e_user.get().strip()
        fullname = self.e_name.get().strip()
        role     = self.c_role.get()
        pw       = self.e_pass.get()
        cf       = self.e_conf.get()

        if not username:
            messagebox.showwarning("","Username is required."); return
        if len(pw) < 4:
            messagebox.showwarning("","Password must be at least 4 characters."); return
        if pw != cf:
            messagebox.showwarning("","Passwords do not match."); return

        hashed = hashlib.sha256(pw.encode()).hexdigest()
        try:
            conn=get_connection(); c=conn.cursor()
            c.execute("SELECT id FROM users WHERE username=?",(username,))
            if c.fetchone():
                messagebox.showwarning("",f"Username '{username}' already exists.")
                conn.close(); return
            c.execute(
                "INSERT INTO users (username,password,role,full_name,created_by) VALUES(?,?,?,?,?)",
                (username, hashed, role, fullname, self.current_user["username"]))
            conn.commit(); conn.close()
            self.on_save(f"User '{username}' ({role}) created."); self.destroy()
        except Exception as e: messagebox.showerror("Error",str(e))
