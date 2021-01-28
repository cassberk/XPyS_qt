from sys import exit as sysExit

from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets import *

class CenterPanel(QWidget):
    def __init__(self, MainWin):
        QWidget.__init__(self)

        CenterPane = QHBoxLayout(self)
        CenterPane.addWidget(QTextEdit())

        self.setLayout(CenterPane)
         
class UI_MainWindow(QMainWindow):
    def __init__(self):
        super(UI_MainWindow, self).__init__()

        self.setCentralWidget(CenterPanel(self))

    def closeEvent(self, event):
         print("Close Test 1")

if __name__ == '__main__':
    MainApp = QApplication([])

    MainGui = UI_MainWindow()
    MainGui.show()

    sysExit(MainApp.exec_())