import sys
import ctypes
from tkinter import messagebox

try:
    from PIL import Image  # noqa: F401
except ImportError:
    messagebox.showerror("Missing library", "Please install Pillow:\n\npip install pillow")
    sys.exit(1)

if sys.platform != "win32":
    messagebox.showerror("Unsupported", "Windows only.")
    sys.exit(1)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """Re-launch as administrator."""
    if getattr(sys, "frozen", False):
        exe = sys.executable
        params = ""
    else:
        exe = sys.executable
        params = f'"{__file__}"'
    ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)
    sys.exit(0)


if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
    else:
        from ui.app import App
        App().mainloop()
