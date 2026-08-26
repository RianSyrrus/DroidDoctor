import customtkinter as ctk
import threading, time
from core.settings_manager import SettingsManager
from core.i18n import I18n
from .theme_manager import ThemeManager
from .tabs.dashboard_tab import DashboardTab
from .tabs.mirror_tab import MirrorTab
from .tabs.debloater_tab import DebloaterTab
from .tabs.storage_tab import StorageTab
from .tabs.tools_tab import ToolsTab
from .components.settings_overlay import SettingsOverlay

class MainWindow(ctk.CTk):
    """Jendela Utama DroidDoctor dengan In-App Modal Settings, Multi-Bahasa, dan Preservasi Tab 100%."""
    def __init__(self, adb_manager, hardware_parser):
        super().__init__()
        self.adb = adb_manager
        self.parser = hardware_parser
        self.settings = SettingsManager.get_instance()

        self.title("DroidDoctor — Android Health & Diagnostics Suite")
        
        # Algoritma Adaptif Layar Universal (Auto-Fit Laptop Layar Kecil & PC Monitor Besar)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        # Target 1422x853 pada layar Full HD (1920x1080+), atau 88-90% proporsional jika layar laptop kecil (1366x768 / 1280x720)
        win_w = max(980, min(1422, int(screen_w * 0.88)))
        win_h = max(600, min(853, int(screen_h * 0.88)))

        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h) // 2)
        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.minsize(960, 580)

        # Set Window Titlebar and Taskbar Icon
        import os, sys
        base_proj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_candidates = [
            os.path.join(base_proj, "assets", "app_icon.ico"),
            os.path.join(os.path.dirname(sys.executable), "assets", "app_icon.ico"),
            os.path.join(os.path.dirname(sys.executable), "_internal", "assets", "app_icon.ico"),
            os.path.join(getattr(sys, '_MEIPASS', ''), "assets", "app_icon.ico")
        ]
        for ic in icon_candidates:
            if os.path.exists(ic):
                try:
                    self.iconbitmap(ic)
                    break
                except Exception:
                    pass

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=("#FFFFFF", "#0E1422"), border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(6, weight=1)

        self._init_sidebar()

        self.content_area = ctk.CTkFrame(self, fg_color=("#F8FAFC", "#0B0F17"), corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        self.current_tab = None
        self._init_tabs()

        # In-App Settings Modal Overlay (Fixed Size 650x480)
        self.settings_overlay = SettingsOverlay(
            self.content_area,
            on_close=self._on_settings_closed,
            on_change=self._on_setting_changed
        )

        self.show_dashboard()
        self.after(200, self.bring_to_front)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.is_running = True
        self.live_thread = threading.Thread(target=self._live_loop, daemon=True)
        self.live_thread.start()

    def _init_sidebar(self):
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=16, pady=(20, 16), sticky="w")
        
        self.lbl_brand = ctk.CTkLabel(
            brand_frame, text="DroidDoctor",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=("#2563EB", "#60A5FA")
        )
        self.lbl_brand.pack(anchor="w")

        self.lbl_subtitle = ctk.CTkLabel(
            brand_frame, text=I18n.t("app_subtitle"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("#64748B", "#94A3B8")
        )
        self.lbl_subtitle.pack(anchor="w")

        self.btn_tab1 = self._make_sidebar_btn(I18n.t("nav_dashboard"), 1, lambda: self._on_user_tab_click(self.tab_dashboard, self.btn_tab1))
        self.btn_tab2 = self._make_sidebar_btn(I18n.t("nav_mirror"), 2, lambda: self._on_user_tab_click(self.tab_mirror, self.btn_tab2))
        self.btn_tab3 = self._make_sidebar_btn(I18n.t("nav_debloater"), 3, lambda: self._on_user_tab_click(self.tab_debloater, self.btn_tab3, is_debloat=True))
        self.btn_tab4 = self._make_sidebar_btn(I18n.t("nav_storage"), 4, lambda: self._on_user_tab_click(self.tab_storage, self.btn_tab4, is_storage=True))
        self.btn_tab5 = self._make_sidebar_btn(I18n.t("nav_tools"), 5, lambda: self._on_user_tab_click(self.tab_tools, self.btn_tab5))

        if not self.settings.get("debloater_tab_visible", False):
            self.btn_tab3.grid_remove()

        self.btn_settings = ctk.CTkButton(
            self.sidebar, text=I18n.t("nav_settings"),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            anchor="w", fg_color="transparent", text_color=("#475569", "#CBD5E1"),
            hover_color=("#E2E8F0", "#1E293B"), height=38, corner_radius=8,
            command=self.show_settings
        )
        self.btn_settings.grid(row=7, column=0, padx=12, pady=(0, 16), sticky="ew")

    def _make_sidebar_btn(self, text: str, row: int, command):
        btn = ctk.CTkButton(
            self.sidebar, text=text,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            anchor="w", fg_color="transparent", text_color=("#475569", "#CBD5E1"),
            hover_color=("#E2E8F0", "#1E293B"), height=38, corner_radius=8,
            command=command
        )
        btn.grid(row=row, column=0, padx=12, pady=4, sticky="ew")
        return btn

    def _init_tabs(self):
        self.tab_dashboard = DashboardTab(self.content_area, self.adb, self.parser)
        self.tab_mirror = MirrorTab(self.content_area, self.adb)
        self.tab_debloater = DebloaterTab(self.content_area, self.adb)
        self.tab_storage = StorageTab(self.content_area, self.adb)
        self.tab_tools = ToolsTab(self.content_area, self.adb, self.parser)

    def _reset_btn_colors(self):
        for btn in [self.btn_tab1, self.btn_tab2, self.btn_tab3, self.btn_tab4, self.btn_tab5]:
            btn.configure(fg_color="transparent", text_color=("#475569", "#CBD5E1"))

    def _on_user_tab_click(self, tab, active_btn, is_debloat=False, is_storage=False):
        if hasattr(self, "settings_overlay") and self.settings_overlay.is_visible:
            self.settings_overlay.hide()
        self._switch_tab(tab, active_btn)
        if is_debloat:
            self.tab_debloater.show_disclaimer_dialog()
        elif is_storage:
            self.tab_storage.scan_storage()

    def show_dashboard(self):
        self._switch_tab(self.tab_dashboard, self.btn_tab1)

    def show_mirror(self):
        self._switch_tab(self.tab_mirror, self.btn_tab2)

    def show_debloater(self):
        self._switch_tab(self.tab_debloater, self.btn_tab3)
        self.tab_debloater.show_disclaimer_dialog()

    def show_storage(self):
        self._switch_tab(self.tab_storage, self.btn_tab4)

    def show_tools(self):
        self._switch_tab(self.tab_tools, self.btn_tab5)

    def show_settings(self):
        if hasattr(self, "settings_overlay"):
            if self.settings_overlay.is_visible:
                self.settings_overlay.hide()
            else:
                self.btn_settings.configure(fg_color=("#DBEAFE", "#1E3A8A"), text_color=("#1D4ED8", "#93C5FD"))
                self.settings_overlay.show()

    def _on_settings_closed(self):
        self.btn_settings.configure(fg_color="transparent", text_color=("#475569", "#CBD5E1"))

    def _on_setting_changed(self, key, value):
        if key == "debloater_tab_visible":
            if value:
                self.btn_tab3.grid(row=3, column=0, padx=12, pady=4, sticky="ew")
            else:
                self.btn_tab3.grid_remove()
                if self.current_tab == self.tab_debloater:
                    self.show_dashboard()
        elif key == "language":
            self._reload_language()
        elif key == "theme":
            self._reset_btn_colors()
            btn_map = {
                self.tab_dashboard: self.btn_tab1,
                self.tab_mirror: self.btn_tab2,
                self.tab_debloater: self.btn_tab3,
                self.tab_storage: self.btn_tab4,
                self.tab_tools: self.btn_tab5
            }
            act_btn = btn_map.get(self.current_tab)
            if act_btn:
                act_btn.configure(fg_color=("#DBEAFE", "#1E3A8A"), text_color=("#1D4ED8", "#93C5FD"))

    def _reload_language(self):
        """Penyegaran teks antarmuka secara dinamis dengan preservasi tab aktif & settings overlay."""
        last_tab_idx = 1
        if self.current_tab == self.tab_mirror:
            last_tab_idx = 2
        elif self.current_tab == self.tab_debloater:
            last_tab_idx = 3
        elif self.current_tab == self.tab_storage:
            last_tab_idx = 4
        elif self.current_tab == self.tab_tools:
            last_tab_idx = 5

        overlay_was_open = hasattr(self, "settings_overlay") and self.settings_overlay.is_visible

        self.lbl_subtitle.configure(text=I18n.t("app_subtitle"))
        self.btn_tab1.configure(text=I18n.t("nav_dashboard"))
        self.btn_tab2.configure(text=I18n.t("nav_mirror"))
        self.btn_tab3.configure(text=I18n.t("nav_debloater"))
        self.btn_tab4.configure(text=I18n.t("nav_storage"))
        self.btn_tab5.configure(text=I18n.t("nav_tools"))
        self.btn_settings.configure(text=I18n.t("nav_settings"))

        # Re-create tab contents for clean translated strings
        if self.current_tab:
            self.current_tab.pack_forget()
        for w in self.content_area.winfo_children():
            if w != getattr(self, "settings_overlay", None):
                w.destroy()
        self._init_tabs()

        tab_map = {
            1: (self.tab_dashboard, self.btn_tab1),
            2: (self.tab_mirror, self.btn_tab2),
            3: (self.tab_debloater, self.btn_tab3),
            4: (self.tab_storage, self.btn_tab4),
            5: (self.tab_tools, self.btn_tab5)
        }
        target_tab, target_btn = tab_map.get(last_tab_idx, (self.tab_dashboard, self.btn_tab1))
        self._reset_btn_colors()
        target_btn.configure(fg_color=("#DBEAFE", "#1E3A8A"), text_color=("#1D4ED8", "#93C5FD"))
        self.current_tab = target_tab
        self.current_tab.pack(fill="both", expand=True, padx=14, pady=14)

        if overlay_was_open:
            self.settings_overlay.show()
            self.settings_overlay.refresh_i18n_texts()
            self.settings_overlay.lift()

    def _switch_tab(self, tab, active_btn):
        tab_name = tab.__class__.__name__
        if self.current_tab == tab:
            print(f"[NAV] Tab '{tab_name}' is already active.")
            return
        if self.current_tab:
            self.current_tab.pack_forget()
        self._reset_btn_colors()
        active_btn.configure(fg_color=("#DBEAFE", "#1E3A8A"), text_color=("#1D4ED8", "#93C5FD"))
        self.current_tab = tab
        self.current_tab.pack(fill="both", expand=True, padx=14, pady=14)
        print(f"[NAV] Switched to active tab: '{tab_name}'")

    def bring_to_front(self):
        """Menjaga agar jendela DroidDoctor tetap berada di posisi depan (Foreground) saat perangkat dicolok atau di-allow."""
        try:
            self.lift()
            self.focus_force()
            self.attributes("-topmost", True)
            self.after(200, lambda: self.attributes("-topmost", False))
        except Exception:
            pass

    def _live_loop(self):
        was_connected = False
        while self.is_running:
            try:
                rate = self.settings.get("polling_rate", 0.5)
                devices = self.adb.get_connected_devices()
                if devices and devices[0].get("state") == "device":
                    current_serial = devices[0]["serial"]
                    is_new_connection = (self.adb.current_serial != current_serial or not was_connected)
                    
                    if is_new_connection:
                        self.adb.select_device(current_serial)
                        was_connected = True
                        self.after(0, self.bring_to_front)
                    
                    if self.current_tab == self.tab_dashboard:
                        data = self.parser.get_all_metrics()
                        if data and self.is_running:
                            self.after(0, lambda d=data: self.tab_dashboard.update_metrics(d))
                else:
                    self.adb.current_serial = None
                    was_connected = False
                    if self.is_running and self.tab_dashboard.is_connected:
                        self.after(0, self.tab_dashboard.set_disconnected)
            except Exception:
                pass
            time.sleep(self.settings.get("polling_rate", 0.5))

    def on_close(self):
        self.is_running = False
        try:
            if hasattr(self, 'tab_mirror') and self.tab_mirror.scrcpy_process:
                self.tab_mirror.stop_mirror()
        except Exception:
            pass
        self.destroy()
