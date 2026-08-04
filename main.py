import sys
from tkinter import messagebox

try:
    from PIL import Image  # noqa: F401
except ImportError:
    messagebox.showerror("Missing library", "Please install Pillow:\n\npip install pillow")
    sys.exit(1)

if sys.platform != "win32":
    messagebox.showerror("Unsupported", "Windows only.")
    sys.exit(1)

from ui.app import App


if __name__ == "__main__":
    App().mainloop()
