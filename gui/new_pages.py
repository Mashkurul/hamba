# =============================================================
# gui/new_pages.py  –  Watchman / Cleaner / Farm Owner pages
# =============================================================
# Pages added for the new roles:
#   IncidentsPage     (Watchman / Farm Owner)
#   CleaningPage      (Cleaner / Farm Owner)
#   NotificationsPage (all roles)
#   OwnerDashboardPage(Farm Owner)
# =============================================================

from datetime import date, datetime
from tkinter import messagebox
import customtkinter as ctk

from database import get_connection
from config import (INCIDENT_TYPES, INCIDENT_PRIORITY, INCIDENT_STATUS,
                    CLEANING_AREAS, CLEANING_TYPES, CLEANING_STATUS,
                    NOTIFICATION_CATEGORIES, NOTIFICATION_PRIORITY)
from gui.theme import *
from gui.widgets import (PrimaryButton, DangerButton, SecondaryButton,
                         StyledLabel, StyledEntry, StyledCombo,
                         SectionCard, PageHeader, DataTable,
                         NotificationBar, BaseDialog, form_row, divider)


def today(): return str(date.today())
def now_time(): return datetime.now().strftime("%H:%M")


# =============================================================
#  INCIDENTS  (Watchman / Farm Owner)
# =============================================================
class IncidentsPage(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color=BG_DARK, corner_radius=0)
        self.user = user
        self.notify = NotificationBar(self)

        PageHeader(self, "Farm Incidents", "Record and monitor security incidents"
                   ).pack(anchor="w", padx=24, pady=(18, 10))
        self.notify.pack_forget()

        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(fill="x", padx=20, pady=(0, 8))
        PrimaryButton(tb, "➕  Record Incident", self._add).pack(side="left", padx=(0, 8))
        SecondaryButton(tb, "🔄 Refresh", self._load).pack(side="left", padx=(0, 8))
        self._search_e = StyledEntry(tb, "Search type / location / status…", 220)
        self._search_e.pack(side="left")
        self._search_e.bind("<KeyRelease>",
                            lambda _: self._filter(self._search_e.get()))

        card = SectionCard(self)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        self.tbl = DataTable(card, [
            ("id", "ID", 45), ("type", "Type", 150), ("priority", "Priority", 80),
            ("status", "Status", 95), ("date", "Date", 95), ("time", "Time", 60),
            ("loc", "Location", 110), ("by", "Reported By", 90),
        ])
        self.tbl.pack(fill="both", expand=True, padx=10, pady=10)

        ab = ctk.CTkFrame(card, fg_color="transparent")
        ab.pack(fill="x", padx=10, pady=(0, 10))
        PrimaryButton(ab, "✏️  Update Status", self._update_status,
                      width=140).pack(side="left")

        self._rows = []
        self._load()

    def _load(self):
        try:
            c = get_connection().execute(
                """SELECT incident_id, incident_type, priority, status, date, time,
                          COALESCE(location,''), COALESCE(reported_by,'')
                   FROM incidents ORDER BY date DESC, time DESC""")
            self._rows = [tuple(r) for r in c.fetchall()]
            c.connection.close()
            self.tbl.load(self._rows)
        except Exception as e:
            self.err(str(e))

    def _filter(self, kw):
        kw = kw.lower()
        self.tbl.load([r for r in self._rows
                       if any(kw in str(v).lower() for v in r)])

    def _add(self):
        IncidentDialog(self, user=self.user,
                       on_save=lambda m: (self.ok(m), self._load()))

    def _update_status(self):
        r = self.tbl.get_selected()
        if not r:
            self.info("Select an incident to update."); return
        StatusDialog(self, incident=r,
                     on_save=lambda m: (self.ok(m), self._load()))

    def ok(self, m):   self.notify.show(m, "success")
    def err(self, m):  self.notify.show(m, "error")
    def info(self, m): self.notify.show(m, "info")


