import enum
from enum import IntEnum
import numpy as np
import random
from collections import Counter
import abc


@enum.unique
class Suit(IntEnum):
    """
    Enum class that represent each Suit
    """
    Hearts = 0
    Spades = 1
    Clubs = 2
    Diamonds = 3

    def __lt__(self, other):
        return self.value < other.value  # Necessary?

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return 'Suit(%r)' % self.name


@enum.unique
class HandValue(IntEnum):
    """
    Enum class that represent all the different hand types possible in poker
    """
    straight_flush = 9
    four_of_a_kind = 8
    full_house = 7
    flush = 6
    straight = 5
    three_of_a_kind = 4
    two_pair = 3
    one_pair = 2
    high_card = 1


class PlayingCard(abc.ABC):  # Abstract base class, acting as blueprint for other classes
    """ Parent class for the different types of playing cards"""

    def __init__(self, suit):
        self.value = None
        self.suit = suit

    def __lt__(self, other):
        return self.get_value() < other.get_value()

    def __eq__(self, other):
        return self.get_value() == other.get_value()

    @abc.abstractmethod
    def get_value(self):
        pass

    @abc.abstractmethod
    def get_suit(self):
        pass


class NumberedCard(PlayingCard):
    """ A class representing all the numbered cards e.g. card 2-10"""

    def __init__(self, value: int, suit: Suit):
        super().__init__(suit)
        self.value = value
        self.suit = suit

    def get_value(self):
        return self.value

    def get_suit(self):
        return self.suit

    def __str__(self):
        return f"{self.value} of {self.suit.name}"

    def __repr__(self):
        return 'Card(%r, %r)' % (self.get_value(), self.suit.name)


class JackCard(PlayingCard):
    """ A class that crates Jack playing cards
       :param suit: suit of card
       :type suit: Suit
       """

    def __init__(self, suit: Suit):
        super().__init__(suit)
        self.value = 11
        self.name = 'Jack'

    def get_value(self):
        return self.value

    def get_suit(self):
        return self.suit

    def __str__(self):
        return f"Jack of {self.suit.name}"

    def __repr__(self):
        return 'Card(%r, %r)' % (self.get_value(), self.suit.name)


class QueenCard(PlayingCard):
    """ A class that creates Queen playing cards"""

    def __init__(self, suit: Suit):
        super().__init__(suit)
        self.value = 12
        self.name = 'Queen'

    def get_value(self):
        return self.value

    def get_suit(self):
        return self.suit

    def __str__(self):
        return f"Queen of {self.suit.name}"

    def __repr__(self):
        return 'Card(%r, %r)' % (self.get_value(), self.suit.name)


class KingCard(PlayingCard):
    """ A class that creates King playing cards"""

    def __init__(self, suit: Suit):
        super().__init__(suit)
        self.value = 13
        self.name = 'King'

    def get_value(self):
        return self.value

    def get_suit(self):
        return self.suit

    def __str__(self):
        return f"King of {self.suit.name}"

    def __repr__(self):
        return 'Card(%r, %r)' % (self.get_value(), self.suit.name)


class AceCard(PlayingCard):
    """ A class that creates Aces playing cards"""

    def __init__(self, suit: Suit):
        super().__init__(suit)
        self.value = 14
        self.name = "Ace"

    def get_value(self):
        return self.value

    def get_suit(self):
        return self.suit

    def __str__(self):
        return f"Ace of {self.suit.name}"

    def __repr__(self):
        return 'Card(%r, %r)' % (self.get_value(), self.suit.name)


class StandardDeck(object):
    """This class is used for representing a standard deck of cards. The deck will contain 52 unique cards"""

    def __init__(self):
        self.deck = []
        for i in range(2, 11):  # Adds the numbered cards
            for j in Suit:
                self.deck.append(NumberedCard(value=i, suit=j))

        for i in Suit:  # Adds the pictured cards
            self.deck.append(JackCard(suit=i))
            self.deck.append(QueenCard(suit=i))
            self.deck.append(KingCard(suit=i))
            self.deck.append(AceCard(suit=i))

    def shuffle(self):
        random.shuffle(self.deck)

    def draw(self):
        if len(self.deck) > 0:
            return self.deck.pop(-1)
        else:
            raise IndexError("Deck is empty")  # Deck is empty


class Hand(object):
    """This class represent a hand with cards"""

    def __init__(self, cards=None):
        if cards is None:
            self.cards = []
        else:
            self.cards = cards

    def add_card(self, card):
        self.cards.append(card)

    def drop_cards(self, indices: list[int]):
        self.cards = np.delete(self.cards, indices)

    def clear_hand(self):
        self.cards = []

    def sort(self):
        self.cards.sort()

    def best_poker_hand(self, table_cards=None):
        """
        This function determines the best pokerhand that a hand can achieve
        :param table_cards: Cards that is shared by all players and can be used to create a pokerhand
        :return: The pokerhand with the highest rank and the highest card
        """
        if table_cards is None:
            table_cards = []
        all_cards = self.cards + table_cards
        ph = PokerHand(all_cards)
        return ph

    def __str__(self):
        return f"Hand containing {self.cards}".replace("Card", "")


