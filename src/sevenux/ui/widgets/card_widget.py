from textual.app import ComposeResult
from textual.widgets import Static


class CardWidget(Static):
    DEFAULT_CSS = """
    CardWidget {
        width: 7;
        height: 4;
        min-width: 7;
        content-align: center middle;
        text-align: center;
        margin: 0 1 0 0;
        text-style: bold;
    }

    CardWidget.number {
        background: #f4f2e8;
        color: #111827;
    }

    CardWidget.number-0 { color: #374151; }
    CardWidget.number-1 { color: #b42318; }
    CardWidget.number-2 { color: #8a5a00; }
    CardWidget.number-3 { color: #187a44; }
    CardWidget.number-4 { color: #006c68; }
    CardWidget.number-5 { color: #006f8e; }
    CardWidget.number-6 { color: #1d5da6; }
    CardWidget.number-7 { color: #4c4db4; }
    CardWidget.number-8 { color: #7140a1; }
    CardWidget.number-9 { color: #9e3f86; }
    CardWidget.number-10 { color: #ad3658; }
    CardWidget.number-11 { color: #a7440b; }
    CardWidget.number-12 { color: #75421d; }

    CardWidget.bonus {
        background: #ffe08a;
        color: #7a4d00;
    }

    CardWidget.action {
        background: #d9f3f4;
        color: #0f2930;
    }

    CardWidget.chance {
        background: #e7ddff;
        color: #5924a6;
    }

    CardWidget.stop {
        background: #ef6351;
        color: #fff7f4;
    }

    CardWidget.draw3 {
        background: #48caad;
        color: #063b2f;
    }

    CardWidget.x2 {
        background: #ffc857;
        color: #714700;
    }

    CardWidget.bonus-plus {
        background: #f9dc5c;
        color: #694900;
    }

    CardWidget.empty-card {
        background: #151923;
        color: #7b8498;
    }
    """

    LABELS = {
        "secondchance": "2E\nCHANCE",
        "draw3": "PIOCHE\n+3",
        "stop": "STOP",
        "x2": "MULTI\nx2",
    }

    def __init__(self, value: str | None = None, *, classes: str | None = None):
        self.value = value
        super().__init__(self._label, classes=self._classes(classes))
        if value is not None:
            self.tooltip = self._tooltip_text

    def compose(self) -> ComposeResult:
        yield from ()

    @property
    def _label(self) -> str:
        if self.value is None:
            return "--"
        if self.value.isdigit():
            return self.value
        if self.value.startswith("+"):
            return self.value
        return self.LABELS.get(self.value, self.value)

    @property
    def _tooltip_text(self) -> str:
        if self.value == "secondchance":
            return "Second Chance"
        if self.value == "draw3":
            return "Pioche 3"
        if self.value == "stop":
            return "Stop"
        if self.value == "x2":
            return "Multiplicateur x2"
        if self.value and self.value.startswith("+"):
            return f"Bonus {self.value}"
        return f"Carte {self.value}"

    def _classes(self, extra_classes: str | None) -> str:
        card_classes = [self._kind]
        value_class = self._value_class
        if value_class is not None:
            card_classes.append(value_class)
        if extra_classes:
            card_classes.append(extra_classes)
        return " ".join(card_classes)

    @property
    def _kind(self) -> str:
        if self.value is None:
            return "empty-card"
        if self.value == "secondchance":
            return "chance"
        if self.value in {"draw3", "stop"}:
            return "action"
        if self.value == "x2" or self.value.startswith("+"):
            return "bonus"
        return "number"

    @property
    def _value_class(self) -> str | None:
        if self.value is None:
            return None
        if self.value.isdigit():
            return f"number-{self.value}"
        if self.value in {"draw3", "stop", "secondchance", "x2"}:
            return self.value
        if self.value.startswith("+"):
            return "bonus-plus"
        return None
