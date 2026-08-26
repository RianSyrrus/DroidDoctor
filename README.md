# DroidDoctor Desktop Suite (v1.0.0 Pro)

> High-Performance Android Hardware Diagnostic, Low-Latency Screen Mirroring, Safe Debloater, and System Maintenance Suite for Windows.

[Baca Dokumentasi dalam Bahasa Indonesia (README_ID.md)](README_ID.md)

---

## Overview

DroidDoctor is an open-source, production-grade desktop management suite engineered for Android technicians, power users, and system developers. Built on top of CustomTkinter, Python 3.10+, and Android Debug Bridge (ADB), it provides comprehensive real-time telemetry, low-latency display mirroring via Scrcpy 4.0, zero-risk package debloating, intelligent storage cleaning, and hardware quality control inspection reports.

---

## Core Capabilities & Features

### 1. Real-Time Hardware Telemetry & Dashboard
* Comprehensive battery metrics: State of Health (SoH), Design Capacity (mAh), Achievable Capacity, Voltage, Operating Temperature, and Charging Wattage.
* RAM and ZRAM Swap telemetry with live memory utilization percentages.
* Storage partition inspection (UFS / eMMC technology and File-Based Encryption status).
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

## System Requirements

* Operating System: Windows 10 (1703+) or Windows 11 (64-bit x64 or ARM64 Prism).
* Android Target: Android 5.0 (Lollipop) up to Android 14+ with USB Debugging enabled.
* Connectivity: Standard USB data cable or Wireless ADB over local Wi-Fi network.

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
