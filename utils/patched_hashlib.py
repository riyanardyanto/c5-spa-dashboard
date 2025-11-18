"""Ensure hashlib provides an "md4" algorithm on startup.

This module attempts to call ``hashlib.new('md4')``. If that fails
it installs a small pure-Python MD4 implementation and monkeypatches
``hashlib.new`` and ``hashlib.md4`` so existing code that calls
``hashlib.new('md4', ...)`` continues to work.

Import this module as early as possible (e.g. in ``main.py``) so
third-party libs such as ``ntlm_auth`` can compute MD4 hashes.
"""

from __future__ import annotations

import hashlib as _hashlib
import copy
from typing import Optional

# Prefer using pycryptodome's MD4 implementation if available. This
# provides a faster, well-tested implementation and avoids using the
# pure-Python fallback unless necessary.
try:
    from Crypto.Hash import MD4 as _CryptoMD4  # type: ignore
except Exception:
    _CryptoMD4 = None


class _MD4:
    # Minimal, public-domain style MD4 implementation.
    # API: update(bytes), digest() -> bytes, hexdigest() -> str, copy() -> _MD4

    _mask32 = 0xFFFFFFFF

    def __init__(self, data: Optional[bytes] = None) -> None:
        # state
        self.A = 0x67452301
        self.B = 0xEFCDAB89
        self.C = 0x98BADCFE
        self.D = 0x10325476
        self.count = 0  # number of bytes processed
        self.buf = b""
        if data:
            self.update(data)

    def _F(self, x, y, z):
        return ((x & y) | (~x & z)) & self._mask32

    def _G(self, x, y, z):
        return ((x & y) | (x & z) | (y & z)) & self._mask32

    def _H(self, x, y, z):
        return (x ^ y ^ z) & self._mask32

    def _rol(self, x, n):
        return ((x << n) | (x >> (32 - n))) & self._mask32

    def _process_block(self, block: bytes) -> None:
        X = [int.from_bytes(block[i * 4 : (i + 1) * 4], "little") for i in range(16)]
        A, B, C, D = self.A, self.B, self.C, self.D

        # Round 1
        s = [3, 7, 11, 19]
        for i in range(16):
            k = i
            A = self._rol((A + self._F(B, C, D) + X[k]) & self._mask32, s[i % 4])
            A, B, C, D = D, A, B, C

        # Round 2
        s = [3, 5, 9, 13]
        for i in range(16):
            k = (i % 4) * 4 + (i // 4)
            A = self._rol(
                (A + self._G(B, C, D) + X[k] + 0x5A827999) & self._mask32, s[i % 4]
            )
            A, B, C, D = D, A, B, C

        # Round 3
        s = [3, 9, 11, 15]
        order = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]
        for i in range(16):
            k = order[i]
            A = self._rol(
                (A + self._H(B, C, D) + X[k] + 0x6ED9EBA1) & self._mask32, s[i % 4]
            )
            A, B, C, D = D, A, B, C

        self.A = (self.A + A) & self._mask32
        self.B = (self.B + B) & self._mask32
        self.C = (self.C + C) & self._mask32
        self.D = (self.D + D) & self._mask32

    def update(self, data: bytes) -> None:
        if not data:
            return
        self.count += len(data)
        data = self.buf + data
        while len(data) >= 64:
            self._process_block(data[:64])
            data = data[64:]
        self.buf = data

    def digest(self) -> bytes:
        # padding
        length_bits = (self.count << 3) & 0xFFFFFFFFFFFFFFFF
        pad = b"\x80" + b"\x00" * ((56 - (self.count + 1) % 64) % 64)
        final = self.buf + pad + length_bits.to_bytes(8, "little")
        # process final blocks
        A, B, C, D = self.A, self.B, self.C, self.D
        data = final
        while len(data):
            self._process_block(data[:64])
            data = data[64:]
        out = (
            self.A.to_bytes(4, "little")
            + self.B.to_bytes(4, "little")
            + self.C.to_bytes(4, "little")
            + self.D.to_bytes(4, "little")
        )
        # restore state
        self.A, self.B, self.C, self.D = A, B, C, D
        return out

    def hexdigest(self) -> str:
        return self.digest().hex()

    def copy(self) -> "_MD4":
        return copy.deepcopy(self)


class _HashWrapper:
    # object that mirrors hashlib objects
    def __init__(self, data: Optional[bytes] = None):
        self._md4 = _MD4(data)

    def update(self, data: bytes) -> None:
        self._md4.update(data)

    def digest(self) -> bytes:
        return self._md4.digest()

    def hexdigest(self) -> str:
        return self._md4.hexdigest()

    def copy(self):
        new = _HashWrapper()
        new._md4 = self._md4.copy()
        return new

    @property
    def name(self):
        return "md4"

    @property
    def block_size(self):
        return 64

    @property
    def digest_size(self):
        return 16


def _install_fallback():
    """Monkeypatch hashlib to provide md4 if missing."""
    try:
        # If this works, nothing to do
        _hashlib.new("md4")
        return
    except Exception:
        pass

    original_new = _hashlib.new

    # If pycryptodome is available, use it.
    if _CryptoMD4 is not None:

        def _new(name, data=b""):
            if isinstance(name, str) and name.lower() == "md4":
                # Crypto's MD4 provides a .new(data=...) constructor
                try:
                    if data:
                        return _CryptoMD4.new(data=data)
                    return _CryptoMD4.new()
                except Exception:
                    # fallback to original behavior on error
                    return original_new(name, data)
            return original_new(name, data)

        try:
            _hashlib.new = _new  # type: ignore[attr-defined]
        except Exception:
            return

        try:
            _hashlib.md4 = lambda data=b"": _CryptoMD4.new(data=data)  # type: ignore[attr-defined]
        except Exception:
            pass

    else:
        # Use pure-Python fallback defined above
        def _new(name, data=b""):
            if isinstance(name, str) and name.lower() == "md4":
                h = _HashWrapper()
                if data:
                    h.update(data)
                return h
            return original_new(name, data)

        # Apply monkeypatches
        try:
            _hashlib.new = _new  # type: ignore[attr-defined]
        except Exception:
            # best-effort only
            return

        try:
            _hashlib.md4 = lambda data=b"": _new("md4", data)  # type: ignore[attr-defined]
        except Exception:
            pass

    # Add to available/guaranteed algorithm sets when possible
    for attr in ("algorithms_available", "algorithms_guaranteed"):
        try:
            s = getattr(_hashlib, attr)
            try:
                s.add("md4")
            except Exception:
                # If it's not a mutable set, try to recreate a new set
                try:
                    new_s = set(s)
                    new_s.add("md4")
                    setattr(_hashlib, attr, new_s)
                except Exception:
                    pass
        except Exception:
            pass


_install_fallback()
