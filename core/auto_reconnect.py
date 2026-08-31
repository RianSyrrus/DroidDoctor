import time
import threading
from typing import Optional
from core.device_bookmarks import DeviceBookmarks
from core.wireless_scanner import WirelessScanner

class AutoReconnectWatchdog:
    """
    Background connection monitor (Watchdog) that continuously evaluates
    wireless device reachability and autonomously re-establishes ADB sessions
    when devices return to the local Wi-Fi network.
    """
    _instance = None

    @classmethod
    def get_instance(cls, adb_manager=None):
        if cls._instance is None:
            cls._instance = AutoReconnectWatchdog(adb_manager)
        elif adb_manager and not cls._instance.adb:
            cls._instance.adb = adb_manager
        return cls._instance

    def __init__(self, adb_manager=None):
        self.adb = adb_manager
        self.interval_seconds = 30
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Starts the background watchdog loop."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stops the background watchdog loop."""
        self._running = False

    def _watchdog_loop(self):
        while self._running:
            time.sleep(self.interval_seconds)
            if not self.adb or not self._running:
                continue

            try:
                # 1. Check if an active device is already communicating
                active_devices = self.adb.get_connected_devices()
                online_serials = [d["serial"] for d in active_devices if d.get("state") == "device"]
                
                # If a device is already online and selected, skip probe
                if online_serials and self.adb.current_serial in online_serials:
                    continue

                # 2. Check saved bookmarks with auto_reconnect enabled
                bookmarks = DeviceBookmarks.get_all()
                for b in bookmarks:
                    if not b.get("auto_reconnect", True):
                        continue
                    
                    ip = b.get("ip", "")
                    last_port = b.get("last_port", "5555")
                    if not ip:
                        continue

                    # Try last known port first
                    if WirelessScanner.is_port_open(ip, int(last_port) if last_port.isdigit() else 5555, timeout=0.2):
                        target = f"{ip}:{last_port}"
                        success, _ = self.adb.connect_wireless(target)
                        if success:
                            break
                    else:
                        # Auto-discover if port changed
                        best_target = WirelessScanner.auto_discover_best_target(ip, self.adb.adb_bin)
                        if best_target:
                            success, _ = self.adb.connect_wireless(best_target)
                            if success:
                                # Update remembered port
                                if ":" in best_target:
                                    new_port = best_target.split(":")[1]
                                    DeviceBookmarks.save_bookmark(ip, alias=b.get("alias"), last_port=new_port)
                                break
            except Exception:
                pass
