import os
import json
import csv
import random

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.stencilview import StencilView
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp

ENTRIES_JSON = "entries.json"
ENTRIES_CSV = "entries.csv"
HISTORY_JSON = "history.json"


def load_entries():
    if os.path.exists(ENTRIES_JSON):
        with open(ENTRIES_JSON, "r", encoding="utf-8") as f:
            return json.load(f)

    entries = []
    if os.path.exists(ENTRIES_CSV):
        with open(ENTRIES_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = row.get("Item")
                if item:
                    entries.append({"Item": item.strip(), "Used": False})
    with open(ENTRIES_JSON, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
    return entries


def save_entries(data):
    with open(ENTRIES_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_history():
    if os.path.exists(HISTORY_JSON):
        with open(HISTORY_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(data):
    with open(HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class SpinnerView(FloatLayout):
    ITEM_HEIGHT = dp(40)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stencil = StencilView(size_hint=(1, 1))
        self.add_widget(self.stencil)
        self.reel = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=dp(2))
        self.stencil.add_widget(self.reel)
        with self.canvas.after:
            Color(1, 1, 1, 0.2)
            self.bar = Rectangle(size=(0, dp(40)), pos=(0, 0))
        self.bind(size=self._update_bar, pos=self._update_bar)

    def _update_bar(self, *args):
        self.bar.size = (self.width, dp(40))
        self.bar.pos = (self.x, self.center_y - dp(20))

    def spin(self, winner, all_entries):
        temp = [random.choice(all_entries)["Item"] for _ in range(20)]
        temp.append(winner)
        self.reel.clear_widgets()
        for text in temp:
            lbl = Label(text=text, size_hint_y=None, height=self.ITEM_HEIGHT)
            self.reel.add_widget(lbl)
        self.reel.height = len(temp) * self.ITEM_HEIGHT
        self.reel.y = self.height
        final_offset = self.reel.height - (self.height / 2 + self.ITEM_HEIGHT / 2)
        Animation.cancel_all(self.reel)
        anim = Animation(y=-final_offset, d=4, t="out_cubic")
        anim.start(self.reel)

    def show_text(self, text):
        self.reel.clear_widgets()
        lbl = Label(text=text, size_hint_y=None, height=self.ITEM_HEIGHT)
        self.reel.add_widget(lbl)
        self.reel.height = self.ITEM_HEIGHT
        self.reel.y = self.height / 2 - self.ITEM_HEIGHT / 2


class HistoryPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", size_hint_x=None, width=0, **kwargs)
        self.visible = False
        self.scroll = ScrollView()
        self.container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        self.container.bind(minimum_height=self.container.setter("height"))
        self.scroll.add_widget(self.container)
        self.add_widget(self.scroll)

    def refresh(self, history):
        self.container.clear_widgets()
        for item in history:
            lbl = Label(text=item, size_hint_y=None, height=dp(30))
            self.container.add_widget(lbl)

    def toggle(self):
        if self.visible:
            Animation(width=0, d=0.3).start(self)
        else:
            Animation(width=dp(200), d=0.3).start(self)
        self.visible = not self.visible


class SpinnerApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        self.entries = load_entries()
        self.history = load_history()

        root = BoxLayout(orientation="horizontal")
        self.history_panel = HistoryPanel()
        self.history_panel.refresh(self.history)

        main = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        self.spinner = SpinnerView(size_hint=(1, 0.7))
        btn_spin = Button(text="Spin Again", size_hint_y=None, height=dp(50))
        btn_spin.bind(on_release=self.on_spin)
        btn_hist = Button(text="Toggle History", size_hint_y=None, height=dp(40))
        btn_hist.bind(on_release=lambda inst: self.history_panel.toggle())
        main.add_widget(self.spinner)
        main.add_widget(btn_spin)
        main.add_widget(btn_hist)

        root.add_widget(main)
        root.add_widget(self.history_panel)
        return root

    def on_spin(self, _):
        unused = [e for e in self.entries if not e.get("Used")]
        if not unused:
            self.spinner.show_text("No more items")
            return
        winner_entry = random.choice(unused)
        winner = winner_entry["Item"]
        for e in self.entries:
            if e["Item"] == winner:
                e["Used"] = True
                break
        save_entries(self.entries)

        self.history.append(winner)
        save_history(self.history)
        self.history_panel.refresh(self.history)

        self.spinner.spin(winner, self.entries)


if __name__ == "__main__":
    SpinnerApp().run()
