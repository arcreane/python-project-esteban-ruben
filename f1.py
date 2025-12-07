from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys

app = QApplication(sys.argv)

loader = QUiLoader()
file = QFile("mainwindow (1).ui")
file.open(QFile.ReadOnly)

window = loader.load(file)
window.show()

sys.exit(app.exec())

