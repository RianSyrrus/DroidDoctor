import customtkinter as ctk
import threading, time
from core.i18n import I18n

class StorageTab(ctk.CTkFrame):
    """
    Intelligent internal storage cleaner view with personal data safety guarantees.
    Scans and cleans application cache, gallery thumbnails, and debug crash logs
    while strictly protecting user media, camera photos, downloads, and documents.
    """
    def __init__(self, master, adb_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.adb = adb_manager
        self.confirm_dialog = None

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header Toolbar
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(2, 10))

        header_info = ctk.CTkFrame(top_bar, fg_color="transparent")
        header_info.pack(side="left")

        ctk.CTkLabel(
            header_info, text=I18n.t("storage_title"),
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_info, text=I18n.t("storage_subtitle"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("#64748B", "#94A3B8")
        ).pack(anchor="w", pady=(2, 0))

        self.btn_scan = ctk.CTkButton(
            top_bar, text=I18n.t("storage_btn_scan"),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#2563EB", hover_color="#1D4ED8", height=38, width=130, corner_radius=8,
            command=self.scan_storage
        )
        self.btn_scan.pack(side="right")

        # Two-Pane Content Area
        # Left Pane: Categories with Checkboxes & Descriptions
        self.left_card = ctk.CTkFrame(self, corner_radius=14, fg_color=("#FFFFFF", "#111827"), border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.left_card.grid(row=1, column=0, sticky="nsew", padx=(4, 6), pady=(0, 10))
        self.left_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.left_card, text=I18n.t("card_storage"),
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=("#2563EB", "#60A5FA")
        ).pack(anchor="w", padx=18, pady=(16, 12))

        self.categories_data = {
            "app_cache": {
                "title": I18n.t("storage_app_cache"),
                "desc": I18n.t("storage_app_cache_desc"),
                "size_mb": 148.5,
                "size_str": "148.5 MB",
                "paths": [
                    "/sdcard/Android/data/com.instagram.android/cache/ (48.2 MB)",
                    "/sdcard/Android/data/com.zhiliaoapp.musically/cache/ (62.1 MB)",
                    "/sdcard/Android/data/com.android.chrome/cache/ (38.2 MB)"
                ]
            },
            "thumbnails": {
                "title": I18n.t("storage_thumbnails"),
                "desc": I18n.t("storage_thumbnails_desc"),
                "size_mb": 84.2,
                "size_str": "84.2 MB",
                "paths": [
                    "/sdcard/DCIM/.thumbnails/.thumbdata4--1967290299 (54.0 MB)",
                    "/sdcard/DCIM/.thumbnails/thumb_gallery_cache.bin (30.2 MB)"
                ]
            },
            "logs": {
                "title": I18n.t("storage_temp_files"),
                "desc": I18n.t("storage_temp_files_desc"),
                "size_mb": 32.0,
                "size_str": "32.0 MB",
                "paths": [
                    "/sdcard/MIUI/debug_log/dump_anr_2024.log (18.4 MB)",
                    "/sdcard/Android/data/com.miui.analytics/files/log/ (13.6 MB)"
                ]
            },
            "empty_folders": {
                "title": I18n.t("storage_empty_folders"),
                "desc": I18n.t("storage_empty_folders_desc"),
                "size_mb": 0.0,
                "size_str": "14 Folders",
                "paths": [
                    "/sdcard/Android/data/com.oldapp.removed/ (Empty)",
                    "/sdcard/Download/.temp_download/ (Empty)",
                    "/sdcard/Tencent/.temp/ (Empty)",
                    "/sdcard/Alarms/.hidden/ (Empty)"
                ]
            }
        }

        self.cat_widgets = {}
        for key, data in self.categories_data.items():
            self._create_category_card(key, data)

        # Right Pane: Personal Data Safety Shield + Itemized File Inspector
        self.right_card = ctk.CTkFrame(self, corner_radius=14, fg_color=("#FFFFFF", "#111827"), border_width=1, border_color=("#E2E8F0", "#1E293B"))
        self.right_card.grid(row=1, column=1, sticky="nsew", padx=(6, 4), pady=(0, 10))
        self.right_card.grid_columnconfigure(0, weight=1)
        self.right_card.grid_rowconfigure(2, weight=1)

        # Green Safety Shield Guarantee Box (High Contrast)
        shield_frame = ctk.CTkFrame(self.right_card, corner_radius=10, fg_color=("#ECFDF5", "#064E3B"), border_width=1, border_color=("#A7F3D0", "#047857"))
        shield_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 12))

        ctk.CTkLabel(
            shield_frame, text=f"🔒 {I18n.t('storage_shield_title')}",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#065F46", "#A7F3D0")
        ).pack(anchor="w", padx=14, pady=(10, 3))

        ctk.CTkLabel(
            shield_frame, text=I18n.t("storage_shield_desc"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("#047857", "#D1FAE5"), wraplength=420, justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 10))

        # File Inspector Header
        inspector_hdr = ctk.CTkFrame(self.right_card, fg_color="transparent")
        inspector_hdr.grid(row=1, column=0, sticky="ew", padx=16, pady=(4, 8))

        ctk.CTkLabel(
            inspector_hdr, text=I18n.t("storage_inspector_title"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=("#2563EB", "#60A5FA")
        ).pack(side="left")

        self.lbl_inspecting_cat = ctk.CTkLabel(
            inspector_hdr, text="",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=("#EFF6FF", "#1E293B"), text_color=("#2563EB", "#60A5FA"),
            corner_radius=6, padx=10, pady=3
        )
        self.lbl_inspecting_cat.pack(side="right")

        # Scrollable File Inspector Box
        self.inspector_scroll = ctk.CTkScrollableFrame(
            self.right_card, corner_radius=10, fg_color=("#F8FAFC", "#0E1422"),
            border_width=1, border_color=("#E2E8F0", "#1E293B")
        )
        self.inspector_scroll.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.inspector_scroll.grid_columnconfigure(0, weight=1)

        self._show_inspector_files("app_cache")

        # 3. Bottom Action Bar
        bottom_bar = ctk.CTkFrame(self, corner_radius=12, fg_color=("#FFFFFF", "#111827"), border_width=1, border_color=("#E2E8F0", "#1E293B"))
        bottom_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 4))
        bottom_bar.grid_columnconfigure(0, weight=1)

        self.lbl_selected_summary = ctk.CTkLabel(
            bottom_bar, text="",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        self.lbl_selected_summary.pack(side="left", padx=20, pady=14)

        self.btn_clean = ctk.CTkButton(
            bottom_bar, text=I18n.t("storage_btn_clean"),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#059669", hover_color="#047857", height=40, width=180, corner_radius=8,
            command=self.prompt_clean_confirmation
        )
        self.btn_clean.pack(side="right", padx=20, pady=10)

        self._update_selected_summary()
        self.after(300, self.scan_storage)

    def _create_category_card(self, key: str, data: dict):
        card = ctk.CTkFrame(self.left_card, fg_color=("#F8FAFC", "#161F30"), corner_radius=10, border_width=1, border_color=("#E2E8F0", "#1E293B"))
        card.pack(fill="x", padx=16, pady=5)
        card.grid_columnconfigure(1, weight=1)

        chk = ctk.CTkCheckBox(
            card, text="", width=22, height=22, corner_radius=5,
            command=self._on_check_toggle
        )
        chk.select()
        chk.grid(row=0, column=0, rowspan=2, padx=(14, 8), pady=12)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="w", pady=(10, 2))

        lbl_title = ctk.CTkLabel(
            info_frame, text=data["title"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        lbl_title.pack(side="left")

        lbl_size = ctk.CTkLabel(
            card, text=data["size_str"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#2563EB", "#60A5FA")
        )
        lbl_size.grid(row=0, column=2, sticky="e", padx=(4, 14), pady=(10, 2))

        lbl_desc = ctk.CTkLabel(
            card, text=data["desc"],
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("#475569", "#CBD5E1"), wraplength=310, justify="left"
        )
        lbl_desc.grid(row=1, column=1, columnspan=2, sticky="w", padx=(0, 14), pady=(0, 10))

        # Make card clickable to inspect files
        for w in [card, info_frame, lbl_title, lbl_desc]:
            w.bind("<Button-1>", lambda e, k=key: self._show_inspector_files(k))

        self.cat_widgets[key] = {
            "chk": chk, "lbl_size": lbl_size, "data": data, "card": card
        }

    def _show_inspector_files(self, category_key: str):
        data = self.categories_data.get(category_key, {})
        self.lbl_inspecting_cat.configure(text=data.get("title", ""))

        # Sorot kartu kategori aktif
        for k, w in self.cat_widgets.items():
            if k == category_key:
                w["card"].configure(border_color=("#2563EB", "#60A5FA"), border_width=2)
            else:
                w["card"].configure(border_color=("#E2E8F0", "#1E293B"), border_width=1)

        for w in self.inspector_scroll.winfo_children():
            w.destroy()

        paths = data.get("paths", [])
        if not paths:
            empty_box = ctk.CTkFrame(self.inspector_scroll, corner_radius=10, fg_color=("#ECFDF5", "#064E3B"), border_width=1, border_color=("#A7F3D0", "#047857"))
            empty_box.pack(fill="x", padx=4, pady=24)
            ctk.CTkLabel(
                empty_box, text="✨ " + I18n.t("storage_cat_clean_title"),
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=("#065F46", "#A7F3D0")
            ).pack(anchor="w", padx=14, pady=(12, 4))
            ctk.CTkLabel(
                empty_box, text=I18n.t("storage_cat_clean_desc"),
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=("#047857", "#D1FAE5"), wraplength=380, justify="left"
            ).pack(anchor="w", padx=14, pady=(0, 12))
            return

        for idx, path_str in enumerate(paths, start=1):
            row = ctk.CTkFrame(
                self.inspector_scroll, fg_color=("#FFFFFF", "#161F30"),
                corner_radius=8, border_width=1, border_color=("#E2E8F0", "#1E293B"), height=42
            )
            row.pack(fill="x", pady=3)
            row.pack_propagate(False)

            ctk.CTkLabel(
                row, text=f"{idx}.", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=("#2563EB", "#60A5FA")
            ).pack(side="left", padx=(10, 6))

            ctk.CTkLabel(
                row, text=path_str, font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=("#0F172A", "#F1F5F9"), anchor="w"
            ).pack(side="left", fill="x", expand=True, padx=4)

    def _on_check_toggle(self):
        self._update_selected_summary()

    def _update_selected_summary(self):
        tot_mb = 0.0
        selected_count = 0
        for key, w in self.cat_widgets.items():
            if w["chk"].get() == 1:
                tot_mb += w["data"].get("size_mb", 0.0)
                selected_count += 1

        size_str = f"{tot_mb:.1f} MB" if tot_mb > 0 else "0.0 MB"
        self.lbl_selected_summary.configure(
            text=I18n.t("storage_selected_total", size=size_str, count=selected_count)
        )

        if selected_count == 0:
            self.btn_clean.configure(state="disabled", fg_color=("#E2E8F0", "#334155"))
        else:
            self.btn_clean.configure(state="normal", fg_color="#059669", hover_color="#047857")

    def scan_storage(self):
        """Memindai penyimpanan riil perangkat yang terhubung melalui ADB."""
        self.btn_scan.configure(state="disabled", text=I18n.t("storage_btn_scanning"))
        
        def _worker():
            results = {
                "app_cache": {"size_mb": 0.0, "size_str": "0.0 MB", "paths": []},
                "thumbnails": {"size_mb": 0.0, "size_str": "0.0 MB", "paths": []},
                "logs": {"size_mb": 0.0, "size_str": "0.0 MB", "paths": []},
                "empty_folders": {"size_mb": 0.0, "size_str": "0 Folders", "paths": []}
            }
            
            try:
                # 1. App Cache
                out_cache = self.adb.shell("du -sk /sdcard/Android/data/*/cache /sdcard/Android/media/*/cache 2>/dev/null", timeout=4.0)
                tot_cache_kb = 0
                for line in out_cache.splitlines():
                    parts = line.strip().split(None, 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        kb = int(parts[0])
                        p = parts[1]
                        tot_cache_kb += kb
                        if kb >= 1024:
                            mb = kb / 1024.0
                            results["app_cache"]["paths"].append(f"{p} ({mb:.1f} MB)")
                        elif kb > 0:
                            results["app_cache"]["paths"].append(f"{p} ({kb} KB)")
                results["app_cache"]["size_mb"] = round(tot_cache_kb / 1024.0, 1)
                results["app_cache"]["size_str"] = f"{results['app_cache']['size_mb']:.1f} MB" if results["app_cache"]["size_mb"] > 0 else (f"{tot_cache_kb} KB" if tot_cache_kb > 0 else "0.0 MB")

                # 2. Thumbnails Cache
                out_thumb = self.adb.shell("du -sk /sdcard/DCIM/.thumbnails /sdcard/Pictures/.thumbnails /sdcard/MIUI/Gallery/cloud/.thumbnailFile 2>/dev/null", timeout=3.0)
                tot_thumb_kb = 0
                for line in out_thumb.splitlines():
                    parts = line.strip().split(None, 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        kb = int(parts[0])
                        p = parts[1]
                        tot_thumb_kb += kb
                        if kb >= 1024:
                            mb = kb / 1024.0
                            results["thumbnails"]["paths"].append(f"{p} ({mb:.1f} MB)")
                        elif kb > 0:
                            results["thumbnails"]["paths"].append(f"{p} ({kb} KB)")
                results["thumbnails"]["size_mb"] = round(tot_thumb_kb / 1024.0, 1)
                results["thumbnails"]["size_str"] = f"{results['thumbnails']['size_mb']:.1f} MB" if results["thumbnails"]["size_mb"] > 0 else (f"{tot_thumb_kb} KB" if tot_thumb_kb > 0 else "0.0 MB")

                # 3. System Logs & Crash Dumps
                out_logs = self.adb.shell("du -sk /sdcard/MIUI/debug_log /sdcard/log /sdcard/MIUI/anr /sdcard/Android/data/com.miui.analytics/files/log 2>/dev/null", timeout=3.0)
                tot_log_kb = 0
                for line in out_logs.splitlines():
                    parts = line.strip().split(None, 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        kb = int(parts[0])
                        p = parts[1]
                        tot_log_kb += kb
                        if kb >= 1024:
                            mb = kb / 1024.0
                            results["logs"]["paths"].append(f"{p} ({mb:.1f} MB)")
                        elif kb > 0:
                            results["logs"]["paths"].append(f"{p} ({kb} KB)")
                results["logs"]["size_mb"] = round(tot_log_kb / 1024.0, 1)
                results["logs"]["size_str"] = f"{results['logs']['size_mb']:.1f} MB" if results["logs"]["size_mb"] > 0 else (f"{tot_log_kb} KB" if tot_log_kb > 0 else "0.0 MB")

                # 4. Empty Hidden Folders
                out_empty = self.adb.shell("find /sdcard/Download /sdcard/Android/data -maxdepth 2 -type d -empty 2>/dev/null | head -n 35", timeout=3.0)
                empty_list = [l.strip() for l in out_empty.splitlines() if l.strip()]
                results["empty_folders"]["paths"] = [f"{p} (Empty)" for p in empty_list]
                results["empty_folders"]["size_str"] = f"{len(empty_list)} Folders"
            except Exception as e:
                print(f"[STORAGE SCAN ERROR] {e}")

            self.after(0, lambda: self._on_scan_done(results))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_scan_done(self, results: dict):
        self.btn_scan.configure(state="normal", text=I18n.t("storage_btn_scan"))
        for key, res_data in results.items():
            if key in self.categories_data and key in self.cat_widgets:
                self.categories_data[key]["size_mb"] = res_data.get("size_mb", 0.0)
                self.categories_data[key]["size_str"] = res_data.get("size_str", "0.0 MB")
                self.categories_data[key]["paths"] = res_data.get("paths", [])
                self.cat_widgets[key]["data"]["size_mb"] = res_data.get("size_mb", 0.0)
                self.cat_widgets[key]["data"]["size_str"] = res_data.get("size_str", "0.0 MB")
                self.cat_widgets[key]["data"]["paths"] = res_data.get("paths", [])
                self.cat_widgets[key]["lbl_size"].configure(text=res_data.get("size_str", "0.0 MB"))

        self._show_inspector_files("app_cache")
        self._update_selected_summary()

    def prompt_clean_confirmation(self):
        if self.confirm_dialog is not None and self.confirm_dialog.winfo_exists():
            self.confirm_dialog.lift()
            self.confirm_dialog.focus_force()
            return
        from ..components.storage_confirm_dialog import StorageConfirmDialog
        
        tot_mb = 0.0
        selected_cats = []
        for key, w in self.cat_widgets.items():
            if w["chk"].get() == 1:
                tot_mb += w["data"].get("size_mb", 0.0)
                selected_cats.append(w["data"].get("title", ""))

        size_str = f"{tot_mb:.1f} MB"
        
        self.confirm_dialog = StorageConfirmDialog(
            self.winfo_toplevel(),
            total_size_str=size_str,
            categories_list=selected_cats,
            on_confirm_callback=self.execute_clean
        )

    def execute_clean(self):
        self.btn_clean.configure(state="disabled", text=I18n.t("storage_btn_cleaning"))
        
        def _clean_worker():
            try:
                # 1. Bersihkan App Cache jika dicentang
                if self.cat_widgets.get("app_cache", {}).get("chk", None) and self.cat_widgets["app_cache"]["chk"].get() == 1:
                    self.adb.shell("rm -rf /sdcard/Android/data/*/cache/* /sdcard/Android/media/*/cache/* 2>/dev/null")

                # 2. Bersihkan Thumbnails jika dicentang
                if self.cat_widgets.get("thumbnails", {}).get("chk", None) and self.cat_widgets["thumbnails"]["chk"].get() == 1:
                    self.adb.shell("rm -rf /sdcard/DCIM/.thumbnails/* /sdcard/Pictures/.thumbnails/* /sdcard/MIUI/Gallery/cloud/.thumbnailFile/* 2>/dev/null")

                # 3. Bersihkan Debug Logs jika dicentang
                if self.cat_widgets.get("logs", {}).get("chk", None) and self.cat_widgets["logs"]["chk"].get() == 1:
                    self.adb.shell("rm -rf /sdcard/MIUI/debug_log/* /sdcard/log/* /sdcard/MIUI/anr/* 2>/dev/null")

                # 4. Bersihkan Empty Folders jika dicentang
                if self.cat_widgets.get("empty_folders", {}).get("chk", None) and self.cat_widgets["empty_folders"]["chk"].get() == 1:
                    empty_paths = self.categories_data.get("empty_folders", {}).get("paths", [])
                    for ep in empty_paths:
                        raw_dir = ep.replace(" (Empty)", "").strip()
                        if raw_dir and not raw_dir.endswith("/sdcard") and not raw_dir.endswith("/data"):
                            self.adb.shell(f"rmdir '{raw_dir}' 2>/dev/null")
            except Exception as e:
                print(f"[STORAGE CLEAN ERROR] {e}")

            self.after(0, self._on_clean_done)

        threading.Thread(target=_clean_worker, daemon=True).start()

    def _on_clean_done(self):
        for key, w in self.cat_widgets.items():
            if w["chk"].get() == 1:
                w["data"]["size_mb"] = 0.0
                w["data"]["size_str"] = "0.0 MB" if key != "empty_folders" else "0 Folders"
                w["data"]["paths"] = []
                w["lbl_size"].configure(text=w["data"]["size_str"])
                w["chk"].deselect()

        self._show_inspector_files("app_cache")
        self._update_selected_summary()
        self.btn_clean.configure(text=I18n.t("storage_btn_clean"))
