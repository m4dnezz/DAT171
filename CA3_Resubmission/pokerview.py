from PyQt5.QtSvg import *
from pokermodel import *


class ActionSection(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model

        # Main buttons
        self.fold = QPushButton("Fold")
        self.call = QPushButton("Call")
        self.raise_bet = QPushButton("Raise")
        self.bet_amount = QSpinBox()
        self.bet_amount.setMinimum(10)
        self.bet_amount.setMaximum(100)
        self.bet_amount.setSingleStep(5)
        self.bet_amount.setSuffix("£")
        self.check = QPushButton("Check")

        hbox = QHBoxLayout()
        hbox.addWidget(self.raise_bet)
        hbox.addWidget(self.bet_amount)

        vbox = QVBoxLayout()
        vbox.addWidget(self.fold)
        vbox.addWidget(self.call)
        vbox.addWidget(self.check)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        def call():
            model.call()

        def raise_event():
            model.raise_bet(self.bet_amount.value())

        def fold_event():
            model.fold()

        def check_event():
            model.check()

        # Controller
        self.fold.clicked.connect(fold_event)
        self.call.clicked.connect(call)
        self.check.clicked.connect(check_event)
        self.raise_bet.clicked.connect(raise_event)

        self.last_bet()

        self.model.last_bet_changed.connect(self.last_bet)

    def last_bet(self):
        self.call.setText("Call:" + str(self.model.last_bet) + "£")


class PotView(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.pot = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.pot)
        self.setLayout(layout)

        self.update()

        self.model.pot_changed.connect(self.update)

    def update(self):
        self.pot.setText(("Current Pot: " + str(self.model.get_pot()) + "£"))


class ActivePlayer(QWidget):
    def __init__(self, model):
        super().__init__()

        self.model = model
        self.active_player_name = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.active_player_name)
        self.setLayout(layout)

        self.player_update()

        self.model.new_active_player.connect(self.player_update)

    def player_update(self):
        self.active_player_name.setText("Active player: " + self.model.players[self.model.active_player].get_name())


class PlayerView(QWidget):  # Almost finished
    def __init__(self, model, player):
        super().__init__()
        self.model = model
        self.player_name = QLabel()
        self.player_credit = QLabel()
        self.player = player

        layout = QVBoxLayout()
        layout.addWidget(self.player_name)
        layout.addWidget(self.player_credit)
        self.setLayout(layout)

        self.player_update()

        self.model.player_credit_changed.connect(self.player_update)

    def player_update(self):
        self.player_name.setText(self.model.players[self.player].get_name())
        self.player_credit.setText(self.model.players[self.player].get_credit() + "£")  #

##################################
##################################


class TableScene(QGraphicsScene):
    """ A scene with a table cloth background """
    def __init__(self):
        super().__init__()
        self.tile = QPixmap('cards/table.png')
        self.setBackgroundBrush(QBrush(self.tile))


class CardItem(QGraphicsSvgItem):
    """ A simple overloaded QGraphicsSvgItem that also stores the card position """
    def __init__(self, renderer, position):
        super().__init__()
        self.setSharedRenderer(renderer)
        self.position = position


