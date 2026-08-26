import customtkinter as ctk
import threading
import re
from core.i18n import I18n

CORE_CRITICAL_PACKAGES = {
    "android", "com.android.systemui", "com.android.settings", "com.google.android.gms",
    "com.android.phone", "com.android.server.telecom", "com.android.providers.telephony",
    "com.android.keyguard", "com.android.packageinstaller", "com.google.android.packageinstaller",
    "com.android.permissioncontroller", "com.google.android.permissioncontroller",
    "com.android.providers.settings", "com.android.shell", "com.miui.home"
}

SAFE_BLOATWARE_PACKAGES = {
    "com.miui.msa.global", "com.miui.analytics", "com.miui.bugreport", "com.miui.yellowpage",
    "com.xiaomi.mipicks", "com.xiaomi.midrop", "com.xiaomi.glgm", "com.miui.hybrid",
    "com.miui.cleanmaster", "com.facemoji.lite.xiaomi", "com.miui.player", "com.miui.videoplayer",
    "com.miui.compass", "com.miui.notes", "com.miui.weather2", "com.facebook.katana",
    "com.facebook.system", "com.facebook.appmanager", "com.facebook.services",
    "com.google.android.apps.tachyon", "com.google.android.videos", "com.google.android.music",
    "com.google.android.feedback", "com.android.egg"
}

FRIENDLY_NAMES = {
    "com.instagram.barcelona": "Threads", "com.instagram.android": "Instagram", "com.linkedin.android": "LinkedIn",
    "com.facebook.katana": "Facebook", "com.facebook.orca": "Messenger", "com.facebook.lite": "Facebook Lite",
    "com.whatsapp": "WhatsApp", "com.whatsapp.w4b": "WhatsApp Business", "org.telegram.messenger": "Telegram",
    "com.twitter.android": "X (Twitter)", "com.tiktok.android": "TikTok", "com.zhiliaoapp.musically": "TikTok Global",
    "com.lemon.lvoverseas": "CapCut Video Editor", "com.spotify.music": "Spotify", "com.reddit.frontpage": "Reddit",
    "com.discord": "Discord", "com.jago.digitalBanking": "Bank Jago", "com.bca": "BCA Mobile",
    "id.co.bca.mybca": "myBCA", "id.bmri.livin": "Livin by Mandiri", "id.co.bri.brimo": "BRImo BRI",
    "src.com.bni": "BNI Mobile Banking", "com.seabank.id": "SeaBank Indonesia", "id.dana": "DANA Dompet Digital",
    "ovo.id": "OVO", "com.gojek.gopay": "GoPay", "com.telkom.mwallet": "LinkAja", "com.shopee.id": "Shopee",
    "com.tokopedia.tkpd": "Tokopedia", "com.grabtaxi.passenger": "Grab", "com.gojek.app": "Gojek",
    "com.hso.motorku": "Motorku X (Honda)", "id.mypertamina.app": "MyPertamina", "com.pln.mobile": "PLN Mobile",
    "id.co.bpjs.mobile": "Mobile JKN (BPJS)", "com.telkomsel.telkomselcm": "MyTelkomsel", "com.indosat.myim3": "myIM3",
    "com.myxl.xlmyxl": "myXL", "com.axis.net": "AXISnet", "com.tri.bima": "bima+ (Tri)",
    "com.intsig.camscanner": "CamScanner", "com.legend.hiwtchMax.app": "HiWatch Max",
    "com.just4funtools.fakegpslocationprofessional": "Fake GPS Location Pro", "de.szalkowski.activitylauncher": "Activity Launcher",
    "moe.shizuku.privileged.api": "Shizuku", "bin.mt.plus": "MT Manager", "ru.zdevs.zarchiver": "ZArchiver",
    "com.tongyi.intl": "Tongyi AI", "com.goodix.gftest": "Goodix Fingerprint Test",
    "com.facemoji.lite.xiaomi": "Facemoji Keyboard Xiaomi", "com.miui.powerkeeper": "MIUI Battery & Performance",
    "com.miui.miservice": "Mi Service & Feedback", "com.miui.msa.global": "MIUI System Ads (MSA)",
    "com.miui.miwallpaper.overlay.customize": "MIUI Live Wallpapers", "com.mi.android.globalFileexplorer": "Mi File Manager",
    "com.miui.face": "MIUI Face Unlock Service", "com.miui.cleanmaster": "MIUI Cleaner (Clean Master)",
    "com.miui.analytics": "MIUI Analytics", "com.miui.bugreport": "MIUI Bug Report", "com.miui.yellowpage": "MIUI Yellow Pages",
    "com.xiaomi.mipicks": "GetApps (Xiaomi App Store)", "com.xiaomi.midrop": "ShareMe (Mi Drop)",
    "com.xiaomi.scanner": "Mi Scanner", "com.xiaomi.glgm": "Games Center Xiaomi", "com.miui.hybrid": "Quick Apps Service",
    "com.miui.compass": "Mi Compass", "com.miui.screenrecorder": "Mi Screen Recorder", "com.miui.weather2": "Mi Weather",
    "com.miui.notes": "Mi Notes", "com.miui.calculator": "Mi Calculator", "com.miui.player": "Mi Music",
    "com.miui.videoplayer": "Mi Video", "com.miui.gallery": "Mi Gallery", "com.android.updater": "System Updater",
    "com.google.android.gms": "Google Play Services", "com.android.vending": "Google Play Store",
    "com.google.android.googlequicksearchbox": "Google Search App", "com.google.android.youtube": "YouTube",
    "com.google.android.apps.photos": "Google Photos", "com.google.android.gm": "Gmail",
    "com.google.android.apps.maps": "Google Maps", "com.android.chrome": "Google Chrome",
    "com.android.providers.contacts": "Contacts Provider", "com.android.providers.media": "Media Provider",
    "com.android.systemui": "System UI", "com.android.settings": "Settings"
}

