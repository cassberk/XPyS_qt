# """Dynamically Build tree"""
# import sip
# sip.setapi('QVariant', 1)

# from PyQt4 import QtGui, QtCore

# class Window(QtGui.QTreeWidget):
#     def __init__(self):
#         QtGui.QTreeWidget.__init__(self)
#         self.setHeaderHidden(True)
#         self.itemExpanded.connect(self.handleExpanded)
#         self.itemClicked.connect(self.handleClicked)
#         self.handleExpanded(self.invisibleRootItem())

#     def depth(self, item):
#         depth = 0
#         while item is not None:
#             item = item.parent()
#             depth += 1
#         return depth

#     def requestData(self):
#         for title in 'One Two Three Four Five'.split():
#             yield title, 'additional data'

#     def addItems(self, parent):
#         depth = self.depth(parent)
#         for title, data in self.requestData():
#             item = QtGui.QTreeWidgetItem(parent, [title])
#             item.setData(0, QtCore.Qt.UserRole, data)
#             if depth < 3:
#                 item.setChildIndicatorPolicy(
#                     QtGui.QTreeWidgetItem.ShowIndicator)

#     def handleExpanded(self, item):
#         if item is not None and not item.childCount():
#             self.addItems(item)

#     def handleClicked(self, item, column):
#         print(item.data(column, QtCore.Qt.UserRole).toPyObject())

# if __name__ == '__main__':

#     import sys
#     app = QtGui.QApplication(sys.argv)
#     window = Window()
#     window.show()
#     sys.exit(app.exec_())




# from PyQt5 import QtCore, QtGui, QtWidgets


# class Widget(QtWidgets.QWidget):
#     def __init__(self, parent=None):
#         super(Widget, self).__init__(parent)
#         lay = QtWidgets.QVBoxLayout(self)
#         tree = QtWidgets.QTreeWidget()
#         tree.setColumnCount(2)
#         lay.addWidget(tree)

#         for i in range(4):
#             parent_it = QtWidgets.QTreeWidgetItem(["{}-{}".format(i, l) for l in range(2)])
#             tree.addTopLevelItem(parent_it)
#             for j in range(5):
#                 it = QtWidgets.QTreeWidgetItem(["{}-{}-{}".format(i, j, l) for l in range(2)])
#                 parent_it.addChild(it)
#         tree.expandAll()

#         tree.itemClicked.connect(self.onItemClicked)

#     @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
#     def onItemClicked(self, it, col):
#         print(it, col, it.text(col))


# if __name__ == '__main__':
#     import sys

#     app = QtWidgets.QApplication(sys.argv)
#     w = Widget()
#     w.show()
#     sys.exit(app.exec_())
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
# from PyQt5.Qt import Qt
# import sys
# class Window(QWidget):
#     def __init__(self):
#         QWidget.__init__(self)
#         self.tree = QTreeWidget(self)

#         #  parent = QTreeWidgetItem(self.tree, ['rigname1'])
#         #  parent.setCheckState(0, Qt.Unchecked)

#         #  QTreeWidgetItem(parent, ['light01'])
#         #  parent = QTreeWidgetItem(parent, ['light02'])

#         #  QTreeWidgetItem(parent, ['object02'])
#         #  self.tree.expandAll()
#         #  self.button = QPushButton('Print', self)
#         #  self.button.clicked.connect(self.handleButton)

#         #  layout = QVBoxLayout(self)
#         #  layout.addWidget(self.tree)
#         #  layout.addWidget(self.button)

#         for i in range(3):
#             parent = QTreeWidgetItem(self.tree)
#             parent.setText(0, "Parent {}".format(i))
#             parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
#             for x in range(5):
#                 child = QTreeWidgetItem(parent)
#                 child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
#                 child.setText(0, "Child {}".format(x))
#                 child.setCheckState(0, Qt.Unchecked)
#         self.tree.show() 
#         self.button = QPushButton('Print', self)
#         # self.button.clicked.connect(self.handleButton)
#         self.button.clicked.connect(self.vrfs_selected)

#         layout = QVBoxLayout(self)
#         layout.addWidget(self.tree)
#         layout.addWidget(self.button)


#     def vrfs_selected(self):
#         iterator = QTreeWidgetItemIterator(self.tree, QTreeWidgetItemIterator.Checked)
#         while iterator.value():
#             print(iterator.value())
#             item = iterator.value()
#             print (item.text(0))    
#             iterator += 1

#     def handleButton(self):
#          iterator = QTreeWidgetItemIterator(self.tree)
#          while iterator.value():
#              item = iterator.value()
#              print(item.text(0))
#              iterator += 1

# if __name__ == '__main__':

