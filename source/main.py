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

        # Add the stylesheet for the QTreeView header
        self.treeView.setStyleSheet("""
        QHeaderView::section {
            background-color: rgb(48, 52, 65);
            color: rgb(206, 253, 255);
            font-weight: bold;
        }
        """)

    def open_folder_dialog(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.model.clear()
            self.model.setHorizontalHeaderLabels(['Name', 'Path'])
            self.search_old_folders(folder_path)

    def search_old_folders(self, folder_path):
        for root, dirs, _ in os.walk(folder_path):
            if "old" in dirs:
                old_folder_path = os.path.join(root, "old")
                parent_item = CheckableStandardItem(os.path.basename(root))
                child_item = QtGui.QStandardItem(old_folder_path)
                parent_item.appendRow([CheckableStandardItem("old"), child_item])
                self.model.appendRow([parent_item, child_item])

    def delete_checked_folders(self):
        indexes = []
        for row in range(self.model.rowCount()):
            parent_item = self.model.item(row, 0)
            for sub_row in range(parent_item.rowCount()):
                child_item = parent_item.child(sub_row, 0)
                if child_item.checkState() == QtCore.Qt.Checked:
                    folder_path = parent_item.child(sub_row, 1).text()
                    try:
                        shutil.rmtree(folder_path)  # フォルダとその中身を再帰的に削除
                        indexes.append((row, sub_row))
                    except Exception as e:
                        QtWidgets.QMessageBox.warning(self, "Error", f"Could not delete '{folder_path}'. Error: {str(e)}")
        
        # Remove checked items from the model
        for row, sub_row in reversed(indexes):
            parent_item = self.model.item(row, 0)
            parent_item.removeRow(sub_row)
            if parent_item.rowCount() == 0:
                self.model.removeRow(row)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
