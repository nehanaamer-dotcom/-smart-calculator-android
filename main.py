from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
import ast
import operator
import re

BG = "#0F172A"
PANEL = "#111C2E"
DISPLAY = "#1E293B"
NUMBER = "#263449"
UTILITY = "#34445A"
BLUE = "#2563EB"
GREEN = "#0D9488"
WHITE = "#F8FAFC"
MUTED = "#94A3B8"
ERROR = "#FCA5A5"

BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def evaluate(expression):
    tree = ast.parse(expression, mode="eval")

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
            left, right = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Div) and right == 0:
                raise ZeroDivisionError
            return BIN_OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
            return UNARY_OPS[type(node.op)](walk(node.operand))
        raise ValueError("Unsupported expression")

    value = walk(tree)
    if not isinstance(value, (int, float)) or value != value or abs(value) == float("inf"):
        raise ValueError("Invalid result")
    return value


class CalculatorRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(16), spacing=dp(12), **kwargs)
        self.expression = ""
        self.finished = False
        self._build()

    def _label(self, text, size, color, bold=False, halign="right"):
        label = Label(
            text=text, font_size=sp(size), color=get_color_from_hex(color),
            bold=bold, halign=halign, valign="middle",
            size_hint_y=None, height=dp(size * 1.65)
        )
        label.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        return label

    def _build(self):
        header = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        header.add_widget(Label(
            text="🧮  الحاسبة الذكية", font_size=sp(22), bold=True,
            color=get_color_from_hex(WHITE), halign="right", valign="middle"
        ))
        self.add_widget(header)

        screen = BoxLayout(
            orientation="vertical", padding=[dp(18), dp(14)],
            spacing=dp(4), size_hint_y=None, height=dp(132)
        )
        screen.canvas.before.clear()
        from kivy.graphics import Color, RoundedRectangle
        with screen.canvas.before:
            Color(*get_color_from_hex(DISPLAY))
            self.screen_bg = RoundedRectangle(pos=screen.pos, size=screen.size, radius=[dp(18)])
        screen.bind(pos=self._update_screen_bg, size=self._update_screen_bg)

        self.expression_label = self._label("0", 19, MUTED)
        self.result_label = self._label("0", 34, "#60A5FA", True)
        screen.add_widget(self.expression_label)
        screen.add_widget(self.result_label)
        self.add_widget(screen)

        keys = [
            ("AC", "utility", self.clear), ("⌫", "utility", self.backspace),
            ("%", "utility", self.percent), ("÷", "operator", lambda: self.add("/")),
            ("7", "number", lambda: self.add("7")), ("8", "number", lambda: self.add("8")),
            ("9", "number", lambda: self.add("9")), ("×", "operator", lambda: self.add("*")),
            ("4", "number", lambda: self.add("4")), ("5", "number", lambda: self.add("5")),
            ("6", "number", lambda: self.add("6")), ("−", "operator", lambda: self.add("-")),
            ("1", "number", lambda: self.add("1")), ("2", "number", lambda: self.add("2")),
            ("3", "number", lambda: self.add("3")), ("+", "operator", lambda: self.add("+")),
            ("(", "utility", lambda: self.add("(")), ("0", "number", lambda: self.add("0")),
            (".", "number", lambda: self.add(".")), (")", "utility", lambda: self.add(")")),
        ]
        grid = GridLayout(cols=4, spacing=dp(9), size_hint_y=1)
        for label, kind, callback in keys:
            grid.add_widget(self._button(label, kind, callback))
        self.add_widget(grid)

        bottom = GridLayout(cols=2, spacing=dp(9), size_hint_y=None, height=dp(62))
        bottom.add_widget(self._button("مسح", "utility", self.clear))
        bottom.add_widget(self._button("=", "equal", self.calculate))
        self.add_widget(bottom)

        self.add_widget(Label(
            text="حاسبة رياضية • تعمل دون إنترنت", font_size=sp(11),
            color=get_color_from_hex("#64748B"), size_hint_y=None, height=dp(22)
        ))

    def _update_screen_bg(self, instance, value):
        self.screen_bg.pos = instance.pos
        self.screen_bg.size = instance.size

    def _button(self, text, kind, callback):
        colors = {
            "number": NUMBER, "utility": UTILITY,
            "operator": BLUE, "equal": GREEN
        }
        button = Button(
            text=text, font_size=sp(22), bold=True,
            color=get_color_from_hex(WHITE),
            background_normal="", background_down="",
            background_color=get_color_from_hex(colors[kind]),
            size_hint_y=None, height=dp(56)
        )
        button.bind(on_release=lambda *_: callback())
        return button

    def refresh(self):
        shown = self.expression.replace("*", "×").replace("/", "÷").replace("-", "−")
        self.expression_label.text = shown or "0"

    def add(self, value):
        if self.finished and (value.isdigit() or value in ".("):
            self.expression = ""
        self.finished = False
        self.expression += value
        self.refresh()

    def clear(self):
        self.expression = ""
        self.finished = False
        self.expression_label.text = "0"
        self.result_label.text = "0"
        self.result_label.color = get_color_from_hex("#60A5FA")

    def backspace(self):
        self.expression = self.expression[:-1]
        self.finished = False
        self.refresh()

    def percent(self):
        match = re.search(r"(\d+(?:\.\d*)?|\.\d+)$", self.expression)
        if match:
            self.expression = self.expression[:match.start()] + str(float(match.group(1)) / 100)
            self.refresh()
            self.finished = False

    def calculate(self):
        if not self.expression:
            return
        try:
            if not re.fullmatch(r"[0-9+\-*/().\s]+", self.expression):
                raise ValueError
            value = evaluate(self.expression)
            answer = "0" if value == 0 else (f"{value:.12g}" if isinstance(value, float) else str(value))
            self.result_label.text = answer
            self.result_label.color = get_color_from_hex("#60A5FA")
            self.finished = True
        except ZeroDivisionError:
            self.result_label.text = "لا يمكن القسمة على صفر"
            self.result_label.color = get_color_from_hex(ERROR)
        except Exception:
            self.result_label.text = "خطأ في العملية"
            self.result_label.color = get_color_from_hex(ERROR)


class CalculatorApp(App):
    title = "الحاسبة الذكية"

    def build(self):
        Window.clearcolor = get_color_from_hex(BG)
        Window.softinput_mode = "below_target"
        return CalculatorRoot()


if __name__ == "__main__":
    CalculatorApp().run()
