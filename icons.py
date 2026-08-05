from PIL import Image, ImageTk, ImageOps

from config import ASSETS, BASE_DIR, ICON_PATH


def resolve_ico():
    ico = ICON_PATH
    if not ico.exists():
        ico = BASE_DIR / "assets" / "beu.ico"
    return ico if ico.exists() else None


def set_window_icon(window):
    """Set beu.ico for title bar / taskbar / Alt+Tab."""
    ico = resolve_ico()
    if not ico:
        return None
    try:
        window.iconbitmap(default=str(ico))
        window.iconbitmap(str(ico))
    except Exception:
        pass
    photo = None
    try:
        img = Image.open(ico).convert("RGBA")
        photo = ImageTk.PhotoImage(img)
        window.iconphoto(True, photo)
    except Exception:
        pass
    return photo


def set_toplevel_icon(win, window_icon_photo=None):
    ico = resolve_ico()
    if not ico:
        return
    try:
        win.iconbitmap(str(ico))
    except Exception:
        pass
    try:
        if window_icon_photo is not None:
            win.iconphoto(True, window_icon_photo)
    except Exception:
        pass


def load_nav_icons(theme_name):
    """Return (icons_dict, refs_list)."""
    mapping = {
        "res": "res_white.png",
        "setting": "setting_white.png",
        "faq": "faq_white.png",
        "info": "info_white.png",
        "translate": "translate_white.png",
        "theme": "theme.png",
        "tiktok": "tiktok_white.png",
        "search": "search_white.png",
        "mods": "tool_white.png",
    }
    is_dark = theme_name == "dark"
    icons = {}
    refs = []
    for key, filename in mapping.items():
        path = ASSETS / filename
        if not path.exists():
            icons[key] = None
            continue
        try:
            img = Image.open(path).convert("RGBA")
            img = img.resize((22, 22), Image.Resampling.LANCZOS)
            if not is_dark:
                r, g, b, a = img.split()
                rgb = Image.merge("RGB", (r, g, b))
                inv = ImageOps.invert(rgb)
                img = Image.merge("RGBA", (*inv.split(), a))
            photo = ImageTk.PhotoImage(img)
            icons[key] = photo
            refs.append(photo)
        except Exception as e:
            print(f"Cannot load {filename}: {e}")
            icons[key] = None
    return icons, refs
