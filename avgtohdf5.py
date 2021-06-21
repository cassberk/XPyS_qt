import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog,qApp, QDialog, QFormLayout, QLabel, QPushButton,QVBoxLayout, QListView,QMessageBox
from PyQt5.QtGui import QIcon, QStandardItem,QStandardItemModel
import os
sys.path.append("/Users/cassberk/code/")
import XPyS.avg
import glob
import h5py
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

        # self.folderSelect = QPushButton()
        # self.folderSelect.setText("Choose Folder")
        # self.folderSelect.clicked.connect(self.loadFolder)

        self.choosePath = QPushButton()
        self.choosePath.setText("Choose Save Location")
        self.choosePath.clicked.connect(self.chooseSavePath)

        self.savepath = QLineEdit()
        # self.savepath.setObjectName("host")
        self.savepath.setFixedWidth(400)
        self.savepathLabel = QLabel('Save Path', self) 

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
        # layout.addWidget(self.folderSelect)
        layout.addWidget(self.choosePath)
        layout.addWidget(self.savepathLabel)
        layout.addWidget(self.savepath)
        layout.addWidget(self.listLabel)
        layout.addWidget(self.listView)
        layout.addWidget(self.clearButton)
        layout.addWidget(self.convertButton)
        self.setLayout(layout)

        self.show()


    def clearList(self):
        self.files = []
        self.model.clear()

    def chooseSavePath(self):
        filter = "All Files (*)"
        file_name = QFileDialog()
        file_name.setFileMode(QFileDialog.ExistingFiles)
        _files,_ = file_name.getOpenFileNames(self, "All Files (*)", "/Volumes/GoogleDrive/Shared drives/StOQD/sample_library", filter)
        self.savepath.setText(_files[0])
        self.samplename.setText(_files[0].split('/')[-1].split('.')[0])

    def loadFiles(self):
        filter = "All Files (*)"
        file_name = QFileDialog()
        file_name.setFileMode(QFileDialog.ExistingFiles)
        _files,_ = file_name.getOpenFileNames(self, "All Files (*)", "/Volumes/GoogleDrive/Shared drives/StOQD/sample_library", filter)
        for i in _files:
            self.files.append(i)
            item = QStandardItem(i)
            self.model.appendRow(item)

    # def loadFolder(self):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.DontUseNativeDialog
    #     _folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

    #     for i in glob.glob(_folder+'/*'):
    #         self.files.append(i)
    #         item = QStandardItem(i)
    #         self.model.appendRow(item)

    def convert(self):
        if self.samplename.text() =='':
            self.error = MessageWindow(message = 'You must name the Sample')
            self.error.show()
            return
        elif self.experimentname.text() =='':
            # print(self.savepath.text())
            # print(self.savepath.text()=='')
            self.error = MessageWindow(message = 'You must name the Experiment')
            self.error.show()
            # msg = QMessageBox()
            # msg.setIcon(QMessageBox.Information)
            # msg.setText("This is a message box")
            # msg.show()
            return

        else:
            if self.savepath.text() == '':
                svpth = '/'+os.path.join(os.path.join(*self.files[0].split('/')[0:-1]),self.samplename.text()+'.hdf5')
                print(svpth)
            else:
                svpth = self.savepath.text()

            with h5py.File(svpth,'a') as f:
                current_groups = [grp for grp in f.keys()]
            if any([self.experimentname.text() in group for group in current_groups]):
                choice = QMessageBox.question(self, 'Experiment already present',
                                                "Experiment already present. \n Do you want to overwrite?",
                                                QMessageBox.Yes | QMessageBox.No)
                if choice == QMessageBox.Yes:
                    print("overwriting")
                    XPyS.avg.avg_to_hdf5(sample_name = self.samplename.text(),experiment_name = self.experimentname.text(),avgfiles = self.files,savepath = svpth,force = False)
                else:
                    pass
            else:
                # shell()
                XPyS.avg.avg_to_hdf5(sample_name = self.samplename.text(),experiment_name = self.experimentname.text(),avgfiles = self.files,savepath = svpth,force = False)
               

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())