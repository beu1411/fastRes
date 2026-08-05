import tkinter as tk

from constants import CURRENT_VERSION


class SidebarMixin:
    def _build_sidebar(self):
        C, T = self.C, self.T

        self.side = tk.Frame(self, bg=C["SIDEBAR"], width=self.sidebar_width_expanded)
        self.side.pack(side="left", fill="y")
        self.side.pack_propagate(False)

        self.top = tk.Frame(self.side, bg=C["SIDEBAR"])
        self.top.pack(fill="x", pady=(12, 0))

        self.toggle_btn = tk.Label(
            self.top, text="«", font=("Segoe UI", 18, "bold"),
            fg=C["ACCENT"], bg=C["SIDEBAR"], cursor="hand2",
            padx=8, pady=2,
        )
        self.toggle_btn.pack(side="left", padx=(8, 0), pady=4)
        self.toggle_btn.bind("<Button-1>", lambda e: self.toggle_sidebar())
        self.toggle_btn.bind("<Enter>", lambda e: self.toggle_btn.config(bg=C["NAV_ACTIVE"], fg=C["ACCENT"]))
        self.toggle_btn.bind("<Leave>", lambda e: self.toggle_btn.config(bg=C["SIDEBAR"], fg=C["ACCENT"]))

        self.logo_frame = tk.Frame(self.top, bg=C["SIDEBAR"])
        self.logo_frame.pack(side="left", fill="x", expand=True)

        self.logo_label = tk.Label(
            self.logo_frame, text="⚡  " + T["app_title"],
            font=("Segoe UI", 15, "bold"), fg=C["ACCENT"], bg=C["SIDEBAR"],
        )
        self.logo_label.pack(anchor="w", padx=(6, 0))

        self.sub_label = tk.Label(
            self.side, text=T["app_sub"], font=("Segoe UI", 8),
            fg=C["TEXT_DIM"], bg=C["SIDEBAR"],
        )
        self.sub_label.pack(anchor="w", padx=20, pady=(1, 2))

        self.version_lbl = tk.Label(
            self.side, text=f"v{CURRENT_VERSION}", font=("Segoe UI", 8),
            fg=C["TEXT_DIM"], bg=C["SIDEBAR"],
        )
        self.version_lbl.pack(anchor="w", padx=20, pady=(0, 2))

        self.handle_lbl = tk.Label(
            self.side, text="@beu1411", font=("Segoe UI", 8),
            fg=C["TEXT_DIM"], bg=C["SIDEBAR"],
        )
        self.handle_lbl.pack(anchor="w", padx=20, pady=(0, 16))

        self.nav_container = tk.Frame(self.side, bg=C["SIDEBAR"])
        self.nav_container.pack(fill="both", expand=True)

        self._nav_item(self.nav_container, "mods", T["nav_mods"], "mods")
        self._nav_item(self.nav_container, "res", T["nav_res"], "resolutions")
        self._nav_item(self.nav_container, "setting", T["nav_settings"], "settings")
        self._nav_item(self.nav_container, "faq", T["nav_faq"], "faq", cmd=self.show_faq)
        self._nav_item(self.nav_container, "info", T["nav_info"], "info")

    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed
        if self.sidebar_collapsed:
            self.side.config(width=self.sidebar_width_collapsed)
            self.toggle_btn.config(text="»")
            self._set_labels_visible(False)
        else:
            self.side.config(width=self.sidebar_width_expanded)
            self.toggle_btn.config(text="«")
            self._set_labels_visible(True)

    def _set_labels_visible(self, visible):
        if visible:
            self.toggle_btn.pack_forget()
            self.logo_frame.pack_forget()
            self.toggle_btn.pack(side="left", padx=(10, 0), pady=4)
            self.logo_frame.pack(side="left", fill="x", expand=True)
            self.logo_label.config(text="⚡  " + self.T["app_title"])
            self.sub_label.pack(anchor="w", padx=20, pady=(1, 2))
            self.version_lbl.pack(anchor="w", padx=20, pady=(0, 2))
            self.handle_lbl.pack(anchor="w", padx=20, pady=(0, 16))
            for page, (frame, icon, text) in self.nav_labels.items():
                text.pack(side="left", fill="x", expand=True, pady=9)
                icon.pack_configure(side="left", expand=False, padx=(12, 8))
        else:
            self.logo_frame.pack_forget()
            self.sub_label.pack_forget()
            self.version_lbl.pack_forget()
            self.handle_lbl.pack_forget()
            self.toggle_btn.pack_forget()
            self.toggle_btn.pack(pady=(10, 6), padx=14)
            for page, (frame, icon, text) in self.nav_labels.items():
                text.pack_forget()
                icon.pack_configure(side="left", expand=True, padx=0)

    def _apply_collapsed_state(self, instant=False):
        if self.sidebar_collapsed:
            self.side.config(width=self.sidebar_width_collapsed)
            self.toggle_btn.config(text="»")
            self._set_labels_visible(False)
        else:
            self.side.config(width=self.sidebar_width_expanded)
            self.toggle_btn.config(text="«")
            self._set_labels_visible(True)

    def _nav_item(self, parent, icon_key, text, page, cmd=None):
        C = self.C
        active = self.current_page == page
        fg = C["ACCENT"] if active else C["TEXT_DIM"]
        bg = C["SIDEBAR"]

        frame = tk.Frame(parent, bg=bg, cursor="hand2")
        frame.pack(fill="x", padx=6, pady=2)

        icon = self.icons.get(icon_key)
        if icon:
            lbl_icon = tk.Label(frame, image=icon, bg=bg)
            lbl_icon.image = icon
            lbl_icon.pack(side="left", padx=(12, 8), pady=9)
        else:
            lbl_icon = tk.Label(frame, text="•", fg=fg, bg=bg, font=("Segoe UI", 12))
            lbl_icon.pack(side="left", padx=(14, 8), pady=9)

        lbl_text = tk.Label(
            frame, text=text,
            font=("Segoe UI", 10, "bold" if active else "normal"),
            fg=fg, bg=bg, anchor="w",
        )
        lbl_text.pack(side="left", fill="x", expand=True, pady=9)

        self.nav_labels[page] = (frame, lbl_icon, lbl_text)

        def on_click(e):
            if page == self.current_page and not cmd:
                return
            self.current_page = page
            self._update_nav_highlight()
            if cmd:
                cmd()
            else:
                self._show_page(page)

        for w in (frame, lbl_icon, lbl_text):
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", lambda e, f=frame, i=lbl_icon, t=lbl_text: self._hover_nav(f, i, t, True))
            w.bind("<Leave>", lambda e, f=frame, i=lbl_icon, t=lbl_text: self._hover_nav(f, i, t, False))

    def _hover_nav(self, frame, icon, text, enter):
        C = self.C
        if enter:
            frame.config(bg=C["NAV_ACTIVE"])
            icon.config(bg=C["NAV_ACTIVE"])
            if not self.sidebar_collapsed:
                text.config(fg=C["ACCENT"], bg=C["NAV_ACTIVE"])
        else:
            frame.config(bg=C["SIDEBAR"])
            icon.config(bg=C["SIDEBAR"])
            if not self.sidebar_collapsed:
                page = None
                for p, (f, i, t) in self.nav_labels.items():
                    if f is frame:
                        page = p
                        break
                active = page == self.current_page
                text.config(
                    fg=C["ACCENT"] if active else C["TEXT_DIM"],
                    bg=C["SIDEBAR"],
                )

    def _update_nav_highlight(self):
        C = self.C
        for page, (frame, icon, text) in self.nav_labels.items():
            active = self.current_page == page
            frame.config(bg=C["SIDEBAR"])
            icon.config(bg=C["SIDEBAR"])
            text.config(
                fg=C["ACCENT"] if active else C["TEXT_DIM"],
                bg=C["SIDEBAR"],
                font=("Segoe UI", 10, "bold" if active else "normal"),
            )
