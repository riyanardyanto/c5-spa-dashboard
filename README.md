# C5 SPA Dashboard

Lightweight desktop dashboard for viewing and reporting SPA metrics.

This repository contains a Tkinter-based GUI that fetches SPA metrics, lets
users create and manage issue cards, save history, and export simple reports.

**Contents:** source code under `src/`, configuration in `config/`, and
sample data in `data/`.

---

## Quick Start

Prerequisites:
- Python 3.12 (recommended)
- A virtual environment (recommended)

Setup (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the app (development):

```powershell
uv run main.py
```

Notes:
- The app reads credentials from environment variables `SPA_USERNAME` and
  `SPA_PASSWORD`, or from `config/config.ini`. Environment variables take
  precedence.
- Logs are written to `logs/`.

---

## Configuration

- `config/config.ini` — main configuration (URL, SSL options, credentials).
- `verify_ssl` — set to `False` only for local testing with self-signed certs.
- `ca_bundle` — path to PEM file to use for SSL verification.

Example `config.ini` snippet:

```ini
[DEFAULT]
environment = development
username = 
password = 
url = https://your-spa.example/db.aspx?
verify_ssl = True
ca_bundle =
```

---

## Building a Standalone Executable

This project uses PyInstaller for packaging. A spec file `SPA-Dashboard.spec`
is provided for faster rebuilds.

Build (PowerShell):

```powershell
uv add --dev pyinstaller
uv run pyinstaller --clean SPA-Dashboard.spec
```

The packaged executable will appear under `dist\` (or `build\` during the
process). When packaging, ensure any external resources referenced at runtime
(assets, templates, CA bundles) are included via `--add-data` or the spec file.

---

## Development notes

- Network client: the code uses `httpx` and `httpx-ntlm` and provides both
  synchronous and asynchronous APIs in `src/services/spa_service.py`.
- If NTLM/MD4 support is required on your platform, install a crypto library
  such as `pycryptodome`.

Async example (recommended for non-blocking UI):

```python
from httpx import AsyncClient
from src.services.spa_service import SPADataProcessor

async with AsyncClient() as client:
    processor = SPADataProcessor(url, config=config, session=client)
    result = await processor.process_async(session=client)
```

---

## Tests

Run unit tests with pytest:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

---

## Troubleshooting

- SSL errors: set `verify_ssl = False` temporarily or provide `ca_bundle`.
- Packaging issues: inspect `build/warn-SPA-Dashboard.txt` for missing
  imports and include the necessary modules/resources in the spec.

---

## License & Contact

This repository does not include an explicit license file. Contact the
maintainer for reuse permissions or contributions.

Maintainer: riyanardyanto

