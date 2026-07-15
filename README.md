# HAMBA – AI Based Cow Management System

A beginner-friendly Python terminal application for managing a cow farm.
Built as a university project using Python 3 and SQLite3.

---

## How to Run

```bash
cd HAMBA
python main.py
```

No external libraries needed. Uses Python built-ins only.

---

## Project Structure

```
HAMBA/
├── main.py                  # Entry point – run this file
├── config.py                # App settings and constants
├── database.py              # Database setup and connection
│
├── models/                  # Data classes (one per table)
│   ├── cow.py
│   ├── employee.py
│   ├── milk.py
│   ├── food.py
│   ├── health.py
│   └── expense.py
│
├── modules/                 # Feature modules
│   ├── cow_management.py
│   ├── milk_management.py
│   ├── food_management.py
│   ├── health_management.py
│   ├── employee_management.py
│   ├── expense_management.py
│   ├── reports.py
│   └── ai_assistant.py
│
├── database/
│   └── hamba.db             # SQLite database (auto-created)
│
└── README.md
```

---

## Features

| Module            | Features                                              |
|-------------------|-------------------------------------------------------|
| Cow Management    | Add, View, Search, Update, Delete cows                |
| Milk Management   | Record daily milk, view history, calculate totals     |
| Food Management   | Feed stock, daily feeding, update/delete records      |
| Health & Medicine | Medical history, vaccinations, disease tracking       |
| Employee Mgmt     | Add staff, attendance, salary info                    |
| Expense & Sales   | Log expenses, milk sales, profit calculation          |
| Reports           | Daily, monthly, milk production, expense reports      |
| AI Assistant      | Rule-based health & production analysis               |

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

| Table       | Purpose                        |
|-------------|--------------------------------|
| cows        | Cow records                    |
| milk        | Daily milk production          |
| food        | Feed stock & daily feeding     |
| health      | Medical / vaccination records  |
| employees   | Staff information              |
| attendance  | Daily attendance               |
| expenses    | Farm expenses                  |
| sales       | Milk sales & revenue           |

---

## Requirements

- Python 3.7 or higher
- No external packages required (uses only built-in libraries)

---

*HAMBA – University Project*
