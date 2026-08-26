import customtkinter as ctk

class ThemeManager:
    """
    Centralized visual theme manager handling dark and light appearance palettes
    inspired by modern UI frameworks (Tailwind Slate and Modern OS design).
    """
    
    THEMES = {
        "light": {
            "bg_primary": "#F8FAFC",
            "bg_secondary": "#FFFFFF",
            "bg_card": "#FFFFFF",
            "bg_card_hover": "#F1F5F9",
            "text_primary": "#0F172A",
            "text_secondary": "#64748B",
            "text_muted": "#94A3B8",
            "accent": "#2563EB",
            "accent_hover": "#1D4ED8",
            "accent_soft": "#EFF6FF",
            "success": "#059669",
            "success_soft": "#ECFDF5",
            "warning": "#D97706",
            "warning_soft": "#FFFBEB",
            "danger": "#E11D48",
            "danger_soft": "#FFF1F2",
            "border": "#E2E8F0",
            "sidebar_bg": "#FFFFFF",
            "card_border": "#E2E8F0"
        },
        "dark": {
            "bg_primary": "#0B0F17",
            "bg_secondary": "#111827",
            "bg_card": "#161F30",
            "bg_card_hover": "#1E293B",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "text_muted": "#64748B",
            "accent": "#3B82F6",
            "accent_hover": "#60A5FA",
            "accent_soft": "#1E293B",
            "success": "#10B981",
            "success_soft": "#064E3B",
            "warning": "#F59E0B",
            "warning_soft": "#78350F",
            "danger": "#F43F5E",
            "danger_soft": "#881337",
            "border": "#1E293B",
            "sidebar_bg": "#0E1422",
            "card_border": "#1E293B"
        }
    }

    current_mode = "light"

    @classmethod
    def set_theme(cls, mode: str):
        """
        Updates the global CustomTkinter appearance mode.

        Args:
            mode (str): Theme mode ('light' or 'dark').
        """
        if mode in ["light", "dark"]:
            cls.current_mode = mode
            ctk.set_appearance_mode(mode)
            print(f"[THEME_MANAGER] Appearance mode updated to: '{mode.upper()}' (Active CtK Mode: {ctk.get_appearance_mode()})")

    @classmethod
    def get_colors(cls):
        """
        Retrieves the color palette dictionary for the currently active theme mode.

        Returns:
            Dict[str, str]: Color token mapping.
        """
        return cls.THEMES.get(cls.current_mode, cls.THEMES["light"])
