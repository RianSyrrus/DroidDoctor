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

class DebloatDisclaimerDialog(ctk.CTkToplevel):
    """Modal Dialog Peringatan & Penafian Tanggung Jawab Debloater dengan i18n."""
    def __init__(self, parent):
        super().__init__(parent)

        self.title(I18n.t("disclaimer_title"))
        self.geometry("500x440")
        self.resizable(False, False)

        self.transient(parent)
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        self.geometry(f"+{max(0, px + (pw // 2) - 250)}+{max(0, py + (ph // 2) - 220)}")
        self.grab_set()

        play_alert()

        self.bind("<Return>", lambda e: self._on_confirm())
        self.bind("<Escape>", lambda e: self._on_confirm())

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(
            container, text=I18n.t("disclaimer_header"),
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=("#DC2626", "#F87171")
        ).pack(anchor="w", pady=(0, 10))

        card = ctk.CTkFrame(
            container, fg_color=("#FEF2F2", "#1C1113"),
            corner_radius=10, border_width=1, border_color=("#FECACA", "#5E1824")
        )
        card.pack(fill="both", expand=True, pady=(0, 16))

        info_points = [
            (I18n.t("disclaimer_p1_title"), I18n.t("disclaimer_p1_desc")),
            (I18n.t("disclaimer_p2_title"), I18n.t("disclaimer_p2_desc")),
            (I18n.t("disclaimer_p3_title"), I18n.t("disclaimer_p3_desc"))
        ]

        for title, desc in info_points:
            item_box = ctk.CTkFrame(card, fg_color="transparent")
            item_box.pack(fill="x", padx=14, pady=8)

            ctk.CTkLabel(
                item_box, text=title,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=("#991B1B", "#FCA5A5")
            ).pack(anchor="w")

            ctk.CTkLabel(
                item_box, text=desc,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=("#450A0A", "#FECACA"), wraplength=420, justify="left"
            ).pack(anchor="w", pady=(2, 0))

        self.btn_confirm = ctk.CTkButton(
            container, text=I18n.t("disclaimer_btn_confirm"),
            height=42, corner_radius=10,
            fg_color="#DC2626", hover_color="#B91C1C", text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._on_confirm
        )
        self.btn_confirm.pack(fill="x", side="bottom")
        self.after(100, lambda: self.btn_confirm.focus_set())

    def _on_confirm(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()