class PokerHand(object):
    """ This class is used to declare the different available poker-hands through static methods"""

    def __init__(self, cards):
        self.handtype = None
        self.highest_card = None
        self.cards = cards
        self.check()

    def check(self):
        """
        This method loops through the static methods until it finds the best pokerhand
        :return: Best pokerhand and the highest card in that hand
        :type: tuple
        """
        list_of_functions = [PokerHand.straightflush, PokerHand.fourofakind, PokerHand.fullhouse, PokerHand.flush,
                             PokerHand.straight, PokerHand.threeofakind, PokerHand.twopair, PokerHand.onepair,
                             PokerHand.highcard]

        for func, val in zip(list_of_functions, HandValue):
            self.handtype = val
            if func(self.cards):
                self.highest_card = self.highcard(self.cards)
                break
        return self.handtype, self.highest_card

    @staticmethod
    def count(cards):
        values = Counter([card.get_value() for card in cards])
        return values

    @staticmethod
    def highcard(cards: list):

        values = [card.get_value() for card in cards]
        values.sort()
        return values[-1]

    @staticmethod
    def onepair(cards: list):

        values = PokerHand.count(cards)
        pair = [v[0] for v in values.items() if v[1] >= 2]
        pair.sort()
        if pair:
            return True
        else:
            return False

    @staticmethod
    def twopair(cards: list):
        values = PokerHand.count(cards)
        twopair = [v[0] for v in values.items() if v[1] >= 2]
        twopair.sort()
        if len(twopair) >= 2:
            return True
        else:
            return False

    @staticmethod
    def threeofakind(cards: list):
        values = PokerHand.count(cards)
        three = [v[0] for v in values.items() if v[1] >= 3]
        three.sort()
        if three:
            return True
        else:
            return False

    @staticmethod
    def straight(cards: list):  # Not working with more than 5 cards
        values = [card.get_value() for card in cards]
        values.sort()
        values_unique = list(dict.fromkeys(values))
        sepcial_case = {2, 3, 4, 5, 14}
        if set(values).intersection(sepcial_case) == sepcial_case:
            return True
        else:
            for i, value in enumerate(values_unique):
                counter = 1
                for j, other_value in enumerate(values_unique):
                    if j <= i:
                        continue
                    elif value == other_value - j + i:
                        counter += 1
                        if counter == 5:
                            return True
            return False

    @staticmethod
    def flush(cards: list):
        suits = [card.get_suit().__str__() for card in cards]  # Convert to string to make hashable
        return any(suits.count(suit) >= 5 for suit in set(suits))

    @staticmethod
    def fullhouse(cards: list):
        value_count = Counter()
        for c in cards:
            value_count[c.get_value()] += 1
        # Find the card ranks that have at least three of a kind
        threes = [v[0] for v in value_count.items() if v[1] >= 3]
        threes.sort()
        # Find the card ranks that have at least a pair
        twos = [v[0] for v in value_count.items() if v[1] >= 2]
        twos.sort()
        # Threes are dominant in full house, lets check that value first:
        for three in reversed(threes):
            for two in reversed(twos):
                if two != three:
                    return True
        return False

    @staticmethod
    def fourofakind(cards: list):
        values = PokerHand.count(cards)
        four = [v[0] for v in values.items() if v[1] >= 4]
        four.sort()
        if four:
            return True
        else:
            return False

    @staticmethod
    def straightflush(cards: list):
        cards.sort()
        vals = [(c.get_value(), c.suit) for c in cards] \
               + [(1, c.suit) for c in cards if c.get_value() == 14]  # Add the aces!
        for c in reversed(cards):  # Starting point (high card)
            # Check if we have the value - k in the set of cards:
            found_straight = True
            for k in range(1, 5):
                if (c.get_value() - k, c.suit) not in vals:
                    found_straight = False
                    break
            if found_straight:
                return True
        return False

    def __lt__(self, other):
        if self.handtype in [1, 2, 3, 4, 8]:  # Only compare highcard if type is less than five cards
            return [self.handtype, self.highest_card] < [other.handtype, other.highest_card]
        else:
            return self.handtype < other.handtype

    def __eq__(self, other):
        if self.handtype in [1, 2, 3, 4, 8]:  # Only compare highcard if type is less than five cards
            return [self.handtype, self.highest_card] == [other.handtype, other.highest_card]
        else:
            return self.handtype == other.handtype

    def __str__(self):
        return f"Pokerhand type: {self.handtype.name} with cards: {self.cards}".replace("Card", "")


