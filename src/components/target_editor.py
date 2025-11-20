from __future__ import annotations

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, EW, NSEW, X
from ttkbootstrap.tooltip import ToolTip

from .editble_tableview import EditableTableView
from src.utils.csvhandle import load_targets_df


class TargetEditor(ttk.Toplevel):
    def __init__(self, file_path: str):
        super().__init__()
        self.title("Target Editor")
        # self.geometry("600x380")
        self.resizable(False, False)

        palette = getattr(self.master, "palette", {}) if self.master else {}
        background = palette.get("background", "#101418")
        self.configure(background=background)

        container = ttk.Frame(self, style="MaterialSurface.TFrame", padding=20)
        container.pack(fill=BOTH, expand=True)

        header = ttk.Frame(container, style="MaterialSurface.TFrame")
        header.pack(fill=X, pady=(0, 12))

        ttk.Label(
            header,
            text="Pengaturan Target",
            style="MaterialTitle.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Perbarui nilai target downtime untuk setiap metrik.",
            style="MaterialSubtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Separator(
            container, orient="horizontal", style="Horizontal.TSeparator"
        ).pack(fill=X, pady=(0, 12))

        content = ttk.Frame(container, style="MaterialSurface.TFrame")
        content.pack(fill=BOTH, expand=True)
        content.columnconfigure(0, weight=1)

        table_card = ttk.Frame(
            content,
            style="MaterialCard.TFrame",
            padding=(16, 12, 16, 16),
        )
        table_card.grid(row=0, column=0, sticky=NSEW)
        table_card.columnconfigure(0, weight=1)

        target_df = load_targets_df(file_path)
        columns = target_df.columns.to_list()
        columns = [{"text": col, "anchor": "w", "width": "100"} for col in columns]
        data = target_df.values.tolist()

        table_container = ttk.Frame(
            table_card,
            style="MaterialCardBody.TFrame",
        )
        table_container.grid(row=1, column=0, sticky=NSEW)
        table_container.columnconfigure(0, weight=1)

        table = EditableTableView(
            table_container,
            coldata=columns,
            rowdata=data,
            height=6,
            editable_columns=list(range(1, len(columns))),
        )
        table.pack(fill=BOTH, expand=True)

        table.load_from_csv(file_path)

        actions = ttk.Frame(table_card, style="MaterialCardBody.TFrame")
        actions.grid(row=2, column=0, sticky=EW, pady=(12, 0))

        save_btn = ttk.Button(
            actions,
            text="Simpan",
            bootstyle="success",
            width=12,
            command=lambda: table.save_to_csv(file_path),
        )
        save_btn.pack(side="right")
        ToolTip(save_btn, "Simpan perubahan target")

        cancel_btn = ttk.Button(
            actions,
            text="Batal",
            bootstyle="secondary",
            width=10,
            command=self.destroy,
        )
        cancel_btn.pack(side="right", padx=(0, 8))
        ToolTip(cancel_btn, "Tutup tanpa menyimpan")