class IncidentDialog(BaseDialog):
    def __init__(self, parent, user, on_save):
        super().__init__(parent, "Record Incident", 480, 470)
        self.user, self.on_save = user, on_save

        def E(ph): return lambda row: StyledEntry(row, ph, 300)
        def C(v):  return lambda row: StyledCombo(row, v, 300)

        self.c_type  = self.add_field("Incident Type *", C(INCIDENT_TYPES))
        self.e_desc  = self.add_field("Description *",   E("What happened?"))
        self.e_date  = self.add_field("Date",            E(today()))
        self.e_time  = self.add_field("Time",            E(now_time()))
        self.e_loc   = self.add_field("Location",        E("e.g. Main Gate"))
        self.c_pri   = self.add_field("Priority",        C(INCIDENT_PRIORITY))
        self.e_date.insert(0, today())
        self.e_time.insert(0, now_time())
        self.add_buttons(self._save)

    def _save(self):
        desc = self.e_desc.get().strip()
        if not desc:
            messagebox.showwarning("", "Description is required."); return
        try:
            conn = get_connection()
            conn.execute("""
                INSERT INTO incidents
                    (reported_by, incident_type, description, date, time, location, priority, status)
                VALUES (?,?,?,?,?,?,?,'Open')
            """, (self.user["username"], self.c_type.get(), desc,
                  self.e_date.get().strip() or today(), self.e_time.get().strip() or now_time(),
                  self.e_loc.get().strip(), self.c_pri.get()))
            conn.commit(); conn.close()
            self.on_save("Incident recorded."); self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


class StatusDialog(BaseDialog):
    def __init__(self, parent, incident, on_save):
        super().__init__(parent, f"Update Incident #{incident[0]}", 420, 240)
        self.incident_id = incident[0]
        self.on_save = on_save
        StyledLabel(self.body,
                    f"{incident[1]}  |  {incident[3]}  |  {incident[4]}",
                    text_color=TEXT_SECONDARY).pack(anchor="w", pady=(0, 10))
        self.c_status = self.add_field("Status", lambda row: StyledCombo(row, INCIDENT_STATUS, 260))
        self.c_status.set(incident[3])
        self.add_buttons(self._save)

    def _save(self):
        try:
            conn = get_connection()
            conn.execute("UPDATE incidents SET status=? WHERE incident_id=?",
                         (self.c_status.get(), self.incident_id))
            conn.commit(); conn.close()
            self.on_save(f"Status → {self.c_status.get()}"); self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# =============================================================
#  CLEANING  (Cleaner / Farm Owner)
# =============================================================
class CleaningPage(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color=BG_DARK, corner_radius=0)
        self.user = user
        self.notify = NotificationBar(self)

        PageHeader(self, "Cleaning & Sanitation",
                   "Track cleaning tasks and sanitation records"
                   ).pack(anchor="w", padx=24, pady=(18, 10))
        self.notify.pack_forget()

        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(fill="x", padx=20, pady=(0, 8))
        PrimaryButton(tb, "➕  Add Cleaning Record", self._add).pack(side="left", padx=(0, 8))
        SecondaryButton(tb, "🔄 Refresh", self._load).pack(side="left")

        card = SectionCard(self)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        self.tbl = DataTable(card, [
            ("id", "ID", 45), ("area", "Area", 150), ("ctype", "Type", 170),
            ("status", "Status", 90), ("date", "Date", 95), ("time", "Time", 60),
            ("remarks", "Remarks", 160),
        ])
        self.tbl.pack(fill="both", expand=True, padx=10, pady=10)

        ab = ctk.CTkFrame(card, fg_color="transparent")
        ab.pack(fill="x", padx=10, pady=(0, 10))
        PrimaryButton(ab, "✅  Mark Complete", self._complete,
                      width=140).pack(side="left", padx=(0, 8))
        DangerButton(ab, "⚠️  Report Problem", self._report, width=140).pack(side="left")

        self._load()

    def _load(self):
        try:
            c = get_connection().execute(
                """SELECT cleaning_id, area, cleaning_type, status, date, time,
                          COALESCE(remarks,'')
                   FROM cleaning ORDER BY date DESC, time DESC""")
            self.tbl.load([tuple(r) for r in c.fetchall()])
            c.connection.close()
        except Exception as e:
            self.err(str(e))

    def _add(self):
        CleaningDialog(self, user=self.user,
                       on_save=lambda m: (self.ok(m), self._load()))

    def _complete(self):
        r = self.tbl.get_selected()
        if not r:
            self.info("Select a task to mark complete."); return
        try:
            conn = get_connection()
            conn.execute("UPDATE cleaning SET status='Completed' WHERE cleaning_id=?", (r[0],))
            conn.commit(); conn.close()
            self.ok(f"Task #{r[0]} marked Completed."); self._load()
        except Exception as e:
            self.err(str(e))

    def _report(self):
        r = self.tbl.get_selected()
        if not r:
            self.info("Select a task to report a problem."); return
        try:
            conn = get_connection()
            conn.execute("""
                UPDATE cleaning SET status='In Progress',
                       remarks = COALESCE(remarks,'') || ' [PROBLEM REPORTED]'
                WHERE cleaning_id=?""", (r[0],))
            conn.commit(); conn.close()
            self.ok("Problem flagged."); self._load()
        except Exception as e:
            self.err(str(e))

    def ok(self, m):   self.notify.show(m, "success")
    def err(self, m):  self.notify.show(m, "error")
    def info(self, m): self.notify.show(m, "info")


