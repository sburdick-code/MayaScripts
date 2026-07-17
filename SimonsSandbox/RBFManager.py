from PySide2 import QtWidgets, QtCore, QtUiTools, QtGui
from shiboken2 import wrapInstance

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds


def mayaMainWindow():
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mainWindowPtr), QtWidgets.QWidget)


class RBFManager(QtWidgets.QDialog):

    UI_FILE = "Z:\Projects\MayaScripts\SimonsSandbox\RBFManagerWidget.ui"

    FILE_FILTERS = "JSON (*.json)"
    selected_filter = "JSON (*.json)"

    def __init__(self, parent=mayaMainWindow()):
        super().__init__(parent)

        self.setWindowTitle("RBF Manager Tool")
        self.setMinimumSize(550, 480)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.initUI()
        self.createConnections()

    def initUI(self):
        f = QtCore.QFile(self.UI_FILE)
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.ui)

        f.close()

    def createConnections(self):

        self.createCustomContextMenu()
        self.setupTables()

        self.ui.Driver_LineEdit.textChanged.connect(self.LoadDriver)
        self.ui.AddDriver_Button.clicked.connect(
            lambda: self.UpdateTextToSelection(self.ui.Driver_LineEdit)
        )
        self.ui.Driven_LineEdit.textChanged.connect(self.LoadDriven)
        self.ui.AddDriven_Button.clicked.connect(
            lambda: self.UpdateTextToSelection(self.ui.Driven_LineEdit)
        )

        self.ui.GenerateID_Button.clicked.connect(self.GenerateID)

        self.ui.Browse_Button.clicked.connect(self.showFileSelectDialog)

        self.ui.ToggleUpdates_Button.clicked.connect(self.ToggleUpdatesButton)

    def setupTables(self):

        # Driver Table
        self.Driver_Table_Model = QtGui.QStandardItemModel(0, 3)  # 1 rows, 4 columns
        self.Driver_Table_Model.setHorizontalHeaderLabels(["Input", "X", "Y", "Z"])
        self.ui.Driver_Table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )
        self.ui.Driver_Table.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )

        self.ui.Driver_Table.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.ui.Driver_Table.customContextMenuRequested.connect(
            self.displayDriverContextMenu
        )

        self.ui.Driver_Table.setModel(self.Driver_Table_Model)

        # Driven Table
        self.Driven_Table_Model = QtGui.QStandardItemModel(0, 3)  # 1 rows, 4 columns
        self.Driven_Table_Model.setHorizontalHeaderLabels(["Input", "X", "Y", "Z"])
        self.ui.Driven_Table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )
        self.ui.Driven_Table.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )

        self.ui.Driven_Table.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.ui.Driven_Table.customContextMenuRequested.connect(
            self.displayDrivenContextMenu
        )

        self.ui.Driven_Table.setModel(self.Driven_Table_Model)

        # Debug Setup some default values
        items = ["rotation", "0.0", "0.0", "0.0"]
        self.addToTable(self.Driver_Table_Model, items)

        # Debug Setup some default values
        items = ["translation", "1", "0.2", "3.0"]
        self.addToTable(self.Driven_Table_Model, items)

    def addToTable(self, model, items):

        formatted = []

        for item in items:
            formatted.append(QtGui.QStandardItem(item))

        model.appendRow(formatted)

    def createCustomContextMenu(self):

        self.context_menu = QtWidgets.QMenu(self)
        action1 = self.context_menu.addAction("Action 1")
        action2 = self.context_menu.addAction("Action 2")
        action3 = self.context_menu.addAction("Action 3")

    def displayDriverContextMenu(self, position):
        item = self.ui.Driver_Table.indexAt(position)

        if item:
            print(item.row(), item.data())

        self.context_menu.exec_(self.ui.Driver_Table.mapToGlobal(position))

    def displayDrivenContextMenu(self, position):
        item = self.ui.Driven_Table.indexAt(position)

        if item:
            print(item.row(), item.data())

        self.context_menu.exec_(self.ui.Driven_Table.mapToGlobal(position))

    def doSomething(self):
        print("### TODO ###")

    def UpdateTextToSelection(self, LineEdit):
        print("Button Pressed")
        selected = cmds.ls(selection=True)[0]
        print(selected)
        LineEdit.setText(str(selected))

    def LoadDriver(self):
        print("Load Driver")

    def LoadDriven(self):
        print("Load Driver")

    def GenerateID(self):
        Driver_Text = self.ui.Driver_LineEdit.text()
        Driven_Text = self.ui.Driven_LineEdit.text()
        self.ui.ID_LineEdit.setText(f"{Driver_Text}->{Driven_Text}")

    def ToggleUpdatesButton(self):
        button_name = self.ui.ToggleUpdates_Button.text()

        if button_name == "Freeze Updates":
            new_name = "Un-Freeze Updates"
        else:
            new_name = "Freeze Updates"

        self.ui.ToggleUpdates_Button.setText(new_name)

    def showFileSelectDialog(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select File", "", self.FILE_FILTERS, self.selected_filter
        )
        if file_path:
            self.ui.FilePath_LineEdit.setText(file_path)


if __name__ == "__main__":
    myWidget = RBFManager()
    myWidget.show()
