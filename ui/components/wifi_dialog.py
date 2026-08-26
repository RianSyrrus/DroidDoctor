import customtkinter as ctk
import threading
import winsound, os
from core.i18n import I18n
from core.settings_manager import SettingsManager

_active_wifi_dialog = None

def play_modal_blocked_sound():
    if not SettingsManager.get_instance().get("sound_effects", True):
        return
    wav_candidates = [
        r"C:\Windows\Media\Windows Background.wav",
        r"C:\Windows\Media\chord.wav",
        r"C:\Windows\Media\Windows Ding.wav"
    ]
    for wav in wav_candidates:
        if os.path.exists(wav):
            try:
                winsound.PlaySound(wav, winsound.SND_FILENAME | winsound.SND_ASYNC)
                return
            except Exception:
                pass
    try:
        winsound.Beep(950, 120)
    except Exception:
        pass

class WifiDialog(ctk.CTkToplevel):
    """Dialog Nirkabel Modal Single-Instance dengan Lokalisasi i18n."""
    def __init__(self, parent, adb_manager, on_success_callback=None):
        global _active_wifi_dialog
        if _active_wifi_dialog is not None and _active_wifi_dialog.winfo_exists():
            _active_wifi_dialog.lift()
            _active_wifi_dialog.focus_force()
            play_modal_blocked_sound()
            return

        super().__init__(parent)
        _active_wifi_dialog = self
        self.adb = adb_manager
        self.parent_win = parent
        self.on_success = on_success_callback

        self.title(I18n.t("wifi_title"))
        self.geometry("380x320")
        self.resizable(False, False)

        self.transient(parent)
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        self.geometry(f"+{max(0, px + (pw // 2) - 190)}+{max(0, py + (ph // 2) - 160)}")
        self.grab_set()

        self.bind("<Return>", lambda e: self.handle_action())
        self.bind("<Escape>", lambda e: self.destroy())

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 10))
        
        ctk.CTkLabel(
            header, text=I18n.t("wifi_title"),
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        ).pack(anchor="w")

        self.mode_var = ctk.StringVar(value=I18n.t("wifi_tab_connect"))
        self.segmented = ctk.CTkSegmentedButton(
            self, values=[I18n.t("wifi_tab_connect"), I18n.t("wifi_tab_pair")],
            variable=self.mode_var, height=30,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.switch_mode
        )
        self.segmented.pack(fill="x", padx=20, pady=(0, 12))

        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.pack(fill="both", expand=True, padx=20)

        self.lbl_ip = ctk.CTkLabel(self.form_frame, text=I18n.t("wifi_lbl_target"), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#334155", "#CBD5E1"))
        self.lbl_ip.pack(anchor="w", pady=(0, 2))
        
        self.entry_ip = ctk.CTkEntry(self.form_frame, placeholder_text="192.168.18.9:40275", height=34, font=ctk.CTkFont(family="Segoe UI", size=12))
        self.entry_ip.pack(fill="x", pady=(0, 8))
        self.entry_ip.bind("<Return>", lambda e: self.handle_action())

        self.lbl_code = ctk.CTkLabel(self.form_frame, text=I18n.t("wifi_lbl_code"), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#334155", "#CBD5E1"))
        self.entry_code = ctk.CTkEntry(self.form_frame, placeholder_text="849201", height=34, font=ctk.CTkFont(family="Segoe UI", size=12))
        self.entry_code.bind("<Return>", lambda e: self.handle_action())

        self.btn_action = ctk.CTkButton(
            self.form_frame, text=I18n.t("wifi_btn_connect"),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#059669", hover_color="#047857", height=36, command=self.handle_action
        )
        self.btn_action.pack(fill="x", pady=(8, 4))

        self.lbl_status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=("#64748B", "#94A3B8"))
        self.lbl_status.pack(pady=(2, 8))

        self.after(100, lambda: self.entry_ip.focus_set())

    def switch_mode(self, value):
        self.lbl_status.configure(text="")
        if value == I18n.t("wifi_tab_pair"):
            self.entry_ip.configure(placeholder_text="192.168.18.9:37123")
            self.lbl_code.pack(anchor="w", pady=(0, 2), before=self.btn_action)
            self.entry_code.pack(fill="x", pady=(0, 8), before=self.btn_action)
            self.btn_action.configure(text=I18n.t("wifi_btn_pair"), fg_color="#2563EB", hover_color="#1D4ED8")
            self.entry_ip.focus_set()
        else:
            self.entry_ip.configure(placeholder_text="192.168.18.9:40275")
            self.lbl_code.pack_forget()
            self.entry_code.pack_forget()
            self.btn_action.configure(text=I18n.t("wifi_btn_connect"), fg_color="#059669", hover_color="#047857")
            self.entry_ip.focus_set()

    def handle_action(self):
        target = self.entry_ip.get().strip()
        mode = self.mode_var.get()

        if not target:
            self.lbl_status.configure(text=I18n.t("wifi_err_target"))
            play_modal_blocked_sound()
            return

        self.btn_action.configure(state="disabled")

        if mode == I18n.t("wifi_tab_pair"):
            code = self.entry_code.get().strip()
            if not code:
                self.lbl_status.configure(text=I18n.t("wifi_err_code"))
                self.btn_action.configure(state="normal")
                self.entry_code.focus_set()
                play_modal_blocked_sound()
                return
            self.lbl_status.configure(text=I18n.t("wifi_status_pairing"))
            threading.Thread(target=self._pair_worker, args=(target, code), daemon=True).start()
        else:
            self.lbl_status.configure(text=I18n.t("wifi_status_connecting"))
            threading.Thread(target=self._conn_worker, args=(target,), daemon=True).start()

    def _pair_worker(self, target, code):
        success, msg = self.adb.pair_wireless(target, code)
        self.after(0, lambda: self._on_pair_done(success, msg))

    def _on_pair_done(self, success, msg):
        self.btn_action.configure(state="normal")
        self.lbl_status.configure(text=msg)
        if success:
            self.segmented.set(I18n.t("wifi_tab_connect"))
            self.switch_mode(I18n.t("wifi_tab_connect"))
            self.lbl_status.configure(text=I18n.t("wifi_pair_success"))
            self.entry_ip.focus_set()
        else:
            play_modal_blocked_sound()

    def _conn_worker(self, target):
        success, msg = self.adb.connect_wireless(target)
        self.after(0, lambda: self._on_conn_done(success, msg))

    def _on_conn_done(self, success, msg):
        self.btn_action.configure(state="normal")
        self.lbl_status.configure(text=msg)
        if success:
            if self.on_success:
                self.on_success()
            self.after(800, self.destroy)
        else:
            play_modal_blocked_sound()

    def destroy(self):
        global _active_wifi_dialog
        _active_wifi_dialog = None
        try:
            self.grab_release()
        except Exception:
            pass
        super().destroy()
