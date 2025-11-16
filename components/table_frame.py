import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview


class TableFrame(ttk.Frame):
    def __init__(self, master: ttk.Frame, palette: dict):
        super().__init__(master, style="MaterialSurface.TFrame")
        self.palette = palette

        # Create Tableview container
        self.result_container = ttk.Frame(self, style="MaterialSurface.TFrame")
        self.result_container.pack(
            side="top", anchor="nw", fill="x", expand=True, padx=0, pady=0
        )

        # Create Tableview
        result_coldata = [
            {"text": "METRIK", "width": 150, "stretch": False},
            {"text": "TARGET", "width": 150, "stretch": True},
            {"text": "ACTUAL", "width": 150, "stretch": True},
        ]
        result_rowdata = [
            ["STOP", "0", "0"],
            ["PR", "0", "0"],
            ["MTBF", "0", "0"],
            ["UPDT", "0", "0"],
            ["PDT", "0", "0"],
            ["NATR", "0", "0"],
        ]

        self.result_table = Tableview(
            self.result_container,
            # bootstyle=INFO,
            height=6,
            coldata=result_coldata,
            rowdata=result_rowdata,
            searchable=False,
        )
        self.result_table.pack(
            side="left",
            anchor="nw",
            fill="x",
            expand=True,
            pady=(0, 10),
            padx=(0, 0),
        )

        # self.target_button = ttk.Button(
        #     self.result_container,
        #     text="Set Target",
        #     bootstyle="success",
        #     width=10,
        # )
        # self.target_button.pack(side="right", anchor="ne", pady=(0, 10), padx=(10, 0))

        issue_coldata = [
            {"text": "Line", "width": 150, "stretch": False},
            {"text": "Issue", "width": 280, "stretch": True, "anchor": "w"},
            {"text": "Stops", "width": 60, "stretch": False, "anchor": "center"},
            {"text": "Downtime", "width": 80, "stretch": False, "anchor": "center"},
        ]

        self.issue_table = Tableview(
            self,
            # bootstyle=INFO,
            coldata=issue_coldata,
            rowdata=[],
            autofit=False,
            searchable=False,
            height=50,
        )
        self.issue_table.pack(pady=(0, 10), padx=(0, 0), fill="y", expand=False)
