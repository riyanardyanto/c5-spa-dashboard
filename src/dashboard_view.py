"""Dashboard layout container for the issue tracker application."""

from __future__ import annotations

from tkinter import messagebox
from typing import List, Optional
from urllib.parse import urlparse

import ttkbootstrap as ttk
import pandas as pd
from tabulate import tabulate

from src.components.header_frame import HeaderFrame
from src.components.issue_card import IssueCardFrame
from src.components.manual_window import ManualWindow
from src.components.report_toplevel import ReportView
from src.components.sidebar import Sidebar
from src.components.table_frame import TableFrame
from src.services.logging_service import log_exception
from src.services.record_service import append_cards_to_csv, build_record_rows
from src.services.spa_service import (
    DataLossesSummary,
    SPADataProcessor,
    MaxRetriesExceededError,
    get_url_period_loss_tree,
)
from src.utils.app_config import AppDataConfig
from src.utils.csvhandle import get_targets_file_path, save_user
from src.utils.csvhandle import load_users
from async_tkinter_loop import async_handler
import asyncio

MATERIAL_SECTION_PADDING = (16, 12, 16, 16)


class DashboardView(ttk.Frame):
    """Compose and expose the widgets used by the dashboard window."""

    def __init__(
        self,
        master: ttk.Window,
        palette: Optional[dict] = None,
        data_config: Optional[AppDataConfig] = None,
    ):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.palette = palette or {}
        self.data_config: Optional[AppDataConfig] = data_config
        self.configure(style="MaterialSurface.TFrame")

        self.sidebar = Sidebar(self, palette=self.palette)
        self.sidebar.pack(anchor="nw", side="left", fill="none", expand=False)

        # Set LU values from config
        if self.data_config and self.data_config.link_up:
            self.sidebar.lu.configure(values=list(self.data_config.link_up))
            # Set default to first value if available
            if self.data_config.link_up:
                self.sidebar.lu.set(self.data_config.link_up[0])

        self.sidebar.btn_get_data.configure(command=self.get_data)
        self.sidebar.btn_save.configure(command=self.save_data)
        self.sidebar.btn_target_editor.configure(command=self.show_target_editor)
        self.sidebar.btn_history.configure(command=self.show_history)
        self.sidebar.btn_report.configure(command=self.show_data)
        if hasattr(self.sidebar, "btn_manual"):
            self.sidebar.btn_manual.configure(command=self.show_manual)

        existing_users = load_users()
        if hasattr(self.sidebar.entry_user, "configure"):
            self.sidebar.entry_user.configure(completevalues=existing_users)

        self.main_view = ttk.Frame(self, style="MaterialSurface.TFrame")
        self.main_view.pack(anchor="nw", side="left", fill="both", expand=True)

        # Header with title, status, and progress indicator
        self.header_frame = HeaderFrame(self.main_view, palette=self.palette)
        self.header_frame.pack(
            pady=(10, 0), anchor="nw", side="top", fill="x", expand=True
        )

        # Main content split into issue table and cards area
        self.main_content = ttk.Frame(
            self.main_view,
            style="MaterialSurface.TFrame",
        )
        self.main_content.pack(anchor="nw", side="top", fill="both", expand=True)

        self.table_frame = TableFrame(self.main_content, palette=self.palette)
        self.table_frame.pack(side="left", fill="y", expand=False, pady=(10, 0))

        self.card_frame = IssueCardFrame(self.main_content, palette=self.palette)
        self.card_frame.pack(side="right", fill="both", expand=True, pady=(0, 0))

        self.table_frame.issue_table.view.bind(
            "<Double-1>", self._handle_issue_row_double_click, add="+"
        )

    @async_handler
    async def save_data(self) -> None:
        """Persist all issue cards to the shared CSV using record_service."""

        self.header_frame.start_progress()
        # Prevent duplicate saves by disabling the save button while operation is running
        if hasattr(self.sidebar, "btn_save"):
            try:
                self.sidebar.btn_save.configure(state="disabled")
            except Exception:
                pass
        try:
            username = (
                getattr(self.sidebar.entry_user, "get", lambda: "")() or ""
            ).strip()
            if not username:
                messagebox.showwarning(
                    "Informasi",
                    "Masukkan nama pengguna sebelum menyimpan data.",
                    parent=self,
                )
                self.sidebar.entry_user.focus_set()
                return

            cards_payload = [card.get_data() for card in self.card_frame.cards.values()]
            rows = build_record_rows(
                cards_payload,
                username=username,
                lu=self.sidebar.lu.get().strip(),
                tanggal=self.sidebar.dt.get_date().strftime("%Y-%m-%d"),
                shift=self.sidebar.select_shift.get().strip(),
            )

            if not rows:
                messagebox.showinfo(
                    "Informasi",
                    "Tidak ada data issue card yang dapat disimpan.",
                    parent=self,
                )
                return

            try:
                # Disk IO and pandas operations can be blocking; offload to a thread
                destination = await asyncio.to_thread(append_cards_to_csv, rows)
            except Exception as exc:  # noqa: BLE001 - surface error to user
                log_exception("Gagal menyimpan data issue card", exc)
                messagebox.showerror(
                    "Gagal",
                    f"Terjadi kesalahan saat menyimpan data: {exc}",
                    parent=self,
                )
                return

            # Save username - keep it in a thread to avoid blocking (lightweight)
            await asyncio.to_thread(save_user, username)
            messagebox.showinfo(
                "Sukses",
                f"Data issue card berhasil disimpan ke:\n{destination}",
                parent=self,
            )
        finally:
            self.header_frame.stop_progress()
            if hasattr(self.sidebar, "btn_save"):
                try:
                    self.sidebar.btn_save.configure(state="normal")
                except Exception:
                    pass

    @async_handler
    async def get_data(self) -> None:
        """Trigger data retrieval process."""
        self.header_frame.start_progress()
        try:
            lu_value = self.sidebar.lu.get().strip("LU")
            func_code = self.sidebar.func_location.get()[:4].strip()
            shift_label = self.sidebar.select_shift.get().strip()
            shift_number = shift_label.split()[-1] if shift_label else ""
            shift_column = shift_label if shift_label else ""
            date_value = self.sidebar.dt.get_date().strftime("%Y-%m-%d")

            url = self._get_url(
                lu_value,
                date_value,
                shift_number,
                func_code,
            )

            target_path = get_targets_file_path(lu_value, func_code)
            try:
                # pd.read_csv is blocking; run it in a thread to avoid freezing the UI
                targets_df = await asyncio.to_thread(pd.read_csv, target_path)
            except (FileNotFoundError, pd.errors.EmptyDataError, OSError):
                targets_df = pd.DataFrame()

            try:
                # SPADataProcessor.process performs network IO and heavy parsing
                # which are blocking; run it on a thread to keep the Tk event loop
                processor = SPADataProcessor(url=url, config=self.data_config)
                await processor.start()
                data_spa = await processor.get_data_spa()
            except MaxRetriesExceededError as exc:
                # Friendly warning for retry exhaustion
                log_exception("Gagal memproses data dari SPA (max retries)", exc)
                messagebox.showwarning(
                    "Gagal mengambil data",
                    f"Gagal mengambil data dari SPA setelah {exc.attempts} kali percobaan. "
                    "Periksa koneksi jaringan Anda atau coba lagi nanti.",
                    parent=self,
                )
                return
            except Exception as exc:  # noqa: BLE001 - propagate via UI and log
                log_exception("Gagal memproses data dari SPA", exc)
                messagebox.showerror(
                    "Gagal",
                    "Terjadi kesalahan saat mengambil data dari SPA. Periksa log untuk detail.",
                    parent=self,
                )
                return

            data_losses = data_spa.data_losses
            stops_reason = data_spa.stops_reason

            if isinstance(data_losses, DataLossesSummary):
                range_value = data_losses.RANGE
                if isinstance(range_value, str) and range_value.strip():
                    self.header_frame.set_time_period(f"Periode: {range_value.strip()}")
                else:
                    self.header_frame.set_time_period("")

            if not targets_df.empty and shift_column:
                target_col = (
                    shift_column if shift_column in targets_df.columns else None
                )
                if target_col:
                    target_lookup = dict(
                        zip(targets_df[targets_df.columns[0]], targets_df[target_col])
                    )
                    rows = self.table_frame.result_table.view.get_children()
                    for row_id in rows:
                        values = list(
                            self.table_frame.result_table.view.item(row_id, "values")
                        )
                        if not values:
                            continue
                        metric_key = values[0]
                        target_value = target_lookup.get(metric_key)
                        if target_value is not None:
                            values[1] = (
                                ""
                                if pd.isna(target_value)
                                else str(target_value).strip("%")
                            )
                            self.table_frame.result_table.view.item(
                                row_id, values=values
                            )

            if isinstance(data_losses, DataLossesSummary):
                metrics_order = ["STOP", "PR", "MTBF", "UPDT", "PDT", "NATR"]
                rows = self.table_frame.result_table.view.get_children()
                for row_id, metric in zip(rows, metrics_order):
                    actual_value = getattr(data_losses, metric, "")
                    values = list(
                        self.table_frame.result_table.view.item(row_id, "values")
                    )
                    if len(values) < 3:
                        continue
                    values[2] = "" if not actual_value else str(actual_value)
                    self.table_frame.result_table.view.item(row_id, values=values)

            if isinstance(stops_reason, list) and stops_reason:
                tree = self.table_frame.issue_table.view
                tree.delete(*tree.get_children())
                for detail in stops_reason:
                    line = detail.Line or ""
                    issue = detail.Detail or ""
                    stops = detail.Stops or ""
                    downtime = detail.Downtime or ""
                    tree.insert("", "end", values=(line, issue, stops, downtime))
        finally:
            self.header_frame.stop_progress()

    def show_data(self) -> None:
        lines: List[str] = []
        for _, card in enumerate(self.card_frame.cards.values(), start=1):
            card_data = card.get_data()
            if not card_data:
                continue

            issue_text = card_data.get("issue", "").strip() or "(Tanpa judul)"
            lines.append(f"*{issue_text}*")

            details = card_data.get("details") or []
            if not details:
                # lines.append("  • Tidak ada detail")
                lines.append("")
                continue

            for _, detail in enumerate(details, start=1):
                detail_text = detail.get("detail", "").strip() or "(Detail kosong)"
                lines.append(f"> {detail_text}")

                actions = detail.get("actions") or []
                if actions:
                    for _, action in enumerate(actions, start=1):
                        action_text = action.strip() or "(Tindakan kosong)"
                        lines.append(f"- {action_text}")
                else:
                    lines.append("")
            lines.append("")

        if not lines:
            messagebox.showinfo(
                "Informasi",
                "Belum ada data issue card yang dapat ditampilkan.",
                parent=self,
            )
            return

        lu = self.sidebar.lu.get().strip("LU")
        func_location = self.sidebar.func_location.get()
        select_shift = self.sidebar.select_shift.get().strip()
        select_date = self.sidebar.dt.get_date().strftime("%Y-%m-%d")

        header = f"*{func_location} {lu}* | {select_date}, {select_shift}"
        content = "\n".join(lines).strip()

        include_table = True
        if hasattr(self.sidebar, "include_table"):
            include_table = bool(self.sidebar.include_table.get())

        if include_table:
            table_headers = ["METRIK", "TARGET", "AKTUAL"]
            table_rows = [
                self.table_frame.result_table.view.item(row_id, "values")
                for row_id in self.table_frame.result_table.view.get_children()
            ]
            if table_rows:
                formatted_table = (
                    f"`{
                        tabulate(
                            table_rows,
                            headers=table_headers,
                            tablefmt='pretty',
                            showindex=False,
                            stralign='left',
                            numalign='left',
                        ).replace('\n', '`\n`')
                    }"
                    + "`"
                )
                content = f"{formatted_table}\n\n{content}"

        if hasattr(self, "report_view") and self.report_view.winfo_exists():
            report_window = self.report_view
        else:
            report_window = ReportView(self, palette=self.palette)
            self.report_view = report_window
            report_window.transient(self.winfo_toplevel())

        report_window.update_content(f"{header}\n{content}")
        report_window.lift()
        report_window.focus_force()

    def show_target_editor(self) -> None:
        """Open the target editor window."""
        from src.components.target_editor import TargetEditor

        lu = self.sidebar.lu.get().strip("LU")
        func_location = self.sidebar.func_location.get()[:4].strip().lower()

        target_path = get_targets_file_path(lu, func_location)
        target_window = TargetEditor(file_path=target_path)
        target_window.transient(self.winfo_toplevel())
        target_window.grab_set()
        target_window.focus_force()

    def show_history(self) -> None:
        """Open the history viewer window."""
        from src.components.history_window import HistoryWindow

        history_window = HistoryWindow(self.winfo_toplevel())
        history_window.transient(self.winfo_toplevel())
        history_window.grab_set()
        history_window.focus_force()

    def show_manual(self) -> None:
        """Display the operation manual window."""

        if (
            hasattr(self, "manual_window")
            and getattr(self, "manual_window").winfo_exists()
        ):
            self.manual_window.lift()
            self.manual_window.focus_force()
            return

        self.manual_window = ManualWindow(self.winfo_toplevel())
        self.manual_window.transient(self.winfo_toplevel())
        self.manual_window.grab_set()
        self.manual_window.focus_force()

    def _handle_issue_row_double_click(self, event) -> None:
        tree = self.table_frame.issue_table.view
        row_id = tree.identify_row(event.y)
        if not row_id:
            return

        values = tree.item(row_id, "values")
        if not values or len(values) < 2:
            return

        issue_text = str(values[1]).strip()
        if not issue_text:
            return

        empty_card_ids = [
            card.card_id
            for card in list(self.card_frame.cards.values())
            if card.get_data() is None
        ]
        for card_id in empty_card_ids:
            card = self.card_frame.cards.get(card_id)
            if card is not None:
                card.delete_card()

        self.card_frame.add_card(issue_text=issue_text)

    def _get_url(self, link_up, date_entry, shift, functional_location="PACK") -> str:
        """Helper method to generate URLs based on environment."""
        env_value = (
            self.data_config.environment
            if isinstance(self.data_config, AppDataConfig)
            else "development"
        ).lower()

        if env_value == "production":
            return get_url_period_loss_tree(
                link_up, date_entry, shift, functional_location
            )

        if env_value == "development":
            return f"http://127.0.0.1:5501/assets/response{shift}.html"

        if env_value == "test":
            candidate = ""
            if isinstance(self.data_config, AppDataConfig) and self.data_config.url:
                candidate = self.data_config.url.strip()

            if candidate:
                parsed = urlparse(candidate)
                if parsed.scheme and parsed.netloc:
                    return candidate

        return ""
