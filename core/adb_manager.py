import os
import time
import subprocess
import threading
import sys

CREATE_NO_WINDOW = 0x08000000 if sys.platform == 'win32' else 0
from typing import Optional, List, Dict, Callable, Tuple

class ADBManager:
    """
    Robust Android Debug Bridge (ADB) controller managing USB and wireless device connections,
    shell execution, screen capture, video recording, and daemon process lifecycle.
    """
    def __init__(self):
        self.current_serial: Optional[str] = None
        self._is_monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._on_device_connected: Optional[Callable[[str], None]] = None
        self._on_device_disconnected: Optional[Callable[[], None]] = None
        
        from .bin_manager import BinManager
        self.adb_bin = BinManager.get_adb_path()
        self.ensure_server_running()

    def ensure_server_running(self) -> bool:
        """
        Ensures the ADB server daemon is active on the local machine (port 5037).

        Returns:
            bool: True if the ADB server responded successfully, False otherwise.
        """
        try:
            cmd = [self.adb_bin, "start-server"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=8.0, creationflags=CREATE_NO_WINDOW)
            return res.returncode == 0
        except Exception:
            return False

    def get_connected_devices(self) -> List[Dict[str, str]]:
        """
        Queries and parses all currently attached Android devices and their operational states.

        Returns:
            List[Dict[str, str]]: List of device dictionaries containing 'serial' and 'state'.
        """
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
        """
        Selects an active device serial for subsequent ADB operations.

        Args:
            serial (str): Target Android device hardware serial or IP:Port.

        Returns:
            bool: True upon selection.
        """
        self.current_serial = serial
        return True

    def get_active_serial(self) -> Optional[str]:
        """
        Retrieves the current active device serial, auto-selecting the first online device if unset.

        Returns:
            Optional[str]: Active device serial string, or None if no device is available.
        """
        if self.current_serial:
            return self.current_serial
        devices = self.get_connected_devices()
        for d in devices:
            if d.get("state") == "device":
                self.current_serial = d["serial"]
                return self.current_serial
        return None

    def shell(self, command: str, timeout: float = 2.5) -> str:
        """
        Executes a shell command on the active Android device.

        Args:
            command (str): Android shell command to execute.
            timeout (float): Subprocess execution timeout in seconds.

        Returns:
            str: Command stdout output, or empty string on failure.
        """
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
        """
        Pairs an Android 11+ device using a 6-digit wireless pairing code.

        Args:
            target (str): Target IP:Port address.
            pairing_code (str): 6-digit pairing code shown on Android device.

        Returns:
            Tuple[bool, str]: (Success status, descriptive result message).
        """
        try:
            cmd = [self.adb_bin, "pair", target.strip(), pairing_code.strip()]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10.0, creationflags=CREATE_NO_WINDOW)
            out = (res.stdout + "\n" + res.stderr).strip()
            if "successfully paired" in out.lower():
                return True, "✅ Successfully Paired!"
            return False, f"Pairing Failed: {out}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def connect_wireless(self, target: str) -> Tuple[bool, str]:
        """
        Establishes a Wireless ADB TCP connection to a specified target.

        Args:
            target (str): Target IP:Port address.

        Returns:
            Tuple[bool, str]: (Success status, descriptive result message).
        """
        try:
            cmd = [self.adb_bin, "connect", target.strip()]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=6.0, creationflags=CREATE_NO_WINDOW)
            out = (res.stdout + "\n" + res.stderr).strip()
            if "connected" in out.lower() and "cannot" not in out.lower() and "failed" not in out.lower():
                self.select_device(target.strip())
                return True, f"✅ Connected to {target}!"
            return False, f"Connection Failed: {out}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_mdns_services(self) -> List[Dict[str, str]]:
        """
        Retrieves active mDNS-discovered Android ADB endpoints.

        Returns:
            List[Dict[str, str]]: List of discovered services.
        """
        try:
            from .wireless_scanner import WirelessScanner
            return WirelessScanner.parse_mdns_services(self.adb_bin)
        except Exception:
            return []

    def enable_tcpip(self, port: int = 5555) -> bool:
        """
        Switches the connected device ADB daemon to TCP/IP listening mode.

        Args:
            port (int): Port number (default 5555).

        Returns:
            bool: True if mode switched successfully.
        """
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
        """
        Reboots the device into the specified operating mode.

        Args:
            mode (str): Reboot target ('', 'recovery', 'bootloader', or 'fastboot').

        Returns:
            bool: True if the reboot command was accepted.
        """
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
        """
        Captures a lossless PNG screenshot directly from the device to a local PC path.

        Args:
            local_destination_path (str): Absolute destination file path on PC.

        Returns:
            bool: True if the screenshot was saved successfully.
        """
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
            
            # Temporary file pull fallback
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
        """
        Initiates a hardware video recording session on the Android device via screenrecord.

        Args:
            remote_path (str): Remote destination path on device.

        Returns:
            Optional[subprocess.Popen]: Process handle if started, None on error.
        """
        try:
            cmd = [self.adb_bin]
            if self.current_serial:
                cmd.extend(["-s", self.current_serial])
            cmd.extend(["shell", "screenrecord", "--bit-rate", "8000000", remote_path])
            return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
        except Exception:
            return None

    def stop_screen_record(self, proc: subprocess.Popen, local_destination_path: str, remote_path: str = "/sdcard/temp_droid_rec.mp4") -> bool:
        """
        Terminates the active video recording session and pulls the MP4 file to the PC.

        Args:
            proc (subprocess.Popen): Active screenrecord process handle.
            local_destination_path (str): Local destination file path on PC.
            remote_path (str): Remote source path on device.

        Returns:
            bool: True if the recording file was transferred successfully.
        """
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
        """
        Disconnects all active wireless ADB sessions and resets the selected serial state.
        """
        try:
            subprocess.run([self.adb_bin, "disconnect"], capture_output=True, timeout=2.0, creationflags=CREATE_NO_WINDOW)
        except Exception:
            pass
        self.current_serial = None
