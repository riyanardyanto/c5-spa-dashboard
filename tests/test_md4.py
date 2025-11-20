import hashlib
import pytest

# The project's MD4 fallback (utils.patched_hashlib) has been removed.
# These tests are still useful to validate that the running Python
# interpreter provides MD4 support; if not present the tests are
# skipped.
if not hasattr(hashlib, "md4"):
    pytest.skip(
        "hashlib.md4 not available in this Python build", allow_module_level=True
    )


def test_md4_new_digest():
    # MD4 digest of ASCII 'abc'
    expected = "a448017aaf21d8525fc10ae87aa6729d"
    assert hashlib.new("md4", b"abc").hexdigest() == expected


def test_hashlib_md4_constructor_exists_and_works():
    assert hasattr(hashlib, "md4")
    expected = "a448017aaf21d8525fc10ae87aa6729d"
    obj = hashlib.md4(b"abc")
    # Some implementations return objects with .hexdigest(), others mimic hashlib
    assert obj.hexdigest() == expected
