from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys
from ControleurAerienApp import ControleurAerienApp
app = QApplication(sys.argv)

loader = QUiLoader()
file = QFile("mainwindow (1).ui")

'''window = loader.load(file)
window.show()'''

fenetre_principale = ControleurAerienApp(file)
fenetre_principale.show()

sys.exit(app.exec())
