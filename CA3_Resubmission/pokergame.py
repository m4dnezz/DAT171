from pokerview import *
import sys

"""Main file that runs the game (initializes the GUI, logic and carlib library)"""


def main():
    qt_app = QApplication(sys.argv)
    model = Poker(["Niclas", "Maithri"], 100)
    w = MainWindow(model)
    w.show()
    qt_app.exec_()


if __name__ == "__main__":
    main()
