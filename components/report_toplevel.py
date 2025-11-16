import tkinter as tk
from typing import Optional

import qrcode
import ttkbootstrap as ttk
import ttkbootstrap.constants as ttc
from PIL import ImageTk


class ReportView(ttk.Toplevel):
    def __init__(self, master: tk.Widget, palette: dict):
        super().__init__(master)
        self.palette = palette
        self.title("Report Window")
        self.geometry("1000x600")
        self._qr_image: Optional[ImageTk.PhotoImage] = None

        self.configure(background=self.palette.get("background", "#101418"))

        container = ttk.Frame(self, style="MaterialSurface.TFrame", padding=12)
        container.pack(fill=ttc.BOTH, expand=True)

        header = ttk.Frame(container, style="MaterialSurface.TFrame")
        header.pack(fill=ttc.X, pady=(0, 8))

        ttk.Label(
            header,
            text="Laporan Issue Card",
            style="MaterialTitle.TLabel",
        ).pack(anchor=ttc.W)
        ttk.Label(
            header,
            text="Ringkasan setiap issue, detail, dan tindakan dalam format teks & QR.",
            style="MaterialSubtitle.TLabel",
        ).pack(anchor=ttc.W, pady=(4, 0))

        ttk.Separator(
            container, orient=ttc.HORIZONTAL, style="Horizontal.TSeparator"
        ).pack(fill=ttc.X, pady=(0, 8))

        body = ttk.Frame(container, style="MaterialSurface.TFrame")
        body.pack(fill=ttc.BOTH, expand=True)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=3)

        text_panel = ttk.Frame(body, style="MaterialSubsection.TFrame", padding=8)
        text_panel.grid(row=0, column=0, sticky=ttc.NSEW, padx=(0, 6))
        text_panel.columnconfigure(0, weight=1)

        ttk.Label(
            text_panel,
            text="Ringkasan Teks",
            style="MaterialChip.TLabel",
        ).pack(anchor=ttc.W, pady=(0, 6))

        text_container = ttk.Frame(text_panel, style="MaterialSubsection.TFrame")
        text_container.pack(fill=ttc.BOTH, expand=True)
        text_container.columnconfigure(0, weight=1)
        text_container.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(text_container, orient=ttc.VERTICAL)
        scrollbar.grid(row=0, column=1, sticky=ttc.NS)

        self.text_report = tk.Text(
            text_container,
            wrap=tk.WORD,
            state="disabled",
            relief=tk.FLAT,
            width=58,
            background=self.palette.get("surface", "#1C1F26"),
            foreground=self.palette.get("on_surface", "#FFFFFF"),
            insertbackground=self.palette.get("primary", "#4C9BFF"),
            highlightthickness=0,
            font=("Consolas", 9, "normal"),
        )
        self.text_report.grid(row=0, column=0, sticky=ttc.NSEW)
        self.text_report.configure(padx=4, pady=4)
        scrollbar.configure(command=self.text_report.yview)
        self.text_report.configure(yscrollcommand=scrollbar.set)

        qr_panel = ttk.Frame(body, style="MaterialSubsection.TFrame", padding=8)
        qr_panel.grid(row=0, column=1, sticky=ttc.NSEW, padx=(6, 0))
        qr_panel.columnconfigure(0, weight=1)
        qr_panel.rowconfigure(1, weight=1)

        ttk.Label(
            qr_panel,
            text="QR Code",
            style="MaterialChip.TLabel",
        ).grid(row=0, column=0, sticky=ttc.W)

        self.qr_label = ttk.Label(
            qr_panel,
            style="MaterialBody.TLabel",
            text="QR belum tersedia",
            anchor=ttc.CENTER,
            padding=12,
        )
        self.qr_label.grid(row=1, column=0, sticky=ttc.NSEW, pady=(6, 0))

    def update_content(self, text: str) -> None:
        """Refresh report text and generate a QR code from the given content."""

        sanitized = text.strip()
        if not sanitized:
            sanitized = "Belum ada data issue card"

        self.text_report.configure(state="normal")
        self.text_report.delete("1.0", tk.END)
        self.text_report.insert("1.0", sanitized)
        self.text_report.configure(state="disabled")

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=6,
            border=2,
        )
        qr.add_data(sanitized)
        qr.make(fit=True)
        primary_color = self.palette.get("primary", "#4C9BFF")
        qr_img = qr.make_image(fill_color=primary_color, back_color="white")
        qr_img = qr_img.resize((420, 420))
        qr_img_tk = ImageTk.PhotoImage(qr_img)

        self.qr_label.configure(image=qr_img_tk, text="")
        self.qr_label.image = qr_img_tk
        self._qr_image = qr_img_tk
