from typing import List, Dict, Optional
from core.settings_manager import SettingsManager

class DeviceBookmarks:
    """
    Manages persistent Android device profiles, custom nicknames (aliases),
    last-known IP/Port pairings, and auto-reconnect preferences.
    """

    @staticmethod
    def get_all() -> List[Dict[str, any]]:
        """
        Retrieves all saved device bookmarks.

        Returns:
            List[Dict[str, any]]: List of saved device dictionary items.
        """
        mgr = SettingsManager.get_instance()
        bookmarks = mgr.get("device_bookmarks", [])
        if not isinstance(bookmarks, list):
            bookmarks = []
        return bookmarks

    @staticmethod
    def save_bookmark(ip: str, alias: str = "", last_port: str = "", auto_reconnect: bool = True) -> Dict[str, any]:
        """
        Adds or updates a device bookmark.

        Args:
            ip (str): Device IPv4 address (e.g. '192.168.1.100').
            alias (str): User-friendly display name (e.g. 'Redmi Note 10S').
            last_port (str): Last successfully connected port number.
            auto_reconnect (bool): Whether to auto-reconnect on startup/watchdog.

        Returns:
            Dict[str, any]: Updated bookmark item.
        """
        ip = ip.strip()
        if not ip:
            return {}

        mgr = SettingsManager.get_instance()
        bookmarks = DeviceBookmarks.get_all()
        
        # Check if already exists
        updated = False
        target_item = None
        for b in bookmarks:
            if b.get("ip") == ip:
                if alias:
                    b["alias"] = alias
                if last_port:
                    b["last_port"] = last_port
                b["auto_reconnect"] = auto_reconnect
                target_item = b
                updated = True
                break

        if not updated:
            target_item = {
                "ip": ip,
                "alias": alias if alias else f"Device {ip}",
                "last_port": last_port if last_port else "5555",
                "auto_reconnect": auto_reconnect
            }
            bookmarks.append(target_item)

        mgr.set("device_bookmarks", bookmarks)
        return target_item

    @staticmethod
    def remove(ip: str) -> bool:
        """
        Deletes a device bookmark by its IP address.

        Args:
            ip (str): Target device IP.

        Returns:
            bool: True if removed, False if not found.
        """
        ip = ip.strip()
        mgr = SettingsManager.get_instance()
        bookmarks = DeviceBookmarks.get_all()
        initial_len = len(bookmarks)
        filtered = [b for b in bookmarks if b.get("ip") != ip]
        
        if len(filtered) != initial_len:
            mgr.set("device_bookmarks", filtered)
            return True
        return False
