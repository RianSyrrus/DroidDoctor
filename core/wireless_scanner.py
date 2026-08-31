import socket
import subprocess
import concurrent.futures
from typing import List, Dict, Optional, Tuple

class WirelessScanner:
    """
    High-speed Wireless ADB discovery engine utilizing native mDNS resolver
    and multi-threaded TCP port probe across Android 11+ dynamic port ranges (37000–45000)
    and legacy port 5555.
    """

    @staticmethod
    def is_port_open(ip: str, port: int, timeout: float = 0.15) -> bool:
        """
        Tests if a specific TCP port is actively listening on the target host.

        Args:
            ip (str): Target IPv4 address.
            port (int): Port number to probe.
            timeout (float): Connection timeout in seconds.

        Returns:
            bool: True if TCP connection was established, False otherwise.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                return s.connect_ex((ip, port)) == 0
        except Exception:
            return False

    @staticmethod
    def scan_target_ports(target_ip: str, start_port: int = 37000, end_port: int = 45000, max_workers: int = 80) -> List[int]:
        """
        Scans common Wireless ADB ports (5555 first, then range 37000-45000) on a target IP address.

        Args:
            target_ip (str): Target IPv4 address.
            start_port (int): Start of dynamic port range (default 37000).
            end_port (int): End of dynamic port range (default 45000).
            max_workers (int): Thread concurrency pool size.

        Returns:
            List[int]: List of open TCP port numbers.
        """
        open_ports = []
        target_ip = target_ip.strip()
        if not target_ip:
            return open_ports

        # 1. Fast probe standard port 5555 first
        if WirelessScanner.is_port_open(target_ip, 5555, timeout=0.25):
            open_ports.append(5555)

        # 2. Parallel scan dynamic range
        ports_to_scan = list(range(start_port, end_port + 1))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_port = {
                executor.submit(WirelessScanner.is_port_open, target_ip, p, 0.12): p
                for p in ports_to_scan
            }
            for future in concurrent.futures.as_completed(future_to_port):
                p = future_to_port[future]
                try:
                    if future.result():
                        open_ports.append(p)
                except Exception:
                    pass

        return sorted(open_ports)

    @staticmethod
    def parse_mdns_services(adb_path: str) -> List[Dict[str, str]]:
        """
        Queries and parses active Android ADB mDNS advertising services via `adb mdns services`.

        Args:
            adb_path (str): Absolute path to adb executable.

        Returns:
            List[Dict[str, str]]: List of discovered services with 'service', 'type', 'target', 'ip', and 'port'.
        """
        services = []
        try:
            res = subprocess.run(
                [adb_path, "mdns", "services"],
                capture_output=True, text=True, timeout=3.0,
                creationflags=0x08000000
            )
            for line in res.stdout.splitlines():
                line = line.strip()
                if not line or "list of discovered" in line.lower() or "mdns daemon" in line.lower():
                    continue
                parts = line.split()
                # Typical format: <service_name> <service_type> <ip:port>
                if len(parts) >= 3:
                    srv_name = parts[0]
                    srv_type = parts[1]
                    target = parts[2]
                    ip = target.split(":")[0] if ":" in target else target
                    port = target.split(":")[1] if ":" in target else ""
                    services.append({
                        "service": srv_name,
                        "type": srv_type,
                        "target": target,
                        "ip": ip,
                        "port": port
                    })
        except Exception:
            pass
        return services

    @staticmethod
    def auto_discover_best_target(target_ip: str, adb_path: str) -> Optional[str]:
        """
        Discovers the optimal 'IP:Port' target string for a device automatically.

        Args:
            target_ip (str): Known or suspected device IP (e.g. '192.168.1.100').
            adb_path (str): Path to ADB executable.

        Returns:
            Optional[str]: 'IP:Port' formatted target string or None if not found.
        """
        target_ip = target_ip.strip()

        # Step 1: Check mDNS services first
        mdns_list = WirelessScanner.parse_mdns_services(adb_path)
        for item in mdns_list:
            if target_ip and item["ip"] == target_ip:
                if "_adb-tls-connect" in item["type"] or "_adb._tcp" in item["type"]:
                    return item["target"]
            elif not target_ip:
                if "_adb-tls-connect" in item["type"] or "_adb._tcp" in item["type"]:
                    return item["target"]

        # Step 2: Fallback to fast multi-threaded port scan if IP is known
        if target_ip:
            ports = WirelessScanner.scan_target_ports(target_ip)
            if ports:
                # Prefer standard 5555 or the first open dynamic port
                chosen_port = 5555 if 5555 in ports else ports[0]
                return f"{target_ip}:{chosen_port}"

        return None