#      import sys
#      app = QApplication(sys.argv)
#      window = Window()
#      window.resize(300, 200)
#      window.show()
#      sys.exit(app.exec_())


# from PyQt5 import QtWidgets
# from PyQt5 import QtCore
# from PyQt5 import QtGui
# from PyQt5.Qt import Qt
# import sys

# def main(): 
#     app     = QtWidgets.QApplication(sys.argv)
#     tree    = QtWidgets.QTreeWidget()
#     headerItem  = QtWidgets.QTreeWidgetItem()
#     item    = QtWidgets.QTreeWidgetItem()

#     for i in range(3):
#         parent = QtWidgets.QTreeWidgetItem(tree)
#         parent.setText(0, "Parent {}".format(i))
#         parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
#         for x in range(5):
#             child = QtWidgets.QTreeWidgetItem(parent)
#             child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
#             child.setText(0, "Child {}".format(x))
#             child.setCheckState(0, Qt.Unchecked)
#     tree.show() 
#     sys.exit(app.exec_())

# def vrfs_selected(self):
#     iterator = QtGui.QTreeWidgetItemIterator(self.tree, QtGui.QTreeWidgetItemIterator.Checked)
#     while iterator.value():
#         item = iterator.value()
#         print (item.text(0))    
#         iterator += 1
        
# if __name__ == '__main__':
#     main()



# def vrfs_selected(self):
#     iterator = QtGui.QTreeWidgetItemIterator(self.tree, QtGui.QTreeWidgetItemIterator.Checked)
#     while iterator.value():
#         item = iterator.value()
#         print (item.text(0))    
#         iterator += 1


# def main():
#     app = QApplication(sys.argv)
#     form = AppForm()
#     form.show()
#     app.exec_()

