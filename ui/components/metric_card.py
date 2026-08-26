import customtkinter as ctk

class MetricCard(ctk.CTkFrame):
    """
    Reusable dashboard metric card widget featuring category tags, primary telemetry readout,
    mini progress indicators, and dynamic status badges.
    """
    def __init__(self, master, title: str, tag: str = "SYS", **kwargs):
        super().__init__(master, corner_radius=14, fg_color=("#FFFFFF", "#161F30"), border_width=1, border_color=("#E2E8F0", "#1E293B"), **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=16, pady=(14, 4), sticky="ew")
        
        self.tag_label = ctk.CTkLabel(
            header, text=tag, font=ctk.CTkFont(family="Segoe UI Variable Display", size=10, weight="bold"),
            fg_color=("#EFF6FF", "#1E293B"), text_color=("#2563EB", "#60A5FA"),
            corner_radius=6, padx=8, pady=2
        )
        self.tag_label.pack(side="left")
        
        self.title_label = ctk.CTkLabel(
            header, text=title, font=ctk.CTkFont(family="Segoe UI Variable Text", size=13, weight="bold"),
            text_color=("#334155", "#CBD5E1")
        )
        self.title_label.pack(side="left", padx=(8, 0))

        self.badge = ctk.CTkLabel(
            header, text="", font=ctk.CTkFont(family="Segoe UI Variable Text", size=10, weight="bold"),
            fg_color=("#F1F5F9", "#1E293B"), text_color=("#059669", "#10B981"),
            corner_radius=6, padx=8, pady=2
        )
        self.badge.pack(side="right")

        self.value_label = ctk.CTkLabel(
            self, text="-", font=ctk.CTkFont(family="Segoe UI Variable Display", size=26, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        self.value_label.grid(row=1, column=0, padx=16, pady=(4, 2), sticky="w")

        self.progress_bar = ctk.CTkProgressBar(
            self, height=5, corner_radius=3, fg_color=("#E2E8F0", "#1E293B"), progress_color="#2563EB"
        )
        self.progress_bar.grid(row=2, column=0, padx=16, pady=(2, 6), sticky="ew")
        self.progress_bar.set(0.0)

        self.sub_label = ctk.CTkLabel(
            self, text="-", font=ctk.CTkFont(family="Segoe UI Variable Text", size=11),
            text_color=("#64748B", "#94A3B8"), justify="left"
        )
        self.sub_label.grid(row=3, column=0, padx=16, pady=(0, 14), sticky="w")

    def update_data(self, value: str, subtitle: str = "", badge_text: str = "", badge_type: str = "blue", progress: float = None):
        """
        Updates the card values, subtitle description, status badge, and progress bar.

        Args:
            value (str): Primary display value.
            subtitle (str): Secondary specification description.
            badge_text (str): Status badge text.
            badge_type (str): Badge color scheme ('green', 'yellow', 'red', or 'blue').
            progress (float): Optional normalized progress value between 0.0 and 1.0.
        """
        self.value_label.configure(text=value)
        if subtitle:
            self.sub_label.configure(text=subtitle)
        
        if badge_text:
            self.badge.configure(text=badge_text)
            if badge_type == "green":
                self.badge.configure(fg_color=("#ECFDF5", "#064E3B"), text_color=("#059669", "#10B981"))
            elif badge_type == "yellow":
                self.badge.configure(fg_color=("#FFFBEB", "#78350F"), text_color=("#D97706", "#F59E0B"))
            elif badge_type == "red":
                self.badge.configure(fg_color=("#FFF1F2", "#881337"), text_color=("#E11D48", "#F43F5E"))
            else:
                self.badge.configure(fg_color=("#EFF6FF", "#1E293B"), text_color=("#2563EB", "#60A5FA"))

        if progress is not None:
            self.progress_bar.set(max(0.0, min(1.0, progress)))
