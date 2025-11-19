"""Material Design inspired styling helpers for the dashboard UI."""

from __future__ import annotations

from typing import Dict, Iterable

import ttkbootstrap as ttk
from tkinter import Misc, font as tkfont

from services.logging_service import log_warning

MATERIAL_PALETTE: Dict[str, str] = {
    # Primary and related
    "primary": "#0d6efd",  # ttkbootstrap/Bootstrap primary
    "on_primary": "#ffffff",
    "primary_container": "#0b5ed7",
    "on_primary_container": "#D6E4FF",
    # Secondary
    "secondary": "#6c757d",
    "on_secondary": "#ffffff",
    # Info/Tertiary (keep `tertiary` for backward compatibility)
    "tertiary": "#0dcaf0",
    "info": "#0dcaf0",
    "on_tertiary": "#000000",
    "on_info": "#000000",
    # Background / Surface (theme-specific - kept dark for "superhero" base theme)
    "background": "#1F2A37",
    "on_background": "#E4ECF5",
    "surface": "#243447",
    "on_surface": "#E4ECF5",
    "surface_variant": "#3A4B5E",
    "on_surface_variant": "#C8D4E3",
    # Outline / variants
    "outline": "#5B7089",
    "outline_variant": "#3A4B5E",
    # Error / Danger
    "error": "#dc3545",
    "on_error": "#ffffff",
    # Warning
    "warning": "#ffc107",
    "on_warning": "#000000",
    # Success
    "success": "#1D9F1D",
    "on_success": "#ffffff",
    # Common light/dark (optional helpers)
    "light": "#f8f9fa",
    "on_light": "#000000",
    "dark": "#212529",
    "on_dark": "#ffffff",
}

_WHITE = "#FFFFFF"
_BLACK = "#000000"


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[idx : idx + 2], 16) for idx in (0, 2, 4))


def _rgb_to_hex(rgb: Iterable[int]) -> str:
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def _mix(color_a: str, color_b: str, ratio: float) -> str:
    ratio = max(0.0, min(ratio, 1.0))
    r1, g1, b1 = _hex_to_rgb(color_a)
    r2, g2, b2 = _hex_to_rgb(color_b)
    r = int(round(r1 + (r2 - r1) * ratio))
    g = int(round(g1 + (g2 - g1) * ratio))
    b = int(round(b1 + (b2 - b1) * ratio))
    return _rgb_to_hex((r, g, b))


def _style_name(base: str, variant: str | None) -> str:
    if not variant:
        return base
    return f"{variant}.{base}"


def _pick_font_family(widget: Misc) -> str:
    try:
        families = tkfont.families(widget)
    except tkfont.TclError as exc:
        log_warning("Gagal mengambil daftar font dari Tk", exc)
        widget.update_idletasks()
        families = tkfont.families(widget)

    preferred = (
        "Roboto",
        "Segoe UI Variable",
        "Segoe UI",
        "Calibri",
        "Arial",
    )
    for name in preferred:
        if name in families:
            return name
    return "Segoe UI"


