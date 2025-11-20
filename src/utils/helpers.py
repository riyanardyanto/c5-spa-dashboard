import sys
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, compatible with PyInstaller.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource.
    """
    base_path = getattr(sys, "_MEIPASS", str(Path(".").resolve()))
    return str(Path(base_path) / relative_path)


def get_script_folder() -> str:
    """
    Get the absolute path to the script folder, compatible with PyInstaller.

    Returns:
        str: The absolute path to the script folder.
    """
    if getattr(sys, "frozen", False):
        return str(Path(sys.executable).parent)
    return str(Path(sys.modules["__main__"].__file__).resolve().parent)