# def main(): 
#     app = QApplication (sys.argv)
#     form = treewin()
#     form.show()
#     app.exec_()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     clock = treewin()
#     clock.show()
#     app.exec_()
#     sys.exit(app.exec_())
"""
MEthod 4 QTreeView for Model
"""
import sys
from collections import deque
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
class view(QWidget):
    def __init__(self, data):
        super(view, self).__init__()
        
        self.tree = QTreeView(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Name', 'Height', 'Weight'])
        self.tree.header().setDefaultSectionSize(180)
        self.tree.setModel(self.model)
        self.importData(data)
        self.tree.expandAll()


    def importData(self, data, root=None):
        self.model.setRowCount(0)
        if root is None:
            root = self.model.invisibleRootItem()
        seen = {}   # List of  QStandardItem
        values = deque(data)
        while values:
            value = values.popleft()
            if value['unique_id'] == 1:
                parent = root
            else:
                pid = value['parent_id']
                if pid not in seen:
                    values.append(value)
                    continue
                parent = seen[pid]
            unique_id = value['unique_id']
            parent.appendRow([
                QStandardItem(value['short_name']),
                QStandardItem(value['height']),
                QStandardItem(value['weight'])
            ])
            seen[unique_id] = parent.child(parent.rowCount() - 1)
if __name__ == '__main__':
    data = [
        {'unique_id': 1, 'parent_id': 0, 'short_name': '', 'height': ' ', 'weight': ' '},
        {'unique_id': 2, 'parent_id': 1, 'short_name': 'Class 1', 'height': ' ', 'weight': ' '},
        {'unique_id': 3, 'parent_id': 2, 'short_name': 'Lucy', 'height': '162', 'weight': '50'},
        {'unique_id': 4, 'parent_id': 2, 'short_name': 'Joe', 'height': '175', 'weight': '65'},
        {'unique_id': 5, 'parent_id': 1, 'short_name': 'Class 2', 'height': ' ', 'weight': ' '},
        {'unique_id': 6, 'parent_id': 5, 'short_name': 'Lily', 'height': '170', 'weight': '55'},
        {'unique_id': 7, 'parent_id': 5, 'short_name': 'Tom', 'height': '180', 'weight': '75'},
        {'unique_id': 8, 'parent_id': 1, 'short_name': 'Class 3', 'height': ' ', 'weight': ' '},
        {'unique_id': 9, 'parent_id': 8, 'short_name': 'Jack', 'height': '178', 'weight': '80'},
        {'unique_id': 10, 'parent_id': 8, 'short_name': 'Tim', 'height': '172', 'weight': '60'}
    ]
    app = QApplication(sys.argv)
    view = view(data)
    view.setGeometry(300, 100, 600, 300)
    view.setWindowTitle('QTreeview Example')
    view.show()
    sys.exit(app.exec_())
    
"""
Method 2
"""
# import sys
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *

# data = [
#     ("Sample1", [
#         ("spectra1", []),
#         ("spectra2", [
#             ("Cellphone", [])
#             ])
#         ]),
#     ("Bob", [
#         ("Wallet", [
#             ("Credit card", []),
#             ("Money", [])
#             ])
#         ])
#     ]

# class Window(QWidget):

#     def __init__(self):
    
#         QWidget.__init__(self)
        
#         self.treeView = QTreeView()
#         self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
#         self.treeView.customContextMenuRequested.connect(self.openMenu)
        
#         self.model = QStandardItemModel()
#         self.addItems(self.model, data)
#         self.treeView.setModel(self.model)
        
#         self.model.setHorizontalHeaderLabels([self.tr("Object")])
        
#         layout = QVBoxLayout()
#         layout.addWidget(self.treeView)
#         self.setLayout(layout)
    
#     def addItems(self, parent, elements):
    
#         for text, children in elements:
#             item = QStandardItem(text)
#             parent.appendRow(item)
#             if children:
#                 self.addItems(item, children)
    
#     def openMenu(self, position):
    
#         indexes = self.treeView.selectedIndexes()
#         if len(indexes) > 0:
        
#             level = 0
#             index = indexes[0]
#             while index.parent().isValid():
#                 index = index.parent()
#                 level += 1
        
#         menu = QMenu()
#         if level == 0:
#             print('ere')
#             menu.addAction(self.tr("Edit person"))
#         elif level == 1:
#             menu.addAction(self.tr("Edit object/container"))
#         elif level == 2:
#             menu.addAction(self.tr("Edit object"))
        
#         menu.exec_(self.treeView.viewport().mapToGlobal(position))


# if __name__ == "__main__":

#     app = QApplication(sys.argv)
#     window = Window()
#     window.show()
#     sys.exit(app.exec_())
    

"""
Method 1 
"""
    # import sys
# from collections import deque
# from PyQt5 import QtCore, QtGui, QtWidgets

# class Window(QtWidgets.QWidget):
#     def __init__(self, data):
#         super(Window, self).__init__()
#         self.tree = QtWidgets.QTreeView(self)
#         layout = QtWidgets.QVBoxLayout(self)
#         layout.addWidget(self.tree)
#         self.model = QtGui.QStandardItemModel()
#         self.model.setHorizontalHeaderLabels(['Name', 'dbID'])
#         self.tree.header().setDefaultSectionSize(180)
#         self.tree.setModel(self.model)
#         self.importData(data)
#         self.tree.expandAll()

#     def importData(self, data, root=None):
#         self.model.setRowCount(0)
#         if root is None:
#             root = self.model.invisibleRootItem()
#         seen = {}
#         values = deque(data)
#         while values:
#             value = values.popleft()
#             if value['level'] == 0:
#                 parent = root
#             else:
#                 pid = value['parent_ID']
#                 if pid not in seen:
#                     values.append(value)
#                     continue
#                 parent = seen[pid]
#             dbid = value['dbID']
#             parent.appendRow([
#                 QtGui.QStandardItem(value['short_name']),
#                 QtGui.QStandardItem(str(dbid)),
#                 ])
#             seen[dbid] = parent.child(parent.rowCount() - 1)

# if __name__ == '__main__':

#     data = [
#         {'level': 0, 'dbID': 77, 'parent_ID': 6, 'short_name': '0:0:0:<new> to 6', 'long_name': '', 'order': 1, 'pos': 0} ,
#         {'level': 1, 'dbID': 88, 'parent_ID': 77, 'short_name': '1:1:1:Store13', 'long_name': '', 'order': 2, 'pos': 1} ,
#         {'level': 0, 'dbID': 442, 'parent_ID': 6, 'short_name': '2:<new>', 'long_name': '', 'order': 1, 'pos': 2} ,
#         {'level': 1, 'dbID': 522, 'parent_ID': 442, 'short_name': '3:<new>', 'long_name': '', 'order': 2, 'pos': 3} ,
#         {'level': 2, 'dbID': 171, 'parent_ID': 522, 'short_name': '3:<new>', 'long_name': '', 'order': 1, 'pos': 3} ,
#         {'level': 0, 'dbID': 456, 'parent_ID': 6, 'short_name': '4:<new>', 'long_name': '', 'order': 1, 'pos': 4} ,
#         {'level': 1, 'dbID': 523, 'parent_ID': 456, 'short_name': '5:<new>', 'long_name': '', 'order': 3, 'pos': 5}
#         ]

#     app = QtWidgets.QApplication(sys.argv)
#     window = Window(data)
#     window.setGeometry(600, 50, 400, 250)
#     window.show()
#     sys.exit(app.exec_())