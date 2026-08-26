import customtkinter as ctk
import winsound, os
from core.i18n import I18n
from core.settings_manager import SettingsManager

def play_alert():
    """
    Plays a standard Windows notification sound if sound effects are enabled in user settings.
    """
    if not SettingsManager.get_instance().get("sound_effects", True):
        return
    try:
        winsound.PlaySound(r"C:\Windows\Media\Windows Background.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass

class StorageConfirmDialog(ctk.CTkToplevel):
    """
    Modal confirmation dialog for storage cleanup operations.
    Displays total reclaimable space summary, selected categories, and safety reassurance.
    """
    def __init__(self, parent, total_size_str: str, categories_list: list, on_confirm_callback):
        super().__init__(parent)
        self.on_confirm = on_confirm_callback

        self.title(I18n.t("storage_confirm_title"))
        self.geometry("480x420")
        self.resizable(False, False)

        self.transient(parent)
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        self.geometry(f"+{max(0, px + (pw // 2) - 240)}+{max(0, py + (ph // 2) - 210)}")
        self.grab_set()

        play_alert()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=22, pady=18)

        ctk.CTkLabel(
            container, text=I18n.t("storage_confirm_header"),
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=("#059669", "#10B981")
        ).pack(anchor="w", pady=(0, 6))

        card = ctk.CTkFrame(container, fg_color=("#ECFDF5", "#064E3B"), corner_radius=10, border_width=1, border_color=("#A7F3D0", "#047857"))
        card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            card, text=I18n.t("storage_confirm_size"),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#065F46", "#A7F3D0")
        ).pack(anchor="w", padx=12, pady=(8, 0))

        ctk.CTkLabel(
            card, text=total_size_str,
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=("#059669", "#34D399")
        ).pack(anchor="w", padx=12, pady=(0, 8))

        # Categories list
        cat_box = ctk.CTkFrame(container, fg_color=("#F8FAFC", "#1E293B"), corner_radius=8, border_width=1, border_color=("#E2E8F0", "#334155"))
        cat_box.pack(fill="x", pady=(0, 10))

        for cat in categories_list:
            row = ctk.CTkFrame(cat_box, fg_color="transparent", height=24)
            row.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(row, text="✓", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#059669", "#10B981")).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(row, text=cat, font=ctk.CTkFont(family="Segoe UI", size=11), text_color=("#334155", "#E2E8F0")).pack(side="left")

        # Safety Reassurance Box
        shield_box = ctk.CTkFrame(container, fg_color=("#EFF6FF", "#1E293B"), corner_radius=8, border_width=1, border_color=("#BFDBFE", "#1E3A8A"))
        shield_box.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            shield_box, text=f"🔒 {I18n.t('storage_shield_title')}",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=("#1D4ED8", "#60A5FA")
        ).pack(anchor="w", padx=10, pady=(6, 2))

        ctk.CTkLabel(
            shield_box, text=I18n.t("storage_shield_desc"),
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=("#1E40AF", "#93C5FD"), wraplength=410, justify="left"
        ).pack(anchor="w", padx=10, pady=(0, 6))

        # Buttons
        btn_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_box.pack(fill="x", side="bottom")

        self.btn_cancel = ctk.CTkButton(
            btn_box, text=I18n.t("confirm_btn_cancel"), width=120, height=36, corner_radius=8,
            fg_color=("#E2E8F0", "#334155"), text_color=("#0F172A", "#F8FAFC"),
            hover_color=("#CBD5E1", "#475569"), font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.destroy
        )
        self.btn_cancel.pack(side="left")

        self.btn_action = ctk.CTkButton(
            btn_box, text=I18n.t("storage_confirm_btn_clean"), width=160, height=36, corner_radius=8,
            fg_color="#059669", hover_color="#047857", text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._do_confirm
        )
        self.btn_action.pack(side="right")

        self.bind("<Escape>", lambda e: self.destroy())
        self.after(100, lambda: self.btn_action.focus_set())

    def _do_confirm(self):
        cb = self.on_confirm
        self.destroy()
        if cb:
            cb()