class CleaningDialog(BaseDialog):
    def __init__(self, parent, user, on_save):
        super().__init__(parent, "Add Cleaning Record", 480, 440)
        self.user, self.on_save = user, on_save

        def E(ph): return lambda row: StyledEntry(row, ph, 300)
        def C(v):  return lambda row: StyledCombo(row, v, 300)

        self.c_area  = self.add_field("Area *",          C(CLEANING_AREAS))
        self.c_type  = self.add_field("Cleaning Type *", C(CLEANING_TYPES))
        self.e_date  = self.add_field("Date",            E(today()))
        self.e_time  = self.add_field("Time",            E(now_time()))
        self.c_stat  = self.add_field("Status",          C(CLEANING_STATUS))
        self.e_rem   = self.add_field("Remarks",         E("Optional"))
        self.e_date.insert(0, today())
        self.e_time.insert(0, now_time())
        self.add_buttons(self._save)

    def _save(self):
        try:
            conn = get_connection()
            conn.execute("""
                INSERT INTO cleaning (cleaner_id, area, cleaning_type, date, time, status, remarks)
                VALUES (?,?,?,?,?,?,?)
            """, (self.user["id"], self.c_area.get(), self.c_type.get(),
                  self.e_date.get().strip() or today(), self.e_time.get().strip() or now_time(),
                  self.c_stat.get(), self.e_rem.get().strip()))
            conn.commit(); conn.close()
            self.on_save("Cleaning record saved."); self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# =============================================================
#  NOTIFICATIONS  (all roles)
# =============================================================
class NotificationsPage(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color=BG_DARK, corner_radius=0)
        self.user = user
        self.notify = NotificationBar(self)

        PageHeader(self, "Notifications", "Farm notices and important alerts"
                   ).pack(anchor="w", padx=24, pady=(18, 10))
        self.notify.pack_forget()

        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(fill="x", padx=20, pady=(0, 8))
        PrimaryButton(tb, "➕  New Notification", self._add,
                      width=170).pack(side="left", padx=(0, 8))
        SecondaryButton(tb, "🔄 Refresh", self._load).pack(side="left")

        card = SectionCard(self)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        self.tbl = DataTable(card, [
            ("id", "ID", 40), ("title", "Title", 180), ("cat", "Category", 100),
            ("pri", "Priority", 90), ("role", "Target", 90),
            ("date", "Created", 130), ("read", "Read", 55),
        ])
        self.tbl.pack(fill="both", expand=True, padx=10, pady=10)

        ab = ctk.CTkFrame(card, fg_color="transparent")
        ab.pack(fill="x", padx=10, pady=(0, 10))
        PrimaryButton(ab, "✓  Mark Read", self._mark_read,
                      width=120).pack(side="left")
        self._load()

    def _load(self):
        try:
            role = self.user.get("role", "all")
            c = get_connection().execute(
                """SELECT id, title, category, priority, target_role, created_at, is_read
                   FROM notifications
                   WHERE target_role IN ('all', ?)
                   ORDER BY id DESC""", (role,))
            self.tbl.load([(r[0], r[1], r[2], r[3], r[4], r[5],
                            "Yes" if r[6] else "No") for r in c.fetchall()])
            c.connection.close()
        except Exception as e:
            self.err(str(e))

    def _add(self):
        NotificationDialog(self, user=self.user,
                           on_save=lambda m: (self.ok(m), self._load()))

    def _mark_read(self):
        r = self.tbl.get_selected()
        if not r:
            self.info("Select a notification."); return
        try:
            conn = get_connection()
            conn.execute("UPDATE notifications SET is_read=1 WHERE id=?", (r[0],))
            conn.commit(); conn.close()
            self.ok("Marked as read."); self._load()
        except Exception as e:
            self.err(str(e))

    def ok(self, m):   self.notify.show(m, "success")
    def err(self, m):  self.notify.show(m, "error")
    def info(self, m): self.notify.show(m, "info")


