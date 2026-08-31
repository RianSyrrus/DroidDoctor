import os
import socket
import random
import string
from typing import Tuple, Optional
from PIL import Image, ImageDraw

class QREngine:
    """
    High-performance QR Code generator for Android 11+ Wireless Debugging pairing,
    local IP resolution, and dynamic visual rendering for CustomTkinter widgets.
    """

    @staticmethod
    def get_local_ip() -> str:
        """
        Detects the primary local IPv4 address of the PC connected to the local Wi-Fi / LAN network.

        Returns:
            str: Local IPv4 address (e.g. '192.168.1.15') or '127.0.0.1' fallback.
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.3)
            # Connect to public DNS to determine default outbound route
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            try:
                hostname = socket.gethostname()
                return socket.gethostbyname(hostname)
            except Exception:
                return "127.0.0.1"

    @staticmethod
    def generate_random_password(length: int = 6) -> str:
        """
        Generates a numeric or alphanumeric pairing code.

        Args:
            length (int): Length of the pairing password.

        Returns:
            str: Random PIN string (e.g. '749201').
        """
        return "".join(random.choices(string.digits, k=length))

    @staticmethod
    def create_adb_pairing_payload() -> Tuple[str, str, str]:
        """
        Generates the standard Android ADB QR Code pairing payload string.
        Format specification: WIFI:T:ADB;S:<service_name>;P:<password>;;

        Returns:
            Tuple[str, str, str]: (QR payload string, service name, password).
        """
        rand_id = "".join(random.choices(string.hexdigits.lower(), k=6))
        service_name = f"DroidDoctor-{rand_id}"
        password = QREngine.generate_random_password(6)
        payload = f"WIFI:T:ADB;S:{service_name};P:{password};;"
        return payload, service_name, password

    @staticmethod
    def generate_qr_image(data: str, size: int = 220, bg_color="#FFFFFF", fg_color="#0F172A") -> Image.Image:
        """
        Generates a high-contrast PIL Image representing the QR code for UI embedding.

        Args:
            data (str): Payload text or URI to encode.
            size (int): Pixel dimension (width & height).
            bg_color (str): Background hex color.
            fg_color (str): Foreground module hex color.

        Returns:
            Image.Image: Formatted PIL Image object ready for CTkImage.
        """
        try:
            import qrcode
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=2,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGBA")
            return img.resize((size, size), Image.Resampling.NEAREST)
        except Exception:
            # Fallback placeholder image if qrcode fails
            fallback = Image.new("RGBA", (size, size), bg_color)
            draw = ImageDraw.Draw(fallback)
            draw.rectangle([(10, 10), (size - 10, size - 10)], outline=fg_color, width=3)
            draw.text((size // 2, size // 2), "QR Unavailable", fill=fg_color, anchor="mm")
            return fallback
