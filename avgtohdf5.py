import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog,qApp, QDialog, QFormLayout, QLabel, QPushButton,QVBoxLayout, QListView
from PyQt5.QtGui import QIcon, QStandardItem,QStandardItemModel
import os
sys.path.append("/Users/cassberk/code/")
import xps_peakfit.avg
import glob
from IPython import embed as shell

class MessageWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self,message):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel(message)
        layout.addWidget(self.label)
        self.setLayout(layout)

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Convert .avg Files to .hdf5'
        self.left = 1000
        self.top = 500
        self.width = 500
        self.height = 500
        self.files = []
        self.initUI()


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.samplename = QLineEdit()
        self.samplename.setObjectName("host")
        self.samplename.setFixedWidth(180)


        self.samplenameLabel = QLabel('Sample Name', self) 

        self.experimentname = QLineEdit()
        self.experimentname.setObjectName("host")
        self.experimentname.setFixedWidth(180)
        self.experimentnameLabel = QLabel('Experiment Name', self) 

        self.fileSelect = QPushButton()
        self.fileSelect.setText("Choose Files")
        self.fileSelect.clicked.connect(self.loadFiles)

        self.folderSelect = QPushButton()
        self.folderSelect.setText("Choose Folder")
        self.folderSelect.clicked.connect(self.loadFolder)

        self.convertButton = QPushButton()
        self.convertButton.setText("Convert")
        self.convertButton.clicked.connect(self.convert)

        self.clearButton = QPushButton()
        self.clearButton.setText("clear")
        self.clearButton.clicked.connect(self.clearList)

        self.listView = QListView()
        self.listView.setFixedWidth(480)
        self.model = QStandardItemModel()
        self.listView.setModel(self.model)
        self.listLabel = QLabel('Files to Convert', self) 


        layout = QFormLayout()
        layout.addWidget(self.samplenameLabel)
        layout.addWidget(self.samplename)
        layout.addWidget(self.experimentnameLabel)
        layout.addWidget(self.experimentname)
        layout.addWidget(self.fileSelect)
        layout.addWidget(self.folderSelect)
        layout.addWidget(self.listLabel)
        layout.addWidget(self.listView)
        layout.addWidget(self.clearButton)
        layout.addWidget(self.convertButton)
        self.setLayout(layout)

        self.show()


    def clearList(self):
        self.files = []
        self.model.clear()

    def loadFiles(self):
        filter = "All Files (*)"
        file_name = QFileDialog()
        file_name.setFileMode(QFileDialog.ExistingFiles)
        _files,_ = file_name.getOpenFileNames(self, "All Files (*)", "C\\Desktop", filter)
        for i in _files:
            self.files.append(i)
            item = QStandardItem(i)
            self.model.appendRow(item)

    def loadFolder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        _folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        for i in glob.glob(_folder+'/*'):
            self.files.append(i)
            item = QStandardItem(i)
            self.model.appendRow(item)

    def convert(self):
        if self.samplename.text() =='':
            self.error = MessageWindow(message = 'You must name the Sample')
            self.error.show()
            return
        elif self.experimentname.text() =='':
            self.error = MessageWindow(message = 'You must name the Experiment')
            self.error.show()
            return

        else:
            xps_peakfit.avg.avg_to_hdf5(sample_name = self.samplename.text(),experiment_name = self.experimentname.text(),filepath = self.files,force = True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())