def apply_material_theme(window: ttk.Window) -> Dict[str, str]:
    """Apply Material-inspired styling to a ttkbootstrap window."""

    palette = MATERIAL_PALETTE.copy()
    style = window.style

    base_theme = "superhero"
    try:
        style.theme_use(base_theme)
    except Exception as exc:  # noqa: BLE001 - fallback ke tema default
        log_warning("Tema superhero tidak tersedia, menggunakan tema default", exc)

    font_family = _pick_font_family(window)
    body_font = (font_family, 8)
    title_font = (font_family, 12, "bold")
    subtitle_font = (font_family, 9, "italic")
    caption_font = (font_family, 9)
    badge_font = (font_family, 9, "bold")
    button_font = (font_family, 8, "bold")
    card_body_bg = _mix(palette["surface"], _WHITE, 0.04)
    card_scroll_bg = _mix(palette["surface"], _BLACK, 0.18)

    style.configure(".", font=body_font)
    window.configure(background=palette["background"])

    style.configure("TFrame", background=palette["background"])
    style.configure(
        "TLabel", background=palette["background"], foreground=palette["on_surface"]
    )

    style.configure(
        "MaterialSurface.TFrame",
        background=palette["surface"],
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "MaterialHeader.TFrame",
        background=palette["surface"],
        borderwidth=0,
        relief="flat",
        padding=(16, 12),
    )

    style.configure(
        "MaterialTitle.TLabel",
        background=palette["surface"],
        foreground=palette["on_surface"],
        font=title_font,
    )
    style.configure(
        "MaterialSubtitle.TLabel",
        background=palette["surface"],
        foreground=palette["on_surface_variant"],
        font=subtitle_font,
    )
    style.configure(
        "MaterialCaption.TLabel",
        background=palette["surface"],
        foreground=palette["on_surface_variant"],
        font=caption_font,
    )
    style.configure(
        "MaterialBadge.TLabel",
        background=_mix(palette["surface_variant"], palette["primary"], 0.35),
        foreground=palette["on_surface"],
        font=badge_font,
        padding=(12, 4),
    )
    style.configure(
        "MaterialSectionTitle.TLabel",
        background=palette["surface"],
        foreground=palette["on_surface"],
        font=(font_family, 12, "bold"),
    )
    style.configure(
        "MaterialChip.TLabel",
        background=_mix(palette["primary"], palette["surface"], 0.55),
        foreground=palette["on_primary"],
        font=(font_family, 9, "bold"),
        padding=(4, 2),
    )
    style.configure(
        "MaterialMuted.TLabel",
        background=palette["surface"],
        foreground=palette["on_surface_variant"],
        font=(font_family, 9),
    )
    style.configure(
        "MaterialCardAccent.TFrame",
        background=palette["primary"],
    )
    style.configure(
        "MaterialSubsection.TFrame",
        background=_mix(palette["surface"], palette["background"], 0.2),
        borderwidth=0,
        relief="flat",
    )

    def configure_button(variant: str, base_color: str, text_color: str) -> None:
        hover = _mix(base_color, _WHITE, 0.12)
        disabled = _mix(base_color, palette["surface"], 0.6)
        style.configure(
            _style_name("TButton", variant),
            background=base_color,
            foreground=text_color,
            relief="flat",
            borderwidth=0,
            focusthickness=2,
            focuscolor=base_color,
            font=button_font,
            padding=(8, 4),
        )
        style.map(
            _style_name("TButton", variant),
            background=[("disabled", disabled), ("pressed", hover), ("active", hover)],
            foreground=[("disabled", _mix(text_color, base_color, 0.5))],
        )

    configure_button("primary", palette["primary"], palette["on_primary"])
    configure_button(
        "success",
        _mix(palette["success"], palette["success"], 0.5),
        palette["on_success"],
    )
    configure_button(
        "info",
        _mix(palette["tertiary"], palette["primary"], 0.2),
        palette["on_tertiary"],
    )
    configure_button("warning", palette["warning"], palette["on_warning"])
    configure_button("danger", palette["error"], palette["on_error"])

    def configure_labelframe(variant: str | None) -> None:
        style.configure(
            _style_name("TLabelframe", variant),
            background=palette["surface"],
            borderwidth=0,
            relief="flat",
            padding=(16, 12),
        )
        style.configure(
            _style_name("TLabelframe.Label", variant),
            background=palette["surface"],
            foreground=palette["on_surface"],
            font=(font_family, 12, "bold"),
            padding=(4, 0),
        )

    for variant in (None, "primary", "success", "info", "warning", "danger"):
        configure_labelframe(variant)

    def configure_entry(variant: str | None) -> None:
        style.configure(
            _style_name("TEntry", variant),
            fieldbackground=palette["surface"],
            background=palette["surface"],
            foreground=palette["on_surface"],
            bordercolor=palette["outline_variant"],
            lightcolor=palette["primary"],
            darkcolor=palette["outline"],
            insertcolor=palette["primary"],
            focusthickness=2,
            focuscolor=palette["primary"],
        )
        style.map(
            _style_name("TEntry", variant),
            fieldbackground=[
                ("disabled", palette["surface_variant"]),
                ("readonly", palette["surface_variant"]),
            ],
            foreground=[("disabled", palette["on_surface_variant"])],
        )

    for variant in (None, "primary", "success", "info", "warning"):
        configure_entry(variant)

    def configure_combobox(variant: str | None) -> None:
        style.configure(
            _style_name("TCombobox", variant),
            fieldbackground=palette["surface"],
            background=palette["surface"],
            foreground=palette["on_surface"],
            bordercolor=palette["outline_variant"],
            lightcolor=palette["primary"],
            darkcolor=palette["outline"],
            arrowcolor=palette["on_surface"],
        )
        style.map(
            _style_name("TCombobox", variant),
            fieldbackground=[
                ("readonly", palette["surface"]),
                ("disabled", palette["surface_variant"]),
            ],
            foreground=[("disabled", palette["on_surface_variant"])],
        )

    for variant in (None, "primary", "success", "info", "warning"):
        configure_combobox(variant)

    style.configure(
        "Treeview",
        background=palette["surface"],
        fieldbackground=palette["surface"],
        foreground=palette["on_surface"],
        bordercolor=palette["surface"],
        lightcolor=palette["surface"],
        darkcolor=palette["surface"],
        rowheight=32,
        font=body_font,
    )
    style.map(
        "Treeview",
        background=[("selected", palette["primary"])],
        foreground=[
            ("selected", palette["on_primary"]),
            ("disabled", palette["on_surface_variant"]),
        ],
    )
    style.configure(
        "Treeview.Heading",
        background=_mix(palette["surface_variant"], palette["primary"], 0.25),
        foreground=palette["on_surface"],
        bordercolor=_mix(palette["surface_variant"], palette["primary"], 0.25),
        relief="flat",
        font=(font_family, 10, "bold"),
        padding=6,
    )
    style.map(
        "Treeview.Heading",
        background=[
            ("pressed", palette["surface_variant"]),
            ("active", palette["surface_variant"]),
        ],
    )

    style.configure(
        "Horizontal.TSeparator",
        background=palette["outline_variant"],
        bordercolor=palette["outline_variant"],
    )
    style.configure(
        "danger.Horizontal.TSeparator",
        background=palette["outline_variant"],
        bordercolor=palette["outline_variant"],
    )

    style.configure(
        "Horizontal.TProgressbar",
        background=palette["primary"],
        troughcolor=palette["surface_variant"],
        bordercolor=palette["surface_variant"],
        thickness=6,
    )
    style.configure(
        "success.Horizontal.TProgressbar",
        background=palette["primary"],
        troughcolor=palette["surface_variant"],
        bordercolor=palette["surface_variant"],
        thickness=6,
    )
    style.configure(
        "success.Striped.Horizontal.TProgressbar",
        background=palette["primary"],
        troughcolor=palette["surface_variant"],
        bordercolor=palette["surface_variant"],
        thickness=6,
    )

    style.configure(
        "MaterialCard.TFrame",
        background=palette["surface"],
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "MaterialCardBody.TFrame",
        background=card_body_bg,
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "MaterialCardMuted.TLabel",
        background=card_body_bg,
        foreground=palette["on_surface_variant"],
        font=(font_family, 9),
    )
    style.configure(
        "MaterialScrollContainer.TFrame",
        background=card_scroll_bg,
        borderwidth=0,
        relief="flat",
    )

    return palette
