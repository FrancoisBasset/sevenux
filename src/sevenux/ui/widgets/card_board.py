from textual.app import ComposeResult
from textual.containers import Horizontal, HorizontalScroll, Vertical
from textual.widget import Widget
from textual.widgets import Static

from sevenux.player import Player
from sevenux.ui.widgets.card_widget import CardWidget


class CardBoard(Widget):
    DEFAULT_CSS = """
    CardBoard {
        height: 8;
        padding: 0 1;
        margin-bottom: 1;
        border: round #343b4c;
        background: #111722;
    }

    CardBoard.active {
        border: heavy #f0b85a;
        background: #1e2a3d;
    }

    CardBoard.stopped {
        border: round #4a5163;
        background: #0d1119;
    }

    CardBoard.knocked-out {
        border: heavy #ef6351;
        background: #251316;
    }

    CardBoard .player-head {
        height: 1;
        margin-bottom: 0;
    }

    CardBoard .player-name {
        width: 1fr;
        text-style: bold;
        color: #f4f7fb;
    }

    CardBoard .player-role {
        width: auto;
        color: #9aa6bd;
        text-align: right;
    }

    CardBoard .player-state {
        width: auto;
        margin-right: 1;
        padding: 0 1;
        text-style: bold;
        color: #111827;
    }

    CardBoard .player-state.stop {
        background: #ffc857;
    }

    CardBoard .player-state.ko {
        background: #ef6351;
        color: #fff7f4;
    }

    CardBoard .cards-row {
        height: 5;
        margin-top: 0;
    }

    CardBoard .player-summary {
        height: 1;
        margin-top: 0;
    }

    CardBoard .score-row {
        height: 1;
    }

    CardBoard .score-current {
        width: 1fr;
        text-style: bold;
        color: #f4f7fb;
    }

    CardBoard .score-total {
        width: auto;
        text-style: bold;
        color: #f0b85a;
        text-align: right;
    }

    """

    def __init__(self, player: Player, *, board_id: str, target_score: int = 200):
        super().__init__(id=board_id)
        self.player = player
        self.target_score = target_score

    def sync(self, *, active: bool):
        self.set_class(active, "active")
        self.set_class(self.player.is_stopped and not self.player.is_knocked_out, "stopped")
        self.set_class(self.player.is_knocked_out, "knocked-out")
        self.refresh(recompose=True)

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="player-head"):
                yield Static(self.player.name, classes="player-name")
                if self.player.is_knocked_out:
                    yield Static("KO", classes="player-state ko")
                elif self.player.is_stopped:
                    yield Static("STOP", classes="player-state stop")
                yield Static(self._role_text, classes="player-role")

            with HorizontalScroll(classes="cards-row"):
                cards = [*self.player.jokers]
                if self.player.has_x2():
                    cards.append(CardLike("x2"))
                if self.player.has_second_chance():
                    cards.append(CardLike("secondchance"))
                cards.extend(self.player.cards)

                if cards:
                    for card in cards:
                        yield CardWidget(card.value)
                else:
                    yield CardWidget()

            with Vertical(classes="player-summary"):
                with Horizontal(classes="score-row"):
                    yield Static(self._round_score_text, classes="score-current")
                    yield Static(self._total_score_text, classes="score-total")

    @property
    def _role_text(self) -> str:
        return "Bot" if self.player.is_bot else "Joueur"

    @property
    def _round_score_text(self) -> str:
        return f"Manche {self.player.current_points}"

    @property
    def _total_score_text(self) -> str:
        return f"Total {self.player.total_points}/{self.target_score}"

class CardLike:
    def __init__(self, value: str):
        self.value = value
