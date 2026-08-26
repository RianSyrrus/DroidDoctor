import customtkinter as ctk
from tkinter import filedialog
import subprocess, os, sys, threading, time
from datetime import datetime
from core.i18n import I18n
from core.settings_manager import SettingsManager

def get_default_recordings_dir() -> str:
    """
    Resolves a valid persistent destination folder for saved screenshots and screen recordings.

    Returns:
        str: Absolute directory path.
    """
    settings = SettingsManager.get_instance()
    saved = settings.get("recording_directory")
    if saved and os.path.exists(saved):
        return saved

    base_proj = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates = [
        os.path.join(base_proj, "recordings"),
        os.path.join(os.path.expanduser("~"), "Desktop", "DroidDoctor Recordings"),
        os.path.join(os.environ.get("USERPROFILE", "C:\\"), "Desktop", "DroidDoctor Recordings")
    ]
    for c in candidates:
        try:
            os.makedirs(c, exist_ok=True)
            if os.path.exists(c):
                settings.set("recording_directory", c)
                return c
        except Exception:
            continue
    fallback = os.path.abspath("recordings")
    settings.set("recording_directory", fallback)
    return fallback

class MirrorTab(ctk.CTkFrame):
    """
    Low-latency Android screen mirroring, HID physical keyboard injection,
    hardware screenshot capture, and MP4 screen recording studio powered by Scrcpy.
    """
    def __init__(self, master, adb_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.adb = adb_manager
        self.settings = SettingsManager.get_instance()
        self.scrcpy_process = None
        self.adb_record_proc = None
        self.is_recording = False
        self.record_start_time = 0

        self.save_dir = get_default_recordings_dir()

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header Toolbar
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=(4, 6))

        ctk.CTkLabel(
            top_bar, text=I18n.t("mirror_title"),
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        ).pack(side="left")

        # Left Column Container
        left_col = ctk.CTkFrame(self, fg_color="transparent")
        left_col.grid(row=1, column=0, sticky="nsew", padx=6, pady=2)
        left_col.grid_columnconfigure(0, weight=1)
        left_col.grid_rowconfigure((0, 1), weight=1)

        # Card 1: Mirror Configuration
        card_mirror = ctk.CTkFrame(left_col, corner_radius=14, fg_color=("#FFFFFF", "#111827"), border_width=1, border_color=("#E2E8F0", "#1E293B"))
        card_mirror.grid(row=0, column=0, sticky="nsew", pady=(0, 6))

        ctk.CTkLabel(
            card_mirror, text=I18n.t("mirror_setting_title"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=("#2563EB", "#60A5FA")
        ).pack(anchor="w", padx=16, pady=(12, 8))

        # Resolution & FPS Grid
        opt_grid = ctk.CTkFrame(card_mirror, fg_color="transparent")
        opt_grid.pack(fill="x", padx=16, pady=(0, 6))
        opt_grid.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(opt_grid, text=I18n.t("mirror_resolution"), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#334155", "#CBD5E1")).grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.opt_res = ctk.CTkOptionMenu(opt_grid, values=["1080p", "720p", "Auto"], height=32)
        saved_res = self.settings.get("mirror_resolution", "1080p")
        self.opt_res.set(saved_res)
        self.opt_res.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(opt_grid, text=I18n.t("mirror_max_fps"), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#334155", "#CBD5E1")).grid(row=0, column=1, sticky="w", pady=(0, 2))
        self.opt_fps = ctk.CTkOptionMenu(opt_grid, values=["60 FPS", "30 FPS"], height=32)
        self.opt_fps.set("60 FPS")
        self.opt_fps.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        # Vertically Stacked Feature Switches
        self.sw_top = ctk.CTkSwitch(card_mirror, text=I18n.t("mirror_always_on_top"), font=ctk.CTkFont(family="Segoe UI", size=11))
        self.sw_top.pack(anchor="w", padx=16, pady=2)

        self.sw_screen_off = ctk.CTkSwitch(card_mirror, text=I18n.t("mirror_turn_screen_off"), font=ctk.CTkFont(family="Segoe UI", size=11))
        if self.settings.get("mirror_auto_turn_off", False):
            self.sw_screen_off.select()
        self.sw_screen_off.pack(anchor="w", padx=16, pady=2)

        self.sw_uhid = ctk.CTkSwitch(card_mirror, text=I18n.t("mirror_uhid_keyboard"), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=("#2563EB", "#60A5FA"))
        self.sw_uhid.select()
        self.sw_uhid.pack(anchor="w", padx=16, pady=2)

        # Mirror Action Buttons Grid
        btn_grid = ctk.CTkFrame(card_mirror, fg_color="transparent")
        btn_grid.pack(fill="x", padx=16, pady=(6, 12))
        btn_grid.grid_columnconfigure((0, 1), weight=1)

        self.btn_start = ctk.CTkButton(
            btn_grid, text=I18n.t("mirror_btn_start"), height=36, corner_radius=8,
            fg_color="#2563EB", hover_color="#1D4ED8", text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.start_mirror
        )
        self.btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.btn_stop = ctk.CTkButton(
            btn_grid, text=I18n.t("mirror_btn_stop"), height=36, corner_radius=8,
            fg_color=("#E2E8F0", "#1E293B"), hover_color=("#CBD5E1", "#334155"), text_color=("#475569", "#CBD5E1"),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), state="disabled",
            command=self.stop_mirror
        )
        self.btn_stop.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # Card 2: Dedicated Media Capture & Recording Studio Card
        card_media = ctk.CTkFrame(left_col, corner_radius=14, fg_color=("#FFFFFF", "#111827"), border_width=1, border_color=("#E2E8F0", "#1E293B"))
        card_media.grid(row=1, column=0, sticky="nsew", pady=(6, 0))

        ctk.CTkLabel(
            card_media, text="📹 " + I18n.t("mirror_media_studio_title"),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        ).pack(anchor="w", padx=16, pady=(10, 6))

        # Capture & Record Buttons Row
        cap_row = ctk.CTkFrame(card_media, fg_color="transparent")
        cap_row.pack(fill="x", padx=16, pady=(0, 6))
        cap_row.grid_columnconfigure((0, 1), weight=1)

        self.btn_screenshot = ctk.CTkButton(
            cap_row, text="📸 " + I18n.t("mirror_btn_screenshot"), height=34, corner_radius=8,
            fg_color=("#F1F5F9", "#1E293B"), hover_color=("#E2E8F0", "#334155"), text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.take_screenshot
        )
        self.btn_screenshot.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.btn_record = ctk.CTkButton(
            cap_row, text="🔴 " + I18n.t("mirror_btn_record_start"), height=34, corner_radius=8,
            fg_color="#DC2626", hover_color="#B91C1C", text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.toggle_on_demand_recording
        )
        self.btn_record.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # Save Directory Box with Browse & Open
        dir_box = ctk.CTkFrame(card_media, fg_color=("#F8FAFC", "#0E1422"), corner_radius=8, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        dir_box.pack(fill="x", padx=16, pady=(0, 8))

        disp_path = os.path.basename(self.save_dir) if len(self.save_dir) > 35 else self.save_dir
        self.lbl_save_dir = ctk.CTkLabel(
            dir_box, text=f"📁 {I18n.t('mirror_rec_location')} {disp_path}",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=("#64748B", "#94A3B8"), justify="left"
        )
        self.lbl_save_dir.pack(anchor="w", padx=10, pady=(6, 4))

        dir_btns = ctk.CTkFrame(dir_box, fg_color="transparent")
        dir_btns.pack(fill="x", padx=10, pady=(0, 6))
        dir_btns.grid_columnconfigure((0, 1), weight=1)

        self.btn_open_folder = ctk.CTkButton(
            dir_btns, text=I18n.t("mirror_btn_open_folder"), height=26, corner_radius=6,
            fg_color=("#EFF6FF", "#1E293B"), hover_color=("#DBEAFE", "#334155"), text_color=("#2563EB", "#60A5FA"),
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            command=self.open_recordings_folder
        )
        self.btn_open_folder.grid(row=0, column=0, sticky="ew", padx=(0, 3))

        self.btn_change_dir = ctk.CTkButton(
            dir_btns, text=I18n.t("mirror_btn_change_folder"), height=26, corner_radius=6,
            fg_color=("#F1F5F9", "#1E293B"), hover_color=("#E2E8F0", "#334155"), text_color=("#475569", "#CBD5E1"),
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            command=self.change_save_directory
        )
        self.btn_change_dir.grid(row=0, column=1, sticky="ew", padx=(3, 0))

        # Status Label
        self.lbl_media_status = ctk.CTkLabel(
            card_media, text="",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=("#059669", "#10B981")
        )
        self.lbl_media_status.pack(anchor="w", padx=16, pady=(0, 6))

        # 3. Right Column: Unified Full-Height Navigation Card
        right_col = ctk.CTkFrame(self, fg_color="transparent")
        right_col.grid(row=1, column=1, sticky="nsew", padx=6, pady=2)
        right_col.grid_columnconfigure(0, weight=1)
        right_col.grid_rowconfigure(0, weight=1)

        nav_card = ctk.CTkFrame(right_col, corner_radius=14, fg_color=("#FFFFFF", "#111827"), border_width=1, border_color=("#E2E8F0", "#1E293B"))
        nav_card.grid(row=0, column=0, sticky="nsew", pady=(0, 0))

        ctk.CTkLabel(
            nav_card, text=I18n.t("mirror_nav_shortcuts"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        ).pack(anchor="w", padx=18, pady=(16, 12))

        # 6 Primary Navigation Buttons
        grid_btn = ctk.CTkFrame(nav_card, fg_color="transparent")
        grid_btn.pack(fill="x", padx=16, pady=(0, 14))
        grid_btn.grid_columnconfigure((0, 1, 2), weight=1)

        self._create_key_btn(grid_btn, 0, 0, I18n.t("mirror_btn_home"), 3)
        self._create_key_btn(grid_btn, 0, 1, I18n.t("mirror_btn_back"), 4)
        self._create_key_btn(grid_btn, 0, 2, I18n.t("mirror_btn_recents"), 187)
        self._create_key_btn(grid_btn, 1, 0, I18n.t("mirror_btn_power"), 26)
        self._create_key_btn(grid_btn, 1, 1, I18n.t("mirror_btn_vol_up"), 24)
        self._create_key_btn(grid_btn, 1, 2, I18n.t("mirror_btn_vol_down"), 25)

        # Quick Android System Controls (Notification Shade & Mute)
        extra_box = ctk.CTkFrame(nav_card, fg_color=("#F8FAFC", "#0E1422"), corner_radius=10, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        extra_box.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkLabel(
            extra_box, text="⚡ Quick Device Controls",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#2563EB", "#60A5FA")
        ).pack(anchor="w", padx=12, pady=(8, 6))

        extra_grid = ctk.CTkFrame(extra_box, fg_color="transparent")
        extra_grid.pack(fill="x", padx=8, pady=(0, 8))
        extra_grid.grid_columnconfigure((0, 1), weight=1)

        btn_notif = ctk.CTkButton(
            extra_grid, text="🔔 Notifications", height=32, corner_radius=6,
            fg_color=("#FFFFFF", "#1E293B"), hover_color=("#F1F5F9", "#334155"), text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=lambda: self.adb.shell("cmd statusbar expand-notifications")
        )
        btn_notif.grid(row=0, column=0, sticky="ew", padx=3)

        btn_qs = ctk.CTkButton(
            extra_grid, text="⚙️ Quick Settings", height=32, corner_radius=6,
            fg_color=("#FFFFFF", "#1E293B"), hover_color=("#F1F5F9", "#334155"), text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=lambda: self.adb.shell("cmd statusbar expand-settings")
        )
        btn_qs.grid(row=0, column=1, sticky="ew", padx=3)

        # Stay Awake Switch
        self.sw_stay_awake = ctk.CTkSwitch(
            nav_card, text=I18n.t("mirror_stay_awake"), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
            command=self.toggle_stay_awake
        )
        self.sw_stay_awake.pack(anchor="w", padx=18, pady=(4, 2))

        self.lbl_stay_awake_desc = ctk.CTkLabel(
            nav_card, text=I18n.t("mirror_stay_awake_desc"),
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=("#64748B", "#94A3B8"), justify="left", wraplength=280
        )
        self.lbl_stay_awake_desc.pack(anchor="w", padx=18, pady=(0, 12))

        self._sync_stay_awake_state()

    def _create_key_btn(self, parent, row: int, col: int, label: str, keycode: int):
        btn = ctk.CTkButton(
            parent, text=label, height=38, corner_radius=8,
            fg_color=("#F1F5F9", "#1E293B"), hover_color=("#E2E8F0", "#334155"), text_color=("#334155", "#E2E8F0"),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=lambda: self.adb.shell(f"input keyevent {keycode}")
        )
        btn.grid(row=row, column=col, padx=3, pady=3, sticky="ew")

    def _sync_stay_awake_state(self):
        def _check():
            val = self.adb.shell("settings get global stay_on_while_plugged_in").strip()
            if val in ["3", "7"]:
                self.after(0, self.sw_stay_awake.select)
            else:
                self.after(0, self.sw_stay_awake.deselect)
        threading.Thread(target=_check, daemon=True).start()

    def toggle_stay_awake(self):
        if self.sw_stay_awake.get() == 1:
            self.adb.shell("settings put global stay_on_while_plugged_in 7")
            self.adb.shell("svc power stayon true")
            print("[POWER] Stay Awake ON.")
        else:
            self.adb.shell("settings put global stay_on_while_plugged_in 0")
            self.adb.shell("svc power stayon false")
            print("[POWER] Stay Awake OFF.")

    def open_recordings_folder(self):
        try:
            os.startfile(self.save_dir)
        except Exception:
            subprocess.Popen(f'explorer "{self.save_dir}"')

    def change_save_directory(self):
        chosen = filedialog.askdirectory(title=I18n.t("mirror_browse_title"), initialdir=self.save_dir)
        if chosen and os.path.exists(chosen):
            self.save_dir = chosen
            self.settings.set("recording_directory", chosen)
            disp_path = os.path.basename(chosen) if len(chosen) > 35 else chosen
            self.lbl_save_dir.configure(text=f"📁 {I18n.t('mirror_rec_location')} {disp_path}")
            print(f"[MEDIA] Custom save directory updated: {chosen}")

    def take_screenshot(self):
        """Mengambil screenshot langsung ke folder aktif."""
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Screenshot_{now_str}.png"
        target_path = os.path.join(self.save_dir, filename)

        self.btn_screenshot.configure(state="disabled")
        self.lbl_media_status.configure(text="📸 Capturing screenshot...", text_color=("#2563EB", "#60A5FA"))

        def _do_snap():
            success = self.adb.take_screenshot(target_path)
            def _update_ui():
                self.btn_screenshot.configure(state="normal")
                if success:
                    msg = I18n.t("mirror_screenshot_saved").format(filename=filename)
                    self.lbl_media_status.configure(text="✓ " + msg, text_color=("#059669", "#10B981"))
                    print(f"[SCREENSHOT] Saved: {target_path}")
                else:
                    self.lbl_media_status.configure(text="❌ Failed to capture screenshot", text_color=("#DC2626", "#F87171"))
            self.after(0, _update_ui)

        threading.Thread(target=_do_snap, daemon=True).start()

    def toggle_on_demand_recording(self):
        """Memulai atau menghentikan perekaman layar MP4 secara on-demand."""
        if not self.is_recording:
            # Mulai Rekam
            self.is_recording = True
            self.record_start_time = time.time()
            self.btn_record.configure(text="⏹️ " + I18n.t("mirror_btn_record_stop"), fg_color="#15803D", hover_color="#166534")
            
            # Start ADB screenrecord process
            self.adb_record_proc = self.adb.start_screen_record("/sdcard/temp_droid_rec.mp4")
            self._update_recording_timer()
            print("[RECORDING] On-Demand Screen recording started.")
        else:
            # Hentikan Rekam
            self.is_recording = False
            self.btn_record.configure(text="⏳ Finalizing...", state="disabled")
            
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Recording_{now_str}.mp4"
            target_path = os.path.join(self.save_dir, filename)

            def _do_stop():
                success = self.adb.stop_screen_record(self.adb_record_proc, target_path, "/sdcard/temp_droid_rec.mp4")
                self.adb_record_proc = None
                def _done_ui():
                    self.btn_record.configure(text="🔴 " + I18n.t("mirror_btn_record_start"), fg_color="#DC2626", hover_color="#B91C1C", state="normal")
                    if success:
                        msg = I18n.t("mirror_record_saved").format(filename=filename)
                        self.lbl_media_status.configure(text="✓ " + msg, text_color=("#059669", "#10B981"))
                        print(f"[RECORDING] Saved to PC: {target_path}")
                    else:
                        self.lbl_media_status.configure(text="❌ Failed to save video recording", text_color=("#DC2626", "#F87171"))
                self.after(0, _done_ui)

            threading.Thread(target=_do_stop, daemon=True).start()

    def _update_recording_timer(self):
        if self.is_recording:
            elapsed = int(time.time() - self.record_start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            time_str = f"{mins:02d}:{secs:02d}"
            msg = I18n.t("mirror_record_active_timer").format(time=time_str)
            self.lbl_media_status.configure(text="🔴 " + msg, text_color=("#DC2626", "#F87171"))
            self.after(1000, self._update_recording_timer)

    def start_mirror(self):
        from core.bin_manager import BinManager
        scrcpy_exe = BinManager.get_scrcpy_path()
        scrcpy_dir = BinManager.get_bin_dir()

        serial = self.adb.get_active_serial() if hasattr(self.adb, 'get_active_serial') else self.adb.current_serial
        args = [scrcpy_exe]
        if serial:
            args.extend(["-s", serial])

        res = self.opt_res.get()
        if res == "1080p":
            args.extend(["-m", "1080"])
        elif res == "720p":
            args.extend(["-m", "720"])

        fps = self.opt_fps.get()
        if "30" in fps:
            args.extend(["--max-fps", "30"])
        else:
            args.extend(["--max-fps", "60"])

        if self.sw_screen_off.get() == 1:
            args.append("--turn-screen-off")

        if self.sw_top.get() == 1:
            args.append("--always-on-top")

        if self.sw_uhid.get() == 1:
            args.append("--keyboard=uhid")

        CREATE_NO_WINDOW = 0x08000000 if sys.platform == 'win32' else 0
        try:
            self.scrcpy_process = subprocess.Popen(
                args,
                cwd=scrcpy_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )
            self.btn_start.configure(state="disabled", fg_color="#059669", text=I18n.t("mirror_status_active"))
            self.btn_stop.configure(state="normal", fg_color="#DC2626", text_color="#FFFFFF")
            self.set_media_status("🟢 Screen Mirror aktif.", ("#059669", "#10B981"), auto_clear_seconds=3)
            
            # Polling langsung di main-thread
            self._schedule_poll()
            
            # Thread cadangan untuk menangkap sinyal OS secara instan
            def _bg_wait(proc):
                try:
                    proc.wait()
                except Exception:
                    pass
                try:
                    self.after(0, self._on_scrcpy_terminated)
                except Exception:
                    pass
            threading.Thread(target=_bg_wait, args=(self.scrcpy_process,), daemon=True).start()

            print(f"[SCRCPY] Process launched PID: {self.scrcpy_process.pid} with cwd {scrcpy_dir}")
        except Exception as e:
            self.set_media_status(f"❌ Scrcpy Error: {e}", ("#DC2626", "#F87171"), auto_clear_seconds=6)
            print(f"[SCRCPY] Failed to start scrcpy: {e}")

    def _schedule_poll(self):
        try:
            if self.winfo_exists() and self.scrcpy_process is not None:
                self.after(250, self._check_scrcpy_status)
        except Exception:
            pass

    def _check_scrcpy_status(self):
        """Memeriksa status proses Scrcpy di thread utama secara berkala."""
        if self.scrcpy_process is not None:
            poll_res = self.scrcpy_process.poll()
            if poll_res is not None:
                print(f"[SCRCPY] Poll detected process exit code: {poll_res}")
                self._on_scrcpy_terminated()
            else:
                self._schedule_poll()

    def _on_scrcpy_terminated(self):
        print("[SCRCPY] _on_scrcpy_terminated triggered. Resetting UI buttons.")
        self.scrcpy_process = None
        try:
            if self.winfo_exists():
                self.btn_start.configure(state="normal", fg_color="#2563EB", text=I18n.t("mirror_btn_start"))
                self.btn_stop.configure(state="disabled", fg_color=("#E2E8F0", "#1E293B"), text_color=("#475569", "#CBD5E1"))
                self.set_media_status("ℹ️ Sesi Screen Mirror selesai.", ("#64748B", "#94A3B8"), auto_clear_seconds=3)
                print("[SCRCPY] UI buttons successfully reset to Start (Blue).")
        except Exception as e:
            print(f"[SCRCPY UI RESET ERROR] {e}")

    def stop_mirror(self):
        """Menghentikan sesi Scrcpy secara instan dan membersihkan proses."""
        print("[SCRCPY] stop_mirror() called by user.")
        if self.scrcpy_process:
            try:
                self.scrcpy_process.terminate()
                self.scrcpy_process.wait(timeout=1)
            except Exception:
                try:
                    self.scrcpy_process.kill()
                except Exception:
                    pass
            self.scrcpy_process = None

        try:
            subprocess.run(["taskkill", "/F", "/IM", "scrcpy.exe"], capture_output=True, creationflags=0x08000000)
        except Exception:
            pass

        self._on_scrcpy_terminated()

    def set_media_status(self, text: str, color=("#059669", "#10B981"), auto_clear_seconds: int = 4):
        """Memperbarui teks status label media dengan timeout pembersihan otomatis."""
        try:
            if hasattr(self, "lbl_media_status") and self.lbl_media_status.winfo_exists():
                self.lbl_media_status.configure(text=text, text_color=color)
                if auto_clear_seconds > 0:
                    def _clear():
                        try:
                            if hasattr(self, "lbl_media_status") and self.lbl_media_status.winfo_exists():
                                if self.lbl_media_status.cget("text") == text:
                                    self.lbl_media_status.configure(text="")
                        except Exception:
                            pass
                    self.after(auto_clear_seconds * 1000, _clear)
        except Exception:
            pass
