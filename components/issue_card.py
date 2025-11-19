import tkinter as tk
import uuid
from pathlib import Path
from tkinter import Menu, messagebox, font as tkfont
from typing import Dict, List, Optional

import ttkbootstrap as ttk
import pandas as pd
from PIL import Image, ImageTk, UnidentifiedImageError
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tooltip import ToolTip

from services.logging_service import log_exception, log_warning
from utils.helpers import resource_path
from utils.material_theme import MATERIAL_PALETTE


_ACTION_ICON: Optional[ImageTk.PhotoImage] = None
_DETAIL_ICON: Optional[ImageTk.PhotoImage] = None
_ADD_ICON: Optional[ImageTk.PhotoImage] = None
_BIN_ICON: Optional[ImageTk.PhotoImage] = None
_QR_ICON: Optional[ImageTk.PhotoImage] = None

_ACTION_ICON_FAILED = False
_DETAIL_ICON_FAILED = False
_ADD_ICON_FAILED = False
_BIN_ICON_FAILED = False
_QR_ICON_FAILED = False


def _resolve_palette(palette: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    resolved = MATERIAL_PALETTE.copy()
    if palette:
        resolved.update(palette)
    return resolved


def _get_action_icon() -> Optional[ImageTk.PhotoImage]:
    global _ACTION_ICON, _ACTION_ICON_FAILED
    if _ACTION_ICON is not None:
        return _ACTION_ICON
    if _ACTION_ICON_FAILED:
        return None
    try:
        image = Image.open(resource_path("assets/approve.png")).resize(
            (16, 16), Image.LANCZOS
        )
        _ACTION_ICON = ImageTk.PhotoImage(image)
    except (FileNotFoundError, UnidentifiedImageError) as exc:
        log_warning("Ikon approve tidak ditemukan atau rusak", exc)
        _ACTION_ICON_FAILED = True
        return None
    return _ACTION_ICON


def _get_detail_icon() -> Optional[ImageTk.PhotoImage]:
    global _DETAIL_ICON, _DETAIL_ICON_FAILED
    if _DETAIL_ICON is not None:
        return _DETAIL_ICON
    if _DETAIL_ICON_FAILED:
        return None
    try:
        image = Image.open(resource_path("assets/info.png")).resize(
            (16, 16), Image.LANCZOS
        )
        _DETAIL_ICON = ImageTk.PhotoImage(image)
    except (FileNotFoundError, UnidentifiedImageError) as exc:
        log_warning("Ikon detail tidak ditemukan atau rusak", exc)
        _DETAIL_ICON_FAILED = True
        return None
    return _DETAIL_ICON


def _get_add_icon() -> Optional[ImageTk.PhotoImage]:
    global _ADD_ICON, _ADD_ICON_FAILED
    if _ADD_ICON is not None:
        return _ADD_ICON
    if _ADD_ICON_FAILED:
        return None
    try:
        image = Image.open(resource_path("assets/add.png")).resize(
            (16, 16), Image.LANCZOS
        )
        _ADD_ICON = ImageTk.PhotoImage(image)
    except (FileNotFoundError, UnidentifiedImageError) as exc:
        log_warning("Ikon tambah tidak ditemukan atau rusak", exc)
        _ADD_ICON_FAILED = True
        return None
    return _ADD_ICON


def _get_bin_icon() -> Optional[ImageTk.PhotoImage]:
    global _BIN_ICON, _BIN_ICON_FAILED
    if _BIN_ICON is not None:
        return _BIN_ICON
    if _BIN_ICON_FAILED:
        return None
    try:
        image = Image.open(resource_path("assets/clear.png")).resize(
            (16, 16), Image.LANCZOS
        )
        _BIN_ICON = ImageTk.PhotoImage(image)
    except (FileNotFoundError, UnidentifiedImageError) as exc:
        log_warning("Ikon hapus tidak ditemukan atau rusak", exc)
        _BIN_ICON_FAILED = True
        return None
    return _BIN_ICON


def _get_qr_icon() -> Optional[ImageTk.PhotoImage]:
    global _QR_ICON, _QR_ICON_FAILED
    if _QR_ICON is not None:
        return _QR_ICON
    if _QR_ICON_FAILED:
        return None
    try:
        image = Image.open(resource_path("assets/qrcode.png")).resize(
            (16, 16), Image.LANCZOS
        )
        _QR_ICON = ImageTk.PhotoImage(image)
    except (FileNotFoundError, UnidentifiedImageError) as exc:
        log_warning("Ikon QR tidak ditemukan atau rusak", exc)
        _QR_ICON_FAILED = True
        return None
    return _QR_ICON


def setup_entry_placeholder(
    entry: ttk.Entry,
    placeholder_text: str,
    *,
    text_color: str = "white",
    placeholder_color: str = "gray",
) -> None:
    """Attach placeholder text behavior to a ttk Entry."""

    def handle_focus_in(_):
        if getattr(entry, "_placeholder_active", False):
            entry.delete(0, "end")
            entry.configure(foreground=text_color)
            entry._placeholder_active = False

    def handle_focus_out(_):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.configure(foreground=placeholder_color)
            entry._placeholder_active = True

    entry.insert(0, placeholder_text)
    entry.configure(foreground=placeholder_color)
    entry._placeholder_active = True
    entry._placeholder_text = placeholder_text
    entry.bind("<FocusIn>", handle_focus_in, add="+")
    entry.bind("<FocusOut>", handle_focus_out, add="+")


# ----------------------------------------------------------------------
# Action Item (klik kanan -> delete)
# ----------------------------------------------------------------------
class ActionItem(ttk.Frame):
    def __init__(
        self,
        master,
        on_remove=None,
        palette: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        super().__init__(master, style="MaterialSubsection.TFrame", **kwargs)
        self.on_remove = on_remove
        self.palette = _resolve_palette(palette)

        self.columnconfigure(1, weight=1)

        bullet_color = self.palette.get("primary", "#4C9BFF")
        self.bullet = ttk.Label(self, text="•", style="MaterialCaption.TLabel")
        self.bullet.grid(row=0, column=0, padx=(40, 5), pady=(5, 0))
        self.bullet.configure(foreground=bullet_color)

        self.entry = ttk.Entry(self, bootstyle="info")
        setup_entry_placeholder(
            self.entry,
            "Tindakan...",
            text_color=self.palette.get("on_surface", "#FFFFFF"),
            placeholder_color=self.palette.get("on_surface_variant", "#8A97AA"),
        )
        self.entry.grid(row=0, column=1, sticky="ew", pady=(2, 2))
        # Make ActionItem.entry text italic to visually distinguish actions
        try:
            current_font = tkfont.Font(font=self.entry.cget("font"))
        except Exception:
            current_font = tkfont.nametofont("TkDefaultFont")
        entry_italic = tkfont.Font(
            family=current_font.cget("family"),
            size=current_font.cget("size"),
            slant="italic",
        )
        self.entry.configure(font=entry_italic)

        self.entry.bind("<Button-3>", self.show_context_menu)
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Delete", command=self.delete_self)

    def focus_entry(self) -> None:
        self.entry.focus_set()

    def show_context_menu(self, event: tk.Event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def delete_self(self):
        if self.on_remove:
            self.on_remove(self)
        self.destroy()

    def get_text(self):
        if getattr(self.entry, "_placeholder_active", False):
            return ""
        return self.entry.get().strip()


# ----------------------------------------------------------------------
# Detail Item (klik kanan -> delete)
# ----------------------------------------------------------------------
class DetailItem(ttk.Frame):
    def __init__(
        self,
        master,
        on_remove=None,
        number: Optional[int] = None,
        palette: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        super().__init__(
            master,
            style="MaterialSubsection.TFrame",
            padding=(5, 5, 5, 5),
            **kwargs,
        )
        self.on_remove = on_remove
        self.palette = _resolve_palette(palette)
        self.action_items: List[ActionItem] = []

        header = ttk.Frame(self, style="MaterialSubsection.TFrame")
        header.pack(fill="x")

        self.index_chip = ttk.Label(
            header,
            text=self._format_label(number),
            style="MaterialChip.TLabel",
            foreground=self.palette.get("on_surface", "#FFFFFF"),
        )
        self.index_chip.pack(side="left")

        self.textbox = ttk.Entry(header, bootstyle="primary")
        setup_entry_placeholder(
            self.textbox,
            "Masukkan detail...",
            text_color=self.palette.get("on_surface", "#FFFFFF"),
            placeholder_color=self.palette.get("on_surface_variant", "#8A97AA"),
        )
        self.textbox.pack(side="left", fill="x", expand=True, padx=(5, 5))
        self.textbox.bind("<Button-3>", self.show_context_menu)

        self.add_action_btn = ttk.Button(
            header,
            bootstyle="primary",
            width=3,
            command=self.add_action,
        )
        action_icon = _get_action_icon()
        if action_icon:
            self.add_action_btn.configure(image=action_icon)
            self.add_action_btn.image = action_icon
        else:
            self.add_action_btn.configure(text="+")
        self.add_action_btn.pack(side="right", padx=(0, 0))
        ToolTip(self.add_action_btn, "Tambah tindakan", delay=0, position="left")

        self.action_container = ttk.Frame(self, style="MaterialSubsection.TFrame")
        self.action_container.pack(fill="x", expand=True)

        self.add_action()

        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Delete Detail", command=self.delete_self)

    @staticmethod
    def _format_label(number: Optional[int]) -> str:
        if number is None:
            return "#"
        return f"# {number}"

    def focus_entry(self) -> None:
        self.textbox.focus_set()

    def set_order(self, index: int) -> None:
        self.index_chip.configure(text=self._format_label(index))

    def show_context_menu(self, event: tk.Event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def add_action(self):
        item = ActionItem(
            self.action_container,
            on_remove=self.remove_action,
            palette=self.palette,
        )
        item.pack(fill="x", pady=(0, 0))
        self.action_items.append(item)
        item.focus_entry()

    def remove_action(self, item):
        if item in self.action_items:
            self.action_items.remove(item)

    def delete_self(self):
        if self.on_remove:
            self.on_remove(self)
        self.destroy()

    def get_data(self):
        if getattr(self.textbox, "_placeholder_active", False):
            detail_text = ""
        else:
            detail_text = self.textbox.get().strip()
        actions = [a.get_text() for a in self.action_items if a.get_text()]
        return {"detail": detail_text, "actions": actions} if detail_text else None


# ----------------------------------------------------------------------
# Issue Card
# ----------------------------------------------------------------------
class IssueCard(ttk.Frame):
    def __init__(
        self,
        master,
        on_delete=None,
        palette: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        super().__init__(master, style="MaterialCard.TFrame", **kwargs)
        self.card_id = str(uuid.uuid4())
        self.on_delete = on_delete
        self.palette = _resolve_palette(palette)
        self.detail_items: List[DetailItem] = []

        self.columnconfigure(1, weight=1)

        accent = ttk.Frame(self, style="MaterialCardAccent.TFrame", width=6)
        accent.grid(row=0, column=0, sticky="ns")
        accent.grid_propagate(False)

        body = ttk.Frame(self, style="MaterialCardBody.TFrame", padding=(10, 5, 10, 5))
        body.grid(row=0, column=1, sticky="nsew")
        body.columnconfigure(0, weight=1)

        header = ttk.Frame(body, style="MaterialCardBody.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        self.issue_entry = ttk.Entry(header, bootstyle="warning")
        setup_entry_placeholder(
            self.issue_entry,
            "Masukkan issue...",
            text_color=self.palette.get("on_surface", "#FFFFFF"),
            placeholder_color=self.palette.get("on_surface_variant", "#85878B"),
        )
        self.issue_entry.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        # Make issue_entry text bold for emphasis
        try:
            current_font = tkfont.Font(font=self.issue_entry.cget("font"))
        except Exception:
            current_font = tkfont.nametofont("TkDefaultFont")
        bold_font = tkfont.Font(
            family=current_font.cget("family"),
            size=current_font.cget("size"),
            weight="bold",
        )
        self.issue_entry.configure(font=bold_font)

        self.add_detail_btn = ttk.Button(
            header,
            bootstyle="warning",
            width=3,
            command=self.add_detail_item,
        )
        detail_icon = _get_detail_icon()
        if detail_icon:
            self.add_detail_btn.configure(image=detail_icon)
            self.add_detail_btn.image = detail_icon
        else:
            self.add_detail_btn.configure(text="+")
        self.add_detail_btn.grid(row=0, column=1, padx=(5, 0), pady=(0, 5), sticky="e")
        ToolTip(self.add_detail_btn, "Tambah detail", delay=0, position="left")

        ttk.Separator(body, orient="horizontal", style="Horizontal.TSeparator").grid(
            row=2, column=0, sticky="ew"
        )

        self.detail_container = ttk.Frame(body, style="MaterialCardBody.TFrame")
        self.detail_container.grid(row=3, column=0, sticky="ew", pady=(0, 0))
        self.detail_container.columnconfigure(0, weight=1)

        self.card_menu = Menu(self, tearoff=0)
        self.card_menu.add_command(label="Delete Card", command=self.delete_card)
        self._context_targets = {
            self,
            body,
            self.detail_container,
            header,
            self.issue_entry,
        }
        for target in self._context_targets:
            target.bind("<Button-3>", self.show_card_menu, add="+")

        self.add_detail_item()

    def show_card_menu(self, event: tk.Event):
        if event.widget not in self._context_targets:
            return
        try:
            self.card_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.card_menu.grab_release()

    def add_detail_item(self):
        item = DetailItem(
            self.detail_container,
            on_remove=self.remove_detail_item,
            number=len(self.detail_items) + 1,
            palette=self.palette,
        )
        item.pack(fill="x", pady=(5, 0))
        self.detail_items.append(item)
        item.focus_entry()
        self._renumber_details()

    def _renumber_details(self) -> None:
        for index, detail in enumerate(self.detail_items, start=1):
            detail.set_order(index)

    def remove_detail_item(self, item):
        if item in self.detail_items:
            self.detail_items.remove(item)
            item.destroy()
            self._renumber_details()

    def delete_card(self):
        if self.on_delete:
            self.on_delete(self.card_id)
        self.destroy()

    def set_issue(self, issue_text: str):
        """Populate the issue entry without triggering placeholder state."""
        self.issue_entry.delete(0, "end")
        self.issue_entry.insert(0, issue_text)
        self.issue_entry.configure(foreground=self.palette.get("on_surface", "#FFFFFF"))
        self.issue_entry._placeholder_active = False

    def get_data(self):
        if getattr(self.issue_entry, "_placeholder_active", False):
            issue = ""
        else:
            issue = self.issue_entry.get().strip()
        details = [item.get_data() for item in self.detail_items if item.get_data()]
        return (
            {"id": self.card_id, "issue": issue, "details": details}
            if issue or details
            else None
        )


# ----------------------------------------------------------------------
# Issue Card Container
# ----------------------------------------------------------------------
class IssueCardFrame(ttk.Frame):
    def __init__(
        self,
        master,
        palette: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        super().__init__(
            master,
            style="MaterialSurface.TFrame",
            padding=(10, 0, 10, 10),
            **kwargs,
        )
        self.palette = _resolve_palette(palette)
        self.cards: Dict[str, IssueCard] = {}

        header = ttk.Frame(self, style="MaterialHeader.TFrame")
        header.pack(side="top", anchor="w", fill="x", pady=(0, 5))

        top_frame = ttk.Frame(header, style="MaterialHeader.TFrame")
        top_frame.pack(side="top", anchor="w", fill="x")

        title_area = ttk.Frame(top_frame, style="MaterialHeader.TFrame")
        title_area.pack(side="left", fill="x", expand=True, anchor="w")

        ttk.Label(
            title_area,
            text="Issue Cards",
            style="MaterialTitle.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            title_area,
            text="Kelola issue downtime dan tindakan.",
            style="MaterialSubtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        ttk.Separator(header, orient="horizontal", style="Horizontal.TSeparator").pack(
            side="top", fill="x", pady=(0, 0)
        )

        controls = ttk.Frame(header, style="MaterialHeader.TFrame")
        controls.pack(side="top", anchor="w", expand=True, fill="x", pady=(5, 0))

        self.cards_badge = ttk.Label(
            controls,
            text="0 Kartu",
            style="MaterialBadge.TLabel",
        )
        self.cards_badge.pack(side="left", anchor="w", pady=(0, 0), padx=(0, 8))

        buttons = ttk.Frame(controls, style="MaterialHeader.TFrame")
        buttons.pack(side="right", anchor="e")

        self.clear_btn = ttk.Button(
            buttons,
            bootstyle="danger",
            width=3,
            command=self.clear_cards,
        )
        bin_icon = _get_bin_icon()
        if bin_icon:
            self.clear_btn.configure(image=bin_icon, compound="image")
            self.clear_btn.image = bin_icon
        self.clear_btn.pack(
            side="right", anchor="e", fill="x", pady=(0, 0), padx=(5, 0)
        )
        ToolTip(self.clear_btn, "Hapus seluruh issue card", delay=0, position="left")

        self.add_card_btn = ttk.Button(
            buttons,
            bootstyle="success",
            width=3,
            command=self.add_card,
        )
        add_icon = _get_add_icon()
        if add_icon:
            self.add_card_btn.configure(image=add_icon, compound="image")
            self.add_card_btn.image = add_icon
        self.add_card_btn.pack(side="right", anchor="e", fill="x", padx=(0, 5))
        ToolTip(self.add_card_btn, "Tambah issue card baru", delay=0, position="left")

        # Separator

        ttk.Separator(self, orient="horizontal", style="Horizontal.TSeparator").pack(
            fill="x", pady=(0, 5)
        )

        self.scrollable = ScrolledFrame(
            self,
            autohide=True,
            # padding=(5, 5, 5, 5),
        )
        self.scrollable.pack(fill="both", expand=True)
        self.scrollable.configure(style="MaterialScrollContainer.TFrame")

        self.cards_container = ttk.Frame(
            self.scrollable,
            style="MaterialScrollContainer.TFrame",
        )
        self.cards_container.pack(fill="both", expand=True, padx=5, pady=0)
        self.cards_container.columnconfigure(0, weight=1)

        self.empty_state = ttk.Label(
            self.cards_container,
            text="Belum ada issue. Tambahkan kartu untuk mulai mencatat.",
            style="MaterialMuted.TLabel",
            anchor="center",
            padding=(12, 24),
            justify="center",
        )

        self._setup_scroll_speed()
        self._update_card_badge()
        self.add_card()

    def _setup_scroll_speed(self) -> None:
        """Configure faster scrolling for the ScrolledFrame."""

        def _on_mousewheel(event):
            self.scrollable.yview_scroll(-3 if event.delta > 0 else 3, "units")
            return "break"

        def _on_linux_scroll(event):
            step = -3 if event.num == 4 else 3
            self.scrollable.yview_scroll(step, "units")
            return "break"

        targets = [
            self.scrollable,
            getattr(self.scrollable, "container", None),
            self.cards_container,
        ]

        for target in targets:
            if target is None:
                continue
            target.bind("<Enter>", lambda _: self.scrollable.focus_set(), add="+")
            target.bind("<MouseWheel>", _on_mousewheel, add="+")
            target.bind("<Button-4>", _on_linux_scroll, add="+")
            target.bind("<Button-5>", _on_linux_scroll, add="+")

    def _show_empty_state(self) -> None:
        if not self.empty_state.winfo_ismapped():
            self.empty_state.pack(fill="x", pady=(12, 0))

    def _hide_empty_state(self) -> None:
        if self.empty_state.winfo_ismapped():
            self.empty_state.pack_forget()

    def add_card(self, issue_text: Optional[str] = None) -> IssueCard:
        """Create a new issue card and register it in the view."""

        card = IssueCard(
            self.cards_container,
            on_delete=self.remove_card,
            palette=self.palette,
        )
        card.pack(fill="x", pady=5)
        self.cards[card.card_id] = card
        if issue_text:
            card.set_issue(issue_text)
        card.issue_entry.focus_set()
        self._update_card_badge()
        return card

    def save_data(self) -> None:
        """Trigger the save dialog to persist card data to CSV."""

        from tkinter import filedialog

        file_path = filedialog.asksaveasfilename(
            title="Simpan Data Kartu sebagai CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not file_path:
            return

        success = self.save_cards_to_csv(file_path, include_index=False)
        if success:
            messagebox.showinfo(
                "Sukses",
                f"Data kartu berhasil disimpan ke:\n{file_path}",
            )
        else:
            messagebox.showerror(
                "Gagal",
                "Terjadi kesalahan saat menyimpan data kartu.",
            )

    def get_cards_dataframe(self) -> pd.DataFrame:
        """Return a DataFrame representing all card data with one action per row."""

        columns = ["card_id", "issue", "detail", "action"]
        records: List[Dict[str, object]] = []

        for card in self.cards.values():
            card_data = card.get_data()
            if not card_data:
                continue

            details = card_data.get("details") or []
            if not details:
                records.append(
                    {
                        "card_id": card_data["id"],
                        "issue": card_data.get("issue", ""),
                        "detail": None,
                        "action": None,
                    }
                )
                continue

            for detail in details:
                actions = detail.get("actions") or []
                if not actions:
                    records.append(
                        {
                            "card_id": card_data["id"],
                            "issue": card_data.get("issue", ""),
                            "detail": detail.get("detail", ""),
                            "action": None,
                        }
                    )
                    continue

                for action in actions:
                    records.append(
                        {
                            "card_id": card_data["id"],
                            "issue": card_data.get("issue", ""),
                            "detail": detail.get("detail", ""),
                            "action": action,
                        }
                    )

        if not records:
            # print("No records found")
            return pd.DataFrame(columns=columns)

        dataframe = pd.DataFrame.from_records(records, columns=columns)
        print(dataframe)
        return dataframe

    def save_cards_to_csv(self, file_path: str, *, include_index: bool = False) -> bool:
        """Append the current card data to the existing CSV file."""

        dataframe = self.get_cards_dataframe()
        if dataframe.empty:
            return False

        target_path = Path(file_path)
        if not target_path.exists():
            return False

        try:
            file_empty = target_path.stat().st_size == 0
        except OSError as exc:
            log_exception("Gagal membaca ukuran file saat ekspor kartu", exc)
            return False

        try:
            dataframe.to_csv(
                target_path,
                mode="a",
                header=file_empty,
                index=include_index,
            )
        except OSError as exc:
            log_exception("Gagal menulis kartu ke file CSV", exc)
            return False

        return True

    def _update_card_badge(self) -> None:
        count = len(self.cards)
        self.cards_badge.configure(text=f"{count} Kartu")
        # if count == 0:
        #     self._show_empty_state()
        # else:
        #     self._hide_empty_state()

    def remove_card(self, card_id: str) -> None:
        """Remove a card reference once it is destroyed."""

        if card_id in self.cards:
            del self.cards[card_id]
            self._update_card_badge()

    def clear_cards(self) -> None:
        """Delete all cards and leave a single empty card for the user."""

        if len(self.cards) <= 1:
            for card in list(self.cards.values()):
                card.destroy()
            self.cards.clear()
            self._update_card_badge()
            self.add_card()
            return

        result = messagebox.askyesno(
            "Konfirmasi",
            f"Apakah Anda yakin ingin menghapus semua {len(self.cards)} kartu?",
            icon="warning",
        )

        if result:
            for card in list(self.cards.values()):
                card.destroy()
            self.cards.clear()
            self._update_card_badge()
            self.add_card()
