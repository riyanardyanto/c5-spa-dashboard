import hashlib

# Ensure the patched module is imported for its side effects (registers md4)
import utils.patched_hashlib  # noqa: F401


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
