# C5 SPA Dashboard

## Credentials

The app no longer stores SPA credentials in the source code. Provide them using
either of the following options before running `uv run main.py`:

1. **Environment variables**

   - `SPA_USERNAME`
   - `SPA_PASSWORD`

2. **`config.ini`**
   - Edit the `username` and `password` fields in the `DEFAULT` section.

Environment variables take precedence over the values in `config.ini`. Leave the
config fields blank (or placeholders) if you prefer using environment variables.

## Building Executable

To create a standalone executable file:

1. **Install PyInstaller** (if not already installed)

   ```powershell
   uv add --dev pyinstaller
   ```

2. **Build the executable**

```powershell
uv run pyinstaller --onefile --name "SPA-Dashboard" --windowed --icon "assets/c5_spa.ico" --add-data "assets;assets" --add-data "components;components" --add-data "services;services" --add-data "utils;utils" --add-data "dashboard_view.py;." main.py
```

Or use the generated spec file for faster rebuild:

```powershell
uv run pyinstaller SPA-Dashboard.spec
```

3. **Find the executable**
   - The executable will be created in the `dist` folder: `dist\SPA-Dashboard.exe`
   - All necessary files (assets, components, services, utils) are bundled into the single executable

## Operation Manual

- **Start the application**
  - Install dependencies with `uv sync` if needed, then launch the UI via `uv run main.py`.
  - Errors and diagnostics are written to `logs/app_errors.log`.
- **Prepare sidebar inputs**
  - Field `User` must be filled before saving; it offers autocomplete from previous entries.
  - Choose `Tanggal`, `Shift`, `Link Up (LU)`, and `Functional Location` to scope SPA data and targets.
  - Toggle `Tampilkan Tabel` if you want the metrics table included in generated reports.
- **Fetch SPA data (optional)**
  - Click `Get Data` to download the latest SPA metrics. The header progress bar animates while processing.
  - Successful fetch populates the metrics table and the issue list; failures surface via a dialog and are logged.
- **Manage issue cards**
  - Cards appear in the right pane. Use `+ Detail` on a card to add problem details and `+` inside a detail to add action steps.
  - Right-click details or actions to delete them. Double-click rows in the issue table to spawn prefilled cards.
  - Use the card menu (right-click) to delete entire cards when no longer needed.
- **Save records**
  - Click `Save`. Valid cards are persisted to the history CSV, and the current user is stored for next time.
  - Any error encountered during save is shown to the user and logged.
- **Review history**
  - `History` opens a window with saved records sorted by newest entry. Use `Refresh` to reload after new saves.
- **Generate report**
  - `Report` opens a preview window combining the metrics table (when enabled) with a Markdown-style summary of cards.
- **Edit targets**
  - `Target Editor` lets you adjust per-shift target values stored alongside the SPA data. Save changes before closing.

## Notes on MD4 and NTLM

The repository previously included an MD4 compatibility shim (`utils/patched_hashlib.py`) and
an associated PyInstaller runtime hook. That fallback has been removed.

If your environment needs MD4 for NTLM authentication, please ensure your
Python build provides MD4 support or install a library such as
`pycryptodome` and add a direct import in your build/run environment as needed.

## SSL verification & self-signed certificates

If your SPA server is using a self-signed certificate or a private CA, the
HTTP client will fail with an SSL verification error unless you configure
verification appropriately. You can control SSL verification through
the `config.ini` options:

- `verify_ssl` — set to `True` (default) to verify certificate chains, or
  `False` to disable verification (less secure; use with caution).
- `ca_bundle` — optional path to a PEM file containing CA certificates to
  trust. If present, this file will be used in preference to `verify_ssl`.

Example `config.ini`:

```ini
[DEFAULT]
environment = development
username = your_username
password = your_password
link_up = LU18,LU21,LU26,LU27
url = https://ots.spappa.aws.private-pmideep.biz/db.aspx?
verify_ssl = False
ca_bundle =
```

Notes:
- It is better to configure a `ca_bundle` (PEM file) referencing a trusted
  CA than disabling verification entirely. Only set `verify_ssl` to `False`
  for development/testing or when you fully understand the security risks.

## HTTP client migration & async usage

This project migrated from `requests` and `requests-ntlm2` to the
`httpx` and `httpx-ntlm` client libraries. The `services.spa_service` module
uses `httpx.AsyncClient` for network I/O and exposes both synchronous and
asynchronous processing APIs:

- `SPADataProcessor.process()` — synchronous, blocking API (backwards compatible)
- `SPADataProcessor.process_async()` — asynchronous API. Use this in async
  contexts (e.g., GUI event loop) to avoid blocking the main thread.

Notes & examples
- If you rely on session reuse, pass a shared `httpx.AsyncClient` instance as
  the `session` parameter and call `process_async(session=...)` to reduce
  connection overhead.
- `httpx` uses `follow_redirects` instead of `allow_redirects`; when updating
  code from `requests`, replace `allow_redirects` with `follow_redirects` and
  handle `httpx.HTTPError` exceptions instead of `requests.exceptions`.

Async usage (recommended for GUI apps):

```python
from httpx import AsyncClient
from services.spa_service import SPADataProcessor

async with AsyncClient() as client:
    processor = SPADataProcessor(url, config=config, session=client)
    processed = await processor.process_async(session=client)
```

Synchronous usage (scripts, tests):

```python
processor = SPADataProcessor(url, config=config)
processed = processor.process()
```

If you prefer to keep `requests` in other scripts or tooling, note the API
differences: `requests.Session` -> `httpx.Client` (sync) or
`httpx.AsyncClient` (async). Adjust your imports and error handling accordingly.

### Downgrade to Python 3.12 (Windows)

If you need to run the project with Python 3.12, follow these instructions to remove the existing venv and create a new one using Python 3.12.

1) Install Python 3.12

- Option A — Winget (recommended on Windows 10/11):

```powershell
winget install --id Python.Python.3.12 -e --source winget
```

- Option B — Download from python.org

  Download the official Python 3.12 installer from https://www.python.org/downloads/release/python-312/ and run it. Make sure to check "Add Python to PATH" and choose the x86/x64 installer that matches your system.

2) Create / recreate the project's venv

```powershell
# Delete previous virtual environment (if any)
If (Test-Path -Path .\.venv) { Remove-Item -Recurse -Force .\.venv }

# Create a new venv using the Python 3.12 executable (adjust path if needed)
C:\Path\To\Python312\python.exe -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Upgrade pip and reinstall dependencies
python -m pip install --upgrade pip
python -m pip install async-tkinter-loop customtkinter lxml openpyxl pandas qrcode httpx httpx-ntlm tabulate ttkbootstrap ttkwidgets

# Install dev dependencies
python -m pip install pyinstaller pytest
```

3) Verify and run tests

```powershell
# Activate the venv if not already
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

Notes:

- If your system already has multiple Python versions, prefer using the full path to the 3.12 interpreter when creating the venv (C:\Python312\python.exe -m venv .venv).
- If any package requires Python >=3.13 or 3.14, you may encounter incompatibility errors; check test failures and package release notes, and pin compatible versions if needed.
- For `pyproject.toml`, this project now declares `requires-python = ">=3.12,<3.13"`. If you'd prefer a wider range (e.g., ">=3.12"), adjust accordingly.
