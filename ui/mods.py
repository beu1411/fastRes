"""
Mods page: game path search, blood checkbox, Play Valorant.
"""
import tkinter as tk
from tkinter import messagebox

from config import save_config
from valorant import (
    detect_valorant_path,
    get_paks_dir,
    LaunchWorker,
)


class ModsMixin:
    def _page_mods(self):
        C, T = self.C, self.T

        header = tk.Frame(self.main, bg=C["BG"])
        header.pack(fill="x", padx=28, pady=(22, 16))
        tk.Label(
            header, text=T["nav_mods"],
            font=("Segoe UI", 14, "bold"),
            fg=C["TEXT"], bg=C["BG"],
        ).pack(side="left")

        card = tk.Frame(
            self.main, bg=C["CARD"],
            highlightbackground=C["BORDER"],
            highlightthickness=1, highlightcolor=C["BORDER"],
        )
        card.pack(fill="x", padx=28, pady=(0, 14))

        tk.Label(
            card, text=T["mods_folder"],
            font=("Segoe UI", 9, "bold"),
            fg=C["TEXT_DIM"], bg=C["CARD"],
        ).pack(anchor="w", padx=18, pady=(16, 8))

        # Fixed-height row so entry and button match
        path_row = tk.Frame(card, bg=C["CARD"], height=36)
        path_row.pack(fill="x", padx=18, pady=(0, 6))
        path_row.pack_propagate(False)

        self.game_path_var = tk.StringVar(value=self.cfg.get("game_path", ""))

        # Wrapper gives text breathing room from the border
        entry_wrap = tk.Frame(
            path_row, bg=C["INPUT"],
            highlightthickness=1,
            highlightbackground=C["BORDER"],
            highlightcolor=C["ACCENT"],
        )
        entry_wrap.pack(side="left", fill="both", expand=True, padx=(0, 8))

        path_entry = tk.Entry(
            entry_wrap,
            textvariable=self.game_path_var,
            font=("Segoe UI", 10),
            bg=C["INPUT"], fg=C["TEXT"],
            insertbackground=C["TEXT"],
            relief="flat", bd=0,
            highlightthickness=0,
        )
        path_entry.pack(fill="both", expand=True, padx=10, pady=6)
        def _entry_focus_in(_e):
            entry_wrap.config(highlightbackground=C["ACCENT"], highlightcolor=C["ACCENT"])

        def _entry_focus_out(_e):
            entry_wrap.config(highlightbackground=C["BORDER"], highlightcolor=C["ACCENT"])
            self._update_path_status(show_toast=True)

        path_entry.bind("<FocusIn>", _entry_focus_in)
        path_entry.bind("<FocusOut>", _entry_focus_out)
        path_entry.bind("<Return>", lambda e: self._update_path_status(show_toast=True))

        search_btn = tk.Frame(path_row, bg=C["ACCENT"], cursor="hand2", width=118)
        search_btn.pack(side="right", fill="y")
        search_btn.pack_propagate(False)

        search_inner = tk.Frame(search_btn, bg=C["ACCENT"])
        search_inner.place(relx=0.5, rely=0.5, anchor="center")

        search_icon = self.icons.get("search")
        if search_icon:
            icon_lbl = tk.Label(search_inner, image=search_icon, bg=C["ACCENT"])
            icon_lbl.image = search_icon
            icon_lbl.pack(side="left", padx=(0, 5))
        else:
            icon_lbl = tk.Label(
                search_inner, text="🔍", font=("Segoe UI", 10),
                fg="white", bg=C["ACCENT"],
            )
            icon_lbl.pack(side="left", padx=(0, 5))

        search_txt = tk.Label(
            search_inner, text=T["mods_search"],
            font=("Segoe UI", 9, "bold"),
            fg="white", bg=C["ACCENT"],
        )
        search_txt.pack(side="left")

        def on_search_enter(e):
            search_btn.config(bg=C["ACCENT_H"])
            search_inner.config(bg=C["ACCENT_H"])
            for w in (icon_lbl, search_txt):
                w.config(bg=C["ACCENT_H"])

        def on_search_leave(e):
            search_btn.config(bg=C["ACCENT"])
            search_inner.config(bg=C["ACCENT"])
            for w in (icon_lbl, search_txt):
                w.config(bg=C["ACCENT"])

        for w in (search_btn, search_inner, icon_lbl, search_txt):
            w.bind("<Button-1>", lambda e: self._search_game_path())
            w.bind("<Enter>", on_search_enter)
            w.bind("<Leave>", on_search_leave)

        tk.Label(
            card, text=T["mods_path_hint"],
            font=("Segoe UI", 8),
            fg=C["TEXT_DIM"], bg=C["CARD"],
            wraplength=520, justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 4))

        self.path_status = tk.Label(
            card, text="",
            font=("Segoe UI", 9),
            fg=C["TEXT_DIM"], bg=C["CARD"],
        )
        self.path_status.pack(anchor="w", padx=18, pady=(0, 14))
        self._update_path_status()

        opt_card = tk.Frame(
            self.main, bg=C["CARD"],
            highlightbackground=C["BORDER"],
            highlightthickness=1, highlightcolor=C["BORDER"],
        )
        opt_card.pack(fill="x", padx=28, pady=(0, 14))

        chk_row = tk.Frame(opt_card, bg=C["CARD"], cursor="hand2")
        chk_row.pack(fill="x", padx=18, pady=14)

        self.blood_var = tk.BooleanVar(value=self.cfg.get("enable_blood", True))

        self._chk_box = tk.Canvas(
            chk_row, width=20, height=20,
            bg=C["CARD"], highlightthickness=0, bd=0,
        )
        self._chk_box.pack(side="left", padx=(0, 12))
        self._draw_checkbox()

        chk_label = tk.Label(
            chk_row, text=T["mods_blood"],
            font=("Segoe UI", 11),
            fg=C["TEXT"], bg=C["CARD"],
            anchor="w", cursor="hand2",
        )
        chk_label.pack(side="left", fill="x", expand=True)

        def toggle_blood(e=None):
            self.blood_var.set(not self.blood_var.get())
            self.cfg["enable_blood"] = self.blood_var.get()
            save_config(self.cfg)
            self._draw_checkbox()

        for w in (chk_row, self._chk_box, chk_label):
            w.bind("<Button-1>", toggle_blood)

        # Play button — slightly smaller
        play_frame = tk.Frame(self.main, bg=C["BG"])
        play_frame.pack(fill="x", padx=28, pady=(4, 12))

        self.play_btn = tk.Frame(play_frame, bg=C["ACCENT"], cursor="hand2", height=44)
        self.play_btn.pack(fill="x")
        self.play_btn.pack_propagate(False)

        self.play_inner = tk.Frame(self.play_btn, bg=C["ACCENT"])
        self.play_inner.place(relx=0.5, rely=0.5, anchor="center")

        self.play_icon_lbl = tk.Label(
            self.play_inner, text="▶",
            font=("Segoe UI", 12, "bold"),
            fg="white", bg=C["ACCENT"],
        )
        self.play_icon_lbl.pack(side="left", padx=(0, 8))

        self.play_txt_lbl = tk.Label(
            self.play_inner, text=T["mods_play"],
            font=("Segoe UI", 12, "bold"),
            fg="white", bg=C["ACCENT"],
        )
        self.play_txt_lbl.pack(side="left")

        def on_play_enter(e):
            if getattr(self, "_launching", False):
                return
            for w in (self.play_btn, self.play_inner, self.play_icon_lbl, self.play_txt_lbl):
                w.config(bg=C["ACCENT_H"])

        def on_play_leave(e):
            if getattr(self, "_launching", False):
                return
            for w in (self.play_btn, self.play_inner, self.play_icon_lbl, self.play_txt_lbl):
                w.config(bg=C["ACCENT"])

        for w in (self.play_btn, self.play_inner, self.play_icon_lbl, self.play_txt_lbl):
            w.bind("<Button-1>", lambda e: self._play_valorant())
            w.bind("<Enter>", on_play_enter)
            w.bind("<Leave>", on_play_leave)

        # Status bar (like Resolutions)
        bar = tk.Frame(self.main, bg=C["CARD"], height=36)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        self.mods_status = tk.StringVar(value=T["status_ready"])
        self.mods_status_lbl = tk.Label(
            bar, textvariable=self.mods_status,
            font=("Segoe UI", 9),
            fg=C["TEXT_DIM"], bg=C["CARD"], anchor="w",
        )
        self.mods_status_lbl.pack(side="left", padx=16)

        self._launching = False

    def _draw_checkbox(self):
        """Thin flat checkmark colored like card background."""
        C = self.C
        box = self._chk_box
        box.delete("all")
        checked = self.blood_var.get()
        box.create_rectangle(
            1, 1, 19, 19,
            outline=C["ACCENT"] if checked else C["BORDER"],
            width=1,
            fill=C["ACCENT"] if checked else C["INPUT"],
        )
        if checked:
            # flatter / thinner V, color matches card bg
            box.create_line(
                4, 10, 8, 14,
                fill=C["CARD"], width=1.5, capstyle="round", joinstyle="round",
            )
            box.create_line(
                8, 14, 15, 5,
                fill=C["CARD"], width=1.5, capstyle="round", joinstyle="round",
            )

    def _set_mods_status(self, msg, success=None):
        C = self.C
        self.mods_status.set(msg)
        if success is True:
            self.mods_status_lbl.config(fg=C["SUCCESS"])
        elif success is False:
            self.mods_status_lbl.config(fg=C["ERROR"])
        else:
            self.mods_status_lbl.config(fg=C["TEXT_DIM"])

    def _update_path_status(self, show_toast=False):
        C, T = self.C, self.T
        path = self.game_path_var.get().strip()
        if not path:
            self.path_status.config(text=T["mods_path_empty"], fg=C["TEXT_DIM"])
            return
        paks = get_paks_dir(path)
        if paks:
            self.path_status.config(text=T["mods_path_ok"], fg=C["SUCCESS"])
            self.cfg["game_path"] = path
            save_config(self.cfg)
        else:
            self.path_status.config(text=T["mods_path_bad"], fg=C["ERROR"])
            if show_toast:
                self.show_toast(T["mods_path_bad"], success=False)

    def _search_game_path(self):
        T = self.T
        self._set_mods_status(T["mods_searching"])
        path = detect_valorant_path()
        if path:
            self.game_path_var.set(path)
            self.cfg["game_path"] = path
            save_config(self.cfg)
            self._update_path_status()
            self._set_mods_status(f"{T['mods_found']}: {path}", success=True)
            self.show_toast(T["mods_found"], success=True)
        else:
            self.path_status.config(text=T["mods_not_found"], fg=self.C["ERROR"])
            self._set_mods_status(T["mods_not_found"], success=False)
            self.show_toast(T["mods_not_found"], success=False)

    def _set_play_state(self, launching):
        C = self.C
        self._launching = launching
        # Only darken (not gray) — uniform color on whole button
        busy = "#1e3a5f" if getattr(self, "theme_name", "dark") == "dark" else "#93c5fd"
        color = busy if launching else C["ACCENT"]
        label = self.T["mods_launching"] if launching else self.T["mods_play"]
        try:
            self.play_txt_lbl.config(text=label, bg=color, fg="white")
            self.play_icon_lbl.config(bg=color, fg="white")
            self.play_btn.config(bg=color)
            if hasattr(self, "play_inner"):
                self.play_inner.config(bg=color)
        except Exception:
            pass

    def _play_valorant(self):
        if getattr(self, "_launching", False):
            return

        path = self.game_path_var.get().strip()
        if not path:
            path = detect_valorant_path()
            if path:
                self.game_path_var.set(path)
                self.cfg["game_path"] = path
                save_config(self.cfg)
                self._update_path_status()

        paks = get_paks_dir(path) if path else None
        enable_blood = self.blood_var.get()

        if enable_blood and not paks:
            self.show_toast(self.T["mods_need_path"].replace("\n", " "), success=False)
            self._set_mods_status(self.T["mods_need_path"].replace("\n", " "), success=False)
            messagebox.showerror(
                self.T["error_title"],
                self.T["mods_need_path"],
            )
            return

        self._set_play_state(True)
        self._set_mods_status(self.T["mods_start"])

        def on_log(msg):
            self.after(0, self._set_mods_status, msg)

        def on_ok():
            self.after(0, self._on_launch_ok)

        def on_err(err):
            self.after(0, self._on_launch_err, err)

        self._launch_worker = LaunchWorker(
            paks_dir=paks,
            enable_blood=enable_blood,
            on_log=on_log,
            on_ok=on_ok,
            on_err=on_err,
            strings=self.T,
        )
        self._launch_worker.start()

    def _on_launch_ok(self):
        self._set_play_state(False)
        self._set_mods_status(self.T["mods_done"], success=True)
        self.show_toast(self.T["mods_done"], success=True)

    def _on_launch_err(self, err):
        self._set_play_state(False)
        self._set_mods_status(str(err), success=False)
        self.show_toast(err, success=False)
