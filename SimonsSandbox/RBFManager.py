from PySide2 import QtWidgets, QtCore, QtUiTools, QtGui
from shiboken2 import wrapInstance

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds

import os


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
        self.setMinimumSize(400, 480)
        self.resize(400, 480)
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

        print(self.getDataFromTable(self.Driver_Table_Model, 0, 1))
        print(self.verifyValidInputs())

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

        self.ui.Save_Button.clicked.connect(self.onSave)

    def verifyValidInputs(self):

        allInputsValid = True

        driverName = self.ui.Driver_LineEdit.text()
        drivenName = self.ui.Driven_LineEdit.text()

        # Check if there is a valid driver obj
        if not cmds.objExists(driverName):
            allInputsValid = False

        # Check if there is a valid driven obj
        if not cmds.objExists(drivenName):
            allInputsValid = False

        # Check if the first value in each row of each table is valid
        for i in range(self.Driver_Table_Model.rowCount()):
            if self.getDataFromTable(self.Driver_Table_Model, i, 0)[0] == "None":
                allInputsValid = False

        for i in range(self.Driven_Table_Model.rowCount()):
            if self.getDataFromTable(self.Driven_Table_Model, i, 0)[0] == "None":
                allInputsValid = False

        # Check if there is a unique ID
        if len(self.ui.ID_LineEdit.text()) <= 0:
            allInputsValid = False

        # Check if the file is being saved to a valid directory
        file_path = self.ui.FilePath_LineEdit.text()
        if not os.path.exists(os.path.dirname(file_path)):
            allInputsValid = False

        return allInputsValid

    def setupTables(self):

        # Driver Table
        self.Driver_Table_Model = QtGui.QStandardItemModel(0, 3)  # 1 rows, 4 columns
        self.Driver_Table_Model.setHorizontalHeaderLabels(["X", "Y", "Z"])
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
        self.Driver_Table_Model.itemChanged.connect(self.onItemChanged)

        self.ui.Driver_Table.setModel(self.Driver_Table_Model)

        for i in range(3):
            self.ui.Driver_Table.setColumnWidth(i, 50)

        # Driven Table
        self.Driven_Table_Model = QtGui.QStandardItemModel(0, 3)  # 1 rows, 4 columns
        self.Driven_Table_Model.setHorizontalHeaderLabels(["X", "Y", "Z"])
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
        self.Driven_Table_Model.itemChanged.connect(self.onItemChanged)

        self.ui.Driven_Table.setModel(self.Driven_Table_Model)

        for i in range(3):
            self.ui.Driven_Table.setColumnWidth(i, 50)

        # Debug Setup some default values
        items = ["0.0", "0.0", "0.0"]
        self.addToTable(self.Driver_Table_Model, items)

        # Debug Setup some default values
        items = ["1", "0.2", "3.0"]
        self.addToTable(self.Driven_Table_Model, items)

    def addToTable(self, model, items):

        formatted = []

        for item in items:
            formatted.append(QtGui.QStandardItem(item))

        model.appendRow(formatted)

    def getDataFromTable(self, model, row, col=-1):

        dataOut = []

        if col == -1:
            for i in range(model.columnCount()):
                dataOut.append(model.item(row, i).text())
        else:
            dataOut.append(model.item(row, col).text())

        return dataOut

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

    def updateRBFNode(self):
        self.createRBFNode()

    def createRBFNode(self):
        if self.verifyValidInputs():

            # Check if a node already exists
            ID = self.ui.ID_LineEdit.text()
            nodeName = f"{ID}_RBF"
            if cmds.objExists(nodeName):
                node = cmds.ls(nodeName)
            else:
                node = cmds.createNode("SoxsRBFNode", name=nodeName, skipSelect=True)

            # Get Driver and Driven data
            driver_text = self.ui.Driver_LineEdit.text()
            driven_text = self.ui.Driven_LineEdit.text()
            driver_channel = self.ui.Driver_ComboBox.currentText().lower()
            driven_channel = self.ui.Driven_ComboBox.currentText().lower()
            setup = self.ui.Setup_ComboBox.currentText()
            setup_index = self.ui.Setup_ComboBox.currentIndex()
            json_path = self.ui.FilePath_LineEdit.text()
            kernel_index = self.ui.Kernel_ComboBox.currentIndex() + 1

            # Clear all attributes on RBF Node
            nodeAttrs = [
                f"{nodeName}.InputX",
                f"{nodeName}.InputY",
                f"{nodeName}.InputZ",
                f"{nodeName}.OutputTranslateX",
                f"{nodeName}.OutputTranslateY",
                f"{nodeName}.OutputTranslateZ",
                f"{nodeName}.OutputRotateX",
                f"{nodeName}.OutputRotateY",
                f"{nodeName}.OutputRotateZ",
                f"{nodeName}.OutputScaleX",
                f"{nodeName}.OutputScaleY",
                f"{nodeName}.OutputScaleZ",
            ]
            for attribute in nodeAttrs:
                destinationAttrs = (
                    cmds.listConnections(attribute, plugs=True, source=False) or []
                )
                sourceAttrs = (
                    cmds.listConnections(attribute, plugs=True, destination=False) or []
                )

                for destAttr in destinationAttrs:
                    cmds.disconnectAttr(attribute, destAttr)
                for srcAttr in sourceAttrs:
                    cmds.disconnectAttr(srcAttr, attribute)

            # Set the Data Path and Data Id on the node
            cmds.setAttr(f"{nodeName}.RBF_DataPath", json_path, type="string")
            cmds.setAttr(f"{nodeName}.RBF_DataId", ID, type="string")
            cmds.setAttr(f"{nodeName}.RBF_Settings", setup_index)
            cmds.setAttr(f"{nodeName}.RBF_Kernel", kernel_index)

            # Set up connections between Driver, Node, and Driven
            # TODO: read the XYZ columns and determine the proper connections

            # Setup X input
            cmds.connectAttr(f"{driver_text}.{driver_channel}X", f"{nodeName}.InputX")

            # If driver setup is 2in
            if setup[0:3] == "2in":
                cmds.connectAttr(
                    f"{driver_text}.{driver_channel}Y", f"{nodeName}.InputY"
                )
            # If driver setup is 3in
            elif setup[0:3] == "3in":
                cmds.connectAttr(
                    f"{driver_text}.{driver_channel}Y", f"{nodeName}.InputY"
                )
                cmds.connectAttr(
                    f"{driver_text}.{driver_channel}Z", f"{nodeName}.InputZ"
                )

            # Setup X output
            cmds.connectAttr(
                f"{nodeName}.Output{driven_channel.title()}X",
                f"{driven_text}.{driven_channel}X",
            )

            # If driven setup is 2out
            if setup[-4:] == "2out":
                cmds.connectAttr(
                    f"{nodeName}.Output{driven_channel.title()}Y",
                    f"{driven_text}.{driven_channel}Y",
                )
            # If driven setup is 3out
            elif setup[-4:] == "3out":
                cmds.connectAttr(
                    f"{nodeName}.Output{driven_channel.title()}Y",
                    f"{driven_text}.{driven_channel}Y",
                )
                cmds.connectAttr(
                    f"{nodeName}.Output{driven_channel.title()}Z",
                    f"{driven_text}.{driven_channel}Z",
                )

    def LoadDriver(self):
        print("Load Driver")

        self.GenerateID()

    def LoadDriven(self):
        print("Load Driver")

        self.GenerateID()

    def GenerateID(self):
        Driver_Text = self.ui.Driver_LineEdit.text()
        Driven_Text = self.ui.Driven_LineEdit.text()
        self.ui.ID_LineEdit.setText(f"{Driver_Text}_to_{Driven_Text}")

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

    def onItemChanged(self, item):

        row = item.row()
        col = item.column()
        value = item.text()
        print(row, col, value)

    def onSave(self):
        self.updateRBFNode()


if __name__ == "__main__":
    myWidget = RBFManager()
    myWidget.show()
