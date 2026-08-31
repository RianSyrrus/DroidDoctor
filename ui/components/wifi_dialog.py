import customtkinter as ctk
import threading
import winsound
import time
import os
from typing import Optional, List, Dict
from core.i18n import I18n
from core.settings_manager import SettingsManager
from core.qr_engine import QREngine
from core.qr_listener import QRPairingListener
from core.wireless_scanner import WirelessScanner
from core.device_bookmarks import DeviceBookmarks

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
    """
    Modern 3-in-1 Wireless ADB Connection Suite:
    1. Real-Time QR Code Camera Pairing with High-Frequency Background Handshake Daemon
    2. Smart Auto-Discovery with Inline 6-Digit PIN Pairing & 1-Click Connect
    3. Manual Pairing Code & Saved Device Profiles (Bookmarks)
    """
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
        self.qr_listener = QRPairingListener(self.adb.adb_bin)
        self._current_pairing_pin = ""

        self.title(I18n.t("wifi_title"))
        self.geometry("480x560")
        self.resizable(False, False)

        self.transient(parent)
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        self.geometry(f"+{max(0, px + (pw // 2) - 240)}+{max(0, py + (ph // 2) - 280)}")
        self.grab_set()

        self.bind("<Escape>", lambda e: self.destroy())

        # Header Frame
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(14, 6))
        
        ctk.CTkLabel(
            header, text=I18n.t("wifi_title"),
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        ).pack(anchor="w")

        # 3-Tab Segmented Button
        self.tab_qr = I18n.t("wifi_tab_qr")
        self.tab_discover = I18n.t("wifi_tab_discover")
        self.tab_manual = I18n.t("wifi_tab_manual")

        self.active_tab_var = ctk.StringVar(value=self.tab_qr)
        self.segmented = ctk.CTkSegmentedButton(
            self, values=[self.tab_qr, self.tab_discover, self.tab_manual],
            variable=self.active_tab_var, height=32,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.switch_tab
        )
        self.segmented.pack(fill="x", padx=20, pady=(0, 8))

        # Content Container Frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20)

        # Status Label Bar at Bottom
        self.lbl_status = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("#64748B", "#94A3B8"), wraplength=440
        )
        self.lbl_status.pack(pady=(2, 8), padx=20)

        # Initialize view (QR Code Tab Default)
        self.render_qr_tab()

    def clear_content(self):
        self.qr_listener.stop()
        for w in self.content_frame.winfo_children():
            w.destroy()
        self.lbl_status.configure(text="")

    def switch_tab(self, value):
        self.clear_content()
        if value == self.tab_qr:
            self.render_qr_tab()
        elif value == self.tab_discover:
            self.render_discover_tab()
        else:
            self.render_manual_tab()

    # =========================================================================
    # TAB 1: 📷 QR CODE PAIRING (REAL-TIME DAEMON HANDSHAKE)
    # =========================================================================
    def render_qr_tab(self):
        desc_lbl = ctk.CTkLabel(
            self.content_frame, text=I18n.t("wifi_qr_instruction"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("#475569", "#94A3B8"), wraplength=440, justify="center"
        )
        desc_lbl.pack(pady=(0, 4))

        payload, srv_name, pin = QREngine.create_adb_pairing_payload()
        local_ip = QREngine.get_local_ip()
        self._current_pairing_pin = pin

        qr_pil = QREngine.generate_qr_image(payload, size=160, bg_color="#FFFFFF", fg_color="#0F172A")
        self.qr_ctk_img = ctk.CTkImage(light_image=qr_pil, dark_image=qr_pil, size=(160, 160))

        qr_box = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF", corner_radius=12, width=172, height=172)
        qr_box.pack(pady=2)
        qr_box.pack_propagate(False)

        self.qr_label = ctk.CTkLabel(qr_box, image=self.qr_ctk_img, text="")
        self.qr_label.pack(expand=True)

        pin_info_txt = I18n.t("wifi_qr_pin_info", pin=pin, ip=local_ip)
        self.pin_lbl = ctk.CTkLabel(
            self.content_frame, text=pin_info_txt,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#2563EB", "#60A5FA")
        )
        self.pin_lbl.pack(pady=(4, 2))

        tip_lbl = ctk.CTkLabel(
            self.content_frame, text=I18n.t("wifi_qr_tip"),
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=("#64748B", "#94A3B8"), wraplength=440, justify="center"
        )
        tip_lbl.pack(pady=(0, 4))

        btn_row = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_row.pack(pady=(2, 0))

        btn_refresh = ctk.CTkButton(
            btn_row, text=I18n.t("wifi_btn_refresh_qr"),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#334155", hover_color="#475569", height=30, width=130,
            command=self.refresh_qr_code
        )
        btn_refresh.pack(side="left", padx=4)

        btn_switch_pin = ctk.CTkButton(
            btn_row, text=I18n.t("wifi_btn_use_pin_tab"),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#2563EB", hover_color="#1D4ED8", height=30,
            command=lambda: self.switch_to_tab(self.tab_discover)
        )
        btn_switch_pin.pack(side="left", padx=4)

        self.lbl_status.configure(text=I18n.t("wifi_qr_listening"))
        
        # Start the background pairing daemon
        self.qr_listener.start(
            pin=pin,
            on_pair=lambda target: self.after(0, lambda: self._on_qr_pair_success(target)),
            on_connect=lambda target: self.after(0, lambda: self._on_qr_connect_success(target)),
            on_status=lambda msg: self.after(0, lambda: self.lbl_status.configure(text=msg))
        )

    def _on_qr_pair_success(self, target: str):
        self.lbl_status.configure(text=I18n.t("wifi_pair_success"))

    def _on_qr_connect_success(self, target: str):
        self.lbl_status.configure(text=I18n.t("wifi_qr_auto_connected"))
        if ":" in target:
            ip, port = target.split(":", 1)
            DeviceBookmarks.save_bookmark(ip, last_port=port)
        if self.on_success:
            self.on_success()
        self.after(800, self.destroy)

    def switch_to_tab(self, tab_name):
        self.segmented.set(tab_name)
        self.switch_tab(tab_name)

    def refresh_qr_code(self):
        payload, srv_name, pin = QREngine.create_adb_pairing_payload()
        local_ip = QREngine.get_local_ip()
        self._current_pairing_pin = pin
        self.qr_listener.update_pin(pin)
        
        qr_pil = QREngine.generate_qr_image(payload, size=160, bg_color="#FFFFFF", fg_color="#0F172A")
        self.qr_ctk_img = ctk.CTkImage(light_image=qr_pil, dark_image=qr_pil, size=(160, 160))
        if hasattr(self, 'qr_label') and self.qr_label.winfo_exists():
            self.qr_label.configure(image=self.qr_ctk_img)
        if hasattr(self, 'pin_lbl') and self.pin_lbl.winfo_exists():
            self.pin_lbl.configure(text=I18n.t("wifi_qr_pin_info", pin=pin, ip=local_ip))

    # =========================================================================
    # TAB 2: 🔍 AUTO-DISCOVERY (SMART SCANNER & INLINE PAIRING)
    # =========================================================================
    def render_discover_tab(self):
        top_bar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 6))

        local_ip = QREngine.get_local_ip()
        subnet_prefix = ".".join(local_ip.split(".")[:3]) + "." if "." in local_ip else "192.168.1."

        self.entry_scan_ip = ctk.CTkEntry(
            top_bar, placeholder_text=f"{subnet_prefix}...", height=34,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.entry_scan_ip.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_scan = ctk.CTkButton(
            top_bar, text=I18n.t("wifi_btn_scan_network"),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#2563EB", hover_color="#1D4ED8", height=34, width=150,
            command=self.start_network_scan
        )
        self.btn_scan.pack(side="right")

        guide_lbl = ctk.CTkLabel(
            self.content_frame, text=I18n.t("wifi_pin_guide"),
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=("#475569", "#94A3B8"), justify="left"
        )
        guide_lbl.pack(anchor="w", pady=(0, 4))

        self.results_scroll = ctk.CTkScrollableFrame(
            self.content_frame, fg_color=("#F1F5F9", "#1E293B"),
            corner_radius=10, height=310
        )
        self.results_scroll.pack(fill="both", expand=True, pady=2)

        # Initial auto-scan on open
        self.after(100, self.start_network_scan)

    def start_network_scan(self):
        self.lbl_status.configure(text=I18n.t("wifi_scanning_network"))
        self.btn_scan.configure(state="disabled")
        for w in self.results_scroll.winfo_children():
            w.destroy()

        target_ip = self.entry_scan_ip.get().strip()
        threading.Thread(target=self._scan_worker, args=(target_ip,), daemon=True).start()

    def _scan_worker(self, target_ip: str):
        endpoints = []
        
        # 1. mDNS Discovery
        mdns_items = WirelessScanner.parse_mdns_services(self.adb.adb_bin)
        for m in mdns_items:
            is_pair = "_adb-tls-pairing" in m.get("type", "")
            endpoints.append({
                "target": m["target"],
                "name": m["service"],
                "is_pairing": is_pair,
                "source": I18n.t("wifi_tag_pairing") if is_pair else I18n.t("wifi_tag_connect")
            })

        # 2. If IP is specified, probe ports 37000-45000 + 5555
        if target_ip:
            open_ports = WirelessScanner.scan_target_ports(target_ip)
            for p in open_ports:
                target_str = f"{target_ip}:{p}"
                if not any(e["target"] == target_str for e in endpoints):
                    endpoints.append({
                        "target": target_str,
                        "name": f"Device {target_ip}",
                        "is_pairing": False,
                        "source": f"Port {p} Open"
                    })

        self.after(0, lambda: self._on_scan_done(endpoints))

    def _on_scan_done(self, endpoints: List[Dict[str, any]]):
        self.btn_scan.configure(state="normal")
        for w in self.results_scroll.winfo_children():
            w.destroy()

        if not endpoints:
            self.lbl_status.configure(text=I18n.t("wifi_scan_no_devices"))
            empty_lbl = ctk.CTkLabel(
                self.results_scroll, text=I18n.t("wifi_scan_no_devices"),
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=("#94A3B8", "#64748B"), justify="center"
            )
            empty_lbl.pack(pady=40)
            return

        self.lbl_status.configure(text=I18n.t("wifi_scan_found_count", count=len(endpoints)))
        for ep in endpoints:
            card = ctk.CTkFrame(self.results_scroll, fg_color=("#E2E8F0", "#0F172A"), corner_radius=8)
            card.pack(fill="x", padx=6, pady=4)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)

            badge_color = "#2563EB" if ep["is_pairing"] else "#059669"
            ctk.CTkLabel(
                info_frame, text=ep["name"],
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=("#0F172A", "#F8FAFC")
            ).pack(anchor="w")

            ctk.CTkLabel(
                info_frame, text=f"{ep['target']}  •  {ep['source']}",
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold" if ep["is_pairing"] else "normal"),
                text_color=badge_color
            ).pack(anchor="w")

            action_frame = ctk.CTkFrame(card, fg_color="transparent")
            action_frame.pack(side="right", padx=10, pady=8)

            if ep["is_pairing"]:
                # Inline PIN input for pairing endpoint
                entry_pin = ctk.CTkEntry(
                    action_frame, placeholder_text="PIN 6-digit", width=85, height=30,
                    font=ctk.CTkFont(family="Segoe UI", size=11)
                )
                entry_pin.pack(side="left", padx=(0, 6))

                btn_pair = ctk.CTkButton(
                    action_frame, text=I18n.t("wifi_btn_pair_now"), width=75, height=30,
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    fg_color="#2563EB", hover_color="#1D4ED8",
                    command=lambda t=ep["target"], e=entry_pin: self._handle_inline_pair(t, e)
                )
                btn_pair.pack(side="left")
            else:
                btn_conn = ctk.CTkButton(
                    action_frame, text=I18n.t("wifi_btn_connect_now"), width=75, height=30,
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    fg_color="#059669", hover_color="#047857",
                    command=lambda t=ep["target"]: self.connect_target(t)
                )
                btn_conn.pack(side="left")

    def _handle_inline_pair(self, target: str, entry_pin_widget: ctk.CTkEntry):
        code = entry_pin_widget.get().strip()
        if not code:
            self.lbl_status.configure(text=I18n.t("wifi_err_code"))
            play_modal_blocked_sound()
            entry_pin_widget.focus_set()
            return
        
        self.lbl_status.configure(text=I18n.t("wifi_status_pairing"))
        threading.Thread(target=self._pair_worker, args=(target, code), daemon=True).start()

    # =========================================================================
    # TAB 3: ⭐ MANUAL & BOOKMARKS
    # =========================================================================
    def render_manual_tab(self):
        input_box = ctk.CTkFrame(self.content_frame, fg_color=("#F1F5F9", "#1E293B"), corner_radius=10)
        input_box.pack(fill="x", pady=(0, 8), padx=2, ipady=4)

        # Mode Segmented (Connect vs Pair)
        self.sub_mode_var = ctk.StringVar(value=I18n.t("wifi_tab_connect"))
        sub_seg = ctk.CTkSegmentedButton(
            input_box, values=[I18n.t("wifi_tab_connect"), I18n.t("wifi_tab_pair")],
            variable=self.sub_mode_var, height=26,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            command=self.switch_sub_mode
        )
        sub_seg.pack(fill="x", padx=10, pady=(4, 6))

        self.lbl_ip = ctk.CTkLabel(input_box, text=I18n.t("wifi_lbl_target"), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#334155", "#CBD5E1"))
        self.lbl_ip.pack(anchor="w", padx=10, pady=(0, 2))

        self.entry_ip = ctk.CTkEntry(input_box, placeholder_text="192.168.1.100:40275", height=32, font=ctk.CTkFont(family="Segoe UI", size=11))
        self.entry_ip.pack(fill="x", padx=10, pady=(0, 4))

        self.lbl_code = ctk.CTkLabel(input_box, text=I18n.t("wifi_lbl_code"), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#334155", "#CBD5E1"))
        self.entry_code = ctk.CTkEntry(input_box, placeholder_text="849201", height=32, font=ctk.CTkFont(family="Segoe UI", size=11))

        self.btn_manual_action = ctk.CTkButton(
            input_box, text=I18n.t("wifi_btn_connect"),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#059669", hover_color="#047857", height=32,
            command=self.handle_manual_action
        )
        self.btn_manual_action.pack(fill="x", padx=10, pady=(4, 4))

        # Bookmarks Section
        ctk.CTkLabel(
            self.content_frame, text=I18n.t("wifi_bookmarks_title"),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#334155", "#CBD5E1")
        ).pack(anchor="w", pady=(2, 2))

        self.bookmarks_scroll = ctk.CTkScrollableFrame(
            self.content_frame, fg_color=("#F1F5F9", "#1E293B"),
            corner_radius=8, height=130
        )
        self.bookmarks_scroll.pack(fill="both", expand=True, pady=(2, 0))
        self.refresh_bookmarks_list()

    def switch_sub_mode(self, value):
        if value == I18n.t("wifi_tab_pair"):
            self.entry_ip.configure(placeholder_text="192.168.1.100:37123")
            self.lbl_code.pack(anchor="w", padx=10, pady=(0, 2), before=self.btn_manual_action)
            self.entry_code.pack(fill="x", padx=10, pady=(0, 4), before=self.btn_manual_action)
            self.btn_manual_action.configure(text=I18n.t("wifi_btn_pair"), fg_color="#2563EB", hover_color="#1D4ED8")
        else:
            self.entry_ip.configure(placeholder_text="192.168.1.100:40275")
            self.lbl_code.pack_forget()
            self.entry_code.pack_forget()
            self.btn_manual_action.configure(text=I18n.t("wifi_btn_connect"), fg_color="#059669", hover_color="#047857")

    def handle_manual_action(self):
        target = self.entry_ip.get().strip()
        mode = self.sub_mode_var.get()

        if not target:
            self.lbl_status.configure(text=I18n.t("wifi_err_target"))
            play_modal_blocked_sound()
            return

        self.btn_manual_action.configure(state="disabled")

        if mode == I18n.t("wifi_tab_pair"):
            code = self.entry_code.get().strip()
            if not code:
                self.lbl_status.configure(text=I18n.t("wifi_err_code"))
                self.btn_manual_action.configure(state="normal")
                play_modal_blocked_sound()
                return
            self.lbl_status.configure(text=I18n.t("wifi_status_pairing"))
            threading.Thread(target=self._pair_worker, args=(target, code), daemon=True).start()
        else:
            self.connect_target(target)

    def refresh_bookmarks_list(self):
        for w in self.bookmarks_scroll.winfo_children():
            w.destroy()

        bookmarks = DeviceBookmarks.get_all()
        if not bookmarks:
            empty_lbl = ctk.CTkLabel(
                self.bookmarks_scroll, text="No saved devices yet.",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=("#94A3B8", "#64748B")
            )
            empty_lbl.pack(pady=15)
            return

        for b in bookmarks:
            ip = b.get("ip", "")
            alias = b.get("alias", ip)
            port = b.get("last_port", "5555")
            target = f"{ip}:{port}"

            b_card = ctk.CTkFrame(self.bookmarks_scroll, fg_color=("#E2E8F0", "#0F172A"), corner_radius=6)
            b_card.pack(fill="x", padx=4, pady=2)

            info = ctk.CTkFrame(b_card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=8, pady=4)

            ctk.CTkLabel(
                info, text=alias,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=("#0F172A", "#F8FAFC")
            ).pack(anchor="w")

            ctk.CTkLabel(
                info, text=target,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=("#64748B", "#94A3B8")
            ).pack(anchor="w")

            btn_del = ctk.CTkButton(
                b_card, text="✕", width=26, height=24,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                fg_color="#EF4444", hover_color="#DC2626",
                command=lambda target_ip=ip: self.delete_bookmark(target_ip)
            )
            btn_del.pack(side="right", padx=(4, 6), pady=4)

            btn_conn = ctk.CTkButton(
                b_card, text=I18n.t("wifi_btn_connect_now"), width=60, height=24,
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                fg_color="#059669", hover_color="#047857",
                command=lambda t=target: self.connect_target(t)
            )
            btn_conn.pack(side="right", padx=2, pady=4)

    def delete_bookmark(self, ip: str):
        DeviceBookmarks.remove(ip)
        self.refresh_bookmarks_list()

    # =========================================================================
    # COMMON CONNECTION WORKERS
    # =========================================================================
    def connect_target(self, target: str):
        self.lbl_status.configure(text=I18n.t("wifi_status_connecting"))
        threading.Thread(target=self._conn_worker, args=(target,), daemon=True).start()

    def _conn_worker(self, target: str):
        success, msg = self.adb.connect_wireless(target)
        
        # Auto-bookmark on successful connection
        if success and ":" in target:
            ip, port = target.split(":", 1)
            DeviceBookmarks.save_bookmark(ip, last_port=port)

        self.after(0, lambda: self._on_conn_done(success, msg))

    def _on_conn_done(self, success: bool, msg: str):
        if hasattr(self, 'btn_manual_action'):
            self.btn_manual_action.configure(state="normal")
        self.lbl_status.configure(text=msg)
        if success:
            if self.on_success:
                self.on_success()
            self.after(800, self.destroy)
        else:
            play_modal_blocked_sound()

    def _pair_worker(self, target: str, code: str):
        success, msg = self.adb.pair_wireless(target, code)
        self.after(0, lambda: self._on_pair_done(success, msg, target))

    def _on_pair_done(self, success: bool, msg: str, target: str):
        if hasattr(self, 'btn_manual_action'):
            self.btn_manual_action.configure(state="normal")
        self.lbl_status.configure(text=msg)
        if success:
            self.lbl_status.configure(text=I18n.t("wifi_pair_then_connect"))
            # If target was IP:PairingPort, auto connect to connection port
            ip = target.split(":")[0] if ":" in target else target
            self.after(600, lambda: self._auto_connect_after_pair(ip))
        else:
            play_modal_blocked_sound()

    def _auto_connect_after_pair(self, ip: str):
        best_target = WirelessScanner.auto_discover_best_target(ip, self.adb.adb_bin)
        if best_target:
            self.connect_target(best_target)
        else:
            self.start_network_scan()

    def destroy(self):
        self.qr_listener.stop()
        global _active_wifi_dialog
        _active_wifi_dialog = None
        try:
            self.grab_release()
        except Exception:
            pass
        super().destroy()
