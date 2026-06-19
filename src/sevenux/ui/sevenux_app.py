from collections.abc import Callable
from dataclasses import dataclass

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Static

from sevenux.PlayerDoubleException import PlayerDoubleException
from sevenux.bot import Bot
from sevenux.card import Card
from sevenux.game import Game
from sevenux.player import Player
from sevenux.ui.widgets.card_board import CardBoard
from sevenux.ui.widgets.card_widget import CardWidget


TargetCallback = Callable[[Player], None]


@dataclass
class PendingChoice:
    prompt: str
    options: list[tuple[str, Player]]
    callback: TargetCallback


class SevenuxApp(App):
    ENABLE_COMMAND_PALETTE = False

    CSS = """
    SevenuxApp {
        background: #0b1018;
        color: #f4f7fb;
    }

    #layout {
        height: 100%;
    }

    #topbar {
        height: 3;
        padding: 0 2;
        background: #151c28;
        border-bottom: tall #2b3446;
    }

    #title {
        width: 1fr;
        text-style: bold;
        color: #f0b85a;
    }

    #deck-status {
        width: auto;
        content-align: right middle;
        color: #a8b0c2;
    }

    #main {
        height: 1fr;
    }

    #players-pane {
        width: 2fr;
        height: 100%;
        padding: 1 2;
    }

    #side-panel {
        width: 1fr;
        min-width: 40;
        height: 100%;
        padding: 1 2 1 1;
        background: #0f1520;
        border-left: heavy #2b3446;
    }

    .panel-title {
        height: 1;
        margin-bottom: 1;
        text-style: bold;
        color: #f4f7fb;
    }

    #turn-status {
        min-height: 4;
        padding: 1;
        margin-bottom: 1;
        border: round #4b5568;
        background: #141f2c;
        color: #eef4ff;
    }

    #ranking {
        min-height: 7;
        padding: 1;
        margin-bottom: 1;
        border: round #3a4457;
        background: #0b111b;
        color: #dce4f2;
    }

    #last-card-wrap {
        height: 9;
        margin-bottom: 1;
        padding: 1;
        border: round #343b4c;
        background: #101826;
    }

    #last-card-title {
        width: 1fr;
        color: #a8b0c2;
    }

    #last-card-slot {
        height: 4;
        margin-top: 1;
        align-horizontal: center;
    }

    #actions {
        height: 3;
        margin-bottom: 1;
    }

    #actions Button {
        width: 1fr;
        margin-right: 1;
    }

    #choice-prompt {
        height: auto;
        margin-bottom: 1;
        color: #f0b85a;
        text-style: bold;
    }

    #choices {
        height: auto;
        margin-bottom: 1;
    }

    #choices Button {
        width: 100%;
        margin-bottom: 1;
    }

    #log-box {
        height: 1fr;
        padding: 1;
        border: round #2f3b4d;
        background: #080c12;
    }

    #log {
        color: #d8deea;
    }

    Footer {
        background: #151c28;
    }
    """

    BINDINGS = [
        ("r", "restart", "Nouvelle partie"),
        ("q", "quit", "Quitter"),
    ]

    MAX_TARGETS = 6
    BOT_DELAY = 0.35
    ROUND_DELAY = 1.4
    MATCH_TARGET_SCORE = 200

    def __init__(self):
        super().__init__()
        self.game = self._create_game()
        self.round_number = 1
        self.turn_index = -1
        self.active_player: Player | None = None
        self.pending_choice: PendingChoice | None = None
        self.waiting_for_human = False
        self.round_transition = False
        self.game_over = False
        self.last_card: Card | None = None
        self.messages: list[str] = []
        self._log(f"Nouvelle partie. Objectif : {self.MATCH_TARGET_SCORE} points.")
        self._log(f"Manche {self.round_number}.")

    def compose(self) -> ComposeResult:
        with Vertical(id="layout"):
            with Horizontal(id="topbar"):
                yield Static("SEVENUX", id="title")
                yield Static("", id="deck-status")

            with Horizontal(id="main"):
                with VerticalScroll(id="players-pane"):
                    yield Static("Joueurs", classes="panel-title")
                    for index, player in enumerate(self.game.players):
                        yield CardBoard(
                            player,
                            board_id=f"player-{index}",
                            target_score=self.MATCH_TARGET_SCORE,
                        )

                with Vertical(id="side-panel"):
                    yield Static("État", classes="panel-title")
                    yield Static("", id="turn-status")
                    yield Static("Classement", classes="panel-title")
                    yield Static("", id="ranking")

                    with Vertical(id="last-card-wrap"):
                        yield Static("Dernière carte", id="last-card-title")
                        with Horizontal(id="last-card-slot"):
                            yield CardWidget()

                    with Horizontal(id="actions"):
                        yield Button("Piocher", id="draw", variant="success")
                        yield Button("Stop", id="stop", variant="warning")
                        yield Button("Relancer", id="restart", variant="primary")

                    yield Static("", id="choice-prompt")
                    with VerticalScroll(id="choices"):
                        for index in range(self.MAX_TARGETS):
                            yield Button("", id=f"target-{index}", variant="primary", disabled=True)

                    yield Static("Journal", classes="panel-title")
                    with VerticalScroll(id="log-box"):
                        yield Static("", id="log")

            yield Footer()

    def on_mount(self):
        self._refresh_ui()
        self._advance_turn()

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id
        if button_id == "draw":
            self._human_draw()
        elif button_id == "stop":
            self._human_stop()
        elif button_id == "restart":
            self.action_restart()
        elif button_id and button_id.startswith("target-"):
            self._choose_target(int(button_id.rsplit("-", 1)[1]))

    def action_restart(self):
        self.game = self._create_game()
        self.round_number = 1
        self.turn_index = -1
        self.active_player = None
        self.pending_choice = None
        self.waiting_for_human = False
        self.round_transition = False
        self.game_over = False
        self.last_card = None
        self.messages = []
        self._log(f"Nouvelle partie. Objectif : {self.MATCH_TARGET_SCORE} points.")
        self._log(f"Manche {self.round_number}.")
        self._refresh_ui()
        self._advance_turn()

    def _create_game(self) -> Game:
        game = Game()
        game.set_player(Player("François"))
        game.add_bot(Bot("Cyprien"))
        game.add_bot(Bot("Nikola"))
        game.add_bot(Bot("Rahim"))
        game.add_bot(Bot("Benazir"))
        return game

    def _advance_turn(self):
        if self.game_over or self.round_transition:
            self._refresh_ui()
            return

        if self._should_finish():
            self._finish_round()
            return

        for _ in self.game.players:
            self.turn_index = (self.turn_index + 1) % len(self.game.players)
            player = self.game.players[self.turn_index]
            if not player.is_stopped:
                self.active_player = player
                break
        else:
            self._finish_round()
            return

        if self.active_player is None:
            self._finish_round()
            return

        self._log(f"Tour de {self.active_player.name}.")
        if self.active_player.is_bot:
            self.waiting_for_human = False
            self._refresh_ui()
            self.set_timer(self.BOT_DELAY, self._play_bot_turn)
            return

        self.waiting_for_human = True
        self._refresh_ui()

    def _human_draw(self):
        if not self._can_human_act:
            return

        player = self.active_player
        if player is None:
            return

        self.waiting_for_human = False
        self._draw_cards(player, 1, self._complete_turn)
        self._refresh_ui()

    def _human_stop(self):
        if not self._can_human_act:
            return

        player = self.active_player
        if player is None:
            return

        player.stop()
        self.waiting_for_human = False
        self._log(f"{player.name} s'arrête avec {player.current_points} points.")
        self._complete_turn()

    def _play_bot_turn(self):
        player = self.active_player
        if (
            player is None
            or not player.is_bot
            or player.is_stopped
            or self.game_over
            or self.round_transition
        ):
            self._refresh_ui()
            return

        bot = player
        if not isinstance(bot, Bot):
            return

        if not bot.decide_draw():
            bot.stop()
            self._log(f"{bot.name} s'arrête avec {bot.current_points} points.")
            self._complete_turn()
            return

        self._draw_cards(bot, 1, self._complete_turn)
        self._refresh_ui()

    def _draw_cards(self, player: Player, count: int, after: Callable[[], None]):
        if count <= 0 or player.is_stopped:
            after()
            return

        if self.game.deck.is_empty():
            self._finish_round()
            return

        card = self.game.deck.draw_card()
        self.last_card = card
        self._log(f"{player.name} pioche {self._card_name(card)}.")

        def continue_chain():
            self._draw_cards(player, count - 1, after)

        self._resolve_card(player, card, continue_chain)

    def _resolve_card(self, actor: Player, card: Card, after: Callable[[], None]):
        if card.is_stop():
            self._resolve_stop(actor, after)
        elif card.is_draw3():
            self._resolve_draw3(actor, after)
        elif card.is_second_chance():
            self._resolve_second_chance(actor, after)
        else:
            self._add_card(actor, card)
            after()

    def _resolve_stop(self, actor: Player, after: Callable[[], None]):
        if actor.is_bot and isinstance(actor, Bot):
            target = actor.decide_stop(self.game.players)
            self._stop_target(actor, target)
            after()
            return

        targets = [bot for bot in self.game.bots_to_choose if bot is not actor]
        if not targets:
            self._stop_target(actor, actor)
            after()
        elif len(targets) == 1:
            self._stop_target(actor, targets[0])
            after()
        else:
            self._request_choice(
                "Carte Stop : choisir qui arrêter",
                [(target.name, target) for target in targets],
                lambda target: self._after_target(lambda: self._stop_target(actor, target), after),
            )

    def _resolve_draw3(self, actor: Player, after: Callable[[], None]):
        if actor.is_bot and isinstance(actor, Bot):
            target = actor.decide_draw3(self.game.players)
            self._log(f"{actor.name} donne +3 cartes à {target.name}.")
            self._draw_cards(target, 3, after)
            return

        targets: list[Player] = [actor, *self.game.bots_to_choose]
        if len(targets) == 1:
            target = targets[0]
            self._log(f"{actor.name} prend les +3 cartes.")
            self._draw_cards(target, 3, after)
            return

        self._request_choice(
            "Carte +3 : choisir qui pioche trois cartes",
            [("Moi", actor), *((target.name, target) for target in self.game.bots_to_choose)],
            lambda target: self._after_target(lambda: self._draw3_target(actor, target), after, target, 3),
        )

    def _resolve_second_chance(self, actor: Player, after: Callable[[], None]):
        if not actor.has_second_chance():
            actor.add_card(Card("secondchance"))
            self._log(f"{actor.name} gagne une Second Chance.")
            after()
            return

        if actor.is_bot and isinstance(actor, Bot):
            target = actor.decide_secondchance(self.game.players)
            self._give_second_chance(actor, target)
            after()
            return

        targets = [
            target
            for target in self.game.players
            if not target.is_stopped and target is not actor and not target.has_second_chance()
        ]
        if not targets:
            self._log(f"{actor.name} garde sa Second Chance.")
            after()
            return

        self._request_choice(
            "Second Chance déjà active : choisir qui la reçoit",
            [(target.name, target) for target in targets],
            lambda target: self._after_target(lambda: self._give_second_chance(actor, target), after),
        )

    def _add_card(self, player: Player, card: Card):
        try:
            player.add_card(card)
        except PlayerDoubleException as error:
            if error.with_second_chance:
                self._log(f"Double évité pour {player.name} : Second Chance consommée.")
            else:
                self._log(f"Double pour {player.name} : la manche est perdue.")
            return

        if card.is_plus_joker():
            self._log(f"{player.name} ajoute un bonus {card.value}.")
        elif card.is_x2():
            self._log(f"{player.name} active x2.")
        else:
            self._log(f"{player.name} monte à {player.current_points} points.")

    def _stop_target(self, actor: Player, target: Player):
        target.stop()
        if actor is target:
            self._log(f"{actor.name} doit s'arrêter.")
        else:
            self._log(f"{actor.name} arrête {target.name}.")

    def _draw3_target(self, actor: Player, target: Player):
        if actor is target:
            self._log(f"{actor.name} prend les +3 cartes.")
        else:
            self._log(f"{actor.name} donne +3 cartes à {target.name}.")

    def _give_second_chance(self, actor: Player, target: Player):
        target.add_card(Card("secondchance"))
        if actor is target:
            self._log(f"{target.name} garde sa Second Chance.")
        else:
            self._log(f"{actor.name} donne une Second Chance à {target.name}.")

    def _request_choice(self, prompt: str, options: list[tuple[str, Player]], callback: TargetCallback):
        self.pending_choice = PendingChoice(prompt, options, callback)
        self.waiting_for_human = False
        self._refresh_ui()

    def _choose_target(self, index: int):
        pending = self.pending_choice
        if pending is None or index >= len(pending.options):
            return

        target = pending.options[index][1]
        self.pending_choice = None
        pending.callback(target)
        self._refresh_ui()

    def _after_target(
        self,
        target_action: Callable[[], None],
        after: Callable[[], None],
        draw_target: Player | None = None,
        draw_count: int = 0,
    ):
        target_action()
        if draw_target is not None and draw_count > 0:
            self._draw_cards(draw_target, draw_count, after)
        else:
            after()

    def _complete_turn(self):
        self.pending_choice = None
        self.waiting_for_human = False
        self._refresh_ui()

        if self._should_finish():
            self._finish_round()
            return

        self.set_timer(self.BOT_DELAY, self._advance_turn)

    def _finish_round(self):
        if self.game_over or self.round_transition:
            self._refresh_ui()
            return

        self.round_transition = True
        self.waiting_for_human = False
        self.pending_choice = None
        self.active_player = None

        self.game.count_scores()
        leader = self._leader
        self._log(
            f"Fin de manche {self.round_number}. "
            f"Leader : {leader.name} ({leader.total_points}/{self.MATCH_TARGET_SCORE})."
        )

        winner = self._match_winner
        if winner is not None:
            self.game_over = True
            self.round_transition = False
            self._log(f"Fin de partie. Vainqueur : {winner.name} avec {winner.total_points} points.")
            self._refresh_ui()
            return

        self._log(f"Préparation de la manche {self.round_number + 1}.")
        self._refresh_ui()
        self.set_timer(self.ROUND_DELAY, self._start_next_round)

    def _start_next_round(self):
        if self.game_over:
            self._refresh_ui()
            return

        self.round_number += 1
        self.game.start_new_round()
        self.turn_index = -1
        self.active_player = None
        self.pending_choice = None
        self.waiting_for_human = False
        self.round_transition = False
        self.last_card = None
        self._log(f"Manche {self.round_number}.")
        self._refresh_ui()
        self._advance_turn()

    def _should_finish(self) -> bool:
        return self.game.deck.is_empty() or len(self.game.players_in_game) == 0

    @property
    def _leader(self) -> Player:
        return max(self.game.players, key=lambda player: player.total_points)

    @property
    def _match_winner(self) -> Player | None:
        eligible_winners = [
            player
            for player in self.game.players
            if player.total_points >= self.MATCH_TARGET_SCORE
        ]
        if not eligible_winners:
            return None
        return max(eligible_winners, key=lambda player: player.total_points)

    @property
    def _can_human_act(self) -> bool:
        return (
            self.waiting_for_human
            and self.pending_choice is None
            and self.active_player is not None
            and not self.active_player.is_bot
            and not self.round_transition
            and not self.game_over
        )

    def _refresh_ui(self):
        if not self.is_mounted:
            return

        self.query_one("#deck-status", Static).update(
            f"M{self.round_number} | Objectif {self.MATCH_TARGET_SCORE} | "
            f"Pioche {len(self.game.deck.cards)}"
        )
        self.query_one("#turn-status", Static).update(self._status_text)
        self.query_one("#ranking", Static).update(self._ranking_text)
        self.query_one("#log", Static).update("\n".join(self.messages[-14:]))

        draw_button = self.query_one("#draw", Button)
        stop_button = self.query_one("#stop", Button)
        draw_button.disabled = not self._can_human_act
        stop_button.disabled = not self._can_human_act

        self._refresh_players()
        self._refresh_last_card()
        self._refresh_choices()

    def _refresh_players(self):
        for index, player in enumerate(self.game.players):
            board = self.query_one(f"#player-{index}", CardBoard)
            board.player = player
            board.target_score = self.MATCH_TARGET_SCORE
            board.sync(active=player is self.active_player)

    def _refresh_last_card(self):
        slot = self.query_one("#last-card-slot")
        slot.remove_children()
        if self.last_card is None:
            slot.mount(CardWidget())
        else:
            slot.mount(CardWidget(self.last_card.value))

    def _refresh_choices(self):
        prompt = self.query_one("#choice-prompt", Static)
        choices = self.query_one("#choices")
        if self.pending_choice is None:
            prompt.update("")
            prompt.display = False
            choices.display = False
        else:
            prompt.update(self.pending_choice.prompt)
            prompt.display = True
            choices.display = True

        for index in range(self.MAX_TARGETS):
            button = self.query_one(f"#target-{index}", Button)
            if self.pending_choice is not None and index < len(self.pending_choice.options):
                label, target = self.pending_choice.options[index]
                button.label = f"{label} ({target.current_points})"
                button.tooltip = f"Choisir {target.name}"
                button.disabled = False
                button.display = True
            else:
                button.disabled = True
                button.display = False

    @property
    def _status_text(self) -> str:
        remaining_cards = len(self.game.deck.cards)
        players_in_game = len(self.game.players_in_game)
        total_players = len(self.game.players)

        if self.game_over:
            winner = self._match_winner
            winner_text = winner.name if winner is not None else self._leader.name
            return f"Fin de partie\nVainqueur : {winner_text}\nR pour relancer."

        if self.round_transition:
            leader = self._leader
            return (
                f"Manche {self.round_number} terminée\n"
                f"Leader : {leader.name}\n"
                "Manche suivante..."
            )

        if self.pending_choice is not None:
            return (
                f"Manche {self.round_number} | Pioche {remaining_cards}\n"
                "Décision requise\n"
                "Choisissez une cible."
            )

        if self.active_player is None:
            return f"Manche {self.round_number}\nPréparation...\nPioche {remaining_cards}"

        if self.active_player.is_bot:
            return (
                f"Manche {self.round_number} | Pioche {remaining_cards}\n"
                f"Tour : {self.active_player.name}\n"
                f"En jeu : {players_in_game}/{total_players}"
            )

        return (
            f"Manche {self.round_number} | Pioche {remaining_cards}\n"
            f"Main : {self.active_player.current_points} pts\n"
            f"Total : {self.active_player.total_points}/{self.MATCH_TARGET_SCORE}"
        )

    @property
    def _ranking_text(self) -> str:
        ranked_players = sorted(
            self.game.players,
            key=lambda player: (player.total_points + player.current_points, player.total_points),
            reverse=True,
        )

        lines: list[str] = []
        for position, player in enumerate(ranked_players, start=1):
            projected_score = player.total_points + player.current_points
            active_marker = "*" if player is self.active_player else " "
            status = "STOP" if player.is_stopped else "ACTIF"
            name = self._compact_name(player.name)
            lines.append(
                f"{active_marker}{position}. {name:<9} "
                f"{projected_score:>3}/{self.MATCH_TARGET_SCORE} "
                f"+{player.current_points:<2} {status}"
            )
        return "\n".join(lines)

    def _compact_name(self, name: str, max_length: int = 9) -> str:
        if len(name) <= max_length:
            return name
        return f"{name[:max_length - 1]}."

    def _card_name(self, card: Card) -> str:
        if card.is_stop():
            return "Stop"
        if card.is_draw3():
            return "Pioche +3"
        if card.is_second_chance():
            return "Second Chance"
        return card.value

    def _log(self, message: str):
        self.messages.append(message)
        if len(self.messages) > 40:
            self.messages = self.messages[-40:]
