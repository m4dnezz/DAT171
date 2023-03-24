from enum import Enum
import pytest
from cardlib import *

# This test assumes you call your suit class "Suit" and the suits "Hearts and "Spades"
def test_cards():

    h5 = NumberedCard(5, Suit.Hearts)
    assert isinstance(h5.suit, Enum)
    assert issubclass(NumberedCard, PlayingCard)
    assert isinstance(h5, PlayingCard)
    assert h5 == h5
    assert h5.get_value() != 4

    sk = KingCard(Suit.Spades)
    assert sk.get_value() == 13
    assert isinstance(sk.suit, Enum)
    assert issubclass(KingCard, PlayingCard)
    assert isinstance(sk, PlayingCard)
    assert sk == sk
    assert sk.get_value() != 8

    ace = AceCard(Suit.Diamonds)
    assert ace.get_value() == 14
    assert isinstance(ace.suit, Enum)
    assert issubclass(AceCard, PlayingCard)
    assert isinstance(ace, PlayingCard)
    assert ace == ace
    assert ace.get_value() != 13

    assert h5 < sk
    assert sk > h5
    assert sk < ace
    assert h5 < ace

    with pytest.raises(TypeError):
        pc = PlayingCard(Suit.Clubs)

    with pytest.raises(TypeError):
        jack = JackCard(8, Suit.Hearts)


# This test assumes you call your shuffle method "shuffle" and the method to draw a card "draw"
def test_deck():
    d = StandardDeck()
    c1 = d.draw()
    c2 = d.draw()
    assert not c1 == c2
    assert isinstance(d, StandardDeck)
    assert len(d.deck) == 50

    d2 = StandardDeck()
    d2.shuffle()
    c3 = d2.draw()
    c4 = d2.draw()
    assert not ((c3, c4) == (c1, c2))
    assert isinstance(d2, StandardDeck)
    assert len(d2.deck) == 50


# This test builds on the assumptions above and assumes you store the cards in the hand in the list "cards",
# and that your sorting method is called "sort" and sorts in increasing order
def test_hand():
    h = Hand()
    assert len(h.cards) == 0
    d = StandardDeck()
    d.shuffle()
    h.add_card(d.draw())
    h.add_card(d.draw())
    h.add_card(d.draw())
    h.add_card(d.draw())
    h.add_card(d.draw())
    assert len(h.cards) == 5

    h.sort()
    for i in range(4):
        assert h.cards[i] < h.cards[i + 1] or h.cards[i] == h.cards[i + 1]

    cards = h.cards.copy()
    h.drop_cards([4, 0, 1])

    assert len(h.cards) == 2
    assert h.cards[0] == cards[2]
    assert h.cards[1] == cards[3]

    h2 = Hand()
    d2 = StandardDeck()
    d2.shuffle()
    h2.add_card(d2.draw())
    h2.add_card(d2.draw())
    h2.add_card(d2.draw())
    h2.add_card(d2.draw())
    h2.add_card(d2.draw())
    h2.drop_cards([3, 4, 1])
    assert len(h.cards) == 2

    comb_1 = [NumberedCard(2, Suit.Hearts), NumberedCard(4, Suit.Diamonds), NumberedCard(2, Suit.Spades),
              NumberedCard(10, Suit.Clubs), NumberedCard(9, Suit.Hearts)]

    comb_2 = [NumberedCard(2, Suit.Spades), NumberedCard(3, Suit.Spades), NumberedCard(4, Suit.Spades),
              NumberedCard(5, Suit.Hearts), NumberedCard(6, Suit.Hearts)]

    assert PokerHand.fullhouse(comb_1) is False
    assert PokerHand.onepair(comb_1) is not False

    assert PokerHand.threeofakind(comb_2) is False
    assert PokerHand.straight(comb_2) is not False


