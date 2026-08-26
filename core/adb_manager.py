import os
import time
import subprocess
import threading
import sys

CREATE_NO_WINDOW = 0x08000000 if sys.platform == 'win32' else 0
from typing import Optional, List, Dict, Callable, Tuple

class ADBManager:
    """
    Manajer komunikasi ADB tangguh dengan proteksi Anti-Freeze,
    dukungan Pairing 6-Digit (Android 11+), Connect Wireless, TCP/IP, dan Auto-Reconnect.
    """
    def __init__(self):
        self.current_serial: Optional[str] = None
        self._is_monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._on_device_connected: Optional[Callable[[str], None]] = None
        self._on_device_disconnected: Optional[Callable[[], None]] = None
        
        from .bin_manager import BinManager
        self.adb_bin = BinManager.get_adb_path()
                
        # Warm-up ADB Server Daemon secara otomatis pada saat inisialisasi
        self.ensure_server_running()

    def ensure_server_running(self) -> bool:
        """Memastikan ADB daemon server aktif di port 5037 saat aplikasi pertama kali dibuka."""
        try:
            cmd = [self.adb_bin, "start-server"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=8.0, creationflags=CREATE_NO_WINDOW)
            return res.returncode == 0
        except Exception:
            return False

    def get_connected_devices(self) -> List[Dict[str, str]]:
        res = []
        try:
            cmd_res = subprocess.run([self.adb_bin, "devices"], capture_output=True, text=True, timeout=4.0, creationflags=CREATE_NO_WINDOW)
            lines = cmd_res.stdout.splitlines()
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                if "\t" in line:
                    serial, state = line.rsplit("\t", 1)
                    res.append({"serial": serial.strip(), "state": state.strip()})
                else:
                    for st in ["device", "offline", "unauthorized", "recovery", "sideload", "authorizing"]:
                        if line.endswith(st):
                            serial = line[:-len(st)].strip()
                            res.append({"serial": serial, "state": st})
                            break
        except Exception:
            pass
        return res

    def select_device(self, serial: str) -> bool:
        self.current_serial = serial
        return True

    def get_active_serial(self) -> Optional[str]:
        if self.current_serial:
            return self.current_serial
        devices = self.get_connected_devices()
        for d in devices:
            if d.get("state") == "device":
                self.current_serial = d["serial"]
                return self.current_serial
        return None

    def shell(self, command: str, timeout: float = 2.5) -> str:
        try:
            cmd = [self.adb_bin]
            if self.current_serial:
                cmd.extend(["-s", self.current_serial])
            cmd.extend(["shell", command])
            
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, errors="ignore", creationflags=CREATE_NO_WINDOW)
            return res.stdout
        except Exception:
            return ""

    def pair_wireless(self, target: str, pairing_code: str) -> Tuple[bool, str]:
        """Melakukan pairing perangkat Android 11+ dengan kode 6-angka."""
        try:
            cmd = [self.adb_bin, "pair", target.strip(), pairing_code.strip()]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10.0, creationflags=CREATE_NO_WINDOW)
            out = (res.stdout + "\n" + res.stderr).strip()
            if "successfully paired" in out.lower():
                return True, "✅ Berhasil Disandingkan (Pairing Sukses)!"
            return False, f"Gagal Pair: {out}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def connect_wireless(self, target: str) -> Tuple[bool, str]:
        """Menyambungkan Wireless ADB ke IP:Port HP."""
        try:
            cmd = [self.adb_bin, "connect", target.strip()]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=6.0, creationflags=CREATE_NO_WINDOW)
            out = (res.stdout + "\n" + res.stderr).strip()
            if "connected" in out.lower() and "cannot" not in out.lower() and "failed" not in out.lower():
                self.select_device(target.strip())
                return True, f"✅ Berhasil Terhubung ke {target}!"
            return False, f"Gagal Konek: {out}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def enable_tcpip(self, port: int = 5555) -> bool:
        try:
            cmd = [self.adb_bin]
            if self.current_serial:
                cmd.extend(["-s", self.current_serial])
            cmd.extend(["tcpip", str(port)])
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5.0, creationflags=CREATE_NO_WINDOW)
            return res.returncode == 0
        except Exception:
            return False

    def reboot(self, mode: str = "") -> bool:
        try:
            cmd = [self.adb_bin]
            if self.current_serial:
                cmd.extend(["-s", self.current_serial])
            if mode in ["recovery", "bootloader", "fastboot"]:
                cmd.extend(["reboot", mode])
            else:
                cmd.append("reboot")
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5.0, creationflags=CREATE_NO_WINDOW)
            return res.returncode == 0
        except Exception:
            return False

    def take_screenshot(self, local_destination_path: str) -> bool:
        """Mengambil screenshot resolusi penuh dari HP langsung ke PC."""
        try:
            cmd = [self.adb_bin]
            if self.current_serial:
                cmd.extend(["-s", self.current_serial])
            cmd.extend(["exec-out", "screencap", "-p"])
            res = subprocess.run(cmd, capture_output=True, timeout=8.0, creationflags=CREATE_NO_WINDOW)
            if res.returncode == 0 and len(res.stdout) > 1000:
                with open(local_destination_path, "wb") as f:
                    f.write(res.stdout)
                return True
            
            # Fallback metode temporary file
            self.shell("screencap -p /sdcard/temp_scr_cap.png")
            pull_cmd = [self.adb_bin]
            if self.current_serial:
                pull_cmd.extend(["-s", self.current_serial])
            pull_cmd.extend(["pull", "/sdcard/temp_scr_cap.png", local_destination_path])
            subprocess.run(pull_cmd, capture_output=True, timeout=8.0, creationflags=CREATE_NO_WINDOW)
            self.shell("rm -f /sdcard/temp_scr_cap.png")
            return os.path.exists(local_destination_path)
        except Exception:
            return False

    def start_screen_record(self, remote_path: str = "/sdcard/temp_droid_rec.mp4") -> Optional[subprocess.Popen]:
        """Memulai perekaman layar HP via ADB shell screenrecord."""
        try:
            cmd = [self.adb_bin]
            if self.current_serial:
                cmd.extend(["-s", self.current_serial])
            cmd.extend(["shell", "screenrecord", "--bit-rate", "8000000", remote_path])
            return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
        except Exception:
            return None

    def stop_screen_record(self, proc: subprocess.Popen, local_destination_path: str, remote_path: str = "/sdcard/temp_droid_rec.mp4") -> bool:
        """Menghentikan perekaman dan mengunduh file MP4 ke PC."""
        try:
            if proc:
                proc.terminate()
                time.sleep(1.0)
            pull_cmd = [self.adb_bin]
            if self.current_serial:
                pull_cmd.extend(["-s", self.current_serial])
            pull_cmd.extend(["pull", remote_path, local_destination_path])
            subprocess.run(pull_cmd, capture_output=True, timeout=15.0, creationflags=CREATE_NO_WINDOW)
            self.shell(f"rm -f {remote_path}")
            return os.path.exists(local_destination_path)
        except Exception:
            return False

    def disconnect_all(self):
        try:
            subprocess.run([self.adb_bin, "disconnect"], capture_output=True, timeout=2.0, creationflags=CREATE_NO_WINDOW)
        except Exception:
            pass
        self.current_serial = None
