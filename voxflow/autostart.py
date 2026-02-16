"""VoxFlow Auto-Start — Manage Windows startup behavior.

Adds/removes VoxFlow from Windows startup using the Registry
(HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run).

Built by AI Evolution Polska
"""
import os
import sys

_REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
_APP_NAME = "VoxFlow"


def get_exe_path() -> str:
    """Get the path to VoxFlow.exe (or the python command if running from source)."""
    if getattr(sys, 'frozen', False):
        # Running as compiled .exe
        return sys.executable
    else:
        # Running from source — return the python command to run
        return f'"{sys.executable}" -m voxflow.main'


def _validate_exe_path(path: str) -> bool:
    """Validate that the path is safe to register in the Windows Registry."""
    if not path or len(path) > 500:
        return False
    # Check for dangerous characters that could be used for injection
    dangerous_chars = {'<', '>', '|', '&', '^', '%', '\n', '\r', '\0'}
    if any(c in path for c in dangerous_chars):
        return False
    return True


def is_autostart_enabled() -> bool:
    """Check if VoxFlow is set to start with Windows."""
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _REGISTRY_PATH,
            0, winreg.KEY_READ,
        ) as key:
            try:
                winreg.QueryValueEx(key, _APP_NAME)
                return True
            except FileNotFoundError:
                return False
    except Exception:
        return False


def enable_autostart():
    """Add VoxFlow to Windows startup."""
    try:
        import winreg
        exe_path = get_exe_path()

        if not _validate_exe_path(exe_path):
            print(f"❌ Auto-start error: Invalid executable path")
            return False

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _REGISTRY_PATH,
            0, winreg.KEY_WRITE,
        ) as key:
            winreg.SetValueEx(key, _APP_NAME, 0, winreg.REG_SZ, exe_path)

        print(f"✅ Auto-start enabled: {exe_path}")
        return True
    except Exception as e:
        print(f"❌ Auto-start error: {e}")
        return False


def disable_autostart():
    """Remove VoxFlow from Windows startup."""
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _REGISTRY_PATH,
            0, winreg.KEY_WRITE,
        ) as key:
            try:
                winreg.DeleteValue(key, _APP_NAME)
            except FileNotFoundError:
                pass
        print("✅ Auto-start disabled")
        return True
    except Exception as e:
        print(f"❌ Auto-start disable error: {e}")
        return False


def set_autostart(enabled: bool):
    """Enable or disable auto-start."""
    if enabled:
        return enable_autostart()
    else:
        return disable_autostart()