GENERIC_WORDS = {'android', 'app', 'mobile', 'client', 'phone', 'global', 'main', 'release', 'intl', 'official', 'service', 'tools', 'tool', 'overlay', 'res'}

def get_friendly_name(pkg: str) -> str:
    """
    Transforms reverse-domain Android package identifiers into human-readable application titles.

    Args:
        pkg (str): Package identifier string (e.g., 'com.instagram.android').

    Returns:
        str: Human-readable application title.
    """
    if pkg in FRIENDLY_NAMES:
        return FRIENDLY_NAMES[pkg]
    parts = pkg.split(".")
    meaningful = [p for p in parts if p.lower() not in {'com', 'org', 'net', 'id', 'co', 'vn', 'io', 'src', 'tv'} and p.lower() not in GENERIC_WORDS]
    if not meaningful:
        meaningful = [p for p in parts if p.lower() not in {'com', 'org', 'net', 'id', 'co'}]
    if not meaningful:
        meaningful = parts

    best = meaningful[-1] if len(meaningful) == 1 else (" ".join(meaningful[-2:]) if len(meaningful) >= 2 else meaningful[0])
    s = re.sub(r'([a-z])([A-Z])', r'   ', best)
    s = re.sub(r'([a-zA-Z])([0-9])', r'   ', s)
    words = [w.capitalize() for w in re.findall(r'[A-Za-z0-9]+', s) if w.lower() not in GENERIC_WORDS]
    result = " ".join(words)
    return result if result else pkg

