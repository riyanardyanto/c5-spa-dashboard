import re


from src.utils import material_theme


HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def test_palette_has_ttkbootstrap_keys():
    palette = material_theme.MATERIAL_PALETTE
    for key in ("primary", "secondary", "success", "info", "warning", "error"):
        assert key in palette, f"Missing palette key: {key}"


def test_on_colors_exist():
    palette = material_theme.MATERIAL_PALETTE
    for key in (
        "on_primary",
        "on_secondary",
        "on_success",
        "on_info",
        "on_warning",
        "on_error",
    ):
        assert key in palette, f"Missing on_* palette key: {key}"


def test_colors_are_valid_hex():
    palette = material_theme.MATERIAL_PALETTE
    invalid = [
        k for k, v in palette.items() if not isinstance(v, str) or not HEX_RE.match(v)
    ]
    assert not invalid, (
        f"The following palette values are not valid hex colors: {invalid}"
    )


def test_roundtrip_hex_rgb():
    # Ensure _hex_to_rgb and _rgb_to_hex are compatible for a few sample colors
    for color in ("#0d6efd", "#ffffff", "#0dcaf0"):
        rgb = material_theme._hex_to_rgb(color)
        assert isinstance(rgb, tuple) and len(rgb) == 3
        back = material_theme._rgb_to_hex(rgb)
        assert back.lower() == color.lower()
