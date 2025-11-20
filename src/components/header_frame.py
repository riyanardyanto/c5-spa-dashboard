import ttkbootstrap as ttk
import ttkbootstrap.constants as ttc


class HeaderFrame(ttk.Frame):
    def __init__(self, master: ttk.Frame, palette: dict):
        super().__init__(master, style="MaterialSurface.TFrame")
        self.palette = palette

        # Create title container
        self.title_container = ttk.Frame(self, style="MaterialSurface.TFrame")
        self.title_container.pack(side=ttc.LEFT, fill=ttc.Y, expand=False)

        # Create header label
        ttk.Label(
            self.title_container,
            text="Issue Tracker Dashboard",
            style="MaterialTitle.TLabel",
        ).pack(side=ttc.TOP, padx=0, pady=0, anchor=ttc.W)
        # Create subtitle label
        ttk.Label(
            self.title_container,
            text="Pantau downtime dan rencana perbaikan secara real-time",
            style="MaterialSubtitle.TLabel",
        ).pack(side=ttc.TOP, padx=0, pady=(0, 0), anchor=ttc.W)

        # Create status container
        self.status_container = ttk.Frame(self, style="MaterialSurface.TFrame")
        self.status_container.pack(
            side=ttc.RIGHT, fill=ttc.Y, expand=True, padx=(10, 10)
        )

        self.time_period = ttk.Label(
            self.status_container,
            text="",
            justify="right",
            anchor="e",
            style="MaterialSubtitle.TLabel",
        )
        self.time_period.pack(pady=(5, 0), fill="x", side=ttc.TOP, anchor=ttc.E)

        self.progressbar = ttk.Progressbar(
            self.status_container,
            mode="indeterminate",
            style="success.Striped.Horizontal.TProgressbar",
            length=1000,
        )
        self.progressbar.pack(fill="x", pady=(5, 0), anchor=ttc.E)

    def set_time_period(self, text: str) -> None:
        """Set the time period label text."""
        self.time_period.config(text=text)

    def start_progress(self) -> None:
        """Start the progress bar animation."""
        self.progressbar.start(10)  # Adjust speed as needed

    def stop_progress(self) -> None:
        """Stop the progress bar animation."""
        self.progressbar.stop()
