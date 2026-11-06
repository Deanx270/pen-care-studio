# The Saturation Point — Pen Care Studio

A local, offline PySide6 service desk for fountain-pen care. Intake records customer and pen details, condition, selected services, an editable estimate and an optional due date. The queue supports search, status and due-date filters, sorting, a selected-job pane, work notes, status changes and pickup. Service summaries can be previewed and sent to a printer or a system PDF printer. Overview links lead to actionable queues; Customers, Services and Reports provide local reference views.

## Run on Windows

On the original development machine, the prepared environment can be used directly from this folder in PowerShell:

```powershell
.\.venv\Scripts\python.exe app.py
```

For a fresh clone or installation with Python 3.10 or newer, create the environment and install dependencies first:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

If your Python installation cannot bootstrap pip into a virtual environment, install dependencies with the system pip instead: `python -m pip install --target .venv/Lib/site-packages -r requirements.txt`.

The default database is `%LOCALAPPDATA%\TheSaturationPoint\PenCareStudio\jobs.sqlite3` and starts empty. Back up this file while the app is closed. To explore sample jobs without mixing them with real records, run:

```powershell
.\.venv\Scripts\python.exe app.py --db demo.sqlite3 --demo
```

Demo data is added only if that database has no jobs. Use `--db PATH` to choose another database. Never use `--demo` against a real empty database.

## Working at the desk

- Use **New intake** (Ctrl+N) to register a job. Check services before adjusting the suggested estimate; changing services recalculates it.
- Use **Jobs** and Ctrl+F to search. Click a column heading to sort. Due today and overdue omit ready, claimed and cancelled jobs.
- Select a job to see its condition, estimate and activity. Add work notes, advance the job, or preview the service summary. The next status follows Received → Inspecting → In service → Ready → Claimed. Pickup and cancellation require confirmation; cancellation cannot be reversed in this release.
- A service summary shows the estimate, not a payment or invoice. Printing depends on your system printer configuration.

This first release records intake details once; editing customer or job details after intake, payment tracking, staff accounts and automatic backups are not included. Activity identifies the operator as “Desk staff”.

## Verification

Run `.\.venv\Scripts\python.exe verify.py` for database and GUI workflow checks using an in-memory database. `capture.py` generates local screenshots in `screenshots/`; its demo databases are separate from real data. Screens were reviewed with Qt scaling at 100%, 150%, and 200%, including a compact 1024×700 logical window. The summary preview was inspected; a physical printer was not exercised.
