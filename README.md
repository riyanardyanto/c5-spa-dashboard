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
