import ctypes
import threading
import tkinter as tk

from config import load_config, load_customs, save_config
from constants import THEMES
from i18n import LANG
from icons import load_nav_icons, set_toplevel_icon, set_window_icon
from ui.sidebar import SidebarMixin
from ui.mods import ModsMixin
from ui.resolutions import ResolutionsMixin
from ui.settings import SettingsMixin
from ui.info import InfoMixin
from ui.dialogs import DialogsMixin

try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False


class App(tk.Tk, SidebarMixin, ModsMixin, ResolutionsMixin, SettingsMixin, InfoMixin, DialogsMixin):
    def __init__(self):
        super().__init__()
        # Ẩn khi build UI → tránh giật lúc mở app
        self.withdraw()

        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("beu.fastres.app.1.0")
        except Exception:
            pass

        self.cfg = load_config()
        self.lang = self.cfg["language"]
        self.theme_name = self.cfg["theme"]
        if self.theme_name == "system":
            self.theme_name = "dark"
        self.C = THEMES.get(self.theme_name, THEMES["dark"])
        self.T = LANG[self.lang]

        self.title("FastRes")
        self.configure(bg=self.C["BG"])
        self.resizable(True, True)
        self.minsize(720, 540)
        self._window_icon_photo = set_window_icon(self)

        w, h = 860, 640
        self.geometry(f"{w}x{h}")
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

        self.customs = load_customs()
        self.faq_win = None
        self.current_page = "mods"
        self.nav_labels = {}
        self.icons = {}
        self.icon_refs = []
        self.tray_icon = None

        self.sidebar_collapsed = False
        self.sidebar_width_expanded = 210
        self.sidebar_width_collapsed = 64
        self._animating = False

        self._load_icons()
        self._build()
        self.bind_all("<MouseWheel>", self._wheel)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Hiện sau khi UI sẵn sàng
        self.update_idletasks()
        self.deiconify()
        self.lift()
        self.focus_force()

        if not self.cfg.get("hide_welcome", False):
            self.after(300, self._show_welcome)

    def _on_close(self):
        """Ẩn vào system tray; cleanup khi thoát hẳn."""
        if HAS_TRAY:
            self.withdraw()
            self._ensure_tray()
        else:
            self._quit_app()

    def _ensure_tray(self):
        if not HAS_TRAY or self.tray_icon is not None:
            return

        def _make_icon():
            # Dùng icon app (beu.ico) thay vì vẽ tạm
            try:
                from config import ICON_PATH, BASE_DIR
                ico = ICON_PATH if ICON_PATH.exists() else BASE_DIR / "assets" / "beu.ico"
                if ico.exists():
                    img = Image.open(ico).convert("RGBA")
                    img = img.resize((64, 64), Image.Resampling.LANCZOS)
                    return img
            except Exception:
                pass
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            d.ellipse((4, 4, 60, 60), fill=(59, 130, 246, 255))
            d.text((20, 16), "F", fill="white")
            return img

        def on_show(icon, item):
            self.after(0, self._restore_from_tray)

        def on_quit(icon, item):
            self.after(0, self._quit_app)

        menu = pystray.Menu(
            pystray.MenuItem(self.T.get("tray_show", "Show FastRes"), on_show, default=True),
            pystray.MenuItem(self.T.get("tray_quit", "Quit"), on_quit),
        )
        self.tray_icon = pystray.Icon("FastRes", _make_icon(), "FastRes", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _restore_from_tray(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _quit_app(self):
        try:
            from valorant import emergency_cleanup, get_paks_dir
            path = self.cfg.get("game_path", "")
            paks = get_paks_dir(path) if path else None
            emergency_cleanup(paks)
        except Exception:
            pass
        try:
            if self.tray_icon is not None:
                self.tray_icon.stop()
        except Exception:
            pass
        self.destroy()

    def _set_toplevel_icon(self, win):
        set_toplevel_icon(win, getattr(self, "_window_icon_photo", None))

    def _load_icons(self):
        self.icons, self.icon_refs = load_nav_icons(self.theme_name)

    def _wheel(self, e):
        try:
            self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
            if hasattr(self, "_redraw_main_thumb"):
                self._redraw_main_thumb()
        except Exception:
            pass

    def show_toast(self, message, success=True):
        if hasattr(self, "toast") and self.toast.winfo_exists():
            self.toast.destroy()
        C = self.C
        self.toast = tk.Frame(self, bg=C["SUCCESS"] if success else C["ERROR"], height=42)
        self.toast.place(x=0, y=-50, relwidth=1)
        tk.Label(self.toast, text=message, font=("Segoe UI", 10, "bold"),
                 fg="white", bg=C["SUCCESS"] if success else C["ERROR"]).pack(pady=10)

        def slide_in(y=-50):
            if y < 0:
                self.toast.place(x=0, y=y, relwidth=1)
                self.after(12, lambda: slide_in(y + 5))
            else:
                self.toast.place(x=0, y=0, relwidth=1)
                self.after(2200, slide_out)

        def slide_out(y=0):
            if y > -50:
                self.toast.place(x=0, y=y, relwidth=1)
                self.after(12, lambda: slide_out(y - 5))
            else:
                if self.toast.winfo_exists():
                    self.toast.destroy()
        slide_in()

    def _build(self):
        for w in self.winfo_children():
            if isinstance(w, tk.Toplevel):
                continue
            w.destroy()
        self.nav_labels.clear()
        self.icon_refs.clear()
        self._load_icons()

        self._build_sidebar()

        self.main = tk.Frame(self, bg=self.C["BG"])
        self.main.pack(side="left", fill="both", expand=True)
        self._show_page(self.current_page)

        if self.sidebar_collapsed:
            self._apply_collapsed_state(instant=True)

    def _show_page(self, page):
        for w in self.main.winfo_children():
            w.destroy()
        if page == "mods":
            self._page_mods()
        elif page == "resolutions":
            self._page_resolutions()
        elif page == "settings":
            self._page_settings()
        elif page == "info":
            self._page_info()

    def change_lang(self, code):
        self.lang = code
        self.cfg["language"] = code
        save_config(self.cfg)
        self.T = LANG[code]
        self._build()

    def change_theme(self, name):
        self.cfg["theme"] = name
        save_config(self.cfg)
        if name == "system":
            name = "dark"
        self.theme_name = name
        self.C = THEMES[name]
        self._build()
