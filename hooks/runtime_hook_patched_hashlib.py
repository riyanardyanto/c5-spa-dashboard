"""Runtime hook for PyInstaller.

This file is executed very early by PyInstaller when the frozen app starts.
Importing `utils.patched_hashlib` here guarantees the MD4 monkeypatch is
applied before any other module (such as ntlm_auth) attempts to call
`hashlib.new('md4')`.

Place this file on the spec's `runtime_hooks` list (done below) so the
hook runs in the bundled exe.
"""

import os
import sys
import time
import tempfile
import traceback


def _safe_write(path: str, text: str) -> None:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        # best-effort only; don't crash the hook
        pass


# Temp file for runtime debug
tmp = os.path.join(tempfile.gettempdir(), "patched_hook_run.txt")
_safe_write(tmp, "--- runtime_hook_patched_hashlib run ---\n")
_safe_write(tmp, f"time={time.strftime('%Y-%m-%d %H:%M:%S')} pid={os.getpid()}\n")
_safe_write(tmp, f"python={sys.version.splitlines()[0]}\n")
_safe_write(tmp, f"sys.path={sys.path}\n")

try:
    import utils.patched_hashlib  # noqa: F401

    _safe_write(tmp, "patched_hashlib: import succeeded\n")
except Exception:
    _safe_write(tmp, "patched_hashlib: import FAILED\n")
    _safe_write(tmp, traceback.format_exc() + "\n")

# Check that hashlib provides md4 now
try:
    import hashlib

    try:
        # algorithms_available may be a set or list; stringify safely
        algs = getattr(hashlib, "algorithms_available", None)
        _safe_write(tmp, f"hashlib.algorithms_available={algs}\n")
    except Exception:
        _safe_write(tmp, "hashlib.algorithms_available: read failed\n")

    try:
        d = hashlib.new("md4", b"abc").hexdigest()
        _safe_write(tmp, f"md4_check=OK hexdigest={d}\n")
    except Exception:
        _safe_write(tmp, "md4_check=FAILED\n")
        _safe_write(tmp, traceback.format_exc() + "\n")
except Exception:
    _safe_write(tmp, "hashlib import failed\n")
    _safe_write(tmp, traceback.format_exc() + "\n")

_safe_write(tmp, "--- end runtime_hook_patched_hashlib ---\n\n")