# This test builds on the assumptions above. Add your type and data for the commented out tests
# and uncomment them!
def test_pokerhands():
    h1 = Hand()
    h1.add_card(QueenCard(Suit.Diamonds))
    h1.add_card(KingCard(Suit.Hearts))

    h2 = Hand()
    h2.add_card(QueenCard(Suit.Hearts))
    h2.add_card(AceCard(Suit.Hearts))

    h3 = Hand()
    h3.add_card(NumberedCard(10, Suit.Hearts))
    h3.add_card(AceCard(Suit.Hearts))

    cl = [NumberedCard(10, Suit.Diamonds), NumberedCard(9, Suit.Diamonds),
          NumberedCard(8, Suit.Clubs), NumberedCard(6, Suit.Spades)]

    ph1 = h1.best_poker_hand(cl)
    ph2 = h2.best_poker_hand(cl)
    phx = h3.best_poker_hand(cl)

    assert isinstance(ph1, PokerHand)
    assert isinstance(ph2, PokerHand)
    assert isinstance(phx, PokerHand)

    # assert # Check ph1 handtype class and data here>
    assert ph1.handtype == HandValue.high_card

    # assert # Check ph2 handtype class and data here>
    assert ph2.handtype == HandValue.high_card

    # assert # Check ph3 handtype class and data here>
    assert phx.handtype == HandValue.one_pair

    assert ph1 < ph2
    assert ph2 < phx

    cl.pop(0)
    cl.append(QueenCard(Suit.Spades))
    ph3 = h1.best_poker_hand(cl)
    ph4 = h2.best_poker_hand(cl)
    assert ph3 < ph4
    assert ph1 < ph2

    # assert # Check ph3 handtype class and data here>
    assert ph3.handtype == HandValue.one_pair

    # assert # Check ph4 handtype class and data here>
    assert ph4.handtype == HandValue.one_pair

    cl = [NumberedCard(4, Suit.Clubs), JackCard(Suit.Spades), KingCard(Suit.Clubs), KingCard(Suit.Spades)]
    ph5 = h1.best_poker_hand(cl)


    # assert # Check ph5 handtype class and data here>
    assert ph5.handtype == HandValue.three_of_a_kind
    assert ph5.handtype != HandValue.straight_flush


empty_hand = Hand()

highcard = [NumberedCard(10, Suit.Diamonds), NumberedCard(9, Suit.Diamonds),
            NumberedCard(8, Suit.Clubs), NumberedCard(6, Suit.Spades)]

assert empty_hand.best_poker_hand(highcard).handtype == HandValue.high_card

onepair = [NumberedCard(10, Suit.Diamonds), NumberedCard(10, Suit.Diamonds),
           NumberedCard(8, Suit.Clubs), NumberedCard(6, Suit.Spades)]

assert empty_hand.best_poker_hand(onepair).handtype == HandValue.one_pair

twopair = [NumberedCard(10, Suit.Diamonds), NumberedCard(10, Suit.Diamonds),
           NumberedCard(6, Suit.Clubs), NumberedCard(6, Suit.Spades)]

tripple_pair = [NumberedCard(10, Suit.Diamonds), NumberedCard(10, Suit.Diamonds), QueenCard(Suit.Clubs),
                NumberedCard(6, Suit.Clubs), NumberedCard(6, Suit.Spades), QueenCard(Suit.Hearts)]

assert empty_hand.best_poker_hand(twopair).handtype == HandValue.two_pair
assert empty_hand.best_poker_hand(tripple_pair).handtype == HandValue.two_pair

three_of_a_kind = [NumberedCard(10, Suit.Diamonds), NumberedCard(6, Suit.Diamonds),
                   NumberedCard(6, Suit.Clubs), NumberedCard(6, Suit.Spades)]

assert empty_hand.best_poker_hand(three_of_a_kind).handtype == HandValue.three_of_a_kind

straight = [NumberedCard(10, Suit.Diamonds), NumberedCard(9, Suit.Diamonds),
            NumberedCard(8, Suit.Clubs), NumberedCard(6, Suit.Spades), NumberedCard(7, Suit.Clubs)]

low_straight = [AceCard(Suit.Diamonds), NumberedCard(2, Suit.Diamonds),
                NumberedCard(3, Suit.Clubs), NumberedCard(4, Suit.Spades), NumberedCard(5, Suit.Clubs)]

stright_seven_cards = [NumberedCard(10, Suit.Diamonds), NumberedCard(9, Suit.Diamonds), NumberedCard(2, Suit.Clubs),
                       NumberedCard(8, Suit.Clubs), NumberedCard(6, Suit.Spades), NumberedCard(7, Suit.Clubs)]

