import os
import sqlite3
from typing import Dict, Any, Optional

class DeviceDB:
    """
    Sub-millisecond offline lookup engine for Android device specifications.
    Uses indexed B-Trees on device codename and model code.
    """

    _instance: Optional["DeviceDB"] = None

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "data", "devices.sqlite")
        self.db_path = db_path
        self._cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_instance(cls) -> "DeviceDB":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def lookup(self, codename: str, model_code: str = "") -> Optional[Dict[str, Any]]:
        """
        Fast lookup device specification using codename and model code.
        """
        cache_key = f"{codename.lower()}:{model_code.lower()}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not os.path.exists(self.db_path):
            return None

        clean_code = codename.strip().lower()
        clean_model = model_code.strip().lower()

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 1. Query by exact codename & model code
            if clean_code and clean_model:
                cursor.execute("""
                SELECT brand, marketing_name, device_codename, model_code, chipset, battery_mah, fast_charge_watt, screen_type, camera_main_mp, storage_type
                FROM devices
                WHERE LOWER(device_codename) = ? AND LOWER(model_code) = ?
                LIMIT 1;
                """, (clean_code, clean_model))
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    self._cache[cache_key] = result
                    conn.close()
                    return result

            # 2. Query by codename
            if clean_code:
                cursor.execute("""
                SELECT brand, marketing_name, device_codename, model_code, chipset, battery_mah, fast_charge_watt, screen_type, camera_main_mp, storage_type
                FROM devices
                WHERE LOWER(device_codename) = ?
                LIMIT 1;
                """, (clean_code,))
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    self._cache[cache_key] = result
                    conn.close()
                    return result

            # 3. Query by model code
            if clean_model:
                cursor.execute("""
                SELECT brand, marketing_name, device_codename, model_code, chipset, battery_mah, fast_charge_watt, screen_type, camera_main_mp, storage_type
                FROM devices
                WHERE LOWER(model_code) = ?
                LIMIT 1;
                """, (clean_model,))
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    self._cache[cache_key] = result
                    conn.close()
                    return result

            conn.close()
        except Exception:
            pass

        return None
