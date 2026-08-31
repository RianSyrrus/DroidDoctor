import time
import threading
import subprocess
from typing import Callable, Optional
from core.wireless_scanner import WirelessScanner

class QRPairingListener:
    """
    High-frequency background daemon that listens for Android 11+ mDNS pairing broadcasts
    triggered when the phone scans the QR code, immediately executing the cryptographic
    handshake (adb pair) and subsequent ADB connection (adb connect).
    """

    def __init__(self, adb_path: str):
        self.adb_bin = adb_path
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._current_pin: str = ""
        self._on_pair: Optional[Callable[[str], None]] = None
        self._on_connect: Optional[Callable[[str], None]] = None
        self._on_status: Optional[Callable[[str], None]] = None

    def start(self, pin: str, on_pair: Callable[[str], None] = None, on_connect: Callable[[str], None] = None, on_status: Callable[[str], None] = None):
        """Starts the active pairing watcher with the specified QR pairing PIN."""
        self._current_pin = pin.strip()
        self._on_pair = on_pair
        self._on_connect = on_connect
        self._on_status = on_status
        self._running = True
        
        if self._thread and self._thread.is_alive():
            return
            
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def update_pin(self, new_pin: str):
        """Updates the active PIN when QR code is refreshed."""
        self._current_pin = new_pin.strip()

    def stop(self):
        """Stops the pairing watcher loop."""
        self._running = False

    def _loop(self):
        attempted_pairs = set()
        
        while self._running:
            try:
                services = WirelessScanner.parse_mdns_services(self.adb_bin)
                
                # 1. Look for Pairing Service broadcasted by phone
                for s in services:
                    if "_adb-tls-pairing" in s.get("type", ""):
                        pair_target = s.get("target", "")
                        pin = self._current_pin
                        
                        # Avoid hammering the same target with failed pins
                        if pair_target and pin and (pair_target, pin) not in attempted_pairs:
                            attempted_pairs.add((pair_target, pin))
                            if self._on_status:
                                self._on_status(f"Handshake detected with {pair_target}... Pairing...")
                            
                            # Execute ADB Pair
                            cmd = [self.adb_bin, "pair", pair_target, pin]
                            res = subprocess.run(cmd, capture_output=True, text=True, timeout=6.0, creationflags=0x08000000)
                            out = (res.stdout + "\n" + res.stderr).strip()
                            
                            if "successfully paired" in out.lower():
                                if self._on_pair:
                                    self._on_pair(pair_target)
                                if self._on_status:
                                    self._on_status(f"Paired successfully to {pair_target}! Connecting...")
                                
                                # Small pause for Android to switch to connect service
                                time.sleep(0.8)
                                ip = pair_target.split(":")[0] if ":" in pair_target else pair_target
                                self._auto_connect_after_pair(ip)
                                self._running = False
                                return

                # 2. Look for existing connect services if already paired
                for s in services:
                    if "_adb-tls-connect" in s.get("type", "") or "_adb._tcp" in s.get("type", ""):
                        conn_target = s.get("target", "")
                        if conn_target:
                            # Try connecting
                            cmd = [self.adb_bin, "connect", conn_target]
                            res = subprocess.run(cmd, capture_output=True, text=True, timeout=4.0, creationflags=0x08000000)
                            out = (res.stdout + "\n" + res.stderr).strip()
                            if "connected" in out.lower() and "failed" not in out.lower() and "cannot" not in out.lower():
                                if self._on_connect:
                                    self._on_connect(conn_target)
                                self._running = False
                                return

            except Exception:
                pass

            time.sleep(0.5)

    def _auto_connect_after_pair(self, ip: str):
        """Discovers connection port and establishes ADB session after successful pair."""
        # Try mDNS first
        time.sleep(0.5)
        services = WirelessScanner.parse_mdns_services(self.adb_bin)
        for s in services:
            if s.get("ip") == ip and ("_adb-tls-connect" in s.get("type", "") or "_adb._tcp" in s.get("type", "")):
                conn_target = s.get("target", "")
                cmd = [self.adb_bin, "connect", conn_target]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5.0, creationflags=0x08000000)
                if "connected" in (res.stdout + res.stderr).lower():
                    if self._on_connect:
                        self._on_connect(conn_target)
                    return

        # Fallback to port scan on that IP
        best_target = WirelessScanner.auto_discover_best_target(ip, self.adb_bin)
        if best_target:
            cmd = [self.adb_bin, "connect", best_target]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5.0, creationflags=0x08000000)
            if "connected" in (res.stdout + res.stderr).lower():
                if self._on_connect:
                    self._on_connect(best_target)