def read_cards():
    """
    Reads all the 52 cards from files.
    :return: Dictionary of SVG renderers
    """
    suit_name = ["Hearts", "Spades", "Clubs", "Diamonds"]
    all_cards = dict()  # Dictionaries let us have convenient mappings between cards and their images

    for suit in suit_name:
        for value_file, value in zip(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'], range(2, 15)):
            file = value_file + suit[0]
            key = (value, suit)  # I'm choosing this tuple to be the key for this dictionary
            all_cards[key] = QSvgRenderer('cards/' + file + '.svg')
    return all_cards


class CardView(QGraphicsView):
    """ A View widget that represents the table area displaying a players cards. """
    # We read all the card graphics as static class variables
    back_card = QSvgRenderer('cards/Red_Back_2.svg')

    all_cards = read_cards()

    def __init__(self, card_model: CardModel, card_spacing: int = 230, padding: int = 10):
        """
        Initializes the view to display the content of the given model
        :param card_model: A model that represents a set of cards. Needs to support the CardModel interface.
        :param card_spacing: Spacing between the visualized cards.
        :param padding: Padding of table area around the visualized cards.
        """
        self.scene = TableScene()
        super().__init__(self.scene)
        self.setStyleSheet("border: transparent;")
        self.card_spacing = card_spacing
        self.padding = padding
        self.model = card_model
        card_model.new_cards.connect(self.change_cards)
        self.change_cards()

    def change_cards(self):
        # Add the cards from scratch
        self.scene.clear()
        for i, card in enumerate(self.model):
            # The ID of the card in the dictionary of images is a tuple with (value, suit), both integers
            graphics_key = (card.get_value(), card.suit.name)

            if self.model.flipped():
                renderer = self.back_card
            else:
                renderer = self.all_cards[graphics_key]

            c = CardItem(renderer, i)

            # Shadow effects are cool!
            shadow = QGraphicsDropShadowEffect(c)
            shadow.setBlurRadius(10.)
            shadow.setOffset(5, 5)
            shadow.setColor(QColor(0, 0, 0, 180))  # Semi-transparent black!
            c.setGraphicsEffect(shadow)

            # Place the cards on the default positions
            c.setPos(c.position * self.card_spacing, 0)
            self.scene.addItem(c)
        self.update_view()

    def update_view(self):
        scale = (self.viewport().height()-2*self.padding)/313
        self.resetTransform()
        self.scale(scale, scale)
        # Put the scene bounding box
        self.setSceneRect(-self.padding//scale, -self.padding//scale,
                          self.viewport().width()//scale, self.viewport().height()//scale)

    def resizeEvent(self, painter):
        # This method is called when the window is resized.
        # If the widget is resize, we got to adjust the card sizes.
        # QGraphicsView automatically re-paints everything when we modify the scene.
        self.update_view()
        super().resizeEvent(painter)

################################
################################


class MainWindow(QWidget):
    def __init__(self, model):
        super().__init__()

        self.model = model
        actionview = ActionSection(self.model)
        activeplayerview = ActivePlayer(self.model)
        playerview1 = PlayerView(self.model, 0)
        playerview2 = PlayerView(self.model, 1)
        potview = PotView(self.model)
        table_cards_view = CardView(self.model.table_cards, card_spacing=150)
        player_one_cards = CardView(self.model.players[0].hand)
        player_two_cards = CardView(self.model.players[1].hand)

        top_layout = QHBoxLayout()
        top_layout.addWidget(table_cards_view)
        top_layout.addWidget(potview)

        middle_layout = QHBoxLayout()
        middle_layout.addWidget(activeplayerview)
        middle_layout.addWidget(actionview)

        bottom_layout = QHBoxLayout()
        player_one_layout = QVBoxLayout()
        player_one_layout.addWidget(player_one_cards)
        player_one_layout.addWidget(playerview1)
        player_two_layout = QVBoxLayout()
        player_two_layout.addWidget(player_two_cards)
        player_two_layout.addWidget(playerview2)

        bottom_layout.addLayout(player_one_layout)
        bottom_layout.addLayout(player_two_layout)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(middle_layout)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)
        self.setWindowTitle("Texas Hold 'em")
        self.setGeometry(500, 50, 1000, 900)

        self.model.alert.connect(self.message_box)
        self.model.game_over.connect(self.game_over)

    def message_box(self, text):
        box = QMessageBox()
        box.setText(text)
        box.setWindowTitle("Game Message")
        box.exec_()

    def game_over(self):
        box = QMessageBox()
        box.setText("Game is over, a player lost all money!")
        box.setWindowTitle("GAME OVER")
        box.exec_()
