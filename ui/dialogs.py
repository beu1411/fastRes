import tkinter as tk

from config import save_config
from faq_data import FAQ
from i18n import LANG


class DialogsMixin:
    def _show_welcome(self):
        C, T = self.C, self.T
        dlg = tk.Toplevel(self)
        dlg.title("FastRes")
        dlg.configure(bg=C["BG"])
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()
        self._set_toplevel_icon(dlg)

        dw, dh = 420, 260
        dlg.geometry(f"{dw}x{dh}")
        dlg.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dw) // 2
        y = self.winfo_y() + (self.winfo_height() - dh) // 2
        dlg.geometry(f"+{x}+{y}")

        lang_bar = tk.Frame(dlg, bg=C["BG"])
        lang_bar.pack(pady=(16, 0))

        def switch_lang(code):
            if code == self.lang:
                return
            self.lang = code
            self.cfg["language"] = code
            save_config(self.cfg)
            self.T = LANG[code]
            msg_lbl.config(text=self.T["welcome_msg"])
            chk.config(text=self.T["welcome_dont"])
            btn_faq.config(text=self.T["welcome_faq"])
            btn_close.config(text=self.T["welcome_close"])
            _update_lang_btns()
            self._build()
            dlg.lift()
            dlg.focus_force()

        def _update_lang_btns():
            if self.lang == "en":
                btn_en.config(bg=C["ACCENT"], fg="white")
                btn_vi.config(bg=C["CARD"], fg=C["TEXT"])
            else:
                btn_en.config(bg=C["CARD"], fg=C["TEXT"])
                btn_vi.config(bg=C["ACCENT"], fg="white")

        btn_en = tk.Button(
            lang_bar, text="ENG", font=("Segoe UI", 9, "bold"),
            bg=C["ACCENT"] if self.lang == "en" else C["CARD"],
            fg="white" if self.lang == "en" else C["TEXT"],
            activebackground=C["ACCENT_H"], activeforeground="white",
            relief="flat", bd=0, padx=14, pady=4, cursor="hand2",
            highlightthickness=0, takefocus=0,
            command=lambda: switch_lang("en"),
        )
        btn_en.pack(side="left", padx=4)

        btn_vi = tk.Button(
            lang_bar, text="VIE", font=("Segoe UI", 9, "bold"),
            bg=C["ACCENT"] if self.lang == "vi" else C["CARD"],
            fg="white" if self.lang == "vi" else C["TEXT"],
            activebackground=C["ACCENT_H"], activeforeground="white",
            relief="flat", bd=0, padx=14, pady=4, cursor="hand2",
            highlightthickness=0, takefocus=0,
            command=lambda: switch_lang("vi"),
        )
        btn_vi.pack(side="left", padx=4)

        msg_lbl = tk.Label(
            dlg, text=T["welcome_msg"],
            font=("Segoe UI", 11), fg=C["TEXT"], bg=C["BG"],
            wraplength=360, justify="center",
        )
        msg_lbl.pack(pady=(18, 14), padx=24)

        dont_var = tk.BooleanVar(value=False)
        chk_frame = tk.Frame(dlg, bg=C["BG"])
        chk_frame.pack(pady=(0, 12))
        chk = tk.Checkbutton(
            chk_frame, text=T["welcome_dont"],
            variable=dont_var, font=("Segoe UI", 9),
            fg=C["TEXT_DIM"], bg=C["BG"],
            activebackground=C["BG"], activeforeground=C["TEXT"],
            selectcolor=C["CARD"], highlightthickness=0, bd=0,
        )
        chk.pack()

        btns = tk.Frame(dlg, bg=C["BG"])
        btns.pack(pady=(4, 18))

        def go_faq():
            if dont_var.get():
                self.cfg["hide_welcome"] = True
                save_config(self.cfg)
            dlg.destroy()
            self.show_faq()

        def do_close():
            if dont_var.get():
                self.cfg["hide_welcome"] = True
                save_config(self.cfg)
            dlg.destroy()

        btn_style = {
            "font": ("Segoe UI", 9),
            "bg": C["CARD"],
            "fg": C["TEXT"],
            "activebackground": C["NAV_ACTIVE"],
            "activeforeground": C["TEXT"],
            "relief": "flat",
            "bd": 0,
            "padx": 16,
            "pady": 7,
            "cursor": "hand2",
            "highlightthickness": 0,
            "takefocus": 0,
        }

        btn_faq = tk.Button(btns, text=T["welcome_faq"], **btn_style, command=go_faq)
        btn_faq.pack(side="left", padx=6)

        btn_close = tk.Button(btns, text=T["welcome_close"], **btn_style, command=do_close)
        btn_close.pack(side="left", padx=6)

        dlg.protocol("WM_DELETE_WINDOW", do_close)

    def show_faq(self):
        if self.faq_win and self.faq_win.winfo_exists():
            self.faq_win.lift()
            return
        C, T = self.C, self.T
        items = FAQ[self.lang]
        win = tk.Toplevel(self)
        self.faq_win = win
        win.title("FAQ")
        win.configure(bg=C["BG"])
        win.resizable(True, True)
        win.minsize(420, 480)
        win.transient(self)
        win.grab_set()
        self._set_toplevel_icon(win)
        fw, fh = 480, 580
        win.geometry(f"{fw}x{fh}")
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - fw) // 2
        y = self.winfo_y() + (self.winfo_height() - fh) // 2
        win.geometry(f"+{x}+{y}")

        def close():
            try:
                win.grab_release()
            except Exception:
                pass
            self.faq_win = None
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", close)

        tk.Label(win, text=T["faq_title"], font=("Segoe UI", 13, "bold"),
                 fg=C["TEXT"], bg=C["BG"]).pack(pady=(18, 12))

        box = tk.Frame(win, bg=C["BG"])
        box.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        canvas = tk.Canvas(box, bg=C["BG"], highlightthickness=0, bd=0)
        canvas.pack(side="left", fill="both", expand=True)

        sb = tk.Canvas(box, width=6, bg=C["BG"], highlightthickness=0, bd=0)
        sb.pack(side="right", fill="y", padx=(6, 0))

        content = tk.Frame(canvas, bg=C["BG"])
        cid = canvas.create_window((0, 0), window=content, anchor="nw")

        def _redraw_thumb(*_):
            sb.delete("all")
            try:
                first, last = canvas.yview()
            except Exception:
                return
            if last - first >= 0.999:
                return
            h = sb.winfo_height()
            if h <= 1:
                return
            thumb_h = max(24, int((last - first) * h))
            thumb_y = int(first * h)
            sb.create_rectangle(1, thumb_y, 5, thumb_y + thumb_h, fill=C["BORDER"], outline="")

        def _on_content_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            _redraw_thumb()

        def _on_canvas_configure(e):
            canvas.itemconfig(cid, width=e.width)
            _redraw_thumb()

        content.bind("<Configure>", _on_content_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        sb.bind("<Configure>", lambda e: _redraw_thumb())

        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
            _redraw_thumb()

        def _bind_wheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                _bind_wheel(child)

        canvas.bind("<MouseWheel>", _on_mousewheel)
        content.bind("<MouseWheel>", _on_mousewheel)
        win.bind("<MouseWheel>", _on_mousewheel)
        sb.bind("<MouseWheel>", _on_mousewheel)

        def _sb_click(e):
            h = sb.winfo_height()
            if h <= 0:
                return
            canvas.yview_moveto(max(0.0, min(1.0, e.y / h)))
            _redraw_thumb()

        sb.bind("<Button-1>", _sb_click)
        sb.bind("<B1-Motion>", _sb_click)

        for i, (q, a) in enumerate(items):
            card = tk.Frame(content, bg=C["CARD"], highlightbackground=C["BORDER"],
                            highlightthickness=1, highlightcolor=C["BORDER"])
            card.pack(fill="x", pady=(0 if i == 0 else 10, 0))
            tk.Label(card, text=q, font=("Segoe UI", 10, "bold"), fg=C["ACCENT"], bg=C["CARD"],
                     wraplength=400, justify="left", anchor="w").pack(fill="x", padx=14, pady=(12, 4))
            tk.Label(card, text=a, font=("Segoe UI", 9), fg=C["TEXT_DIM"], bg=C["CARD"],
                     wraplength=400, justify="left", anchor="w").pack(fill="x", padx=14, pady=(0, 12))

        _bind_wheel(content)
        tk.Frame(content, bg=C["BG"], height=12).pack()

        tk.Button(win, text=T["btn_close"], font=("Segoe UI", 9, "bold"), bg=C["ACCENT"], fg="white",
                  relief="flat", bd=0, padx=20, pady=7, cursor="hand2",
                  highlightthickness=0, takefocus=0, command=close).pack(pady=(0, 16))
