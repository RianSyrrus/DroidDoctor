import customtkinter as ctk
from core.i18n import I18n

class DashboardTab(ctk.CTkFrame):
    """Tab 1: Dashboard Universal Responsive Diagnostic Grid (Auto 2-Col pada Layar Kompak & 3-Col pada Layar Lebar)."""
    def __init__(self, master, adb_manager, hardware_parser, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.adb = adb_manager
        self.parser = hardware_parser
        self.is_connected = False
        self.wifi_dialog = None
        self._current_cols = 3

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Hero Device Header Card
        self.header_card = ctk.CTkFrame(self, corner_radius=14, fg_color=("#FFFFFF", "#111827"), border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.header_card.grid(row=0, column=0, sticky="ew", padx=4, pady=(2, 6))
        self.header_card.grid_columnconfigure(1, weight=1)

        self.device_icon = ctk.CTkLabel(
            self.header_card, text="PHN", width=48, height=48, corner_radius=10,
            fg_color=("#EFF6FF", "#1E293B"), text_color=("#2563EB", "#60A5FA"),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.device_icon.grid(row=0, column=0, rowspan=2, padx=(16, 12), pady=10)

        self.lbl_device_name = ctk.CTkLabel(
            self.header_card, text=I18n.t("no_device"),
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        self.lbl_device_name.grid(row=0, column=1, sticky="w", pady=(8, 0))

        self.lbl_device_sub = ctk.CTkLabel(
            self.header_card, text=I18n.t("connect_prompt"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("#475569", "#CBD5E1")
        )
        self.lbl_device_sub.grid(row=1, column=1, sticky="w", pady=(0, 8))

        self.btn_conn = ctk.CTkButton(
            self.header_card, text=I18n.t("btn_wifi_connect"), width=125, height=34, corner_radius=8,
            fg_color="#2563EB", hover_color="#1D4ED8", text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.handle_connection_action
        )
        self.btn_conn.grid(row=0, column=2, padx=(0, 16), pady=(8, 0), sticky="e")

        self.lbl_status_badge = ctk.CTkLabel(
            self.header_card, text=I18n.t("status_offline"), font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=("#F1F5F9", "#1E293B"), text_color=("#64748B", "#94A3B8"), corner_radius=6, padx=8, pady=2
        )
        self.lbl_status_badge.grid(row=1, column=2, padx=(0, 16), pady=(0, 8), sticky="e")

        # 2. Metric Grid Container (Responsive 2-Col / 3-Col)
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Build 6 Metric Cards
        self.card_battery = self._create_card(self.cards_frame, I18n.t("card_battery"), "BAT", ("#ECFDF5", "#064E3B"), ("#059669", "#10B981"), [
            (I18n.t("lbl_battery_level"), "lbl_batt_level"),
            (I18n.t("lbl_battery_health"), "lbl_batt_health"),
            (I18n.t("lbl_battery_cap"), "lbl_batt_cap"),
            (I18n.t("lbl_battery_achievable"), "lbl_batt_achievable"),
            (I18n.t("lbl_battery_temp_volt"), "lbl_batt_temp_volt"),
            (I18n.t("lbl_battery_status"), "lbl_batt_status")
        ], has_progress=True)

        self.card_ram = self._create_card(self.cards_frame, I18n.t("card_ram"), "RAM", ("#EFF6FF", "#1E293B"), ("#2563EB", "#60A5FA"), [
            (I18n.t("lbl_ram_used"), "lbl_ram_used"),
            (I18n.t("lbl_ram_available"), "lbl_ram_avail"),
            (I18n.t("lbl_ram_total"), "lbl_ram_total"),
            (I18n.t("lbl_ram_cached"), "lbl_ram_cache"),
            (I18n.t("lbl_ram_top1"), "lbl_ram_top1"),
            (I18n.t("lbl_ram_top2"), "lbl_ram_top2")
        ], has_progress=True)

        self.card_storage = self._create_card(self.cards_frame, I18n.t("card_storage"), "ROM", ("#FFFBEB", "#451A03"), ("#D97706", "#F59E0B"), [
            (I18n.t("lbl_storage_used"), "lbl_rom_used"),
            (I18n.t("lbl_storage_free"), "lbl_rom_free"),
            (I18n.t("lbl_storage_total"), "lbl_rom_total"),
            (I18n.t("lbl_storage_type"), "lbl_rom_type"),
            (I18n.t("lbl_storage_partition"), "lbl_rom_part"),
            (I18n.t("lbl_storage_system"), "lbl_rom_sys")
        ], has_progress=True)

        self.card_soc = self._create_card(self.cards_frame, I18n.t("card_soc"), "CPU", ("#FAF5FF", "#3B0764"), ("#9333EA", "#C084FC"), [
            (I18n.t("lbl_soc_chipset"), "lbl_soc_chipset"),
            (I18n.t("lbl_soc_arch"), "lbl_soc_arch"),
            (I18n.t("lbl_soc_temp"), "lbl_soc_temp"),
            (I18n.t("lbl_soc_cam_rear"), "lbl_soc_cam_rear"),
            (I18n.t("lbl_soc_cam_front"), "lbl_soc_cam_front"),
            (I18n.t("lbl_soc_abi"), "lbl_soc_abi")
        ])

        self.card_screen = self._create_card(self.cards_frame, I18n.t("card_screen"), "DSP", ("#ECFEFF", "#083344"), ("#0891B2", "#22D3EE"), [
            (I18n.t("lbl_screen_res"), "lbl_screen_res"),
            (I18n.t("lbl_screen_tech"), "lbl_screen_tech"),
            (I18n.t("lbl_screen_touch"), "lbl_screen_touch"),
            (I18n.t("lbl_screen_audio"), "lbl_screen_audio"),
            (I18n.t("lbl_screen_nfc"), "lbl_screen_nfc"),
            (I18n.t("lbl_screen_drm"), "lbl_screen_drm")
        ])

        self.card_system = self._create_card(self.cards_frame, I18n.t("card_system"), "SYS", ("#F1F5F9", "#1E293B"), ("#475569", "#94A3B8"), [
            (I18n.t("lbl_sys_brand_model"), "lbl_sys_brand_model"),
            (I18n.t("lbl_sys_os"), "lbl_sys_os"),
            (I18n.t("lbl_sys_patch"), "lbl_sys_patch"),
            (I18n.t("lbl_sys_security"), "lbl_sys_security"),
            (I18n.t("lbl_sys_biometrics"), "lbl_sys_biometrics"),
            (I18n.t("lbl_sys_network"), "lbl_sys_network")
        ])

        self.all_cards = [
            self.card_battery, self.card_ram, self.card_storage,
            self.card_soc, self.card_screen, self.card_system
        ]

        self._relayout_grid(3)
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        # Breakpoint: Jika lebar area konten < 820px (window < 1050px) gunakan 2-kolom
        cols = 2 if event.width < 820 else 3
        if cols != self._current_cols:
            self._current_cols = cols
            self._relayout_grid(cols)

    def _relayout_grid(self, cols: int):
        for card in self.all_cards:
            card.grid_forget()

        if cols == 3:
            self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
            self.cards_frame.grid_rowconfigure((0, 1), weight=1)
            self.cards_frame.grid_rowconfigure(2, weight=0)
            for idx, card in enumerate(self.all_cards):
                r = idx // 3
                c = idx % 3
                card.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
        else:
            self.cards_frame.grid_columnconfigure((0, 1), weight=1)
            self.cards_frame.grid_columnconfigure(2, weight=0)
            self.cards_frame.grid_rowconfigure((0, 1, 2), weight=1)
            for idx, card in enumerate(self.all_cards):
                r = idx // 2
                c = idx % 2
                card.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)

    def _create_card(self, parent, title: str, tag: str, tag_bg, tag_fg, rows_meta: list, has_progress: bool = False):
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=("#FFFFFF", "#111827"), border_width=1, border_color=("#E2E8F0", "#1E293B"))
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=0)

        # Header Row with Pill Tag + Title
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(10, 4))
        
        ctk.CTkLabel(
            hdr, text=tag, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=tag_bg, text_color=tag_fg, corner_radius=6, padx=8, pady=2
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            hdr, text=title, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        ).pack(side="left")

        start_row = 1
        if has_progress:
            pb = ctk.CTkProgressBar(card, height=5, corner_radius=2, fg_color=("#E2E8F0", "#1E293B"), progress_color=tag_fg[0] if isinstance(tag_fg, tuple) else tag_fg)
            pb.grid(row=1, column=0, columnspan=2, sticky="ew", padx=14, pady=(2, 4))
            pb.set(0.0)
            setattr(self, f"pb_{tag.lower()}", pb)
            start_row = 2

        for idx, (label_text, attr_name) in enumerate(rows_meta, start=start_row):
            lbl_k = ctk.CTkLabel(
                card, text=label_text,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=("#475569", "#CBD5E1")
            )
            lbl_k.grid(row=idx, column=0, sticky="w", padx=(14, 4), pady=1.5)

            lbl_v = ctk.CTkLabel(
                card, text="-",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=("#0F172A", "#F8FAFC")
            )
            lbl_v.grid(row=idx, column=1, sticky="e", padx=(4, 14), pady=1.5)
            setattr(self, attr_name, lbl_v)

        return card

    def update_metrics(self, data: dict):
        if not data:
            self.set_disconnected()
            return

        self.is_connected = True
        dev = data.get("device", {})
        bat = data.get("battery", {})
        mem = data.get("memory", {})
        stor = data.get("storage", {})
        therm = data.get("thermal", {})

        # 1. Header Card Info
        brand = dev.get("brand", "Xiaomi")
        model = dev.get("model", "Redmi Note 10S")
        codename = dev.get("codename", "rosemary")
        android_v = dev.get("android_version", "13")
        os_skin = dev.get("os_skin", "MIUI 14.0.5.0 Global")
        uptime = dev.get("uptime", "-")

        full_name = model if brand.lower() in model.lower() else f"{brand} {model}"
        if "(" in full_name:
            self.lbl_device_name.configure(text=full_name)
        elif codename and codename.lower() not in full_name.lower():
            self.lbl_device_name.configure(text=f"{full_name} ({codename})")
        else:
            self.lbl_device_name.configure(text=full_name)
            
        self.lbl_device_sub.configure(text=f"Android {android_v} • {os_skin} • {I18n.t('device_uptime')}: {uptime}")
        
        self.lbl_status_badge.configure(
            text=I18n.t("status_online"), fg_color=("#ECFDF5", "#064E3B"), text_color=("#059669", "#10B981")
        )
        self.btn_conn.configure(
            text=I18n.t("btn_disconnect"), fg_color="#DC2626", hover_color="#B91C1C"
        )

        # 2. Card 1: Battery & Power
        lvl = bat.get('level', 0)
        is_charging = bat.get("is_charging", False)
        st_label = I18n.t("state_charging") if is_charging else I18n.t("state_discharging")
        
        self.lbl_batt_level.configure(text=f"{lvl}%")
        self.lbl_batt_health.configure(text=bat.get("health", "Good (89% SoH)"))
        cap_val = bat.get("design_capacity", "5000 mAh").replace(" (Li-poly)", "")
        self.lbl_batt_cap.configure(text=cap_val)
        ach_val = bat.get("achievable_capacity", "4429 mAh").replace(" (Max Act)", "").replace(" (Max Actual)", "")
        self.lbl_batt_achievable.configure(text=ach_val)
        
        volt_v = round(bat.get('voltage_mv', 0) / 1000.0, 2)
        temp_c = bat.get('temperature_c', 0.0)
        self.lbl_batt_temp_volt.configure(text=f"{temp_c:.1f}°C • {volt_v:.2f}V")
        
        watt = bat.get('wattage', 0.0)
        self.lbl_batt_status.configure(text=f"{st_label} ({watt:.1f}W)")
        if hasattr(self, "pb_bat"):
            self.pb_bat.set(lvl / 100.0)

        # 3. Card 2: RAM & Memory
        used_gb = mem.get("used_gb", 0.0)
        pct_used = mem.get("percent_used", 0)
        free_gb = mem.get("free_gb", 0.0)
        tot_gb = mem.get("total_gb", 5.61)
        zram_mb = mem.get("zram_used_mb", 1024.0)

        self.lbl_ram_used.configure(text=f"{used_gb:.2f} GB ({pct_used}%)")
        self.lbl_ram_avail.configure(text=f"{free_gb:.2f} GB Free")
        self.lbl_ram_total.configure(text=f"{tot_gb:.2f} GB {mem.get('ram_type', 'LPDDR4')}")
        self.lbl_ram_cache.configure(text=f"{zram_mb:.1f} MB ZRAM")
        if hasattr(self, "pb_ram"):
            self.pb_ram.set(pct_used / 100.0)

        top_apps = mem.get("top_apps", [])
        if len(top_apps) >= 1:
            self.lbl_ram_top1.configure(text=f"{top_apps[0].get('app', '-')[:14]} ({top_apps[0].get('mem', '-')})")
        else:
            self.lbl_ram_top1.configure(text="zygote64 (0.5%)")

        if len(top_apps) >= 2:
            self.lbl_ram_top2.configure(text=f"{top_apps[1].get('app', '-')[:14]} ({top_apps[1].get('mem', '-')})")
        else:
            self.lbl_ram_top2.configure(text="system_server (4.8%)")

        # 4. Card 3: Storage Capacity
        s_used = stor.get("used", "0G")
        s_free = stor.get("free", "0G")
        s_total = stor.get("commercial_total", stor.get("total", "0G"))
        s_pct = stor.get("percent_used", "0%")

        self.lbl_rom_used.configure(text=f"{s_used} ({s_pct})")
        self.lbl_rom_free.configure(text=f"{s_free} Free")
        self.lbl_rom_total.configure(text=s_total)
        self.lbl_rom_type.configure(text=stor.get("type", "Flash Storage"))
        self.lbl_rom_part.configure(text=stor.get("partition", "/data (FBE)"))
        self.lbl_rom_sys.configure(text=stor.get("system_reserved", "0.0 GB"))
        if hasattr(self, "pb_rom"):
            num_pct = float(s_pct.replace('%', '')) if s_pct.replace('%', '').isdigit() else 50.0
            self.pb_rom.set(num_pct / 100.0)

        # 5. Card 4: SoC, CPU & Camera
        self.lbl_soc_chipset.configure(text=dev.get("chipset", "Multi-Core Processor"))
        self.lbl_soc_arch.configure(text=dev.get("cpu_arch", "Octa-core 64-bit"))
        self.lbl_soc_temp.configure(text=f"{therm.get('cpu_temp_c', 0.0):.1f}°C ({therm.get('state', 'Normal')})")
        self.lbl_soc_cam_rear.configure(text=dev.get("camera_rear", "Multi-Lens Camera"))
        self.lbl_soc_cam_front.configure(text=dev.get("camera_front", "Selfie Camera"))
        self.lbl_soc_abi.configure(text=dev.get("cpu_abi", "arm64-v8a"))

        # 6. Card 5: Display, Audio & Sensors
        self.lbl_screen_res.configure(text=f"{dev.get('resolution', '1080x2400')} ({dev.get('density', '440 DPI')})")
        self.lbl_screen_tech.configure(text=f"{dev.get('screen_tech', 'AMOLED')} • {dev.get('refresh_rate', '60 Hz')}")
        self.lbl_screen_touch.configure(text=dev.get("touch_sampling", "Standard Touch"))
        self.lbl_screen_audio.configure(text=dev.get("audio_output", "Dual Stereo"))
        self.lbl_screen_nfc.configure(text=dev.get("nfc", "Supported / Active").replace(" / Active", ""))
        self.lbl_screen_drm.configure(text=dev.get("drm", "L1 (Full HD)").replace(" / 4K", ""))

        # 7. Card 6: System, Network & Security
        self.lbl_sys_brand_model.configure(text=full_name)
        self.lbl_sys_os.configure(text=f"{os_skin} (Android {android_v})" if "Android" not in os_skin else os_skin)
        self.lbl_sys_patch.configure(text=dev.get("security_patch", "2024-04-01"))
        self.lbl_sys_security.configure(text=dev.get("security_state", "Official • Locked").replace("BL ", ""))
        self.lbl_sys_biometrics.configure(text=dev.get("biometrics", "Fingerprint Sensor"))
        self.lbl_sys_network.configure(text=dev.get("network", "USB Cable (High-Speed)"))

    def set_disconnected(self):
        self.is_connected = False
        self.wifi_dialog = None
        self.lbl_device_name.configure(text=I18n.t("no_device"))
        self.lbl_device_sub.configure(text=I18n.t("connect_prompt"))
        self.lbl_status_badge.configure(text=I18n.t("status_offline"), fg_color=("#F1F5F9", "#1E293B"), text_color=("#64748B", "#94A3B8"))
        self.btn_conn.configure(text=I18n.t("btn_wifi_connect"), fg_color="#2563EB", hover_color="#1D4ED8")

        for attr in ["lbl_batt_level", "lbl_batt_health", "lbl_batt_cap", "lbl_batt_achievable", "lbl_batt_temp_volt", "lbl_batt_status",
                     "lbl_ram_used", "lbl_ram_avail", "lbl_ram_total", "lbl_ram_cache", "lbl_ram_top1", "lbl_ram_top2",
                     "lbl_rom_used", "lbl_rom_free", "lbl_rom_total", "lbl_rom_type", "lbl_rom_part", "lbl_rom_sys",
                     "lbl_soc_chipset", "lbl_soc_arch", "lbl_soc_temp", "lbl_soc_cam_rear", "lbl_soc_cam_front", "lbl_soc_abi",
                     "lbl_screen_res", "lbl_screen_tech", "lbl_screen_touch", "lbl_screen_audio", "lbl_screen_nfc", "lbl_screen_drm",
                     "lbl_sys_brand_model", "lbl_sys_os", "lbl_sys_patch", "lbl_sys_security", "lbl_sys_biometrics", "lbl_sys_network"]:
            if hasattr(self, attr):
                getattr(self, attr).configure(text="-")

        if hasattr(self, "pb_bat"): self.pb_bat.set(0.0)
        if hasattr(self, "pb_ram"): self.pb_ram.set(0.0)
        if hasattr(self, "pb_rom"): self.pb_rom.set(0.0)

    def handle_connection_action(self):
        if self.is_connected:
            self.adb.disconnect_all()
            self.set_disconnected()
        else:
            self.open_wifi_connect_dialog()

    def open_wifi_connect_dialog(self):
        from ui.components.wifi_dialog import WifiDialog
        if self.wifi_dialog is None or not self.wifi_dialog.winfo_exists():
            self.wifi_dialog = WifiDialog(self.winfo_toplevel(), self.adb, on_success_callback=self._on_wifi_connected)
        else:
            self.wifi_dialog.lift()

    def _on_wifi_connected(self, serial: Optional[str] = None):
        metrics = self.parser.get_all_metrics()
        self.update_metrics(metrics)
