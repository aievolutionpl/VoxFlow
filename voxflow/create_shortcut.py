"""Create desktop shortcut for VoxFlow.

Built by AI Evolution Polska
"""
import os
import sys
import re


def _sanitize_path(path: str) -> str:
    """Sanitize a file path to prevent injection in PowerShell commands."""
    # Remove characters that could be used for PowerShell injection
    return re.sub(r'[`$\{\}\[\];&|]', '', path)


def create_shortcut():
    """Create a desktop shortcut for VoxFlow.exe."""
    try:
        import ctypes.wintypes
        
        # Get desktop path
        CSIDL_DESKTOP = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, 0, buf)
        desktop = buf.value
    except Exception:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    # Determine exe path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    exe_path = os.path.join(project_dir, "dist", "VoxFlow", "VoxFlow.exe")
    icon_path = os.path.join(project_dir, "assets", "voxflow.ico")
    shortcut_path = os.path.join(desktop, "VoxFlow.lnk")

    if not os.path.exists(exe_path):
        print(f"❌ VoxFlow.exe not found at: {exe_path}")
        print("   Run BUILD_EXE.bat first!")
        return False

    try:
        # Use COM to create shortcut
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        if os.path.exists(icon_path):
            shortcut.IconLocation = icon_path
        shortcut.Description = "VoxFlow — Lokalne rozpoznawanie mowy • AI Evolution Polska"
        shortcut.save()
        print(f"✅ Shortcut created: {shortcut_path}")
        return True
    except ImportError:
        # Fallback: use PowerShell with sanitized paths
        safe_shortcut = _sanitize_path(shortcut_path)
        safe_exe = _sanitize_path(exe_path)
        safe_workdir = _sanitize_path(os.path.dirname(exe_path))
        safe_icon = _sanitize_path(icon_path)

        ps_script = f'''
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut("{safe_shortcut}")
$sc.TargetPath = "{safe_exe}"
$sc.WorkingDirectory = "{safe_workdir}"
$sc.IconLocation = "{safe_icon}"
$sc.Description = "VoxFlow"
$sc.Save()
'''
        import subprocess
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            print(f"✅ Shortcut created: {shortcut_path}")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False


if __name__ == "__main__":
    create_shortcut()
