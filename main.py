import ttkbootstrap as ttk

from src.dashboard_view import DashboardView
from src.services.logging_service import (
    install_global_exception_handler,
    log_exception,
    log_warning,
)
from src.utils.app_config import read_config
from src.utils.material_theme import apply_material_theme
from src.utils.helpers import resource_path
from async_tkinter_loop import async_mainloop


def main() -> None:
    install_global_exception_handler()
    try:
        root = ttk.Window(
            title="C5 SPA Dashboard",
            themename="superhero",
            size=(1250, 650),
            minsize=(1250, 650),
        )
        try:
            root.iconbitmap(resource_path("assets/c5_spa.ico"))
        except Exception as icon_exc:  # noqa: BLE001 - non-fatal, log only
            log_warning("Gagal memuat ikon aplikasi", icon_exc)

        palette = apply_material_theme(root)
        data_config = read_config()
        dashboard = DashboardView(master=root, palette=palette, data_config=data_config)
        dashboard.pack(fill="both", expand=True)
        async_mainloop(root)
    except Exception as exc:  # noqa: BLE001 - fatal but logged
        log_exception("Unhandled error dalam siklus utama aplikasi", exc)
        raise


if __name__ == "__main__":
    main()