class DebloaterTab(ctk.CTkFrame):
    """
    Safe package management and non-destructive debloater interface.
    Allows user-space package disabling, uninstallation (`pm uninstall -k --user 0`),
    and instant package restoration with safety whitelisting.
    """
    def __init__(self, master, adb_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.adb = adb_manager
        self.packages_data = []
        self._search_job = None
        self.display_limit = 45

        # Header Toolbar
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=6, pady=(4, 6))

        ctk.CTkLabel(
            top_bar, text=I18n.t("debloater_title"),
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        ).pack(side="left")

        self.btn_scan = ctk.CTkButton(
            top_bar, text=I18n.t("debloater_btn_scan"),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#2563EB", hover_color="#1D4ED8", height=34, corner_radius=8,
            command=self.scan_packages
        )
        self.btn_scan.pack(side="right", padx=(10, 0))

        self.search_entry = ctk.CTkEntry(
            top_bar, placeholder_text=I18n.t("debloater_search_placeholder"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=34, width=340, corner_radius=8
        )
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", self._on_search_key)

        # 2. Segmented Filter Bar
        filter_bar = ctk.CTkFrame(self, fg_color="transparent")
        filter_bar.pack(fill="x", padx=6, pady=(0, 8))

        self.filter_var = ctk.StringVar(value=I18n.t("debloater_tab_all"))
        self.segmented_filter = ctk.CTkSegmentedButton(
            filter_bar, values=[I18n.t("debloater_tab_all"), I18n.t("debloater_tab_safe"), I18n.t("debloater_tab_user"), I18n.t("debloater_tab_system")],
            variable=self.filter_var, height=32, corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=lambda v: self.render_list(reset_scroll=True)
        )
        self.segmented_filter.pack(side="left")

        self.lbl_count = ctk.CTkLabel(
            filter_bar, text=I18n.t("debloater_count", count=0),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("#64748B", "#94A3B8")
        )
        self.lbl_count.pack(side="right")

        # 3. Scrollable List Box
        self.list_frame = ctk.CTkScrollableFrame(
            self, corner_radius=14,
            fg_color=("#FFFFFF", "#161F30"),
            border_width=1, border_color=("#E2E8F0", "#1E293B")
        )
        self.list_frame.pack(fill="both", expand=True, padx=4, pady=(2, 4))
        self.list_frame.grid_columnconfigure(0, weight=1)

        self.lbl_empty = ctk.CTkLabel(
            self.list_frame, text=I18n.t("debloater_empty"),
            font=ctk.CTkFont(family="Segoe UI", size=13), text_color=("#64748B", "#94A3B8")
        )
        self.lbl_empty.pack(pady=50)

    def show_disclaimer_dialog(self):
        from ..components.debloat_disclaimer_dialog import DebloatDisclaimerDialog
        self.after(50, lambda: DebloatDisclaimerDialog(self.winfo_toplevel()))

    def _on_search_key(self, event):
        if self._search_job:
            self.after_cancel(self._search_job)
        self._search_job = self.after(250, lambda: self.render_list(reset_scroll=True))

    def scan_packages(self):
        self.btn_scan.configure(state="disabled", text=I18n.t("debloater_btn_scanning"))
        def _worker():
            dis_out = self.adb.shell("pm list packages -d")
            disabled_set = set([line.replace("package:", "").strip() for line in dis_out.splitlines() if line.strip()])

            user_out = self.adb.shell("pm list packages -3")
            user_set = set([line.replace("package:", "").strip() for line in user_out.splitlines() if line.strip()])

            sys_out = self.adb.shell("pm list packages -s")
            sys_set = set([line.replace("package:", "").strip() for line in sys_out.splitlines() if line.strip()])

            parsed = []
            for pkg in sorted(user_set):
                parsed.append({
                    "pkg": pkg, "type": "USER", "name": get_friendly_name(pkg),
                    "is_disabled": pkg in disabled_set,
                    "safety": "USER"
                })

            for pkg in sorted(sys_set):
                safety = "CORE" if pkg in CORE_CRITICAL_PACKAGES else ("SAFE" if pkg in SAFE_BLOATWARE_PACKAGES else "SYSTEM")
                parsed.append({
                    "pkg": pkg, "type": "SYSTEM", "name": get_friendly_name(pkg),
                    "is_disabled": pkg in disabled_set,
                    "safety": safety
                })

            self.packages_data = parsed
            self.after(0, self._on_scan_done)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_scan_done(self):
        self.btn_scan.configure(state="normal", text=I18n.t("debloater_btn_scan"))
        self.display_limit = 45
        self.render_list(reset_scroll=True)

    def render_list(self, reset_scroll: bool = False):
        if reset_scroll:
            self.display_limit = 45

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        search_q = self.search_entry.get().strip().lower()
        active_filter = self.filter_var.get()

        filtered = []
        for item in self.packages_data:
            if active_filter == I18n.t("debloater_tab_user") and item["type"] != "USER":
                continue
            if active_filter == I18n.t("debloater_tab_system") and item["type"] != "SYSTEM":
                continue
            if active_filter == I18n.t("debloater_tab_safe") and item.get("safety") != "SAFE":
                continue

            if search_q:
                if search_q not in item["pkg"].lower() and search_q not in item["name"].lower():
                    continue
            filtered.append(item)

        self.lbl_count.configure(text=I18n.t("debloater_count", count=len(filtered)))

        if not filtered:
            ctk.CTkLabel(
                self.list_frame, text=I18n.t("debloater_no_match"),
                font=ctk.CTkFont(family="Segoe UI", size=13), text_color=("#64748B", "#94A3B8")
            ).pack(pady=40)
            self._reset_scroll_to_top()
            return

        to_render = filtered[:self.display_limit]
        for item in to_render:
            pkg = item["pkg"]
            pkg_type = item["type"]
            app_name = item["name"]
            is_disabled = item.get("is_disabled", False)
            safety = item.get("safety", "SYSTEM")

            row = ctk.CTkFrame(
                self.list_frame, fg_color=("#F8FAFC", "#111827"),
                corner_radius=10, border_width=1, border_color=("#E2E8F0", "#1E293B"),
                height=52
            )
            row.pack(fill="x", padx=8, pady=3)
            row.pack_propagate(False)

            if safety == "CORE":
                badge_text = I18n.t("debloater_badge_core")
                badge_fg = ("#F1F5F9", "#1E293B")
                badge_tc = ("#64748B", "#94A3B8")
            elif safety == "SAFE":
                badge_text = I18n.t("debloater_badge_safe")
                badge_fg = ("#ECFDF5", "#064E3B")
                badge_tc = ("#059669", "#10B981")
            elif safety == "USER":
                badge_text = I18n.t("debloater_badge_user")
                badge_fg = ("#EFF6FF", "#1E293B")
                badge_tc = ("#2563EB", "#60A5FA")
            else:
                badge_text = I18n.t("debloater_badge_system")
                badge_fg = ("#FEF3C7", "#78350F")
                badge_tc = ("#D97706", "#FBBF24")

            lbl_badge = ctk.CTkLabel(
                row, text=badge_text, font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                fg_color=badge_fg, text_color=badge_tc, corner_radius=6, padx=8, pady=2
            )
            lbl_badge.pack(side="left", padx=(12, 10))

            info_box = ctk.CTkFrame(row, fg_color="transparent")
            info_box.pack(side="left", fill="both", expand=True, pady=6)

            lbl_title = ctk.CTkLabel(
                info_box, text=app_name,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=("#0F172A", "#F8FAFC")
            )
            lbl_title.pack(anchor="w")

            lbl_sub = ctk.CTkLabel(
                info_box, text=pkg,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=("#64748B", "#94A3B8")
            )
            lbl_sub.pack(anchor="w")

            act_box = ctk.CTkFrame(row, fg_color="transparent")
            act_box.pack(side="right", padx=(6, 12))

            if safety == "CORE":
                lbl_locked = ctk.CTkLabel(
                    act_box, text=I18n.t("debloater_locked"), font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    fg_color=("#F1F5F9", "#1E293B"), text_color=("#64748B", "#94A3B8"),
                    corner_radius=8, padx=12, pady=6
                )
                lbl_locked.pack(side="right")
            else:
                if is_disabled:
                    btn_toggle = ctk.CTkButton(
                        act_box, text=I18n.t("debloater_btn_enable"), width=88, height=30, corner_radius=8,
                        fg_color="#059669", hover_color="#047857", text_color="#FFFFFF",
                        font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                        command=lambda p=pkg, it=item, r_row=row: self.execute_enable(p, it, r_row)
                    )
                else:
                    btn_toggle = ctk.CTkButton(
                        act_box, text=I18n.t("debloater_btn_disable"), width=88, height=30, corner_radius=8,
                        fg_color="#E11D48", hover_color="#BE123C", text_color="#FFFFFF",
                        font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                        command=lambda p=pkg, n=app_name, it=item, s=safety, r_row=row: self.prompt_action("disable", p, n, it, s, r_row)
                    )
                btn_toggle.pack(side="left", padx=3)

                btn_uninstall = ctk.CTkButton(
                    act_box, text=I18n.t("debloater_btn_uninstall"), width=74, height=30, corner_radius=8,
                    fg_color=("#FEE2E2", "#450A0A"), text_color=("#DC2626", "#F87171"),
                    hover_color=("#FECACA", "#7F1D1D"),
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    command=lambda p=pkg, n=app_name, it=item, s=safety, r_row=row: self.prompt_action("uninstall", p, n, it, s, r_row)
                )
                btn_uninstall.pack(side="left", padx=3)

        if len(filtered) > self.display_limit:
            btn_more = ctk.CTkButton(
                self.list_frame, text="↓ " + I18n.t("debloater_btn_load_more"),
                height=38, corner_radius=10, fg_color=("#EFF6FF", "#1E293B"), text_color=("#2563EB", "#60A5FA"),
                hover_color=("#DBEAFE", "#334155"), font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                command=self._load_more
            )
            btn_more.pack(fill="x", padx=14, pady=12)

        if reset_scroll:
            self._reset_scroll_to_top()

    def _reset_scroll_to_top(self):
        try:
            self.list_frame._parent_canvas.yview_moveto(0.0)
        except Exception:
            pass

    def _load_more(self):
        self.display_limit += 45
        self.render_list(reset_scroll=False)

    def prompt_action(self, action_type: str, pkg: str, app_name: str, item_dict: dict, safety: str, row_widget):
        from ..components.confirm_dialog import ConfirmDialog
        title = I18n.t("confirm_title_uninstall") if action_type == "uninstall" else I18n.t("confirm_title_disable")
        callback = (lambda: self.execute_uninstall(pkg, item_dict, row_widget)) if action_type == "uninstall" else (lambda: self.execute_disable(pkg, item_dict, row_widget))

        require_challenge = (safety == "SYSTEM" and action_type == "uninstall")

        ConfirmDialog(
            self.winfo_toplevel(),
            title=title,
            app_name=app_name,
            package_name=pkg,
            is_system=(safety != "USER"),
            action_type=action_type,
            require_challenge=require_challenge,
            on_confirm_callback=callback
        )

    def execute_disable(self, pkg: str, item_dict: dict, row_widget):
        res = self.adb.shell(f"pm disable-user --user 0 {pkg}")
        item_dict["is_disabled"] = True
        for child in row_widget.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                btns = [b for b in child.winfo_children() if isinstance(b, ctk.CTkButton)]
                if btns:
                    btns[0].configure(
                        text=I18n.t("debloater_btn_enable"), fg_color="#059669", hover_color="#047857",
                        command=lambda p=pkg, it=item_dict, r=row_widget: self.execute_enable(p, it, r)
                    )

    def execute_enable(self, pkg: str, item_dict: dict, row_widget):
        self.adb.shell(f"pm enable {pkg}; cmd package install-existing {pkg}")
        item_dict["is_disabled"] = False
        for child in row_widget.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                btns = [b for b in child.winfo_children() if isinstance(b, ctk.CTkButton)]
                if btns:
                    btns[0].configure(
                        text=I18n.t("debloater_btn_disable"), fg_color="#E11D48", hover_color="#BE123C",
                        command=lambda p=pkg, n=item_dict["name"], it=item_dict, s=item_dict.get("safety", "SYSTEM"), r=row_widget: self.prompt_action("disable", p, n, it, s, r)
                    )

    def execute_uninstall(self, pkg: str, item_dict: dict, row_widget):
        self.adb.shell(f"pm uninstall --user 0 {pkg}")
        row_widget.destroy()
        if item_dict in self.packages_data:
            self.packages_data.remove(item_dict)
        self.lbl_count.configure(text=I18n.t("debloater_count", count=len(self.packages_data)))
