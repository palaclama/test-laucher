import json
from pathlib import Path

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

PASSWORD = "1234"
CONFIG = Path(__file__).parent / "launcher_apps.json"


def installed_apps():
    """Return launchable Android apps as (label, package name)."""
    from jnius import autoclass

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Intent = autoclass("android.content.Intent")
    activity = PythonActivity.mActivity
    pm = activity.getPackageManager()
    packages = pm.getInstalledApplications(0)
    found = []
    for i in range(packages.size()):
        info = packages.get(i)
        package = str(info.packageName)
        if package == str(activity.getPackageName()):
            continue
        intent = pm.getLaunchIntentForPackage(package)
        if intent is not None:
            label = str(pm.getApplicationLabel(info))
            found.append((label, package))
    return sorted(found, key=lambda row: row[0].lower())


class BlackLauncher(App):
    def build(self):
        Window.clearcolor = (0.025, 0.025, 0.025, 1)
        self.selected = self.load_selection()
        self.all_apps = []
        self.root_box = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        self.show_home()
        return self.root_box

    def load_selection(self):
        try:
            data = json.loads(CONFIG.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else None
        except (OSError, ValueError):
            return None

    def save_selection(self):
        CONFIG.write_text(json.dumps(self.selected, ensure_ascii=False), encoding="utf-8")

    def reset_view(self):
        self.root_box.clear_widgets()

    def show_home(self):
        self.reset_view()
        header = BoxLayout(size_hint_y=None, height=dp(52))
        header.add_widget(Label(text="", size_hint_x=1))
        exit_button = Button(text="⏻", font_size=dp(24), size_hint=(None, None),
                             size=(dp(54), dp(48)), background_color=(0.12, 0.12, 0.12, 1))
        exit_button.bind(on_release=self.ask_password)
        header.add_widget(exit_button)
        self.root_box.add_widget(header)

        if self.selected is None:
            self.root_box.add_widget(Label(text="Elegí tus aplicaciones", font_size=dp(24)))
            self.root_box.add_widget(Label(text="La selección se bloquea después de guardar.",
                                           font_size=dp(15), color=(0.72, 0.72, 0.72, 1)))
            btn = Button(text="Cargar aplicaciones", size_hint=(1, None), height=dp(56),
                         background_color=(0.18, 0.18, 0.18, 1))
            btn.bind(on_release=self.load_apps)
            self.root_box.add_widget(btn)
            return

        self.root_box.add_widget(Label(text="", size_hint_y=0.2))
        scroll = ScrollView()
        grid = GridLayout(cols=3, spacing=dp(14), padding=dp(6), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for app in self.selected:
            tile = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(122), spacing=dp(4))
            button = Button(text="▣", font_size=dp(43), background_color=(0.10, 0.10, 0.10, 1))
            button.bind(on_release=lambda _b, package=app["package"]: self.launch(package))
            tile.add_widget(button)
            tile.add_widget(Label(text=app["label"], font_size=dp(12), halign="center",
                                  valign="middle", text_size=(dp(100), None)))
            grid.add_widget(tile)
        scroll.add_widget(grid)
        self.root_box.add_widget(scroll)
        self.root_box.add_widget(Label(text="", size_hint_y=0.2))

    def load_apps(self, *_):
        try:
            self.all_apps = installed_apps()
        except Exception as error:
            self.message("No se pudieron cargar las apps", str(error))
            return
        self.show_picker()

    def show_picker(self):
        self.reset_view()
        self.root_box.add_widget(Label(text="Seleccioná las aplicaciones", size_hint_y=None,
                                       height=dp(48), font_size=dp(21)))
        scroll = ScrollView()
        listing = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        listing.bind(minimum_height=listing.setter("height"))
        self.checks = {}
        for label, package in self.all_apps:
            row = Button(text=f"□   {label}", size_hint_y=None, height=dp(48), halign="left",
                         background_color=(0.10, 0.10, 0.10, 1))
            self.checks[package] = False
            row.bind(on_release=lambda button, p=package: self.toggle(button, p))
            listing.add_widget(row)
        scroll.add_widget(listing)
        self.root_box.add_widget(scroll)
        save = Button(text="Guardar selección", size_hint_y=None, height=dp(54),
                      background_color=(0.22, 0.22, 0.22, 1))
        save.bind(on_release=self.finish_selection)
        self.root_box.add_widget(save)

    def toggle(self, button, package):
        self.checks[package] = not self.checks[package]
        button.text = ("☑   " if self.checks[package] else "□   ") + button.text[3:]

    def finish_selection(self, *_):
        self.selected = [{"label": label, "package": package}
                         for label, package in self.all_apps if self.checks.get(package)]
        if not self.selected:
            self.selected = None
            self.message("Elegí al menos una app", "Marcá una o más aplicaciones antes de guardar.")
            return
        self.save_selection()
        self.show_home()

    def launch(self, package):
        from jnius import autoclass
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        intent = activity.getPackageManager().getLaunchIntentForPackage(package)
        if intent is not None:
            activity.startActivity(intent)

    def ask_password(self, *_):
        layout = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        from kivy.uix.textinput import TextInput
        field = TextInput(password=True, multiline=False, hint_text="Contraseña", size_hint_y=None,
                          height=dp(48))
        layout.add_widget(Label(text="Ingresá la contraseña para salir"))
        layout.add_widget(field)
        popup = Popup(title="Salir del launcher", content=layout, size_hint=(0.85, None), height=dp(210))
        confirm = Button(text="Aceptar", size_hint_y=None, height=dp(46))
        layout.add_widget(confirm)
        def check(_button):
            if field.text == PASSWORD:
                popup.dismiss()
                App.get_running_app().stop()
            else:
                field.text = ""
                field.hint_text = "Contraseña incorrecta"
        confirm.bind(on_release=check)
        popup.open()

    def message(self, title, text):
        Popup(title=title, content=Label(text=text), size_hint=(0.85, None), height=dp(190)).open()


if __name__ == "__main__":
    BlackLauncher().run()
