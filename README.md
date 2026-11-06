# The Saturation Point — Pen Care Studio

An offline Windows desktop application for staff managing fountain-pen care jobs, built with PySide6 and SQLite.

## Features

- Customer and pen intake, editable details, condition notes, services, estimates, and due dates.
- Searchable job queue with status and due-date filters.
- Work notes, status updates, cancellation, and pickup.
- Payment records, remaining balance against the estimate, reports, and printable service summaries.
- Local staff login and a separate demo workspace.

## Run the Windows app

1. Download the provided ZIP and choose **Extract All**.
2. Open **Pen Care Studio.exe**. Keep the `_internal` folder beside it. No Python installation is needed.
3. Create a staff password of at least eight characters on first launch; use it for later sign-ins. There is no password reset.
4. For sample records, check **Open demo workspace (sample data)** at sign-in. Uncheck it to return to real jobs.

## Data and backups

Data is stored in `%LOCALAPPDATA%\TheSaturationPoint\PenCareStudio`:

- `jobs.sqlite3`: real records and the hashed staff password.
- `jobs-demo.sqlite3`: separate demo records.

Close the app before copying these files to back them up. The database is not encrypted.

Payments cannot be edited, deleted, or refunded. Balances compare recorded payments with estimates, not final invoices; payments on cancelled jobs remain in report totals.

## Developer setup

Requires Python 3.10 or newer on Windows. Run from the source folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

For an isolated sample database:

```powershell
.\.venv\Scripts\python.exe app.py --db test.sqlite3 --demo
```

Run the automated checks:

```powershell
.\.venv\Scripts\python.exe verify.py
.\.venv\Scripts\python.exe verify_access.py
.\.venv\Scripts\python.exe verify_payments.py
.\.venv\Scripts\python.exe verify_design.py
```

Build the Windows package:

```powershell
.\.venv\Scripts\python.exe -m pip install PyInstaller==6.22.0
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean "Pen Care Studio.spec"
Copy-Item START_HERE.txt "dist\Pen Care Studio\START_HERE.txt"
```

ZIP the entire `dist\Pen Care Studio` folder for distribution.