stright_eight_cards = [NumberedCard(10, Suit.Diamonds), NumberedCard(9, Suit.Diamonds), NumberedCard(7, Suit.Clubs),
                       NumberedCard(6, Suit.Clubs), NumberedCard(3, Suit.Spades), NumberedCard(4, Suit.Clubs), JackCard(Suit.Hearts)]

stright_four_cards = [NumberedCard(2, Suit.Diamonds), NumberedCard(3, Suit.Diamonds),
                      NumberedCard(4, Suit.Clubs), NumberedCard(5, Suit.Spades)]

assert empty_hand.best_poker_hand(straight).handtype == HandValue.straight
assert empty_hand.best_poker_hand(low_straight).handtype == HandValue.straight
assert empty_hand.best_poker_hand(stright_seven_cards).handtype == HandValue.straight
assert empty_hand.best_poker_hand(stright_four_cards).handtype != HandValue.straight
assert empty_hand.best_poker_hand(stright_eight_cards).handtype != HandValue.straight

flush = [NumberedCard(10, Suit.Diamonds), NumberedCard(9, Suit.Diamonds),
         NumberedCard(8, Suit.Diamonds), NumberedCard(6, Suit.Diamonds), NumberedCard(10, Suit.Diamonds)]

assert empty_hand.best_poker_hand(flush).handtype == HandValue.flush
assert empty_hand.best_poker_hand(flush).handtype != HandValue.straight_flush

four_of_a_kind = [NumberedCard(10, Suit.Diamonds), NumberedCard(10, Suit.Diamonds),
                  NumberedCard(10, Suit.Clubs), NumberedCard(10, Suit.Spades)]

assert empty_hand.best_poker_hand(four_of_a_kind).handtype == HandValue.four_of_a_kind
assert empty_hand.best_poker_hand(four_of_a_kind).handtype != HandValue.three_of_a_kind

full_house = [NumberedCard(10, Suit.Diamonds), NumberedCard(10, Suit.Diamonds), NumberedCard(8, Suit.Diamonds),
              NumberedCard(5, Suit.Clubs), NumberedCard(5, Suit.Spades), NumberedCard(5, Suit.Hearts)]

assert empty_hand.best_poker_hand(full_house).handtype == HandValue.full_house

straight_flush = [NumberedCard(6, Suit.Diamonds), NumberedCard(9, Suit.Diamonds), AceCard(Suit.Diamonds), QueenCard(Suit.Clubs),
                  NumberedCard(8, Suit.Diamonds), NumberedCard(10, Suit.Diamonds), NumberedCard(7, Suit.Diamonds)]

assert empty_hand.best_poker_hand(straight_flush).handtype == HandValue.straight_flush
assert empty_hand.best_poker_hand(straight_flush).handtype != HandValue.flush

# Testing errors from previous hand-in
test = [QueenCard(Suit.Hearts), KingCard(Suit.Hearts), QueenCard(Suit.Spades), NumberedCard(8, Suit.Diamonds),
        NumberedCard(9, Suit.Clubs), NumberedCard(6, Suit.Spades)]

assert empty_hand.best_poker_hand(test).handtype == HandValue.one_pair
assert empty_hand.best_poker_hand(test).handtype != HandValue.full_house

test2 = [QueenCard(Suit.Hearts), AceCard(Suit.Hearts), QueenCard(Suit.Spades), NumberedCard(8, Suit.Diamonds),
         NumberedCard(9, Suit.Clubs), NumberedCard(6, Suit.Spades)]

assert empty_hand.best_poker_hand(test2).handtype == HandValue.one_pair
assert empty_hand.best_poker_hand(test2).handtype != HandValue.full_house

test3 = [QueenCard(Suit.Hearts), AceCard(Suit.Hearts), QueenCard(Suit.Spades), NumberedCard(8, Suit.Diamonds),
         NumberedCard(8, Suit.Clubs), NumberedCard(6, Suit.Spades), NumberedCard(10, Suit.Spades)]

assert empty_hand.best_poker_hand(test3).handtype == HandValue.two_pair


