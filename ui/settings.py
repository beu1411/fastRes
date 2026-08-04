import tkinter as tk


class SettingsMixin:
    def _page_settings(self):
        C, T = self.C, self.T
        tk.Label(self.main, text=T["settings_title"], font=("Segoe UI", 14, "bold"),
                 fg=C["TEXT"], bg=C["BG"]).pack(anchor="w", padx=28, pady=(22, 18))

        self._setting_dropdown_row(
            icon_key="translate",
            title=T["lang_label"],
            value=T["lang_vi"] if self.lang == "vi" else T["lang_en"],
            command=self._popup_language,
        )

        theme_text = {
            "dark": T["theme_dark"],
            "light": T["theme_light"],
            "system": T["theme_system"],
        }.get(self.cfg.get("theme", "dark"), T["theme_dark"])

        self._setting_dropdown_row(
            icon_key="theme",
            title=T["theme_label"],
            value=theme_text,
            command=self._popup_theme,
        )

    def _setting_dropdown_row(self, icon_key, title, value, command):
        C = self.C
        btn_bg = C["CARD"]
        btn_hover = C["NAV_ACTIVE"]

        outer = tk.Frame(self.main, bg=C["BG"])
        outer.pack(fill="x", padx=28, pady=4)

        left = tk.Frame(outer, bg=C["BG"])
        left.pack(side="left", anchor="center")

        icon = self.icons.get(icon_key)
        if icon:
            lbl = tk.Label(left, image=icon, bg=C["BG"])
            lbl.image = icon
            lbl.pack(side="left", padx=(0, 10))

        tk.Label(left, text=title, font=("Segoe UI", 11), fg=C["TEXT"], bg=C["BG"]).pack(side="left")

        select = tk.Frame(outer, bg=btn_bg, cursor="hand2")
        select.pack(side="right")

        border = tk.Frame(select, bg=C["BORDER"])
        border.pack()
        inner = tk.Frame(border, bg=btn_bg)
        inner.pack(padx=1, pady=1)

        content = tk.Frame(inner, bg=btn_bg)
        content.pack(padx=11, pady=6)

        val_lbl = tk.Label(content, text=value, font=("Segoe UI", 10), fg=C["TEXT"], bg=btn_bg)
        val_lbl.pack(side="left")

        arrow = tk.Label(content, text="  ▾", font=("Segoe UI", 8), fg=C["TEXT_DIM"], bg=btn_bg)
        arrow.pack(side="left")

        def on_click(e):
            command(select)

        def on_enter(e):
            border.config(bg=C["ACCENT"])
            for w in (select, inner, content, val_lbl, arrow):
                w.config(bg=btn_hover)

        def on_leave(e):
            border.config(bg=C["BORDER"])
            for w in (select, inner, content, val_lbl, arrow):
                w.config(bg=btn_bg)

        for w in (select, border, inner, content, val_lbl, arrow):
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

    def _popup_language(self, widget):
        menu = tk.Menu(
            self, tearoff=0,
            bg=self.C["CARD"], fg=self.C["TEXT"],
            activebackground=self.C["ACCENT"], activeforeground="white",
            bd=0, font=("Segoe UI", 10), relief="flat",
        )
        menu.add_command(label=self.T["lang_en"], command=lambda: self.change_lang("en"))
        menu.add_command(label=self.T["lang_vi"], command=lambda: self.change_lang("vi"))
        try:
            x = widget.winfo_rootx()
            y = widget.winfo_rooty() + widget.winfo_height() + 2
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _popup_theme(self, widget):
        menu = tk.Menu(
            self, tearoff=0,
            bg=self.C["CARD"], fg=self.C["TEXT"],
            activebackground=self.C["ACCENT"], activeforeground="white",
            bd=0, font=("Segoe UI", 10), relief="flat",
        )
        menu.add_command(label=self.T["theme_light"], command=lambda: self.change_theme("light"))
        menu.add_command(label=self.T["theme_dark"], command=lambda: self.change_theme("dark"))
        menu.add_command(label=self.T["theme_system"], command=lambda: self.change_theme("system"))
        try:
            x = widget.winfo_rootx()
            y = widget.winfo_rooty() + widget.winfo_height() + 2
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()
