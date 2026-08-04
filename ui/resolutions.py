import tkinter as tk
from tkinter import messagebox

from config import save_customs
from constants import PRESETS
from resolution import set_resolution


class ResolutionsMixin:
    def _page_resolutions(self):
        C, T = self.C, self.T
        header = tk.Frame(self.main, bg=C["BG"])
        header.pack(fill="x", padx=24, pady=(20, 12))
        tk.Label(header, text=T["header_res"], font=("Segoe UI", 14, "bold"),
                 fg=C["TEXT"], bg=C["BG"]).pack(side="left")
        tk.Button(header, text=T["btn_create"], font=("Segoe UI", 9, "bold"),
                  bg=C["ACCENT"], fg="white", activebackground=C["ACCENT_H"],
                  relief="flat", bd=0, padx=14, pady=6, cursor="hand2",
                  highlightthickness=0, takefocus=0,
                  command=self.create_dialog).pack(side="right")

        box = tk.Frame(self.main, bg=C["BG"])
        box.pack(fill="both", expand=True, padx=24, pady=(0, 10))

        self.canvas = tk.Canvas(box, bg=C["BG"], highlightthickness=0, bd=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.sb = tk.Canvas(box, width=6, bg=C["BG"], highlightthickness=0, bd=0)
        self.sb.pack(side="right", fill="y", padx=(6, 0))

        self.list_frame = tk.Frame(self.canvas, bg=C["BG"])
        self.win_id = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        def _redraw_main_thumb(*_):
            self.sb.delete("all")
            try:
                first, last = self.canvas.yview()
            except Exception:
                return
            if last - first >= 0.999:
                return
            h = self.sb.winfo_height()
            if h <= 1:
                return
            thumb_h = max(24, int((last - first) * h))
            thumb_y = int(first * h)
            self.sb.create_rectangle(1, thumb_y, 5, thumb_y + thumb_h,
                                     fill=C["BORDER"], outline="")

        def _on_list_configure(e):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            _redraw_main_thumb()

        def _on_canvas_configure(e):
            self.canvas.itemconfig(self.win_id, width=e.width)
            _redraw_main_thumb()

        self.list_frame.bind("<Configure>", _on_list_configure)
        self.canvas.bind("<Configure>", _on_canvas_configure)
        self.sb.bind("<Configure>", lambda e: _redraw_main_thumb())

        def _sb_click(e):
            h = self.sb.winfo_height()
            if h <= 0:
                return
            self.canvas.yview_moveto(max(0.0, min(1.0, e.y / h)))
            _redraw_main_thumb()

        self.sb.bind("<Button-1>", _sb_click)
        self.sb.bind("<B1-Motion>", _sb_click)
        self._redraw_main_thumb = _redraw_main_thumb

        bar = tk.Frame(self.main, bg=C["CARD"], height=36)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        self.status = tk.StringVar(value=T["status_ready"])
        self.status_lbl = tk.Label(bar, textvariable=self.status, font=("Segoe UI", 9),
                                   fg=C["TEXT_DIM"], bg=C["CARD"], anchor="w")
        self.status_lbl.pack(side="left", padx=16)
        self.refresh()

    def refresh(self):
        C, T = self.C, self.T
        if hasattr(self, "win_id"):
            try:
                self.canvas.itemconfigure(self.win_id, state="hidden")
            except Exception:
                pass

        for w in self.list_frame.winfo_children():
            w.destroy()

        tk.Label(self.list_frame, text=T["section_default"], font=("Segoe UI", 9, "bold"),
                 fg=C["TEXT_DIM"], bg=C["BG"], anchor="w").pack(fill="x", pady=(4, 8))
        for label, w, h in PRESETS:
            self._row(label, w, h, False)

        tk.Label(self.list_frame, text=T["section_custom"], font=("Segoe UI", 9, "bold"),
                 fg=C["TEXT_DIM"], bg=C["BG"], anchor="w").pack(fill="x", pady=(18, 8))

        if self.customs:
            for w, h in self.customs:
                self._row(f"{w} × {h}", w, h, True)
        else:
            empty = tk.Frame(self.list_frame, bg=C["CARD"], highlightbackground=C["BORDER"],
                             highlightthickness=1, highlightcolor=C["BORDER"])
            empty.pack(fill="x", pady=4)
            tk.Label(empty, text=T["no_custom"], font=("Segoe UI", 10),
                     fg=C["TEXT_DIM"], bg=C["CARD"]).pack(pady=(16, 4))
            tk.Label(empty, text=T["no_custom_desc"], font=("Segoe UI", 9),
                     fg=C["TEXT_DIM"], bg=C["CARD"]).pack(pady=(0, 16))

        tk.Frame(self.list_frame, bg=C["BG"], height=20).pack()

        self.list_frame.update_idletasks()
        if hasattr(self, "win_id"):
            try:
                self.canvas.itemconfigure(self.win_id, state="normal")
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                if hasattr(self, "_redraw_main_thumb"):
                    self._redraw_main_thumb()
            except Exception:
                pass

    def _row(self, label, w, h, is_custom):
        C, T = self.C, self.T
        row = tk.Frame(self.list_frame, bg=C["CARD"], highlightbackground=C["BORDER"],
                       highlightthickness=1, highlightcolor=C["BORDER"])
        row.pack(fill="x", pady=5)
        row.columnconfigure(0, weight=1)

        tk.Label(row, text=label, font=("Segoe UI", 11), fg=C["TEXT"], bg=C["CARD"],
                 anchor="w").grid(row=0, column=0, sticky="w", padx=16, pady=13)

        btns = tk.Frame(row, bg=C["CARD"])
        btns.grid(row=0, column=1, sticky="e", padx=12, pady=8)

        apply_btn = tk.Label(
            btns, text=T["btn_apply"], font=("Segoe UI", 9),
            bg=C["ACCENT"], fg="white", padx=14, pady=5, cursor="hand2",
        )
        apply_btn.pack(side="left", padx=(0, 6))
        apply_btn.bind("<Button-1>", lambda e, ww=w, hh=h: self.apply(ww, hh))
        apply_btn.bind("<Enter>", lambda e: apply_btn.config(bg=C["ACCENT_H"]))
        apply_btn.bind("<Leave>", lambda e: apply_btn.config(bg=C["ACCENT"]))

        if is_custom:
            del_btn = tk.Label(
                btns, text=T["btn_delete"], font=("Segoe UI", 9),
                bg=C["BORDER"], fg=C["TEXT_DIM"], padx=12, pady=5, cursor="hand2",
            )
            del_btn.pack(side="left")
            del_btn.bind("<Button-1>", lambda e, ww=w, hh=h: self.delete(ww, hh))
            del_btn.bind("<Enter>", lambda e: del_btn.config(bg=C["NAV_ACTIVE"], fg=C["TEXT"]))
            del_btn.bind("<Leave>", lambda e: del_btn.config(bg=C["BORDER"], fg=C["TEXT_DIM"]))

    def apply(self, w, h):
        ok, code = set_resolution(w, h)
        T = self.T
        if ok:
            msg = T["msg_applied"].format(w=w, h=h)
            self.status_lbl.config(fg=self.C["SUCCESS"])
            self.status.set(msg)
            self.show_toast(msg, True)
        else:
            msg = T["msg_error"]
            self.status_lbl.config(fg=self.C["ERROR"])
            self.status.set(msg)
            self.show_toast(msg, False)

    def delete(self, w, h):
        T = self.T
        if not messagebox.askyesno("Delete", T["delete_confirm"].format(w=w, h=h)):
            return
        self.customs = [(a, b) for a, b in self.customs if (a, b) != (w, h)]
        save_customs(self.customs)
        self.refresh()
        msg = T["msg_deleted"].format(w=w, h=h)
        self.status_lbl.config(fg=self.C["TEXT_DIM"])
        self.status.set(msg)
        self.show_toast(msg, True)

    def create_dialog(self):
        C, T = self.C, self.T
        dlg = tk.Toplevel(self)
        dlg.title(T["create_title"])
        dlg.configure(bg=C["BG"])
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()
        self._set_toplevel_icon(dlg)
        dw, dh = 360, 280
        dlg.geometry(f"{dw}x{dh}")
        dlg.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dw) // 2
        y = self.winfo_y() + (self.winfo_height() - dh) // 2
        dlg.geometry(f"+{x}+{y}")

        tk.Label(dlg, text=T["create_title"], font=("Segoe UI", 12, "bold"),
                 fg=C["TEXT"], bg=C["BG"]).pack(pady=(18, 4))
        tk.Label(dlg, text=T["create_hint"], font=("Segoe UI", 8),
                 fg=C["TEXT_DIM"], bg=C["BG"]).pack(pady=(0, 14))

        form = tk.Frame(dlg, bg=C["BG"])
        form.pack(padx=28, fill="x")
        tk.Label(form, text=T["width"], font=("Segoe UI", 9), fg=C["TEXT_DIM"], bg=C["BG"]).grid(row=0, column=0, sticky="w")
        we = tk.Entry(form, font=("Segoe UI", 12), bg=C["INPUT"], fg=C["TEXT"], insertbackground=C["TEXT"],
                      relief="flat", highlightthickness=1, highlightbackground=C["BORDER"], highlightcolor=C["ACCENT"])
        we.grid(row=1, column=0, sticky="ew", pady=(4, 14), ipady=7, padx=(0, 10))
        tk.Label(form, text=T["height"], font=("Segoe UI", 9), fg=C["TEXT_DIM"], bg=C["BG"]).grid(row=0, column=1, sticky="w")
        he = tk.Entry(form, font=("Segoe UI", 12), bg=C["INPUT"], fg=C["TEXT"], insertbackground=C["TEXT"],
                      relief="flat", highlightthickness=1, highlightbackground=C["BORDER"], highlightcolor=C["ACCENT"])
        he.grid(row=1, column=1, sticky="ew", pady=(4, 14), ipady=7)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        def save():
            try:
                w = int(we.get().strip())
                h = int(he.get().strip())
            except Exception:
                messagebox.showerror("Error", T["err_number"], parent=dlg)
                return
            if w < 640 or h < 640:
                messagebox.showerror("Error", T["err_small"], parent=dlg)
                return
            if w > 7680 or h > 7680:
                messagebox.showerror("Error", T["err_large"], parent=dlg)
                return
            if max(w, h) / min(w, h) > 3.5:
                messagebox.showerror("Error", T["err_ratio"], parent=dlg)
                return
            if (w, h) in [(a, b) for _, a, b in PRESETS] or (w, h) in self.customs:
                messagebox.showinfo("Exists", T["err_exists"], parent=dlg)
                return
            self.customs.append((w, h))
            save_customs(self.customs)
            self.refresh()
            msg = T["msg_added"].format(w=w, h=h)
            self.status_lbl.config(fg=C["SUCCESS"])
            self.status.set(msg)
            self.show_toast(msg, True)
            dlg.destroy()

        btns = tk.Frame(dlg, bg=C["BG"])
        btns.pack(pady=10)
        tk.Button(btns, text=T["btn_cancel"], font=("Segoe UI", 9), bg=C["CARD"], fg=C["TEXT"],
                  relief="flat", bd=0, padx=18, pady=7, cursor="hand2",
                  highlightthickness=0, takefocus=0, command=dlg.destroy).pack(side="left", padx=6)
        tk.Button(btns, text=T["btn_save"], font=("Segoe UI", 9, "bold"), bg=C["ACCENT"], fg="white",
                  activebackground=C["ACCENT_H"], relief="flat", bd=0, padx=22, pady=7, cursor="hand2",
                  highlightthickness=0, takefocus=0, command=save).pack(side="left", padx=6)
        we.focus_set()
