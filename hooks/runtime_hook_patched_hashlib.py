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


# Controlled debug output: enable by setting environment variable
# PATCHED_HASHLIB_HOOK_DEBUG=1
DEBUG = os.environ.get("PATCHED_HASHLIB_HOOK_DEBUG", "0").lower() in (
    "1",
    "true",
    "yes",
    "y",
)

# Decide a safe log path inside the project when possible (safer for packaged apps)
# Preference order:
# 1. If a `logs` directory exists or can be created next to the executable (frozen)
#    or next to the project root (source), use that.
# 2. Otherwise fall back to the system temp directory.


def _determine_log_path(filename: str) -> str:
    # base_dir: when frozen, place next to the exe; otherwise use project root
    try:
        if getattr(sys, "frozen", False):
            base = os.path.dirname(sys.executable)
        else:
            # hook lives in <project>/hooks/, so parent of hooks is project root
            base = os.path.dirname(os.path.dirname(__file__))
    except Exception:
        base = None

    if base:
        logs_dir = os.path.join(base, "logs")
        try:
            os.makedirs(logs_dir, exist_ok=True)
            # try to create a test file to ensure writable
            test_path = os.path.join(logs_dir, ".write_test")
            with open(test_path, "w", encoding="utf-8") as tf:
                tf.write("")
            try:
                os.remove(test_path)
            except Exception:
                pass
            return os.path.join(logs_dir, filename)
        except Exception:
            # fall back to tempdir
            pass

    return os.path.join(tempfile.gettempdir(), filename)


tmp = _determine_log_path("patched_hook_run.txt")
if DEBUG:
    _safe_write(tmp, "--- runtime_hook_patched_hashlib run ---\n")
    _safe_write(tmp, f"time={time.strftime('%Y-%m-%d %H:%M:%S')} pid={os.getpid()}\n")
    _safe_write(tmp, f"python={sys.version.splitlines()[0]}\n")
    _safe_write(tmp, f"sys.path={sys.path}\n")

try:
    import utils.patched_hashlib  # noqa: F401

    if DEBUG:
        _safe_write(tmp, "patched_hashlib: import succeeded\n")
except Exception:
    if DEBUG:
        _safe_write(tmp, "patched_hashlib: import FAILED\n")
        _safe_write(tmp, traceback.format_exc() + "\n")

# Check that hashlib provides md4 now
try:
    import hashlib

    try:
        # algorithms_available may be a set or list; stringify safely
        algs = getattr(hashlib, "algorithms_available", None)
        if DEBUG:
            _safe_write(tmp, f"hashlib.algorithms_available={algs}\n")
    except Exception:
        if DEBUG:
            _safe_write(tmp, "hashlib.algorithms_available: read failed\n")

    try:
        d = hashlib.new("md4", b"abc").hexdigest()
        if DEBUG:
            _safe_write(tmp, f"md4_check=OK hexdigest={d}\n")
    except Exception:
        if DEBUG:
            _safe_write(tmp, "md4_check=FAILED\n")
            _safe_write(tmp, traceback.format_exc() + "\n")
except Exception:
    if DEBUG:
        _safe_write(tmp, "hashlib import failed\n")
        _safe_write(tmp, traceback.format_exc() + "\n")

if DEBUG:
    _safe_write(tmp, "--- end runtime_hook_patched_hashlib ---\n\n")
