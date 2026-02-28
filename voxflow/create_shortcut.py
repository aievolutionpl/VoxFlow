"""Create a desktop shortcut for VoxFlow — works for both venv and EXE builds.

Built by AI Evolution Polska
"""
import os
import sys
import re
import subprocess


def _sanitize_path(path: str) -> str:
    """Sanitize a file path to prevent injection in PowerShell commands."""
    return re.sub(r'[`$\{\}\[\];&|]', '', path)


def _get_desktop() -> str:
    """Return the current user's Desktop path (Windows)."""
    try:
        import ctypes
        import ctypes.wintypes
        CSIDL_DESKTOP = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, 0, buf)
        if buf.value:
            return buf.value
    except Exception:
        pass
    return os.path.join(os.path.expanduser("~"), "Desktop")


def _create_via_powershell(shortcut_path: str, target: str, workdir: str,
                            icon_path: str, description: str, args: str = "") -> bool:
    """Create a .lnk shortcut by writing and running a temp PowerShell script."""
    import tempfile

    # Build PS1 content — use single-quoted PS strings for paths (no backslash escaping needed)
    # For Arguments we use double-quoted PS string with escaped inner quotes
    ps_lines = [
        "$ws = New-Object -ComObject WScript.Shell",
        f"$sc = $ws.CreateShortcut('{shortcut_path}')",
        f"$sc.TargetPath = '{target}'",
        f"$sc.WorkingDirectory = '{workdir}'",
    ]
    if args:
        # args may contain double quotes; escape them as ` in PS double-quoted string
        escaped_args = args.replace('"', '`"')
        ps_lines.append(f'$sc.Arguments = "{escaped_args}"')
    if os.path.exists(icon_path):
        ps_lines.append(f"$sc.IconLocation = '{icon_path},0'")
    ps_lines += [
        f"$sc.Description = '{description}'",
        "$sc.WindowStyle = 7",
        "$sc.Save()",
    ]

    ps_script = "\r\n".join(ps_lines)

    # Write to a temp file — use utf-8-sig (BOM) so PowerShell reads it correctly
    fd, ps_path = tempfile.mkstemp(suffix=".ps1", prefix="voxflow_sc_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8-sig") as f:
            f.write(ps_script)

        result = subprocess.run(
            [
                "powershell",
                "-NoProfile", "-NonInteractive",
                "-ExecutionPolicy", "Bypass",
                "-File", ps_path,
            ],
            capture_output=True, text=True, timeout=20,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"  [PS fallback error] {e}")
        return False
    finally:
        try:
            os.unlink(ps_path)
        except OSError:
            pass



def create_desktop_shortcut_for_bat(project_dir: str) -> bool:
    """Create a desktop shortcut that launches START_VOXFLOW.bat.

    This is the primary shortcut created after install.bat runs.
    It doesn't require an EXE — just the venv + source.
    """
    desktop       = _get_desktop()
    shortcut_path = os.path.join(desktop, "VoxFlow.lnk")
    launcher_bat  = os.path.join(project_dir, "START_VOXFLOW.bat")
    icon_path     = os.path.join(project_dir, "assets", "voxflow.ico")
    cmd_exe       = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "cmd.exe")
    # Launch minimized (/c runs and closes the interim window; start hides it)
    args          = f'/c "{launcher_bat}"'

    if not os.path.exists(launcher_bat):
        print(f"❌ START_VOXFLOW.bat not found: {launcher_bat}")
        return False

    # --- Try win32com first (most reliable) ---
    try:
        import win32com.client  # type: ignore
        shell    = win32com.client.Dispatch("WScript.Shell")
        sc       = shell.CreateShortCut(shortcut_path)
        sc.TargetPath       = cmd_exe
        sc.Arguments        = args
        sc.WorkingDirectory = project_dir
        sc.Description      = "VoxFlow — Lokalne dyktowanie głosem • AI Evolution Polska"
        sc.WindowStyle      = 7  # minimized (hides cmd flash)
        if os.path.exists(icon_path):
            sc.IconLocation = icon_path
        sc.save()
        print(f"✅ Skrót na pulpicie: {shortcut_path}")
        return True
    except ImportError:
        pass

    # --- Fallback: PowerShell ---
    ok = _create_via_powershell(
        shortcut_path=shortcut_path,
        target=cmd_exe,
        workdir=project_dir,
        icon_path=icon_path,
        description="VoxFlow — Lokalne dyktowanie głosem",
        args=args,
    )
    if ok:
        print(f"✅ Skrót na pulpicie: {shortcut_path}")
    else:
        print(f"⚠️  Nie udało się stworzyć skrótu. Możesz ręcznie przeciągnąć START_VOXFLOW.bat na pulpit.")
    return ok


def create_desktop_shortcut_for_exe(project_dir: str) -> bool:
    """Create a desktop shortcut pointing directly at VoxFlow.exe (portable/EXE build)."""
    desktop       = _get_desktop()
    shortcut_path = os.path.join(desktop, "VoxFlow.lnk")
    exe_path      = os.path.join(project_dir, "VoxFlow.exe")
    icon_path     = os.path.join(project_dir, "assets", "voxflow.ico")

    if not os.path.exists(exe_path):
        print(f"❌ VoxFlow.exe nie znaleziony: {exe_path}")
        return False

    try:
        import win32com.client  # type: ignore
        shell = win32com.client.Dispatch("WScript.Shell")
        sc    = shell.CreateShortCut(shortcut_path)
        sc.TargetPath       = exe_path
        sc.WorkingDirectory = project_dir
        sc.Description      = "VoxFlow — Lokalne dyktowanie głosem"
        if os.path.exists(icon_path):
            sc.IconLocation = icon_path
        sc.save()
        print(f"✅ Skrót na pulpicie: {shortcut_path}")
        return True
    except ImportError:
        pass

    ok = _create_via_powershell(
        shortcut_path=shortcut_path,
        target=exe_path,
        workdir=project_dir,
        icon_path=icon_path,
        description="VoxFlow — Lokalne dyktowanie głosem",
    )
    if ok:
        print(f"✅ Skrót na pulpicie: {shortcut_path}")
    else:
        print("⚠️  Nie udało się stworzyć skrótu do EXE.")
    return ok


# ── Legacy entry point (backwards compat) ──────────────────────────────────────
def create_shortcut():
    """Legacy: create EXE shortcut. Called from old build scripts."""
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    exe_dir = os.path.join(project_dir, "dist", "VoxFlow")
    return create_desktop_shortcut_for_exe(exe_dir)


if __name__ == "__main__":
    # Called directly — prefer bat launcher if venv exists, else EXE
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    if os.path.exists(os.path.join(project_dir, "START_VOXFLOW.bat")):
        create_desktop_shortcut_for_bat(project_dir)
    else:
        create_shortcut()
