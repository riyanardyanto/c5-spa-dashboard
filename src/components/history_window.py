import pandas as pd
import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview

from src.utils.csvhandle import get_database_file_path


class HistoryWindow(ttk.Toplevel):
    def __init__(self, master: ttk.Window):
        super().__init__(master)
        self.title("Issue Cards History")
        self.geometry("1200x650")
        self.minsize(800, 400)
        self.configure(background="#101418")

        container = ttk.Frame(
            self, padding=(16, 18, 16, 16), style="MaterialSurface.TFrame"
        )
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container, style="MaterialSurface.TFrame")
        header.pack(fill="x", pady=(0, 12))

        ttk.Label(
            header,
            text="Issue Cards History",
            style="MaterialTitle.TLabel",
        ).pack(side="left")

        self.btn_refresh = ttk.Button(
            header,
            text="Refresh",
            bootstyle="info-outline",
            command=self.load_data,
        )
        self.btn_refresh.pack(side="right")

        table_card = ttk.Frame(
            container, style="MaterialCard.TFrame", padding=(16, 14, 16, 18)
        )
        table_card.pack(fill="both", expand=True)
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(1, weight=1)

        ttk.Label(
            table_card, text="Riwayat Tersimpan", style="MaterialChip.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        self._table_container = ttk.Frame(table_card, style="MaterialCardBody.TFrame")
        self._table_container.grid(row=1, column=0, sticky="nsew")

        self.empty_state = ttk.Label(
            self._table_container,
            text="Belum ada riwayat tersimpan.",
            style="MaterialMuted.TLabel",
            anchor="center",
            padding=(12, 40),
            justify="center",
        )

        self.table: Tableview | None = None
        self.df = self._load_csv_data()
        self._render_table()

    def _load_csv_data(self) -> pd.DataFrame:
        """Load data from CSV file."""
        try:
            csv_path = get_database_file_path()
            header_df = pd.read_csv(csv_path, nrows=0)
            available_columns = list(header_df.columns)

            desired_order = [
                "tanggal",
                "shift",
                "lu",
                "issue",
                "detail",
                "action",
                "user",
                # "saved_at",
            ]
            usecols = [col for col in desired_order if col in available_columns]

            dtype_map = {column: "string" for column in (usecols or available_columns)}

            df = pd.read_csv(
                csv_path,
                usecols=usecols or None,
                dtype=dtype_map,
                na_filter=False,
                memory_map=True,
            )
            if usecols:
                df = df.reindex(columns=usecols)

            sort_candidates = []
            if "tanggal" in df.columns:
                sort_candidates.append("tanggal")
            if "shift" in df.columns:
                sort_candidates.append("shift")

            if sort_candidates:
                df = df.sort_values(by=sort_candidates, ascending=False).reset_index(
                    drop=True
                )

            return df
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return pd.DataFrame()

    def _prepare_table_data(self, df: pd.DataFrame) -> tuple[list, list]:
        """Convert DataFrame to Tableview format."""
        if df.empty:
            return [], []

        # Column headers
        coldata = df.columns.tolist()

        # Row data as list of tuples
        rowdata = list(df.itertuples(index=False, name=None))

        return coldata, rowdata

    def load_data(self):
        """Reload data from CSV file and refresh table."""
        self.df = self._load_csv_data()
        self._render_table()

    def _render_table(self) -> None:
        if self.table is not None:
            self.table.destroy()
            self.table = None

        if self.empty_state.winfo_ismapped():
            self.empty_state.pack_forget()

        if self.df.empty:
            self.empty_state.pack(fill="both", expand=True)
            return

        coldata, rowdata = self._prepare_table_data(self.df)
        self.table = Tableview(
            self._table_container,
            coldata=coldata,
            rowdata=rowdata,
            searchable=True,
            bootstyle="info",
            height=28,
            autofit=True,
            # paginated=True,
            # pagesize=30,
            yscrollbar=True,
        )
        for column in ("issue", "detail", "action"):
            if column in coldata:
                col_index = coldata.index(column)
                self.table.view.column(col_index, stretch=True)
        if "user" in coldata:
            user_index = coldata.index("user")
            self.table.view.column(user_index, width=200, minwidth=140, stretch=False)
        self.table.pack(fill="both", expand=True)
