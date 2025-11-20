import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame


class ManualWindow(ttk.Toplevel):
    """Display a read-only manual explaining the dashboard usage."""

    def __init__(self, master: ttk.Window):
        super().__init__(master)
        self.title("Operation Manual")
        self.geometry("900x620")
        self.minsize(720, 480)
        self.configure(background="#101418")

        container = ttk.Frame(
            self, padding=(18, 18, 18, 18), style="MaterialSurface.TFrame"
        )
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container, style="MaterialSurface.TFrame")
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(
            header,
            text="Panduan Penggunaan Dashboard",
            style="MaterialTitle.TLabel",
        ).pack(side="left")

        content_frame = ScrolledFrame(
            container,
            autohide=True,
            padding=(0, 0, 12, 0),
            bootstyle="round",
            style="MaterialCardBody.TFrame",
        )
        content_frame.pack(fill="both", expand=True)

        body = ttk.Frame(
            content_frame, style="MaterialCardBody.TFrame", padding=(8, 12, 8, 24)
        )
        body.pack(fill="both", expand=True)

        sections = [
            (
                "Memulai Aplikasi",
                [
                    "Jalankan `uv sync` jika belum memasang dependensi, kemudian jalankan `uv run main.py`.",
                    "Semua error tersimpan di `logs/app_errors.log` untuk pengecekan lanjutan.",
                ],
            ),
            (
                "Panel Sidebar",
                [
                    "`User` : masukkan nama operator. Diperlukan sebelum menyimpan data dan mendukung autocomplete dari riwayat.",
                    "`Tanggal` : pilih tanggal referensi data SPA dengan DateEntry.",
                    "`Shift` : pilih shift kerja (1/2/3) menggunakan radio button.",
                    "`LU` : pilih line (misalnya LU18) yang akan diproses.",
                    "`Functional Location` : pilih PACKER/MAKER untuk menyesuaikan target.",
                    "Tombol `Get Data` : mengambil data SPA, progress bar di header akan menyala selama proses.",
                    "Tombol `Save Data` : menyimpan issue card ke database CSV, sekaligus menyimpan nama pengguna.",
                    "`Include Table` toggle : tentukan apakah tabel metrik akan muncul di report.",
                    "Tombol `View Report` : menampilkan jendela ringkasan issue card dan tabel (jika dipilih).",
                    "Tombol `Edit Targets` : membuka editor target per shift untuk LU/Functional Location terpilih.",
                    "Tombol `History` : membuka histori penyimpanan issue card dalam tabel terurut.",
                ],
            ),
            (
                "Tabel Metrik",
                [
                    "Kiri menampilkan target dan aktual metrik SPA (STOP, PR, dll).",
                    "Klik `Get Data` akan mengisi nilai berdasarkan data SPA dan target CSV.",
                    "Nilai target dapat diedit lewat tombol `Edit Targets`.",
                ],
            ),
            (
                "Issue Cards",
                [
                    "Area kanan berisi daftar issue card. Satu kartu merepresentasikan satu masalah.",
                    "Gunakan tombol `Tambah Detail` (ikon info) untuk menambah detail pada kartu.",
                    "Dalam setiap detail, tombol `Tambah Tindakan` (ikon centang) menambah daftar aksi.",
                    "Klik kanan pada detail atau tindakan untuk menghapus entri tersebut.",
                    "Klik kanan pada kartu untuk menghapus kartu secara keseluruhan.",
                    "Klik ganda baris SPA Issue di tabel kiri akan membuat kartu baru dengan judul otomatis.",
                ],
            ),
            (
                "Menyimpan dan Riwayat",
                [
                    "Pastikan kolom `User` terisi sebelum menekan `Save Data`.",
                    "Jika tidak ada data, aplikasi akan memberi tahu dan menyarankan peninjauan.",
                    "Riwayat penyimpanan dapat dilihat melalui tombol `History`, data ditampilkan terbaru di atas.",
                    "Tombol `Refresh` di History memuat ulang data CSV tanpa menutup jendela.",
                ],
            ),
            (
                "Laporan",
                [
                    "Tombol `View Report` menyusun ringkasan teks dari kartu dan, bila diaktifkan, tabel metrik.",
                    "Isi laporan dapat langsung disalin atau digunakan untuk dokumentasi harian.",
                ],
            ),
        ]

        for title, items in sections:
            section_frame = ttk.Frame(body, style="MaterialCardBody.TFrame")
            section_frame.pack(fill="x", pady=(0, 16))
            ttk.Label(
                section_frame,
                text=title,
                style="MaterialSubtitle.TLabel",
            ).pack(anchor="w", pady=(0, 6))

            for item in items:
                ttk.Label(
                    section_frame,
                    text=f"• {item}",
                    style="MaterialBody.TLabel",
                    wraplength=780,
                    justify="left",
                ).pack(anchor="w", pady=(1, 1))

        ttk.Button(
            container,
            text="Tutup",
            bootstyle="danger-outline",
            command=self.destroy,
        ).pack(anchor="e", pady=(12, 0))
