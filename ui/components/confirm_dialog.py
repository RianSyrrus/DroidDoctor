import customtkinter as ctk
import winsound, os
from core.i18n import I18n
from core.settings_manager import SettingsManager

def play_alert():
    if not SettingsManager.get_instance().get("sound_effects", True):
        return
    try:
        winsound.PlaySound(r"C:\Windows\Media\Windows Background.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass

class ConfirmDialog(ctk.CTkToplevel):
    """Dialog Konfirmasi Keamanan Penonaktifan & Penghapusan dengan i18n."""
    def __init__(self, parent, title: str, app_name: str, package_name: str, is_system: bool, action_type: str, on_confirm_callback, require_challenge: bool = False):
        super().__init__(parent)
        self.on_confirm = on_confirm_callback
        self.action_type = action_type
        self.require_challenge = require_challenge
        
        is_uninstall = (action_type == "uninstall")
        default_kw = I18n.t("challenge_keyword_uninstall") if is_uninstall else I18n.t("challenge_keyword_disable")
        self.challenge_keyword = default_kw.upper()

        dlg_title = I18n.t("confirm_title_uninstall") if is_uninstall else I18n.t("confirm_title_disable")
        self.title(dlg_title)
        self.geometry("460x360" if require_challenge else "460x290")
        self.resizable(False, False)

        self.transient(parent)
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        dialog_h = 360 if require_challenge else 290
        self.geometry(f"+{max(0, px + (pw // 2) - 230)}+{max(0, py + (ph // 2) - (dialog_h // 2))}")
        self.grab_set()

        play_alert()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=22, pady=18)

        header_text = I18n.t("confirm_header_uninstall") if is_uninstall else I18n.t("confirm_header_disable")
        ctk.CTkLabel(
            container, text=header_text,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=("#DC2626", "#F87171")
        ).pack(anchor="w", pady=(0, 8))

        card = ctk.CTkFrame(container, fg_color=("#F8FAFC", "#1E293B"), corner_radius=10, border_width=1, border_color=("#E2E8F0", "#334155"))
        card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            card, text=app_name,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        ).pack(anchor="w", padx=12, pady=(8, 2))

        ctk.CTkLabel(
            card, text=package_name,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("#64748B", "#94A3B8")
        ).pack(anchor="w", padx=12, pady=(0, 8))

        desc_text = I18n.t("confirm_desc_uninstall") if is_uninstall else I18n.t("confirm_desc_disable")
        ctk.CTkLabel(
            container, text=desc_text,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("#475569", "#CBD5E1"), wraplength=410, justify="left"
        ).pack(anchor="w", pady=(0, 10))

        if require_challenge:
            challenge_box = ctk.CTkFrame(container, fg_color=("#FEF2F2", "#450A0A"), corner_radius=8, border_width=1, border_color=("#FECACA", "#7F1D1D"))
            challenge_box.pack(fill="x", pady=(0, 12))

            prompt_str = I18n.t("confirm_challenge_prompt", keyword=self.challenge_keyword)
            ctk.CTkLabel(
                challenge_box, text=prompt_str,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=("#B91C1C", "#FCA5A5")
            ).pack(anchor="w", padx=10, pady=(6, 4))

            self.entry_challenge = ctk.CTkEntry(challenge_box, height=32, placeholder_text=f"{self.challenge_keyword}...", font=ctk.CTkFont(family="Segoe UI", size=12))
            self.entry_challenge.pack(fill="x", padx=10, pady=(0, 8))
            self.entry_challenge.bind("<KeyRelease>", self._check_challenge)
            self.after(100, lambda: self.entry_challenge.focus_set())

        btn_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_box.pack(fill="x", side="bottom")

        self.btn_cancel = ctk.CTkButton(
            btn_box, text=I18n.t("confirm_btn_cancel"), width=120, height=36, corner_radius=8,
            fg_color=("#E2E8F0", "#334155"), text_color=("#0F172A", "#F8FAFC"),
            hover_color=("#CBD5E1", "#475569"), font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.destroy
        )
        self.btn_cancel.pack(side="left")

        btn_confirm_text = I18n.t("confirm_btn_uninstall") if is_uninstall else I18n.t("confirm_btn_disable")
        self.btn_action = ctk.CTkButton(
            btn_box, text=btn_confirm_text, width=150, height=36, corner_radius=8,
            fg_color="#DC2626" if not require_challenge else ("#E2E8F0", "#334155"),
            text_color="#FFFFFF" if not require_challenge else ("#94A3B8", "#64748B"),
            state="normal" if not require_challenge else "disabled",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._do_confirm
        )
        self.btn_action.pack(side="right")

        self.bind("<Escape>", lambda e: self.destroy())

    def _check_challenge(self, event):
        val = self.entry_challenge.get().strip().upper()
        if val == self.challenge_keyword:
            self.btn_action.configure(state="normal", fg_color="#DC2626", hover_color="#B91C1C", text_color="#FFFFFF")
        else:
            self.btn_action.configure(state="disabled", fg_color=("#E2E8F0", "#334155"), text_color=("#94A3B8", "#64748B"))

    def _do_confirm(self):
        cb = self.on_confirm
        self.destroy()
        if cb:
            cb()
