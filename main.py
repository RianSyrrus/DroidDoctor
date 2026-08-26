import os
import sys
import ctypes
import multiprocessing

# 1. Wajib untuk PyInstaller di Windows agar subprocess/worker tidak memicu loop eksekusi
if __name__ == "__main__":
    multiprocessing.freeze_support()

# 2. Amankan stdout & stderr saat berjalan di mode --noconsole Windows dan catat ke log file
log_path = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "droiddoctor.log")
try:
    log_f = open(log_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = log_f
    sys.stderr = log_f
    print(f"\n--- [DROIDDOCTOR START] PID {os.getpid()} ---")
except Exception:
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

import customtkinter as ctk

# Aktifkan Windows ClearType & High-DPI Awareness V2 agar font 100% tajam & bebas pixel
try:
    # Set PROCESS_PER_MONITOR_DPI_AWARE_V2 (Windows 10 1703+)
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Pastikan Font Smoothing ClearType aktif pada level Windows GDI
try:
    SPI_SETFONTSMOOTHING = 0x004B
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETFONTSMOOTHING, 1, 0, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
except Exception:
    pass

# Set AppUserModelID agar taskbar Windows mengikat ikon kustom DroidDoctor
try:
    myappid = "riansyrrus.droiddoctor.suite.1.0.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

from core.adb_manager import ADBManager
from core.hardware_parser import HardwareParser
from ui.main_window import MainWindow

def main():
    print("=" * 60)
    print("  DroidDoctor v1.0.0 Pro — Android Health & Diagnostics Suite")
    print("=" * 60)
    from core.settings_manager import SettingsManager
    from core.i18n import I18n
    saved_theme = SettingsManager.get_instance().get("theme", "light")
    saved_lang = SettingsManager.get_instance().get("language", "en")
    I18n.set_language(saved_lang)
    print(f"[BOOT] Loaded Config -> Theme: '{saved_theme}', Language: '{saved_lang}'")
    
    ctk.set_appearance_mode(saved_theme)
    ctk.set_default_color_theme("blue")
    
    print("[BOOT] Initializing ADB Manager & Hardware Parser...")
    adb = ADBManager()
    parser = HardwareParser(adb)
    
    print("[BOOT] Launching MainWindow Desktop GUI...")
    app = MainWindow(adb, parser)
    try:
        app.mainloop()
    finally:
        try:
            if "log_f" in globals() and log_f:
                log_f.flush()
                log_f.close()
        except Exception:
            pass
        sys.exit(0)

if __name__ == "__main__":
    main()
