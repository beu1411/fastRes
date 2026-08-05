import ctypes
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


class App(tk.Tk, SidebarMixin, ModsMixin, ResolutionsMixin, SettingsMixin, InfoMixin, DialogsMixin):
    def __init__(self):
        super().__init__()

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

        self.sidebar_collapsed = False
        self.sidebar_width_expanded = 210
        self.sidebar_width_collapsed = 64
        self._animating = False

        self._load_icons()
        self._build()
        self.bind_all("<MouseWheel>", self._wheel)
        if not self.cfg.get("hide_welcome", False):
            self.after(200, self._show_welcome)

        # Emergency cleanup on close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        try:
            from valorant import emergency_cleanup, get_paks_dir
            path = self.cfg.get("game_path", "")
            paks = get_paks_dir(path) if path else None
            emergency_cleanup(paks)
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
