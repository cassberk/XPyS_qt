import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QHBoxLayout

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        button1 = QPushButton("Button1", self)
        button1.setObjectName("Button1")
        button2 = QPushButton("Button2", self)
        button2.setObjectName("Button2")

        layout = QHBoxLayout()
        layout.addWidget(button1)
        layout.addWidget(button2)
        self.setLayout(layout)

        self.setWindowTitle("MainWindow Demo")
        self.resize(800, 600)

        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.pyqtSlot()
    def on_Button3_clicked(self):
        print("Button1 is clicked")

    @QtCore.pyqtSlot()
    def on_Button2_clicked(self):
        print("Button2 is clicked")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())