import customtkinter as ctk
from core.settings_manager import SettingsManager
from core.i18n import I18n
from ..theme_manager import ThemeManager

class SettingsOverlay(ctk.CTkFrame):
    """In-App Modal Settings Card Terpusat Sempurna (Zero-Artifact, Fixed Center 650x480)."""
    def __init__(self, master, on_close=None, on_change=None, **kwargs):
        super().__init__(
            master, width=650, height=480, corner_radius=14,
            fg_color=("#FFFFFF", "#111827"),
            border_width=1, border_color=("#CBD5E1", "#1E293B"),
            **kwargs
        )
        self.grid_propagate(False)
        self.pack_propagate(False)

        self.on_close_cb = on_close
        self.on_change_cb = on_change
        self.settings = SettingsManager.get_instance()
        self.is_visible = False
        self.current_page_fn = self._show_appearance

        self.grid_columnconfigure(0, weight=0, minsize=200)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Nav Bar (Fixed 200px)
        self.nav_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=("#F1F5F9", "#0E1422"), border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame.grid_propagate(False)
        self.nav_frame.grid_columnconfigure(0, weight=1)

        self.lbl_title_nav = ctk.CTkLabel(
            self.nav_frame, text=I18n.t("settings_title"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        self.lbl_title_nav.pack(anchor="w", padx=16, pady=(18, 14))

        self.btn_nav1 = self._make_nav_btn(I18n.t("settings_cat_appearance"), self._show_appearance)
        self.btn_nav2 = self._make_nav_btn(I18n.t("settings_cat_engine"), self._show_engine)
        self.btn_nav3 = self._make_nav_btn(I18n.t("settings_cat_security"), self._show_security)
        self.btn_nav4 = self._make_nav_btn(I18n.t("settings_cat_about"), self._show_about)

        # Right Content Area (Fixed 450px)
        self.right_container = ctk.CTkFrame(self, width=450, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=16)
        self.right_container.grid_propagate(False)
        self.right_container.grid_columnconfigure(0, weight=1)
        self.right_container.grid_rowconfigure(1, weight=1)

        # Header with Close [ X ] Button
        self.top_hdr = ctk.CTkFrame(self.right_container, height=36, fg_color="transparent")
        self.top_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        self.lbl_section_title = ctk.CTkLabel(
            self.top_hdr, text=I18n.t("settings_title"),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#64748B", "#94A3B8")
        )
        self.lbl_section_title.pack(side="left", padx=2)

        self.btn_close = ctk.CTkButton(
            self.top_hdr, text="✕", width=32, height=32, corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=("#F1F5F9", "#1E293B"), text_color=("#64748B", "#94A3B8"),
            hover_color=("#E2E8F0", "#334155"),
            command=self.hide
        )
        self.btn_close.pack(side="right")

        self.active_frame = None
        self._show_appearance()

    def _make_nav_btn(self, text: str, command):
        btn = ctk.CTkButton(
            self.nav_frame, text=text,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            anchor="w", fg_color="transparent", text_color=("#475569", "#CBD5E1"),
            hover_color=("#E2E8F0", "#1E293B"), height=36, corner_radius=8, command=command
        )
        btn.pack(fill="x", padx=10, pady=2)
        return btn

    def _reset_nav_highlights(self):
        for btn in [self.btn_nav1, self.btn_nav2, self.btn_nav3, self.btn_nav4]:
            btn.configure(fg_color="transparent", text_color=("#475569", "#CBD5E1"))

    def _switch_page(self, active_btn):
        if self.active_frame:
            self.active_frame.destroy()
        self._reset_nav_highlights()
        active_btn.configure(fg_color=("#DBEAFE", "#1E3A8A"), text_color=("#1D4ED8", "#93C5FD"))
        self.active_frame = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.active_frame.grid(row=1, column=0, sticky="nsew")

    def _show_appearance(self):
        self.current_page_fn = self._show_appearance
        self._switch_page(self.btn_nav1)
        
        ctk.CTkLabel(self.active_frame, text=I18n.t("settings_cat_appearance"), font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor="w", pady=(0, 14))

        ctk.CTkLabel(self.active_frame, text=I18n.t("settings_lbl_theme"), font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=("#334155", "#CBD5E1")).pack(anchor="w", pady=(0, 6))
        cur_theme = self.settings.get("theme", "light")
        theme_val = I18n.t("settings_theme_light") if cur_theme == "light" else I18n.t("settings_theme_dark")
        
        self.seg_theme = ctk.CTkSegmentedButton(
            self.active_frame, values=[I18n.t("settings_theme_light"), I18n.t("settings_theme_dark")], height=36,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._on_theme_changed
        )
        self.seg_theme.set(theme_val)
        self.seg_theme.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(self.active_frame, text=I18n.t("settings_lbl_language"), font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=("#334155", "#CBD5E1")).pack(anchor="w", pady=(0, 6))
        cur_lang = self.settings.get("language", "en")
        lang_val = "English (US)" if cur_lang == "en" else "Bahasa Indonesia"
        
        self.seg_lang = ctk.CTkSegmentedButton(
            self.active_frame, values=["English (US)", "Bahasa Indonesia"], height=36,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._on_lang_changed
        )
        self.seg_lang.set(lang_val)
        self.seg_lang.pack(fill="x", pady=(0, 14))

        self.sw_sound = ctk.CTkSwitch(
            self.active_frame, text=I18n.t("settings_sw_sound"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self._on_sound_toggle
        )
        if self.settings.get("sound_effects", True):
            self.sw_sound.select()
        else:
            self.sw_sound.deselect()
        self.sw_sound.pack(anchor="w", pady=(6, 0))

    def _show_engine(self):
        self.current_page_fn = self._show_engine
        self._switch_page(self.btn_nav2)
        
        ctk.CTkLabel(self.active_frame, text=I18n.t("settings_cat_engine"), font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor="w", pady=(0, 14))

        ctk.CTkLabel(self.active_frame, text=I18n.t("settings_lbl_rate"), font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=("#334155", "#CBD5E1")).pack(anchor="w", pady=(0, 6))
        rate = self.settings.get("polling_rate", 0.5)
        rate_map = {0.5: I18n.t("settings_rate_fast"), 1.5: I18n.t("settings_rate_balanced"), 3.0: I18n.t("settings_rate_eco")}
        
        self.seg_rate = ctk.CTkSegmentedButton(
            self.active_frame, values=[I18n.t("settings_rate_fast"), I18n.t("settings_rate_balanced"), I18n.t("settings_rate_eco")], height=36,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self._on_rate_changed
        )
        self.seg_rate.set(rate_map.get(rate, I18n.t("settings_rate_fast")))
        self.seg_rate.pack(fill="x", pady=(0, 14))



    def _show_security(self):
        self.current_page_fn = self._show_security
        self._switch_page(self.btn_nav3)

        ctk.CTkLabel(self.active_frame, text=I18n.t("settings_cat_security"), font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor="w", pady=(0, 14))

        self.sw_debloat_vis = ctk.CTkSwitch(
            self.active_frame, text=I18n.t("settings_sw_debloat_vis"),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._on_debloat_vis_toggle
        )
        if self.settings.get("debloater_tab_visible", False):
            self.sw_debloat_vis.select()
        else:
            self.sw_debloat_vis.deselect()
        self.sw_debloat_vis.pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            self.active_frame,
            text=I18n.t("settings_desc_debloat_vis"),
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color=("#64748B", "#94A3B8"), wraplength=380, justify="left"
        ).pack(anchor="w", pady=(0, 16))

        self.sw_challenge = ctk.CTkSwitch(
            self.active_frame, text=I18n.t("settings_sw_challenge"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=lambda: self.settings.set("debloater_require_challenge", self.sw_challenge.get() == 1)
        )
        if self.settings.get("debloater_require_challenge", True):
            self.sw_challenge.select()
        else:
            self.sw_challenge.deselect()
        self.sw_challenge.pack(anchor="w", pady=(0, 8))

    def _show_about(self):
        self.current_page_fn = self._show_about
        self._switch_page(self.btn_nav4)

        ctk.CTkLabel(self.active_frame, text=I18n.t("settings_cat_about"), font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor="w", pady=(0, 10))

        # Main Spec Card (Pixel-Perfect 2-Column Grid)
        card = ctk.CTkFrame(self.active_frame, fg_color=("#F8FAFC", "#111827"), corner_radius=12, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        card.pack(fill="x", pady=(0, 12))

        # Header with Logo & Version Badge
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(14, 10))

        ctk.CTkLabel(hdr, text=I18n.t("settings_about_header"), font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), text_color=("#2563EB", "#60A5FA")).pack(side="left")
        ctk.CTkLabel(hdr, text="v1.0.0 PRO", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), fg_color=("#ECFDF5", "#064E3B"), text_color=("#059669", "#10B981"), corner_radius=6, padx=8, pady=2).pack(side="right")

        # 2-Column Grid (Perfect Vertical Straight Alignment)
        grid_spec = ctk.CTkFrame(card, fg_color="transparent")
        grid_spec.pack(fill="x", padx=16, pady=(0, 14))
        grid_spec.grid_columnconfigure(0, weight=0)
        grid_spec.grid_columnconfigure(1, weight=1)

        specs = [
            ("Developer", "RianSyrrus"),
            ("Engine", "Scrcpy 4.0 (SDL 3.4.8 • libavcodec 62)"),
            ("ADB Core", "Android Debug Bridge 1.0.41 (v35.0.1)"),
            ("Architecture", "Windows 64-bit (x64) • ARM64 Prism"),
            ("License", "Open Source (MIT) • Production-Grade")
        ]

        for idx, (label_key, val_text) in enumerate(specs):
            # Left Key (Straight alignment, bold)
            lbl_k = ctk.CTkLabel(
                grid_spec, text=label_key,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=("#475569", "#94A3B8")
            )
            lbl_k.grid(row=idx, column=0, sticky="w", padx=(0, 16), pady=3)

            # Right Value (Right-aligned, clean contrast)
            lbl_v = ctk.CTkLabel(
                grid_spec, text=val_text,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold" if idx == 0 else "normal"),
                text_color=("#2563EB", "#60A5FA") if idx == 0 else ("#0F172A", "#F8FAFC")
            )
            lbl_v.grid(row=idx, column=1, sticky="e", pady=3)

        # Description Box
        ctk.CTkLabel(
            self.active_frame,
            text=I18n.t("settings_about_desc"),
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color=("#475569", "#CBD5E1"), wraplength=380, justify="left"
        ).pack(anchor="w", pady=(2, 0))

    def _on_theme_changed(self, choice: str):
        choice_str = str(choice).lower()
        mode = "dark" if ("dark" in choice_str or "gelap" in choice_str) else "light"
        print(f"[SETTINGS_OVERLAY] Theme choice clicked: '{choice}' -> Setting Mode: '{mode}'")
        self.settings.set("theme", mode)
        ThemeManager.set_theme(mode)
        if self.on_change_cb:
            self.on_change_cb("theme", mode)

    def _on_lang_changed(self, choice: str):
        new_lang = "en" if "English" in choice else "id"
        if new_lang != I18n.get_language():
            print(f"[SETTINGS_OVERLAY] Language switched in-place to: '{new_lang}'")
            I18n.set_language(new_lang)
            if self.on_change_cb:
                self.on_change_cb("language", new_lang)
            self.refresh_i18n_texts()

    def refresh_i18n_texts(self):
        self.lbl_title_nav.configure(text=I18n.t("settings_title"))
        self.lbl_section_title.configure(text=I18n.t("settings_title"))
        self.btn_nav1.configure(text=I18n.t("settings_cat_appearance"))
        self.btn_nav2.configure(text=I18n.t("settings_cat_engine"))
        self.btn_nav3.configure(text=I18n.t("settings_cat_security"))
        self.btn_nav4.configure(text=I18n.t("settings_cat_about"))
        if self.current_page_fn:
            self.current_page_fn()

    def _on_sound_toggle(self):
        self.settings.set("sound_effects", self.sw_sound.get() == 1)

    def _on_rate_changed(self, choice: str):
        if "0.5" in choice:
            self.settings.set("polling_rate", 0.5)
        elif "1.5" in choice:
            self.settings.set("polling_rate", 1.5)
        else:
            self.settings.set("polling_rate", 3.0)

    def _on_debloat_vis_toggle(self):
        is_vis = (self.sw_debloat_vis.get() == 1)
        self.settings.set("debloater_tab_visible", is_vis)
        if self.on_change_cb:
            self.on_change_cb("debloater_tab_visible", is_vis)

    def show(self):
        self.is_visible = True
        self.place(relx=0.5, rely=0.5, anchor="center")
        self.lift()
        print("[SETTINGS_OVERLAY] Settings opened in-app centered overlay.")

    def hide(self):
        self.is_visible = False
        self.place_forget()
        if self.on_close_cb:
            self.on_close_cb()
        print("[SETTINGS_OVERLAY] Settings closed.")
