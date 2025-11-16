from pathlib import Path

import pandas as pd

from services.logging_service import log_warning
from .helpers import get_script_folder

columns = ["Metrics", "Shift 1", "Shift 2", "Shift 3"]
data = [
    ("STOP", "3", "3", "3"),
    ("PR", "65.0%", "69.2%", "77.5%"),
    ("MTBF", "150.0", "150.0", "150.0"),
    ("UPDT", "4.1%", "4.1%", "4.1%"),
    ("PDT", "10.0%", "10.0%", "10.0%"),
    ("NATR", "4.0%", "4.0%", "4.0%"),
]


def get_targets_file_path(lu, func_location: str = None):
    script_folder = Path(get_script_folder())
    target_folder = script_folder / "target"
    target_folder.mkdir(parents=True, exist_ok=True)

    filename = target_folder / f"target_{func_location.lower()}_{lu}.csv"
    if not filename.exists():
        df = pd.DataFrame(data, columns=columns)
        df.to_csv(filename, index=False)

    return str(filename)


def load_targets_df(filename=None):
    """Memuat pengaturan dari file CSV"""

    return pd.read_csv(filename)


def get_database_file_path() -> str:
    script_folder = Path(get_script_folder())
    data_folder = script_folder / "data"
    data_folder.mkdir(parents=True, exist_ok=True)

    filename = data_folder / "database.csv"
    if not filename.exists():
        pd.DataFrame(
            columns=[
                "card_id",
                "lu",
                "tanggal",
                "shift",
                "issue",
                "detail",
                "action",
                "user",
                "saved_at",
            ]
        ).to_csv(filename, index=False)

    return str(filename)


def get_users_file_path() -> str:
    """Get or create the users CSV file path."""
    script_folder = Path(get_script_folder())
    data_folder = script_folder / "data"
    data_folder.mkdir(parents=True, exist_ok=True)

    filename = data_folder / "users.csv"
    if not filename.exists():
        pd.DataFrame(columns=["username"]).to_csv(filename, index=False)

    return str(filename)


def load_users() -> list[str]:
    """Load unique usernames from the users CSV file."""
    try:
        df = pd.read_csv(get_users_file_path())
        return sorted(df["username"].dropna().unique().tolist())
    except Exception as exc:  # noqa: BLE001 - fallback ke daftar kosong
        log_warning("Gagal memuat daftar pengguna dari CSV", exc)
        return []


def save_user(username: str) -> None:
    """Append a new username to the users CSV if it doesn't exist."""
    if not username or not username.strip():
        return

    username = username.strip()
    filepath = get_users_file_path()

    try:
        df = pd.read_csv(filepath)
        if username not in df["username"].values:
            new_row = pd.DataFrame([{"username": username}])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(filepath, index=False)
    except Exception as exc:  # noqa: BLE001 - lanjutkan tanpa menghentikan aplikasi
        log_warning("Gagal menyimpan nama pengguna ke CSV", exc)
