import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog,qApp
from PyQt5.QtGui import QIcon
import os

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 file dialogs - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        # self.initUI()
        self.openFileNamesDialog()
        # self.loadFiles()
        # self.quit()
        # self.exit()
        sys.exit()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        # self.openFileNameDialog()
        self.openFileNamesDialog()
        # self.saveFileDialog()
        # self.show_file_dialog()
        self.show()

    # def show_file_dialog(self):
    #     selected_dir = QFileDialog.getExistingDirectory(self, caption='Choose Directory', directory=os.getcwd())
    #     self.lineEdit_save_location.setText(selected_dir) 

    # def openFileNameDialog(self):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.DontUseNativeDialog
    #     fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
    #     if fileName:
    #         print(fileName)
    # def loadFiles(self):
    #     filter = "All Files (*)"
    #     file_name = QFileDialog()
    #     file_name.setFileMode(QFileDialog.ExistingFiles)
    #     names = file_name.getOpenFileNames(self, "Open files", "C\\Desktop", filter)
    #     print(names[0])

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        # files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)
    
    # def saveFileDialog(self):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.DontUseNativeDialog
    #     fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
    #     if fileName:
    #         print(fileName)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())