# The Saturation Point — Pen Care Studio

A local Windows/Python PySide6 staff service desk for fountain-pen care. The app records customer and pen intake, condition, requested services, estimates and due dates; supports editing, search, status and due-date filtering, notes and pickup; and records payments separately from estimates. The job detail and printable service summary show payments and the remaining amount against the estimate. Reports distinguish claimed-job estimates from actual payments recorded.

## For the professor (Windows ZIP)

1. Download the ZIP, right-click it in File Explorer and choose **Extract All**.
2. Open the extracted folder and double-click **Pen Care Studio.exe**. Keep the `_internal` folder beside the executable.
3. On first launch, create and confirm a staff password of at least eight characters. Remember it; there is no password reset. On later launches, sign in with it.
4. To explore sample records, check **Open demo workspace (sample data)** before opening. The title says **DEMO DATA**. Uncheck it on the next sign-in to return to real jobs.

`START_HERE.txt` beside the executable contains the same instructions. The app runs offline; Python and a terminal are not needed for the packaged version.

## Local data and backups

The Windows user’s real data and staff-password hash are stored in `%LOCALAPPDATA%\TheSaturationPoint\PenCareStudio\jobs.sqlite3`. Demo jobs are in `jobs-demo.sqlite3` in the same directory. In File Explorer paste `%LOCALAPPDATA%\TheSaturationPoint\PenCareStudio` into the address bar to locate them. Close the app and copy the database files to back them up. The app does not store its database in the ZIP or application folder. Existing job and payment records remain in place when the staff login table is added.

The one local staff password uses a randomly salted PBKDF2-HMAC-SHA256 hash, not plain text. This is a local sign-in, not full database encryption or protection from someone with access to the Windows files. Back up the real database with its password hash. There is no built-in password recovery.

## Demonstration flow

1. Sign in with **Open demo workspace** checked. Select **Jobs** and search for `Pilot Custom` or filter by **Overdue**.
2. Select **New intake**, enter a customer and a Lamy Safari, note its condition, select a service, set an estimate and due date, and save.
3. Select the new ticket and choose **Edit intake** to change its details. Add a work note if desired.
4. Advance it through **Inspecting**, **In service**, and **Ready**. Select **Record payment**, enter an amount and method, and save. Compare the estimate, amount recorded, and remaining amount.
5. Open **Service summary**, then choose **Mark claimed** and confirm pickup. Open **Reports** to compare claimed estimates with payments recorded. Use a different demo job to demonstrate cancellation.

Payments are append-only: correction, deletion, and refunds are not supported. Payments made before cancellation remain in the report total; new payments cannot be added to cancelled jobs. The remaining amount is relative to the estimate, not a final invoice. Printed output depends on the system printer.

## Developer setup

Requires Python 3.10 or newer on Windows. From the source folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

To use an isolated developer database, run `.\.venv\Scripts\python.exe app.py --db test.sqlite3`; create its own staff password on first launch. The sign-in demo checkbox creates a separate `test-demo.sqlite3`. `--demo` requires an explicit `--db` path and seeds that database only if it contains no jobs.

Run `.\.venv\Scripts\python.exe verify.py`, `verify_access.py`, and `verify_payments.py` (with the Python executable) for the automated checks. To build on Windows, install PyInstaller 6.22.0 (`.\.venv\Scripts\python.exe -m pip install PyInstaller==6.22.0`) and run `.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean "Pen Care Studio.spec"`; copy `START_HERE.txt` into `dist\Pen Care Studio` before zipping that folder.


## Desktop layout and design checks

The interface uses larger Segoe UI body and table text, serif page titles, a warm paper workspace, and labelled status badges. The queue groups pen and customer on two lines. Below 1180 logical pixels, selected-job details use the full content width; **Back to queue** preserves the current filters. Dialog content scrolls on short displays while Save and Cancel remain reachable.

Run `python verify_design.py` with the project environment to check shared header placement, count alignment, keyboard activation, compact navigation, empty-state actions, and dialog bounds. `python review_refinement.py` captures all pages with empty and fictional in-memory data in `screenshots/refinement`. Set `QT_SCALE_FACTOR` to `1.5` or `2` for additional scaling checks. These checks do not open the real database.

## Repository layout

The local `saturation-point` directory is the Git repository root. GitHub therefore shows `app.py`, `store.py`, and the other project files directly at the repository root; no enclosing `saturation-point` folder is expected after cloning.

Source, automated checks, the current visual-review script, packaging configuration, and user instructions are tracked. Local planning references, generated presentations, screenshots, databases, virtual environments, builds, and distribution ZIPs are excluded. Downloadable Windows packages are prepared separately from the source repository.
