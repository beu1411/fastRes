import ctypes
import os
import subprocess
from pathlib import Path

user32 = ctypes.windll.user32


class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", ctypes.c_wchar * 32), ("dmSpecVersion", ctypes.c_ushort),
        ("dmDriverVersion", ctypes.c_ushort), ("dmSize", ctypes.c_ushort),
        ("dmDriverExtra", ctypes.c_ushort), ("dmFields", ctypes.c_ulong),
        ("dmPositionX", ctypes.c_long), ("dmPositionY", ctypes.c_long),
        ("dmDisplayOrientation", ctypes.c_ulong), ("dmDisplayFixedOutput", ctypes.c_ulong),
        ("dmColor", ctypes.c_short), ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short), ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short), ("dmFormName", ctypes.c_wchar * 32),
        ("dmLogPixels", ctypes.c_ushort), ("dmBitsPerPel", ctypes.c_ulong),
        ("dmPelsWidth", ctypes.c_ulong), ("dmPelsHeight", ctypes.c_ulong),
        ("dmDisplayFlags", ctypes.c_ulong), ("dmDisplayFrequency", ctypes.c_ulong),
    ]


def set_resolution(w, h):
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    dm.dmPelsWidth = w
    dm.dmPelsHeight = h
    dm.dmFields = 0x80000 | 0x100000
    result = user32.ChangeDisplaySettingsW(ctypes.byref(dm), 0)
    return result == 0, result


def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def set_monitors_state(disable=True):
    """Disable or enable all PnP Monitor devices. Requires admin."""
    if not is_admin():
        return False, "admin"
    action = "Disable-PnpDevice" if disable else "Enable-PnpDevice"
    ps = (
        f"Get-PnpDevice -Class Monitor -ErrorAction SilentlyContinue | "
        f"ForEach-Object {{ {action} -InstanceId $_.InstanceId -Confirm:$false -ErrorAction SilentlyContinue }}"
    )
    try:
        flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            capture_output=True, text=True, timeout=30, creationflags=flags,
        )
        return True, "ok"
    except Exception:
        return False, "fail"


def _find_nvcplui():
    """Search common install locations for NVIDIA Control Panel."""
    fixed = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
        / "NVIDIA Corporation" / "Control Panel Client" / "nvcplui.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
        / "NVIDIA Corporation" / "Control Panel Client" / "nvcplui.exe",
    ]
    for p in fixed:
        if p.is_file():
            return p

    roots = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "NVIDIA Corporation",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "NVIDIA Corporation",
    ]
    for root in roots:
        if not root.is_dir():
            continue
        try:
            for dirpath, dirnames, filenames in os.walk(root):
                rel = Path(dirpath).relative_to(root)
                if len(rel.parts) > 3:
                    dirnames.clear()
                    continue
                for fn in filenames:
                    if fn.lower() == "nvcplui.exe":
                        return Path(dirpath) / fn
        except OSError:
            pass

    try:
        import winreg
        for hive, sub in (
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\nvcplui.exe"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\nvcplui.exe"),
        ):
            try:
                key = winreg.OpenKey(hive, sub)
                try:
                    val, _ = winreg.QueryValueEx(key, "")
                    if val and Path(val).is_file():
                        winreg.CloseKey(key)
                        return Path(val)
                except OSError:
                    pass
                winreg.CloseKey(key)
            except OSError:
                pass
    except Exception:
        pass

    return None


def open_nvidia_control_panel():
    """Open NVIDIA Control Panel. Never call bare startfile('nvcplui.exe')."""
    exe = _find_nvcplui()
    if exe:
        try:
            subprocess.Popen([str(exe)], cwd=str(exe.parent))
            return True
        except Exception:
            try:
                os.startfile(str(exe))
                return True
            except Exception:
                pass

    # Store / Start Menu NVIDIA Control Panel via PowerShell
    try:
        flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        ps = (
            "$app = Get-StartApps | Where-Object { $_.Name -match 'NVIDIA' -and $_.Name -match 'Control' } "
            "| Select-Object -First 1; "
            "if ($app) { Start-Process \"shell:AppsFolder\\$($app.AppID)\"; exit 0 } else { exit 1 }"
        )
        r = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            capture_output=True, timeout=15, creationflags=flags,
        )
        if r.returncode == 0:
            return True
    except Exception:
        pass

    return False
