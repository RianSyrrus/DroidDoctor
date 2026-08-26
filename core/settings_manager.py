import os
import sys
import json

def get_settings_file() -> str:
    """
    Resolves the persistent writable path for the user configuration file.

    Returns:
        str: Path to %LOCALAPPDATA%/DroidDoctor/config.json in frozen mode or local config.json in dev mode.
    """
    if getattr(sys, 'frozen', False):
        appdata_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "DroidDoctor")
        os.makedirs(appdata_dir, exist_ok=True)
        return os.path.join(appdata_dir, "config.json")
    
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

DEFAULT_SETTINGS = {
    "theme": "light",
    "language": "en",
    "sound_effects": True,
    "polling_rate": 0.5,
    "mirror_resolution": "1080p",
    "mirror_fps": 60,
    "mirror_auto_turn_off": False,
    "debloater_tab_visible": False,
    "debloater_require_challenge": True,
    "debloater_disclaimer_mode": "always"
}

class SettingsManager:
    """
    Singleton configuration manager handling persistent user preferences,
    UI theme settings, polling rates, and safety switches.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        """
        Retrieves the global singleton instance of SettingsManager.

        Returns:
            SettingsManager: Singleton configuration manager instance.
        """
        if cls._instance is None:
            cls._instance = SettingsManager()
        return cls._instance

    def __init__(self):
        self.settings_file = get_settings_file()
        self._settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        """
        Loads configuration settings from disk, applying defaults for any missing keys.
        """
        if not os.path.exists(self.settings_file):
            bundle_config = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.json")
            if os.path.exists(bundle_config):
                try:
                    with open(bundle_config, "r", encoding="utf-8") as f:
                        self._settings.update(json.load(f))
                except Exception:
                    pass
            self.save()
            return

        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self._settings.update(saved)
            except Exception:
                self._settings = DEFAULT_SETTINGS.copy()
        else:
            self.save()

    def save(self):
        """
        Serializes current settings to disk in JSON format.
        """
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=4)
        except Exception:
            pass

    def get(self, key, default=None):
        """
        Retrieves a setting value by key.

        Args:
            key (str): Configuration setting key.
            default: Optional fallback value if key does not exist.

        Returns:
            Any: Configuration value.
        """
        return self._settings.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        """
        Updates a setting value and immediately persists changes to disk.

        Args:
            key (str): Configuration setting key.
            value: Value to store.
        """
        self._settings[key] = value
        self.save()
