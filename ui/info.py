import tkinter as tk
import webbrowser

from PIL import Image, ImageTk

from config import ASSETS
from constants import CURRENT_VERSION


class InfoMixin:
    def _page_info(self):
        C, T = self.C, self.T
        tk.Label(self.main, text=T["info_title"], font=("Segoe UI", 14, "bold"),
                 fg=C["TEXT"], bg=C["BG"]).pack(anchor="w", padx=28, pady=(22, 18))

        card = tk.Frame(self.main, bg=C["CARD"], highlightbackground=C["BORDER"],
                        highlightthickness=1, highlightcolor=C["BORDER"])
        card.pack(fill="x", padx=28, pady=4)

        head = tk.Frame(card, bg=C["CARD"])
        head.pack(fill="x", padx=20, pady=(18, 6))

        tk.Label(head, text="⚡ FastRes", font=("Segoe UI", 16, "bold"),
                 fg=C["ACCENT"], bg=C["CARD"]).pack(side="left")
        tk.Label(head, text=f"v{CURRENT_VERSION}", font=("Segoe UI", 10),
                 fg=C["TEXT_DIM"], bg=C["CARD"]).pack(side="right")

        tk.Label(card, text=T["app_sub"], font=("Segoe UI", 10),
                 fg=C["TEXT_DIM"], bg=C["CARD"]).pack(anchor="w", padx=20, pady=(0, 4))
        tk.Label(card, text=T["info_desc"], font=("Segoe UI", 10),
                 fg=C["TEXT"], bg=C["CARD"], wraplength=480, justify="left").pack(
            anchor="w", padx=20, pady=(0, 6))
        tk.Label(card, text=T["info_feature"], font=("Segoe UI", 10),
                 fg=C["TEXT"], bg=C["CARD"], wraplength=480, justify="left").pack(
            anchor="w", padx=20, pady=(0, 12))

        tk.Frame(card, bg=C["BORDER"], height=1).pack(fill="x", padx=20, pady=(4, 12))

        bottom = tk.Frame(card, bg=C["CARD"])
        bottom.pack(fill="x", padx=20, pady=(0, 16))

        tk.Label(bottom, text=T["info_dev"], font=("Segoe UI", 10),
                 fg=C["TEXT_DIM"], bg=C["CARD"]).pack(side="left")

        tiktok_icon = self.icons.get("tiktok")
        tiktok_photo = None
        tiktok_path = ASSETS / "tiktok_white.png"
        if tiktok_path.exists():
            try:
                img = Image.open(tiktok_path).convert("RGBA")
                img = img.resize((16, 16), Image.Resampling.LANCZOS)
                tiktok_photo = ImageTk.PhotoImage(img)
                self.icon_refs.append(tiktok_photo)
            except Exception:
                tiktok_photo = tiktok_icon

        tiktok_btn = tk.Frame(bottom, bg="#010101", cursor="hand2")
        tiktok_btn.pack(side="right")

        border = tk.Frame(tiktok_btn, bg=C["BORDER"])
        border.pack()
        inner = tk.Frame(border, bg="#010101")
        inner.pack(padx=1, pady=1)

        content = tk.Frame(inner, bg="#010101")
        content.pack(padx=12, pady=6)

        if tiktok_photo:
            icon_lbl = tk.Label(content, image=tiktok_photo, bg="#010101")
            icon_lbl.image = tiktok_photo
            icon_lbl.pack(side="left", padx=(0, 6))
        else:
            icon_lbl = tk.Label(content, text="♪", font=("Segoe UI", 10), fg="white", bg="#010101")
            icon_lbl.pack(side="left", padx=(0, 6))

        txt_lbl = tk.Label(content, text=T["info_tiktok"], font=("Segoe UI", 9, "bold"),
                           fg="white", bg="#010101")
        txt_lbl.pack(side="left")

        def open_tiktok(e=None):
            webbrowser.open("https://www.tiktok.com/@beuu1411")

        def on_enter(e):
            border.config(bg="#fe2c55")
            for w in (tiktok_btn, inner, content, icon_lbl, txt_lbl):
                w.config(bg="#1a1a1a")

        def on_leave(e):
            border.config(bg=C["BORDER"])
            for w in (tiktok_btn, inner, content, icon_lbl, txt_lbl):
                w.config(bg="#010101")

        for w in (tiktok_btn, border, inner, content, icon_lbl, txt_lbl):
            w.bind("<Button-1>", open_tiktok)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