class NotificationDialog(BaseDialog):
    def __init__(self, parent, user, on_save):
        super().__init__(parent, "New Notification", 480, 460)
        self.user, self.on_save = user, on_save

        def E(ph): return lambda row: StyledEntry(row, ph, 300)
        def C(v):  return lambda row: StyledCombo(row, v, 300)

        self.e_title = self.add_field("Title *",        E("Notification title"))
        self.e_msg   = self.add_field("Message",        E("Details"))
        self.c_cat   = self.add_field("Category",       C(NOTIFICATION_CATEGORIES))
        self.c_pri   = self.add_field("Priority",       C(NOTIFICATION_PRIORITY))
        self.c_role  = self.add_field("Target Role",    C(["all", "admin", "worker",
                                                           "salesman", "watchman",
                                                           "cleaner", "farm_owner"]))
        self.add_buttons(self._save)

    def _save(self):
        title = self.e_title.get().strip()
        if not title:
            messagebox.showwarning("", "Title is required."); return
        try:
            conn = get_connection()
            conn.execute("""
                INSERT INTO notifications
                    (title, message, category, priority, target_role, created_by, created_at)
                VALUES (?,?,?,?,?,?,?)
            """, (title, self.e_msg.get().strip(), self.c_cat.get(),
                  self.c_pri.get(), self.c_role.get(), self.user["username"],
                  datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit(); conn.close()
            self.on_save("Notification sent."); self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# =============================================================
#  OWNER DASHBOARD  (Farm Owner)
# =============================================================
class OwnerDashboardPage(ctk.CTkFrame):
    """Farm owner's high-level farm summary + monitoring."""

    def __init__(self, master, user):
        super().__init__(master, fg_color=BG_DARK, corner_radius=0)
        self.user = user
        self.notify = NotificationBar(self)

        PageHeader(self, "Farm Overview",
                   "Complete farm statistics at a glance"
                   ).pack(anchor="w", padx=24, pady=(18, 10))
        self.notify.pack_forget()

        try:
            stats = self._stats()
        except Exception:
            stats = {}

        # ── Stat cards ──
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.pack(fill="x", padx=20, pady=(0, 12))
        cards = [
            ("Total Cows",  stats.get("cows", 0),    "🐄", PRIMARY),
            ("Healthy",     stats.get("healthy", 0), "✅", SUCCESS),
            ("Sick",        stats.get("sick", 0),    "🤒", DANGER),
            ("Milk Today",  f"{stats.get('milk_today', 0):.1f} L", "🥛", INFO),
            ("Employees",   stats.get("employees", 0), "👷", WARNING),
            ("Attendance",  stats.get("att_today", 0), "📋", ACCENT),
        ]
        for i, (t, v, ic, col) in enumerate(cards):
            from gui.widgets import StatCard
            StatCard(sf, t, v, ic, col).grid(
                row=0, column=i, padx=6, pady=4, sticky="ew", ipady=4)
            sf.grid_columnconfigure(i, weight=1)

        # ── Two info panels ──
        lower = ctk.CTkFrame(self, fg_color="transparent")
        lower.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        lower.grid_columnconfigure(0, weight=1)
        lower.grid_columnconfigure(1, weight=1)
        lower.grid_rowconfigure(0, weight=1)

        def panel(col, title, lines):
            c = SectionCard(lower)
            c.grid(row=0, column=col, padx=(0, 8) if col == 0 else (8, 0),
                   sticky="nsew")
            ctk.CTkLabel(c, text=title, font=("Segoe UI", 13, "bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w", padx=14, pady=(12, 4))
            divider(c, padx=14, pady=0)
            box = ctk.CTkTextbox(c, fg_color=INPUT_BG, text_color=TEXT_PRIMARY,
                                 font=("Consolas", 11), border_color=BORDER,
                                 border_width=1, corner_radius=8, wrap="word")
            box.pack(fill="both", expand=True, padx=10, pady=(8, 10))
            box.insert("end", lines)
            box.configure(state="disabled")
            return c

        panel(0, "📊  Farm Health", self._health_lines(stats))
        panel(1, "🕒  Recent Activity", self._activity_lines())

    def _stats(self):
        conn = get_connection(); c = conn.cursor(); m = today()[:7]
        def q(sql, *a):
            c.execute(sql, a); r = c.fetchone(); return r[0] if r else 0
        return {
            "cows":       q("SELECT COUNT(*) FROM cows"),
            "healthy":    q("SELECT COUNT(*) FROM cows WHERE status='Active'"),
            "sick":       q("SELECT COUNT(*) FROM cows WHERE status='Sick'"),
            "milk_today": q("SELECT COALESCE(SUM(liters),0) FROM milk WHERE date=?", today()),
            "employees":  q("SELECT COUNT(*) FROM employees WHERE status='Active'"),
            "att_today":  q("SELECT COUNT(*) FROM attendance WHERE date=?", today()),
            "low_stock":  q("SELECT COUNT(*) FROM food WHERE quantity_kg < 50"),
            "vacc":       q("""SELECT COUNT(*) FROM health WHERE record_type='Vaccination'
                               AND date BETWEEN date('now') AND date('now','+30 days')"""),
            "rev":        q("SELECT COALESCE(SUM(total_amount),0) FROM sales WHERE date LIKE ?", m + "%"),
            "exp":        q("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date LIKE ?", m + "%"),
            "incidents":  q("SELECT COUNT(*) FROM incidents WHERE status IN ('Open','In Progress')"),
            "cleaning":   q("SELECT COUNT(*) FROM cleaning WHERE status IN ('Pending','In Progress')"),
        }

    def _health_lines(self, s):
        lines = []
        lines.append(f"  Low stock items      : {s.get('low_stock', 0)}")
        lines.append(f"  Vaccinations due     : {s.get('vacc', 0)}")
        lines.append("")
        lines.append(f"  Open incidents       : {s.get('incidents', 0)}")
        lines.append(f"  Pending cleaning     : {s.get('cleaning', 0)}")
        lines.append("")
        net = s.get("rev", 0) - s.get("exp", 0)
        lines.append(f"  Month revenue        : {s.get('rev', 0):,.2f}")
        lines.append(f"  Month expenses       : {s.get('exp', 0):,.2f}")
        lines.append(f"  Month net            : {net:,.2f}")
        return "\n".join(lines)

    def _activity_lines(self):
        lines = []
        try:
            conn = get_connection(); c = conn.cursor()
            c.execute("""SELECT date, category, amount FROM expenses
                         ORDER BY id DESC LIMIT 5""")
            rows = c.fetchall()
            if rows:
                lines.append("  — Recent Expenses —")
                for r in rows:
                    lines.append(f"  {r['date']}  {r['category']:<10} {r['amount']:>9.2f}")
                lines.append("")
            c.execute("""SELECT date, liters_sold, total_amount FROM sales
                         ORDER BY id DESC LIMIT 5""")
            rows = c.fetchall()
            if rows:
                lines.append("  — Recent Sales —")
                for r in rows:
                    lines.append(f"  {r['date']}  {r['liters_sold']:>6.1f} L  {r['total_amount']:>9.2f}")
                lines.append("")
            c.execute("""SELECT date, incident_type, status FROM incidents
                         ORDER BY id DESC LIMIT 5""")
            rows = c.fetchall()
            if rows:
                lines.append("  — Recent Incidents —")
                for r in rows:
                    lines.append(f"  {r['date']}  {r['incident_type']:<18} {r['status']}")
            conn.close()
        except Exception as e:
            lines.append(f"  Error: {e}")
        if len(lines) == 0:
            lines.append("  No recent activity.")
        return "\n".join(lines)

    def ok(self, m):   self.notify.show(m, "success")
    def err(self, m):  self.notify.show(m, "error")
    def info(self, m): self.notify.show(m, "info")
