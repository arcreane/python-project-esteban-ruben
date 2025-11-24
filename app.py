from PySide6.QtWidgets import QApplication
from ControleurAerienApp import ControleurAerienApp
import sys

UI_FILE_NAME = "mainwindow (1).ui"

if __name__ == '__main__':
    app = QApplication(sys.argv)

    fenetre_principale = ControleurAerienApp(UI_FILE_NAME)
    fenetre_principale.show()

    if fenetre_principale.avions:
        fenetre_principale.selectionner_avion(fenetre_principale.avions[0].identifiant)

    sys.exit(app.exec())