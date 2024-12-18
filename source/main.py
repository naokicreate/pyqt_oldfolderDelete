# -*- coding: utf-8 -*-
import sys
import os
import shutil
from PyQt5 import QtCore, QtGui, QtWidgets
from ui_files.page01_ui import Ui_MainWindow

class CheckableStandardItem(QtGui.QStandardItem):
    def __init__(self, text=''):
        super().__init__(text)
        self.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.setCheckState(QtCore.Qt.Unchecked)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.model = QtGui.QStandardItemModel()
        self.treeView.setModel(self.model)
        self.pushButton_Search.clicked.connect(self.open_folder_dialog)
        self.pushButton_Delete.clicked.connect(self.delete_checked_folders)
        self.toolButton_Reload.clicked.connect(self.reload_search)

        # Add the stylesheet for the QTreeView header
        self.treeView.setStyleSheet("""
        QHeaderView::section {
            background-color: rgb(48, 52, 65);
            color: rgb(206, 253, 255);
            font-weight: bold;
        }
        """)

        self.current_folder_path = None

    def open_folder_dialog(self):
        search_text = self.lineEdit.text()
        if not search_text:
            QtWidgets.QMessageBox.warning(self, "Error", "Please enter a search term")
            return

        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.current_folder_path = folder_path
            self.search_folder(folder_path, search_text)

    def search_folder(self, folder_path, search_text):
        if os.path.exists(folder_path):
            self.model.clear()
            self.model.setHorizontalHeaderLabels(['Name', 'Path'])
            self.add_items(self.model, folder_path, search_text)
        else:
            QtWidgets.QMessageBox.warning(self, "Error", f"Folder does not exist: {folder_path}")

    def add_items(self, parent, folder_path, search_text):
        for root, dirs, files in os.walk(folder_path):
            for name in dirs + files:
                if search_text.lower() in name.lower():
                    item = CheckableStandardItem(name)
                    item.setData(os.path.join(root, name), QtCore.Qt.UserRole)
                    parent.appendRow([item, QtGui.QStandardItem(os.path.join(root, name))])

    def reload_search(self):
        if self.current_folder_path:
            search_text = self.lineEdit.text()
            if search_text:
                self.search_folder(self.current_folder_path, search_text)
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "検索するフォルダ名を入力してください。")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "No folder selected for reloading search")

    def delete_checked_folders(self):
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item.checkState() == QtCore.Qt.Checked:
                shutil.rmtree(item.data(QtCore.Qt.UserRole))
                self.model.removeRow(row)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
