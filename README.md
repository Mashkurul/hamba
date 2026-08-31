# HAMBA – AI Based Cow Management System

A farm management system for cows with **two interfaces**:
- **Terminal app** — beginner-friendly, uses only Python built-ins
- **Desktop GUI** — dark-themed interface built with CustomTkinter

Built as a university project using Python 3 and SQLite3.

---

## How to Run

**Terminal version:**

```bash
cd HAMBA
python main.py
```

**Desktop GUI version:**

```bash
pip install customtkinter
python app.py
```

Default login: `admin` / `admin123` (change it after first login). 

---

## Project Structure

```
HAMBA/
├── main.py                  # Terminal entry point
├── app.py                   # GUI entry point (CustomTkinter)
├── config.py                # App settings, roles & constants
├── database.py              # Database setup & connection
│
├── models/                  # Data classes (one per table)
│   ├── cow.py  ├── employee.py  ├── milk.py
│   ├── food.py ├── health.py    └── expense.py
│
├── modules/                 # Terminal feature modules
│   ├── auth.py              # Login, user management, passwords
│   ├── cow_management.py    ├── milk_management.py
│   ├── food_management.py   ├── health_management.py
│   ├── employee_management.py
│   ├── expense_management.py
│   ├── reports.py           ├── ai_assistant.py
│   ├── incident_management.py   # Watchman security incidents
│   ├── cleaning_management.py   # Cleaner sanitation records
│   ├── notifications.py         # Notifications & alerts
│   └── farm_owner.py            # Farm Owner dashboard & menu
│
├── gui/                     # Desktop GUI files
│   ├── login_window.py      # Sign-in screen
│   ├── main_window.py       # Main window & sidebar navigation
│   ├── pages.py             # Feature pages (cows, milk, etc.)
│   ├── new_pages.py         # Incidents, cleaning, notifications,
│   │                        #   owner dashboard
│   ├── widgets.py           # Reusable widgets (tables, dialogs…)
│   └── theme.py             # Colors, fonts & sizes
│
├── database/
│   └── hamba.db             # SQLite database (auto-created)
│
└── README.md
```

---

## Roles & Permissions

| Role        | Access                                                                 |
|-------------|------------------------------------------------------------------------|
| Admin       | Full access + user management (can create all accounts)               |
| Farm Owner  | Full operational access: farm summary, all modules, reports, AI       |
| Worker      | Cows, milk, food, health, AI assistant                                |
| Salesman    | Milk, expense & sales, reports                                        |
| Watchman    | Own attendance, incidents, notifications, alerts, employee presence,  |
|             | read-only cow status, milk report                                     |
| Cleaner     | Cleaning tasks & records, sanitation problems, notifications, alerts  |

Admin can create accounts for: **Worker, Salesman, Watchman, Cleaner and Farm Owner**.

---

## Features

| Module              | Features                                                     |
|---------------------|--------------------------------------------------------------|
| Authentication      | Login, role-based menus, change password, user management    |
| Cow Management      | Add, view, search, update, delete cows                       |
| Milk Management     | Record daily milk, view history, calculate totals            |
| Food Management     | Feed stock, daily feeding, update/delete records             |
| Health & Medicine   | Medical history, vaccinations, disease tracking              |
| Employee Mgmt       | Add staff, attendance, salary info                           |
| Expense & Sales     | Log expenses, milk sales, profit calculation                 |
| Reports             | Daily, monthly, milk production, expense reports             |
| AI Assistant        | Rule-based health & production analysis                      |
| Incidents           | Security incidents: theft, visitors, fire, equipment damage… |
| Cleaning            | Sanitation tasks, records, problem reporting                 |
| Notifications       | Role-targeted notices and important/emergency alerts         |

---

## AI Assistant Rules

The AI assistant is **rule-based** (no API required):

- Milk production drops → suggests nutrition improvement
- Underweight cow (<300kg) → suggests feed increase
- Symptom "fever" → recommends vet contact
- Symptom "cough" → recommends isolation
- Symptom "diarrhea" → recommends water & vet check
- 3+ disease events in 7 days → outbreak alert
- General farm tips available on demand

---

## Database Tables

| Table         | Purpose                              |
|---------------|--------------------------------------|
| cows          | Cow records                          |
| milk          | Daily milk production                |
| food          | Feed stock & daily feeding           |
| health        | Medical / vaccination records        |
| employees     | Staff information                    |
| attendance    | Daily attendance                     |
| expenses      | Farm expenses                        |
| sales         | Milk sales & revenue                 |
| users         | Login accounts (hashed passwords)    |
| incidents     | Security incident reports            |
| cleaning      | Cleaning & sanitation records        |
| notifications | Notices and important alerts         |

---

## Requirements

- Python 3.7 or higher
- Terminal app: no external packages (built-ins only)
- GUI app: `customtkinter`

---

*HAMBA*
