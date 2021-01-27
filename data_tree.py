
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.Qt import Qt
import sys

class DataTreeHandler(QWidget):
    def __init__(self,treeparent = None, treechildren = None):
        QWidget.__init__(self)
        self.treeparent = treeparent
        self.children = treechildren
        self.tree = QTreeWidget(self)
        self.tree.itemChanged[QTreeWidgetItem, int].connect(self.vrfs_selected)
        self.iter = 0
        self.add_tree()        
              
        self.tree.show() 

        self.adtreebutton = QPushButton('addtree', self)
        self.adtreebutton.clicked.connect(self.add_tree)

        self.button = QPushButton('Print', self)
        self.button.clicked.connect(self.vrfs_selected)

        self.clearbutton = QPushButton('cleartree', self)
        self.clearbutton.clicked.connect(self.cleartree)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        layout.addWidget(self.adtreebutton)
        layout.addWidget(self.button)
        layout.addWidget(self.clearbutton)


    def add_tree(self):
        i=self.iter
        parent = QTreeWidgetItem(self.tree)
        # parent.setText(0, "Parent {}".format(i))
        parent.setText(0,self.treeparent)

        parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

        for ch in self.children:
            child1 = QTreeWidgetItem(parent)
            child1.setFlags(child1.flags() | Qt.ItemIsUserCheckable)
            child1.setText(0, ch)
            child1.setCheckState(0, Qt.Unchecked)
            # for x in range(5):
            #     child2 = QTreeWidgetItem(child1)
            #     child2.setFlags(child2.flags() | Qt.ItemIsUserCheckable)
            #     child2.setText(0, "Child {}".format(x))
            #     child2.setCheckState(0, Qt.Unchecked)

#         for i in range(3):
#             parent = QTreeWidgetItem(self.tree)
#             parent.setText(0, "Parent {}".format(i))
#             parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
#             for x in range(5):
#                 child = QTreeWidgetItem(parent)
#                 child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
#                 child.setText(0, "Child {}".format(x))
#                 child.setCheckState(0, Qt.Unchecked)

        self.iter +=1

    def vrfs_selected(self):
        iterlist = []
        iterator = QTreeWidgetItemIterator(self.tree, QTreeWidgetItemIterator.Checked)
        while iterator.value():
            item = iterator.value()
            if item.text(0) not in self.treeparent:
                iterlist.append(item.text(0))    
            iterator += 1
        self.updatelist =  iterlist



    def handleButton(self):
         iterator = QTreeWidgetItemIterator(self.tree)
         while iterator.value():
             item = iterator.value()
             print(item.text(0))
             iterator += 1

    # def cleartreechild(self):
    #     self.vrfs_selected()
    #     tree.takeTopLevelItem(tree.indexOfTopLevelItem(i))

    def cleartree(self):
        self.tree.clear()
        self.iter=0


if __name__ == '__main__':

     import sys
     app = QApplication(sys.argv)
     window = DataTreeHandler()
     window.resize(300, 200)
     window.show()
     sys.exit(app.exec_())

