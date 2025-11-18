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
uv run pyinstaller --onefile --name "SPA-Dashboard" --windowed --icon "assets/c5_spa.ico" --add-data "assets;assets" --add-data "components;components" --add-data "services;services" --add-data "utils;utils" --add-data "hooks;hooks" --add-data "dashboard_view.py;." main.py
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

## MD4 fallback (ntlm / SPA auth compatibility)

Starting from this commit the application includes a safe runtime fallback
for the MD4 hash algorithm used by some NTLM libraries. This solves the
ValueError "unsupported hash type md4" that can occur on Python builds
where OpenSSL does not expose MD4.

What changed

`main.py`. It ensures `hashlib.new('md4', ...)` and `hashlib.md4(...)`
are available at runtime. If the system has `pycryptodome` installed,
that implementation is preferred; otherwise a compact pure-Python MD4
implementation is used as a fallback.

Why this helps

call `hashlib.new('md4', ...)`. If your Python/OpenSSL does not support
MD4, those calls raise a ValueError and the app fails when fetching
SPA data. The fallback restores compatibility without requiring a
system-level OpenSSL rebuild.

Optional: prefer a compiled implementation

MD4 implementation and better performance. On Windows `pycryptodomex`
may attempt to build C extensions and require the Microsoft C++ Build
Tools (Visual C++ 14.0+). If you want the compiled implementation,
either install a wheel or install the build tools:

```powershell
# Install the pure-Python-friendly package (wheels available)
.\.venv\Scripts\Activate.ps1
python -m pip install pycryptodome

# Or, to build pycryptodomex from source on Windows you'll need the
# Visual C++ Build Tools. Download and install them from:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

Testing the MD4 support

Run the tests in the project's venv:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

If you prefer not to install compiled crypto libraries, the fallback
remains in place and the application will continue to function correctly
— at lower performance for MD4-heavy workloads.

PyInstaller runtime hook (included)

- This repository includes a PyInstaller runtime hook at `hooks/runtime_hook_patched_hashlib.py`.
  The hook ensures the patched MD4 implementation is loaded early in frozen
  builds so that extensions or libraries which call `hashlib.new('md4', ...)`
  succeed at runtime.

- Usage:

  - When building with PyInstaller from the command line, pass the hook with
    the `--runtime-hook` option. Example:

  uv run pyinstaller --onefile --name "SPA-Dashboard" --windowed --icon "assets/c5_spa.ico" --add-data "assets;assets" --add-data "components;components" --add-data "services;services" --add-data "utils;utils" --add-data "hooks;hooks" --add-data "dashboard_view.py;." --runtime-hook hooks/runtime_hook_patched_hashlib.py main.py

  - If you prefer using a spec file, add the hook path to the `Analysis` as
    `runtime_hooks`: e.g.

    Analysis(
    [...],
    runtime_hooks=['hooks/runtime_hook_patched_hashlib.py'],
    [...]
    )

  Why this helps:

  - In a frozen application imports and module initialization happen in a
    different order and earlier than when running from source. The runtime
    hook forces the patched MD4 shim to be loaded before other modules that
    might request MD4, avoiding `ValueError: unsupported hash type md4` in
    the frozen executable.

  - The hook is low-risk: it only ensures the same fallback behavior that's
    used when running from source via `utils/patched_hashlib.py`.

Hook debug & log location

- The runtime hook supports optional diagnostic logging controlled by the
  environment variable `PATCHED_HASHLIB_HOOK_DEBUG`. When set to a truthy
  value (`1`, `true`, `yes`, `y`) the hook emits a small diagnostic file
  named `patched_hook_run.txt`.

- Where the file is written:

  - When running from source the hook will try to create and write to
    `logs/patched_hook_run.txt` in the project root.
  - When running a frozen executable the hook will try to write to
    `logs/patched_hook_run.txt` next to the executable.
  - If those locations are not writable the hook falls back to the system
    temporary directory.

- Example (PowerShell): enable debug and build/run so the hook writes logs:

```powershell
$env:PATCHED_HASHLIB_HOOK_DEBUG='1'; uv run pyinstaller --onefile --name "SPA-Dashboard" --windowed --icon "assets/c5_spa.ico" --add-data "assets;assets" --add-data "components;components" --add-data "services;services" --add-data "utils;utils" --add-data "hooks;hooks" --add-data "dashboard_view.py;." --runtime-hook hooks/runtime_hook_patched_hashlib.py main.py
```

After running, inspect `logs/patched_hook_run.txt` next to the project or
executable; if it's not present check the system temp directory.
