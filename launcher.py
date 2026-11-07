import json
import os
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog

APP_DIR = Path(os.getenv("APPDATA", Path.home())) / "BlackLauncher"
CONFIG = APP_DIR / "apps.json"
PASSWORD = "1234"
BG = "#080808"
FG = "#f4f4f4"


class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Black Launcher")
        self.configure(bg=BG)
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda event: None)
        self.apps = self.load_apps()

        if self.apps is None:
            self.show_setup()
        else:
            self.show_launcher()

    def load_apps(self):
        try:
            return json.loads(CONFIG.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_setup(self):
        self.clear()
        tk.Label(
            self,
            text="BLACK LAUNCHER",
            bg=BG,
            fg=FG,
            font=("Segoe UI", 28, "bold"),
        ).pack(pady=(70, 12))

        tk.Label(
            self,
            text="Elegí las aplicaciones que querés tener.\n"
                 "Al guardar, la selección queda bloqueada.",
            bg=BG,
            fg="#bdbdbd",
            font=("Segoe UI", 14),
        ).pack(pady=8)

        self.selection = []
        self.listbox = tk.Listbox(
            self,
            width=58,
            height=10,
            bg="#171717",
            fg=FG,
            font=("Segoe UI", 12),
        )
        self.listbox.pack(pady=18)

        buttons = tk.Frame(self, bg=BG)
        buttons.pack()

        tk.Button(
            buttons,
            text="Agregar aplicación",
            command=self.add_app,
            font=("Segoe UI", 12),
            padx=14,
            pady=9,
        ).pack(side="left", padx=6)

        tk.Button(
            buttons,
            text="Guardar y bloquear selección",
            command=self.save_setup,
            font=("Segoe UI", 12, "bold"),
            padx=14,
            pady=9,
        ).pack(side="left", padx=6)

    def add_app(self):
        path = filedialog.askopenfilename(
            title="Elegí una aplicación o acceso directo",
            filetypes=[
                ("Aplicaciones", "*.exe *.lnk *.bat *.cmd"),
                ("Todos los archivos", "*.*"),
            ],
        )

        if path and all(app["path"].lower() != path.lower()
                        for app in self.selection):
            name = Path(path).stem.replace("_", " ")
            self.selection.append({"name": name, "path": path})
            self.listbox.insert("end", f"▣  {name}")

    def save_setup(self):
        if not self.selection:
            messagebox.showinfo(
                "Sin aplicaciones",
                "Agregá al menos una aplicación para continuar.",
            )
            return

        APP_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG.write_text(
            json.dumps(self.selection, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.apps = self.selection
        self.show_launcher()

    def show_launcher(self):
        self.clear()

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=30, pady=18)

        tk.Button(
            top,
            text="⏻",
            command=self.request_exit,
            bg=BG,
            fg=FG,
            font=("Segoe UI", 19),
            relief="flat",
        ).pack(side="right")

        area = tk.Frame(self, bg=BG)
        area.pack(expand=True)

        columns = min(5, max(1, len(self.apps)))

        for i, app in enumerate(self.apps):
            tile = tk.Frame(area, bg=BG, padx=12, pady=12)
            tile.grid(row=i // columns, column=i % columns)

            tk.Button(
                tile,
                text="▣",
                command=lambda selected=app: self.launch(selected),
                bg="#191919",
                fg=FG,
                font=("Segoe UI", 42),
                width=3,
                height=1,
                relief="flat",
            ).pack()

            tk.Label(
                tile,
                text=app["name"],
                bg=BG,
                fg=FG,
                font=("Segoe UI", 12),
                wraplength=140,
            ).pack(pady=(8, 0))

    def launch(self, app):
        try:
            if os.name == "nt":
                os.startfile(app["path"])
            else:
                subprocess.Popen([app["path"]])
        except Exception as error:
            messagebox.showerror(
                "No se pudo abrir",
                f"No pude iniciar {app['name']}:\n{error}",
            )

    def request_exit(self):
        password = simpledialog.askstring(
            "Salir del launcher",
            "Ingresá la contraseña:",
            show="*",
            parent=self,
        )

        if password == PASSWORD:
            self.destroy()
        elif password is not None:
            messagebox.showerror(
                "Contraseña incorrecta",
                "La contraseña no es correcta.",
            )


if __name__ == "__main__":
    Launcher().mainloop()
