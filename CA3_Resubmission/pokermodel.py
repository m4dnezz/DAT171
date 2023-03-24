from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cardlib
import abc

# TODO: Code cleanup and renaming
# TODO: Comments
###########################


class CardModel(QObject):
    """ Base class that described what is expected from the CardView widget """

    new_cards = pyqtSignal()  #: Signal should be emited when cards change.

    @abc.abstractmethod
    def __iter__(self):
        """Returns an iterator of card objects"""

    @abc.abstractmethod
    def flipped(self):
        """Returns true of cards should be drawn face down"""


class HandModel(cardlib.Hand, CardModel):
    def __init__(self):
        cardlib.Hand.__init__(self)
        CardModel.__init__(self)
        self.flipped_cards = False

    def __iter__(self):
        return iter(self.cards)

    def flip(self, state):
        # Flips over the cards (to hide them)
        self.flipped_cards = state
        self.new_cards.emit()

    def flipped(self):
        # This model only flips all or no cards, so we don't care about the index.
        return self.flipped_cards

    def add_card(self, card):
        super().add_card(card)
        self.new_cards.emit()

    def clear_hand(self):
        super().clear_hand()
        self.new_cards.emit()


class TableCardsModel(HandModel, CardModel):
    def __init__(self):
        CardModel.__init__(self)
        self.cards = []
        self.flipped_cards = False

    def add_card(self, card):
        super().add_card(card)
        self.new_cards.emit()

    def __iter__(self):
        return iter(self.cards)

    def flipped(self):
        # This model only flips all or no cards, so we don't care about the index.
        return self.flipped_cards

##########################


class Player(QObject):
    player_changed = pyqtSignal()

    def __init__(self, name, credit):
        super().__init__()
        self.player = [name, credit]
        self.name = name
        self.credit = credit
        self.hand = HandModel()

    def win(self, amount):
        pass

    def lose(self, amount):
        pass

    def get_name(self):
        return str(self.name)

    def get_credit(self):
        return str(self.credit)


class Pot(QObject):
    def __init__(self):
        super().__init__()
        self.credit = 0

    def clear(self):
        self.credit = 0


class Poker(QObject):
    new_active_player = pyqtSignal()
    pot_changed = pyqtSignal()
    player_credit_changed = pyqtSignal()
    last_bet_changed = pyqtSignal()
    alert = pyqtSignal(str)
    game_over = pyqtSignal()

    def __init__(self, players, credit):
        super().__init__()
        self.table_cards = TableCardsModel()
        self.pot = Pot()
        self.players = [Player(name, credit) for name in players]
        self.deck = None
        self.active_player = 0
        self.inactive_player = 1
        self.check_player = 0
        self.last_bet = 0
        self.state = None
        self.new_round()

    def new_round(self):
        self.pot.clear()
        self.deck = cardlib.StandardDeck()
        self.deck.shuffle()
        self.table_cards.clear_hand()
        self.state = 0
        self.last_bet = 0
        self.next_player()
        self.check_player = self.active_player

        for player in self.players:
            player.hand.clear_hand()
            player.hand.add_card(self.deck.draw())
            player.hand.add_card(self.deck.draw())

        for player in self.players:
            if player.credit == 0:
                self.game_over.emit()
                self.alert.emit("Resetting credits...")
                self.players[0].credit = 100
                self.players[1].credit = 100
                self.player_credit_changed.emit()

        self.pot_changed.emit()
        self.new_active_player.emit()
        self.last_bet_changed.emit()

    def call(self):
        if self.last_bet != 0:
            if self.last_bet <= self.players[self.active_player].credit:
                self.pot.credit += self.last_bet  # Need to be larger than last bet
                self.players[self.active_player].credit -= self.last_bet
                self.pot_changed.emit()
                self.player_credit_changed.emit()
                if self.players[self.active_player].credit == 0 and self.players[self.inactive_player].credit == 0:  # both players All-in
                    for i in range(4 - self.state):
                        self.next_turn()
                else:
                    self.last_bet = 0
                    self.next_turn()
                    self.next_player()
                    self.last_bet_changed.emit()
            else:
                pass  # all in function
        else:
            self.alert.emit("You can't call, previous player have not made any bets!")

    def raise_bet(self, amount):
        if amount > self.players[self.inactive_player].credit:
            amount = self.players[self.inactive_player].credit
            self.alert.emit("your bet was adjusted to match the other players credit limit")

        bet = self.last_bet + amount

        if bet <= self.players[self.active_player].credit:
            self.pot.credit += bet
            self.players[self.active_player].credit -= bet
            self.last_bet = bet - self.last_bet
            self.next_player()
            self.pot_changed.emit()
            self.player_credit_changed.emit()
            self.last_bet_changed.emit()
        else:
            self.alert.emit("You can't bet more money than you have!")

    def fold(self):
        self.players[self.inactive_player].credit += self.pot.credit
        self.player_credit_changed.emit()
        self.new_round()

    def check(self):
        if self.last_bet == 0:
            if self.active_player == self.check_player:
                self.next_player()
            elif self.active_player != self.check_player:
                self.last_bet = 0
                self.next_turn()
                self.next_player()
        else:
            self.alert.emit("You can't check when previous player betted!")

    def next_turn(self):
        if self.state == 0:
            self.flopp()
            self.state += 1
        elif self.state == 1:
            self.turn()
            self.state += 1
        elif self.state == 2:
            self.river()
            self.state = 3
        else:
            self.evaluate()

    def flopp(self):
        self.table_cards.add_card(self.deck.draw())
        self.table_cards.add_card(self.deck.draw())
        self.table_cards.add_card(self.deck.draw())
        self.check_player = self.inactive_player

    def turn(self):
        self.table_cards.add_card(self.deck.draw())
        self.check_player = self.inactive_player

    def river(self):
        self.table_cards.add_card(self.deck.draw())
        self.check_player = self.inactive_player

    def next_player(self):
        self.active_player = (1 + self.active_player) % 2
        self.inactive_player = (1 + self.inactive_player) % 2
        self.new_active_player.emit()

    def get_active_player(self):
        return self.players[self.active_player]

    def get_pot(self):
        return self.pot.credit

    def evaluate(self):
        players_ph = []
        for player in self.players:
            players_ph.append(player.hand.best_poker_hand(self.table_cards.cards))

        if players_ph[0] < players_ph[1]:
            self.players[1].credit += self.pot.credit
            self.player_credit_changed.emit()
            self.alert.emit(f"Maithri won with {players_ph[1].handtype.name} over Niclas {players_ph[0].handtype.name}")
            self.new_round()

        elif players_ph[0] > players_ph[1]:
            self.players[0].credit += self.pot.credit
            self.player_credit_changed.emit()
            self.alert.emit(f"Niclas won with {players_ph[0].handtype.name} over Maithris {players_ph[1].handtype.name}")
            self.new_round()

        else:
            self.players[0].credit += self.pot.credit / 2
            self.players[1].credit += self.pot.credit / 2
            self.player_credit_changed.emit()
            self.alert.emit(f"Pot splitted between players\nBoth player with hand {players_ph[0].handtype.name} and"
                            f" same high-card")
            self.new_round()


