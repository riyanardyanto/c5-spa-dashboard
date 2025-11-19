from typing import Optional

import ttkbootstrap as ttk
from PIL import Image, ImageTk, UnidentifiedImageError
from ttkbootstrap.constants import SUCCESS, W, X
from ttkbootstrap.tooltip import ToolTip
from ttkwidgets.autocomplete import AutocompleteCombobox

from utils.helpers import resource_path


class Sidebar(ttk.Frame):
    def __init__(self, master: ttk.Frame, palette: Optional[dict] = None):
        super().__init__(master, style="MaterialSurface.TFrame")
        self.home_frame = master
        self.palette = palette or {}
        self.select_shift = ttk.StringVar()
        self.include_table = ttk.BooleanVar(value=True)

        self.container = ttk.Frame(
            self, style="MaterialSurface.TFrame", padding=(8, 12)
        )
        self.container.pack(fill="both", expand=True)

        self._create_logo(self.container)
        self._create_query_widgets(self.container)
        self._create_toplevel_widgets(self.container)
        self._create_save_widgets(self.container)

        ttk.Frame(self.container, style="MaterialSurface.TFrame").pack(
            fill="both", expand=True
        )

    def _create_logo(self, parent: ttk.Frame) -> None:
        """Render logo and heading in the sidebar."""

        header = ttk.Frame(parent, style="MaterialSurface.TFrame")
        header.pack(fill=X, pady=(0, 10))

        try:
            self.photo = ImageTk.PhotoImage(
                image=Image.open(resource_path("assets/c5_spa.ico")).resize((80, 80))
            )
        except (FileNotFoundError, UnidentifiedImageError):
            self.photo = None

        if self.photo:
            ttk.Label(header, image=self.photo, anchor="center").pack(pady=(0, 8))

        ttk.Separator(parent, orient="horizontal", style="Horizontal.TSeparator").pack(
            fill=X, pady=(0, 0)
        )

    def _create_query_widgets(self, parent: ttk.Frame) -> None:
        """Create Material-styled controls for query parameters."""

        section = ttk.Frame(parent, style="MaterialCard.TFrame", padding=(12, 5, 12, 5))
        section.pack(fill=X, pady=(0, 8))
        section.columnconfigure(0, weight=1)

        self.lu = ttk.Combobox(
            section,
            bootstyle="success",
            width=14,
            cursor="hand2",
        )
        # Default value will be set from config in dashboard_view
        self.lu.pack(fill=X, pady=(8, 4))

        self.func_location = ttk.Combobox(
            section,
            bootstyle="success",
            width=14,
            cursor="hand2",
            values=["PACKER", "MAKER"],
        )
        self.func_location.set("PACKER")
        self.func_location.pack(fill=X, pady=(0, 6))

        self.dt = ttk.DateEntry(
            section,
            bootstyle=SUCCESS,
            width=11,
            dateformat=r"%Y-%m-%d",
            cursor="hand2",
        )
        self.dt.pack(fill=X, pady=(0, 8))

        radio_frame = ttk.Frame(section, style="MaterialCardBody.TFrame")
        radio_frame.pack(fill=X, pady=(0, 8))
        shifts = ["Shift 1", "Shift 2", "Shift 3"]
        for shift in shifts:
            ttk.Radiobutton(
                radio_frame,
                bootstyle=SUCCESS,
                variable=self.select_shift,
                text=shift,
                value=shift,
                cursor="hand2",
            ).pack(anchor=W, pady=1)
        self.select_shift.set("Shift 1")

        self.btn_get_data = self._create_button(
            section, "Get Data", "success", "Get data stop reason from SPA"
        )
        self.btn_get_data.pack(fill=X, pady=(2, 0))

        ttk.Separator(parent, orient="horizontal", style="Horizontal.TSeparator").pack(
            fill=X, pady=(0, 0)
        )

    def _create_save_widgets(self, parent: ttk.Frame) -> None:
        """Create the user selector and save action within a Material card."""

        section = ttk.Frame(parent, style="MaterialCard.TFrame", padding=(12, 5, 12, 5))
        section.pack(fill=X, pady=(0, 8))
        section.columnconfigure(0, weight=1)

        self.entry_user = AutocompleteCombobox(section, width=12, cursor="hand2")
        self.entry_user.pack(fill=X, pady=(8, 6))
        ToolTip(self.entry_user, "Select Username", delay=0)

        self.btn_save = self._create_button(
            section, "Save Data", "primary", "Save to Excel"
        )
        self.btn_save.pack(fill=X)

        ttk.Separator(parent, orient="horizontal", style="Horizontal.TSeparator").pack(
            fill=X, pady=(0, 0)
        )

    def _create_toplevel_widgets(self, parent: ttk.Frame) -> None:
        """Create shortcuts to auxiliary windows and toggles."""

        section = ttk.Frame(parent, style="MaterialCard.TFrame", padding=(12, 5, 12, 5))
        section.pack(fill=X, pady=(0, 8))
        section.columnconfigure(0, weight=1)

        self.btn_report = self._create_button(
            section, "View Report", "warning", "Open Report Window"
        )
        self.btn_report.pack(fill=X, pady=(8, 2))

        style = ttk.Style()
        style.configure(
            "success.TButton", foreground=self.palette.get("on_primary", "#FFFFFF")
        )

        toggle_container = ttk.Frame(section, style="MaterialCardBody.TFrame")
        toggle_container.pack(fill=X, pady=(0, 20))

        self.check_table = ttk.Checkbutton(
            toggle_container,
            text="Include Table",
            bootstyle="round-toggle",
            variable=self.include_table,
        )
        toggle_style = self.check_table.cget("style")
        if toggle_style:
            style.configure(
                toggle_style,
                font=("Segoe UI", 8, "italic"),
                foreground=self.palette.get("on_surface_variant", "#8A97AA"),
            )
        self.check_table.pack(fill=X, pady=(2, 0))

        self.btn_target_editor = self._create_button(
            section, "Edit Targets", "info", "Open Target Editor"
        )
        self.btn_target_editor.pack(fill=X, pady=2)

        self.btn_history = self._create_button(
            section, "History", "info", "Open History Window"
        )
        self.btn_history.pack(fill=X, pady=(8, 2))

        self.btn_manual = self._create_button(
            section, "Manual", "info", "Lihat panduan penggunaan"
        )
        self.btn_manual.pack(fill=X, pady=(8, 2))

        ttk.Separator(parent, orient="horizontal", style="Horizontal.TSeparator").pack(
            fill=X, pady=(0, 0)
        )

    def _create_button(
        self, parent: ttk.Frame, text: str, style, tooltip_text: str
    ) -> ttk.Button:
        """Helper method to create a Material-friendly button with tooltip."""

        button = ttk.Button(
            master=parent,
            text=text,
            bootstyle=style,
            cursor="hand2",
        )
        btn_style = button.cget("style")
        if btn_style:
            ttk_style = ttk.Style()
            text_color = self.palette.get("on_primary", "#FFFFFF")
            disabled_color = self.palette.get("on_surface_variant", "#8A97AA")
            ttk_style.configure(btn_style, foreground=text_color)
            ttk_style.map(
                btn_style,
                foreground=[
                    ("disabled", disabled_color),
                    ("pressed", text_color),
                    ("active", text_color),
                    ("", text_color),
                ],
            )
        ToolTip(button, tooltip_text, delay=0)
        return button
