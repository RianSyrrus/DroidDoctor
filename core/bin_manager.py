import os
import sys
import shutil

class BinManager:
    """
    Central binary asset manager ensuring ADB and Scrcpy binaries execute
    from a persistent LocalAppData directory in frozen/portable mode, preventing
    PyInstaller temporary directory (_MEIPASS) lockups during application shutdown.
    """
    _cached_bin_dir = None

    @classmethod
    def get_bin_dir(cls) -> str:
        """
        Resolves the absolute path to the directory containing executable binaries.

        Returns:
            str: Path to local project bin directory or persistent AppData bin directory.
        """
        if cls._cached_bin_dir and os.path.exists(cls._cached_bin_dir):
            return cls._cached_bin_dir

        # 1. Local development mode
        base_proj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_bin = os.path.join(base_proj, "bin", "scrcpy")
        if os.path.exists(os.path.join(local_bin, "adb.exe")):
            cls._cached_bin_dir = local_bin
            return local_bin

        # 2. Frozen/Portable PyInstaller mode
        local_app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        persistent_dir = os.path.join(local_app_data, "DroidDoctor", "bin", "scrcpy")
        os.makedirs(persistent_dir, exist_ok=True)

        meipass = getattr(sys, '_MEIPASS', '')
        if meipass:
            src_dir = os.path.join(meipass, "bin", "scrcpy")
            if os.path.exists(src_dir):
                for item in os.listdir(src_dir):
                    s = os.path.join(src_dir, item)
                    d = os.path.join(persistent_dir, item)
                    try:
                        if not os.path.exists(d) or (os.path.isfile(s) and os.path.getsize(s) != os.path.getsize(d)):
                            if os.path.isdir(s):
                                shutil.copytree(s, d, dirs_exist_ok=True)
                            else:
                                shutil.copy2(s, d)
                    except Exception:
                        pass

        cls._cached_bin_dir = persistent_dir
        return persistent_dir

    @classmethod
    def get_adb_path(cls) -> str:
        """
        Resolves the absolute path to the ADB executable.

        Returns:
            str: Absolute path to adb.exe or 'adb' system fallback.
        """
        bin_dir = cls.get_bin_dir()
        adb_exe = os.path.join(bin_dir, "adb.exe")
        if os.path.exists(adb_exe):
            return adb_exe
        return "adb"

    @classmethod
    def get_scrcpy_path(cls) -> str:
        """
        Resolves the absolute path to the Scrcpy executable.

        Returns:
            str: Absolute path to scrcpy.exe or 'scrcpy' system fallback.
        """
        bin_dir = cls.get_bin_dir()
        scrcpy_exe = os.path.join(bin_dir, "scrcpy.exe")
        if os.path.exists(scrcpy_exe):
            return scrcpy_exe
        return "scrcpy"
