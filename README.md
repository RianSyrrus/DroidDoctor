# DroidDoctor Desktop Suite (v1.2.3 Pro)

> High-Performance Android Hardware Diagnostics, Wireless ADB QR Code Suite, Low-Latency Screen Mirroring, Safe Non-Root Debloater, and System Maintenance Suite for Windows.

[![Release](https://img.shields.io/badge/Release-v1.2.3--Pro-blue.svg)](https://github.com/RianSyrrus/DroidDoctor/releases)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Baca Dokumentasi dalam Bahasa Indonesia (README_ID.md)](README_ID.md)

---

## ⚠️ Project Status & Known Limitations

> **Development Phase:** `v1.1.1 Patch Release (Active Development / Public Beta)`

DroidDoctor is actively developed to support the entire spectrum of Android devices. Due to massive hardware fragmentation, custom OEM kernels, and proprietary vendor implementations:

1. **Hardware Telemetry Variations:** Some proprietary battery State of Health (SoH) algorithms, fast-charging wattage readouts, or multi-lens camera configurations on specific vendor ROMs (such as Samsung One UI, Vivo Funtouch, Realme UI, or Transsion XOS) may require continuous community property mapping.
2. **Platform & Driver Quirks:** Non-standard USB data cables, missing OEM ADB drivers, or aggressive battery saving features on certain phones may affect ADB daemon polling latency.
3. **Community Telemetry Mapping (Call for Feedback):** If you discover missing chipset specifications, unmapped battery capacities, or metric inaccuracies on your specific phone model, please open an issue in [GitHub Issues](https://github.com/RianSyrrus/DroidDoctor/issues) with your device model and `getprop` output.

---

## Overview

DroidDoctor is an open-source, production-grade desktop management suite engineered for Android technicians, power users, and system developers. Built on top of CustomTkinter, Python 3.10+, and Android Debug Bridge (ADB), it provides comprehensive real-time telemetry, low-latency display mirroring via Scrcpy 4.0, zero-risk package debloating, intelligent storage cleaning, and hardware quality control inspection reports.

---

## Core Capabilities & Features

### 1. Real-Time Hardware Telemetry & Dashboard
* **Offline Device Database:** Built-in offline database covering **50,000+ Android models** for instant commercial marketing name lookup, factory design capacity, and sub-millisecond specs recognition.
* Comprehensive battery metrics: State of Health (SoH), Design Capacity (mAh), Achievable Capacity, Voltage, Operating Temperature, and Charging Wattage.
* RAM and ZRAM Swap telemetry with live memory utilization percentages.
* Storage partition inspection (UFS 4.0 / 3.1 / 2.2 / 2.1 vs eMMC 5.1 technology and File-Based Encryption status).
* Display panel diagnostics: Refresh rate (Hz), Screen Resolution, Density (DPI), and Widevine DRM level (L1/L3).
* Camera and processor specifications (SoC, architecture, multi-sensor optical layout).

### 2. High-Performance Screen Mirroring & Device Control
* Powered by Scrcpy 4.0 (SDL 3.4.8 and libavcodec 62).
* Low-latency video streaming up to 60 FPS with selectable resolutions (1080p / 720p).
* Integrated USB HID Keyboard emulation (physical PC keyboard mapping to Android input).
* Dedicated hardware navigation shortcuts: Home, Back, App Switcher (Recents), Power, Volume Up, Volume Down, and USB Stay Awake toggle.
* Lossless screenshot capture and screen recording output saved directly to local directory.

### 3. Non-Destructive Debloater & App Manager
* Non-root user space uninstallation (`pm uninstall -k --user 0`). Applications can be restored instantly with a single click.
* Immutable safety whitelist: Core system packages (such as `com.android.systemui`, `com.android.settings`, and system launchers) are locked to prevent system instability.
* Settings-Locked Technician Mode: The Debloater tab is hidden by default and accessible only when explicitly enabled via Application Settings.
* Type-to-Confirm challenge for system package operations.

### 4. Protected Storage Cleanup
* Intelligent cache and thumbnail cleaner without touching user data.
* Whitelist protection for user media: `DCIM/Camera`, `Pictures`, `Downloads`, `Documents`, and `WhatsApp Media` are strictly locked and exempt from deletion.
* Itemized file inspector for transparent review before executing cleanup.

### 5. Technician Utilities & QC Inspection
* Export official hardware diagnostic reports (.TXT) and Quality Control (QC) inspection certificates.
* Automated package installer supporting APK overwrite, downgrade tolerance (`-r -d -t`), and test build installation.
* Battery calibration reset via kernel batterystats dump.
* One-click reboot commands: Normal System, Recovery Mode, and Bootloader / Fastboot Mode.

---

## 🔌 Device Connection Guide (USB & Wireless ADB)

Before using DroidDoctor, ensure your Android device has **USB Debugging** or **Wireless Debugging** enabled. Follow the instructions below based on your preferred connection method:

### 1. Enabling Developer Options & USB Debugging (First-Time Setup)
1. Open phone **Settings** > **About Phone** (or **About Device**).
2. Tap **Build Number** (or **OS Version** / **MIUI/HyperOS Version**) **7 times** consecutively until the popup *"You are now a developer!"* appears.
3. Navigate to **Settings** > **System** > **Developer Options** (or **Additional Settings** > **Developer Options** on Xiaomi / OPPO / Vivo / Realme).
4. Enable **USB Debugging** (toggle ON).
   * *Xiaomi / POCO / Redmi Users:* Also enable **"Install via USB"** and **"USB debugging (Security settings)"** (requires Mi Account login).

### 2. Connecting via USB Cable (Recommended)
1. Connect your phone to your PC/laptop using a standard USB data cable (ensure it is a data cable, not charging-only).
2. On your phone screen, a prompt titled **"Allow USB debugging?"** will appear.
3. Check the box **"Always allow from this computer"**, then tap **Allow** (OK).
4. DroidDoctor will automatically detect the device and populate the dashboard within 1 second.

### 3. Connecting via Wi-Fi (Wireless ADB Connection Suite)
* **Method 1: Instant QR Code Scan (Android 11+ Developer Options):**
  1. Connect your PC and Android phone to the **same Wi-Fi network**.
  2. On your phone, go to **Developer Options** > **Wireless Debugging** > tap **"Pair device with QR code"**.
  3. In DroidDoctor, open **Wi-Fi Connect** (Tab: **📷 Scan QR Code**) and point your phone camera at the screen.
  4. DroidDoctor's real-time handshake daemon pairs and connects automatically in **< 1 second**!
* **Method 2: Smart Auto-Discovery & Inline PIN:**
  1. Open **Wi-Fi Connect** > **🔍 Auto-Discovery**.
  2. Click **Scan Network for Devices**. Active endpoints and pairing services are discovered automatically.
  3. Enter the 6-digit pairing PIN shown on your phone and click **Pair PIN** for instant 1-click connection.
* **Method 3: Saved Bookmarks & Legacy TCP/IP (Port 5555):**
  1. Save frequently used phone profiles and nicknames in **⭐ Manual & Bookmarks** for instant reconnection.

### 🛠️ Common Connection Troubleshooting
* **Device not detected:** Re-plug the USB cable, switch the USB connection mode on your phone from *"Charging only"* to *"File Transfer (MTP)"*, or try a different USB port.
* **Authorization stuck on "Offline" / "Unauthorized":** Go to **Developer Options** on your phone > tap **"Revoke USB debugging authorizations"**, then re-plug the cable and tap **Allow**.

---

## Getting Started

### Option A: Setup Installer (Recommended for Standard Installation)
1. Download `DroidDoctor-Setup-v1.2.3.exe` from [GitHub Releases](https://github.com/RianSyrrus/DroidDoctor/releases).
2. Run the installer wizard to install DroidDoctor to your Start Menu and Desktop.

### Option B: Portable Standalone Executable (Zero Installation)
1. Download `DroidDoctor-v1.2.3-Portable.zip` from [GitHub Releases](https://github.com/RianSyrrus/DroidDoctor/releases).
2. Extract the archive and launch `DroidDoctor.exe`. No external Python or ADB installation is required.

### Option C: Run from Source Code (For Developers)

```bash
# 1. Clone the repository
git clone https://github.com/RianSyrrus/DroidDoctor.git
cd DroidDoctor

# 2. Create and activate a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Launch the application
python main.py
```

---

## System Requirements

* **Operating System:** Windows 10 (1703+) or Windows 11 (64-bit x64 or ARM64 Prism).
* **Android Target:** Android 5.0 (Lollipop) up to Android 16+ (HyperOS 3.0 / Android 16) with USB Debugging enabled.
* **Connectivity:** Standard USB data cable or Wireless ADB over local Wi-Fi network.

---

## Safety Guidelines & Legal Disclaimer

### Safety Architecture
1. **Non-Root Operation:** DroidDoctor interacts exclusively via standard Android Debug Bridge protocol. It does not flash unauthorized recovery images or modify the raw bootloader partition.
2. **User 0 Isolation:** Debloating operations do not remove binaries from the read-only `/system` partition. Factory reset or one-click restore will reinstate all factory packages.
3. **Data Protection:** Personal file directories are strictly whitelisted against automatic deletion.

### Disclaimer
This software is provided "as is", without warranty of any kind, express or implied. The author shall not be held liable for any damages or unintended consequences resulting from the misuse of this tool. Modifying system packages and executing ADB maintenance tasks should be performed with appropriate technical discretion.

---

## Third-Party Components & Acknowledgements

DroidDoctor integrates and acknowledges the following open-source projects:

* **Scrcpy:** Developed by [Genymobile](https://github.com/Genymobile/scrcpy). Used for high-speed, low-latency Android display mirroring and HID input injection.
* **Android SDK Platform-Tools:** Developed by [Google LLC](https://developer.android.com/tools/releases/platform-tools). Used for device communication via Android Debug Bridge (ADB).
* **CustomTkinter:** Developed by [Tom Schimansky](https://github.com/TomSchimansky/CustomTkinter). Used for modern desktop graphical user interface components.

---

## Author & License

* **Developer:** RianSyrrus
* **License:** Open Source under the [MIT License](LICENSE).

