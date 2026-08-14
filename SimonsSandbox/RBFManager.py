try:
    # Qt5
    from PySide2 import QtWidgets, QtCore, QtUiTools, QtGui
    from shiboken2 import wrapInstance
except:
    # Qt6
    from PySide6 import QtWidgets, QtCore, QtUiTools, QtGui
    from shiboken6 import wrapInstance

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds

import os
import numpy as np
import math
import json


def mayaMainWindow():
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mainWindowPtr), QtWidgets.QWidget)


class RBFManager(QtWidgets.QDialog):

    UI_FILE = r"Z:\Projects\MayaScripts\SimonsSandbox\RBFManagerWidget.ui"

    FILE_FILTERS = "JSON (*.json)"
    SELECTED_FILTER = "JSON (*.json)"

    curRow = -1

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

        self.ui.Driver_LineEdit.textChanged.connect(self.LoadDriver)
        self.ui.AddDriver_Button.clicked.connect(
            lambda: self.UpdateTextToSelection(self.ui.Driver_LineEdit)
        )
        self.ui.Driven_LineEdit.textChanged.connect(self.LoadDriven)
        self.ui.AddDriven_Button.clicked.connect(
            lambda: self.UpdateTextToSelection(self.ui.Driven_LineEdit)
        )

        self.ui.ClearDriver_Button.clicked.connect(self.onClearDriver)
        self.ui.ClearDriven_Button.clicked.connect(self.onClearDriven)

        self.ui.Driver_ComboBox.currentIndexChanged.connect(self.GenerateID)
        self.ui.Driven_ComboBox.currentIndexChanged.connect(self.GenerateID)

        self.ui.GenerateID_Button.clicked.connect(self.GenerateID)

        self.ui.Browse_Button.clicked.connect(self.showFileSelectDialog)

        self.ui.ToggleUpdates_Button.clicked.connect(self.onToggleUpdates)

        self.ui.Delete_Button.clicked.connect(self.onDeleteRBFConnection)

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

        # Setup default value for combo boxes
        self.ui.DriverSetup_ComboBox.setCurrentIndex(6)
        self.ui.DrivenSetup_ComboBox.setCurrentIndex(6)

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

    def addToTable(self, model, items):

        formatted = []

        for item in items:
            formatted.append(QtGui.QStandardItem(str(item)))

        model.appendRow(formatted)

    def removeFromTable(self, model, row):
        model.removeRow(row)

    def clearTable(self, model):

        for row in range(model.rowCount()):
            model.removeRow(0)

    def clearAllTables(self, check=False):
        print("Clear All Tables")
        print(self.Driver_Table_Model.rowCount())
        if check and self.Driver_Table_Model.rowCount() > 0:
            result = QtWidgets.QMessageBox.question(
                self,
                "Confirm",
                "Clear the tables?",
                QtWidgets.QMessageBox.StandardButton.Yes
                | QtWidgets.QMessageBox.StandardButton.No,
            )

            if result == QtWidgets.QMessageBox.StandardButton.Yes:
                print("chose yes!")
                self.clearTable(self.Driver_Table_Model)
                self.clearTable(self.Driven_Table_Model)
            else:
                return

        else:
            self.clearTable(self.Driver_Table_Model)
            self.clearTable(self.Driven_Table_Model)

    def getDataFromTable(self, model, row, col=-1):

        dataOut = []

        if col == -1:
            for i in range(model.columnCount()):
                if self.isNumber(model.item(row, i).text()):
                    dataOut.append(float(model.item(row, i).text()))
        else:
            if self.isNumber(model.item(row, col).text()):
                dataOut.append(float(model.item(row, col).text()))
            else:
                print("lol! You triggered an error >:)")
                dataOut.append("I'm here to cause an error >:)")

        return dataOut

    def getAllDataFromTable(self, model):

        dataOut = []

        if model is self.Driver_Table_Model:
            setup = self.ui.DriverSetup_ComboBox.currentText()
            print("SAVING INPUTS")
        else:
            setup = self.ui.DrivenSetup_ComboBox.currentText()
            print("SAVING OUTPUTS")

        for i in range(model.rowCount()):
            row = []
            if "x" in setup:
                row.append(self.getDataFromTable(model, i, 0)[0])
            if "y" in setup:
                row.append(self.getDataFromTable(model, i, 1)[0])
            if "z" in setup:
                row.append(self.getDataFromTable(model, i, 2)[0])

            dataOut.append(row)

        print(dataOut)

        return dataOut

    def createCustomContextMenu(self):

        self.edit_context_menu = QtWidgets.QMenu(self)
        action_GoTo = self.edit_context_menu.addAction("Go To Position")
        action_Delete = self.edit_context_menu.addAction("Delete Row")

        action_GoTo.triggered.connect(self.onGoToPosition)
        action_Delete.triggered.connect(self.onDeleteRow)

        self.add_context_menu = QtWidgets.QMenu(self)
        action_Add = self.add_context_menu.addAction("Add New")

        action_Add.triggered.connect(self.onAddNew)

    def displayDriverContextMenu(self, position):

        item = self.ui.Driver_Table.indexAt(position)
        cPosition = position + QtCore.QPoint(20, 25)

        if item:

            if item.row() == -1:  # Nothing is selected
                self.add_context_menu.exec_(self.ui.Driver_Table.mapToGlobal(cPosition))

            else:
                self.curRow = item.row()

                self.edit_context_menu.exec_(
                    self.ui.Driver_Table.mapToGlobal(cPosition)
                )

    def displayDrivenContextMenu(self, position):
        item = self.ui.Driven_Table.indexAt(position)
        cPosition = position + QtCore.QPoint(20, 25)

        if item:

            if item.row() == -1:  # Nothing is selected
                self.add_context_menu.exec_(self.ui.Driven_Table.mapToGlobal(cPosition))

            else:
                self.curRow = item.row()

                self.edit_context_menu.exec_(
                    self.ui.Driven_Table.mapToGlobal(cPosition)
                )

    def UpdateTextToSelection(self, LineEdit):
        selected = cmds.ls(selection=True)[0]
        LineEdit.setText(str(selected))

    def updateRBFNode(self):
        self.createRBFNode()

    def createRBFNode(self):
        if self.verifyValidInputs():

            # Check if a node already exists
            ID = self.ui.ID_LineEdit.text()
            nodeName = f"{ID}_RBF"
            json_path = self.ui.FilePath_LineEdit.text()
            kernel_index = self.ui.Kernel_ComboBox.currentIndex() + 1

            if cmds.objExists(nodeName):
                node = cmds.ls(nodeName)
            else:
                node = cmds.createNode("SoxsRBFNode", name=nodeName, skipSelect=True)

            # Write to the Json
            driverData = self.getAllDataFromTable(self.Driver_Table_Model)
            drivenData = self.getAllDataFromTable(self.Driven_Table_Model)
            driverMtrx = np.array(driverData)
            drivenMtrx = np.array(drivenData)
            weights = RBFCalc.calculate_weights_matrix(
                driverMtrx, drivenMtrx, kernel_index
            )

            driverSetup = self.ui.DriverSetup_ComboBox.currentText()
            drivenSetup = self.ui.DrivenSetup_ComboBox.currentText()
            attributeData = [driverSetup, drivenSetup]

            writeData = {
                ID: {
                    "setup": attributeData,
                    "inputs": driverData,
                    "outputs": drivenData,
                    "weights": weights.tolist(),
                }
            }

            if not os.path.isfile(json_path):
                with open(json_path, "w") as f:
                    f.write("")

            # Read the JSON
            try:
                with open(json_path, "r") as f:

                    try:
                        fileData = json.load(f)

                        # edit fileData's values and update to the set ones
                        fileData[ID]["setup"] = attributeData
                        fileData[ID]["inputs"] = driverData
                        fileData[ID]["outputs"] = drivenData
                        fileData[ID]["weights"] = weights.tolist()

                    except:
                        fileData = writeData

            except FileNotFoundError:
                cmds.error(f"Could not write json to : {json_path}")
                return

            # Write to the JSON
            with open(json_path, "w") as f:
                json.dump(fileData, f)
                f.truncate()

            # Connect up the node
            self.connectNode()

    def LoadDriver(self):
        print("Load Driver")

        self.GenerateID()

    def LoadDriven(self):
        print("Load Driven")

        self.GenerateID()

    def GenerateID(self):
        Driver_Text = self.ui.Driver_LineEdit.text()
        Driven_Text = self.ui.Driven_LineEdit.text()

        Driver_Channel = self.ui.Driver_ComboBox.currentText().lower()
        Driven_Channel = self.ui.Driven_ComboBox.currentText().lower()

        self.ui.ID_LineEdit.setText(
            f"{Driver_Text}_{Driver_Channel}_to_{Driven_Text}_{Driven_Channel}"
        )

        self.updateEditableProperties()

    def updateEditableProperties(self):
        nodes = self.getRBFNode()
        if len(nodes) > 0:
            id = self.ui.ID_LineEdit.text()
            node = nodes[0]
            json_path = cmds.getAttr(f"{node}.RBF_DataPath")
            self.ui.FilePath_LineEdit.setText(json_path)

            kernel_index = cmds.getAttr(f"{node}.RBF_Kernel") - 1
            self.ui.Kernel_ComboBox.setCurrentIndex(kernel_index)

            with open(json_path, "r") as f:
                fileData = json.load(f)
                self.ui.DriverSetup_ComboBox.setCurrentText(fileData[id]["setup"][0])
                self.ui.DrivenSetup_ComboBox.setCurrentText(fileData[id]["setup"][1])

            self.populateTable()

        else:
            doCheck = True
            self.clearAllTables(doCheck)
            # self.ui.FilePath_LineEdit.setText("")

    def showFileSelectDialog(self):
        file_path, self.SELECTED_FILTER = QtWidgets.QFileDialog.getSaveFileName(
            self, "Select File", "", self.FILE_FILTERS, self.SELECTED_FILTER
        )
        if file_path:
            self.ui.FilePath_LineEdit.setText(file_path)

    def onItemChanged(self, item):

        row = item.row()
        col = item.column()
        value = item.text()

    def onSave(self):
        self.updateRBFNode()

    def onAddNew(self):

        DriverName = self.ui.Driver_LineEdit.text()
        DrivenName = self.ui.Driven_LineEdit.text()
        DriverAttr = self.ui.Driver_ComboBox.currentText().lower()
        DrivenAttr = self.ui.Driven_ComboBox.currentText().lower()
        DriverSetup = self.ui.DriverSetup_ComboBox.currentText()
        DrivenSetup = self.ui.DrivenSetup_ComboBox.currentText()

        if cmds.objExists(DriverName) and cmds.objExists(DrivenName):
            try:
                DriverPos = cmds.getAttr(f"{DriverName}.{DriverAttr}")[0]
                DrivenPos = cmds.getAttr(f"{DrivenName}.{DrivenAttr}")[0]
                DriverPos = [f"{item:.3f}" for item in DriverPos]
                DrivenPos = [f"{item:.3f}" for item in DrivenPos]

                if "x" not in DriverSetup:
                    DriverPos[0] = ""
                if "y" not in DriverSetup:
                    DriverPos[1] = ""
                if "z" not in DriverSetup:
                    DriverPos[2] = ""

                if "x" not in DrivenSetup:
                    DrivenPos[0] = ""
                if "y" not in DrivenSetup:
                    DrivenPos[1] = ""
                if "z" not in DrivenSetup:
                    DrivenPos[2] = ""

                self.addToTable(self.Driver_Table_Model, DriverPos)
                self.addToTable(self.Driven_Table_Model, DrivenPos)

            except:
                cmds.warning(
                    "Please select a valid Driver and Driven before adding positions!"
                )
        else:
            cmds.warning(
                "Please select a valid Driver and Driven before adding positions!"
            )

    def onDeleteRow(self):
        if self.curRow >= 0:
            self.removeFromTable(self.Driver_Table_Model, self.curRow)
            self.removeFromTable(self.Driven_Table_Model, self.curRow)

    def getXYZ(self, index):
        out = "X"
        if index == 1:
            out = "Y"
        elif index == 2:
            out = "Z"
        return out

    def isNumber(self, text):
        try:
            float(text)
            return True
        except ValueError:
            return False

    def onGoToPosition(self):
        DriverName = self.ui.Driver_LineEdit.text()
        DrivenName = self.ui.Driven_LineEdit.text()
        DriverAttr = self.ui.Driver_ComboBox.currentText().lower()
        DrivenAttr = self.ui.Driven_ComboBox.currentText().lower()
        DriverSetup = self.ui.DriverSetup_ComboBox.currentText()
        DrivenSetup = self.ui.DrivenSetup_ComboBox.currentText()

        DriverPos = self.getDataFromTable(self.Driver_Table_Model, self.curRow)
        DrivenPos = self.getDataFromTable(self.Driven_Table_Model, self.curRow)

        print(DriverPos)

        if cmds.objExists(DriverName) and cmds.objExists(DrivenName):
            index = 0

            if "x" in DriverSetup:
                attr = f"{DriverName}.{DriverAttr}X"
                pos = float(DriverPos[index])
                cmds.setAttr(attr, pos)
                index += 1
            if "y" in DriverSetup:
                attr = f"{DriverName}.{DriverAttr}Y"
                pos = float(DriverPos[index])
                cmds.setAttr(attr, pos)
                index += 1
            if "z" in DriverSetup:
                attr = f"{DriverName}.{DriverAttr}Z"
                pos = float(DriverPos[index])
                cmds.setAttr(attr, pos)

            index = 0

            if "x" in DrivenSetup:
                attr = f"{DrivenName}.{DrivenAttr}X"
                pos = float(DrivenPos[index])
                cmds.setAttr(attr, pos)
                index += 1
            if "y" in DrivenSetup:
                attr = f"{DrivenName}.{DrivenAttr}Y"
                pos = float(DrivenPos[index])
                cmds.setAttr(attr, pos)
                index += 1
            if "z" in DrivenSetup:
                attr = f"{DrivenName}.{DrivenAttr}Z"
                pos = float(DrivenPos[index])
                cmds.setAttr(attr, pos)

        else:
            cmds.warning(
                "Please select a valid Driver and Driven before adding positions!"
            )

    def getRBFNode(self):

        nodes = []

        driverName = self.ui.Driver_LineEdit.text()
        drivenName = self.ui.Driven_LineEdit.text()

        if cmds.objExists(driverName) and cmds.objExists(drivenName):
            id = self.ui.ID_LineEdit.text()
            nodeName = f"{id}_RBF"

            nodes = cmds.ls(nodeName, ap=True)

            if len(nodes) <= 0:
                cmds.warning(f"No RBF Node found for {nodeName}")

        return nodes

    def onDeleteRBFConnection(self):

        id = self.ui.ID_LineEdit.text()
        nodes = self.getRBFNode()

        doCheck = True
        self.clearAllTables(doCheck)

        for node in nodes:

            # Clean up the data from the JSON
            json_path = cmds.getAttr(f"{node}.RBF_DataPath")

            with open(json_path, "r+") as f:
                file_data = json.load(f)
                file_data.pop(id)
                json.dump(file_data, f)

            # Delete the node itself
            cmds.delete(node)

            cmds.warning(f"Deleted RBF node {node}")

    def populateTable(self):
        id = self.ui.ID_LineEdit.text()
        json_path = self.ui.FilePath_LineEdit.text()

        self.clearTable(self.Driver_Table_Model)
        self.clearTable(self.Driven_Table_Model)

        with open(json_path, "r") as f:
            file_data = json.load(f)

            if id in file_data:
                node_data = file_data[id]

                DriverSetup = node_data["setup"][0]
                DrivenSetup = node_data["setup"][1]
                inputs = node_data["inputs"]
                outputs = node_data["outputs"]
                weights = node_data["weights"]

        print("INPUTS")
        for item in inputs:
            index = 0
            tableItem = ["", "", ""]

            if "x" in DriverSetup:
                tableItem[0] = item[index]
                index += 1
            if "y" in DriverSetup:
                tableItem[1] = item[index]
                index += 1
            if "z" in DriverSetup:
                tableItem[2] = item[index]

            print(tableItem)
            self.addToTable(self.Driver_Table_Model, tableItem)

        print("OUTPUTS")
        for item in outputs:
            index = 0
            tableItem = ["", "", ""]

            if "x" in DrivenSetup:
                tableItem[0] = item[index]
                index += 1
            if "y" in DrivenSetup:
                tableItem[1] = item[index]
                index += 1
            if "z" in DrivenSetup:
                tableItem[2] = item[index]

            print(tableItem)
            self.addToTable(self.Driven_Table_Model, tableItem)

    def onClearDriver(self):
        self.ui.Driver_LineEdit.setText("")

    def onClearDriven(self):
        self.ui.Driven_LineEdit.setText("")

    def onToggleUpdates(self):

        button_name = self.ui.ToggleUpdates_Button.text()

        if button_name == "Freeze Updates":
            new_name = "Un-Freeze Updates"
            self.disconnectNode()
        else:
            new_name = "Freeze Updates"
            self.connectNode()

        self.ui.ToggleUpdates_Button.setText(new_name)

    def disconnectNode(self):

        # Check if a node already exists
        ID = self.ui.ID_LineEdit.text()
        nodeName = f"{ID}_RBF"

        if not cmds.objExists(nodeName):
            cmds.error(f"Could not find node for : {nodeName}")
            return

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

    def getSetupIndex(self, iString, oString):
        setupArray = [
            "1in->1out",
            "1in->2out",
            "1in->3out",
            "2in->1out",
            "2in->2out",
            "2in->3out",
            "3in->1out",
            "3in->2out",
            "3in->3out",
        ]

        lookupString = f"{len(iString)}in->{len(oString)}out"

        return setupArray.index(lookupString)

    def connectNode(self):

        # Check if a node already exists
        ID = self.ui.ID_LineEdit.text()
        nodeName = f"{ID}_RBF"

        if not cmds.objExists(nodeName):
            cmds.error(f"Could not find node for : {nodeName}")
            return

        # Get Driver and Driven data
        driver_text = self.ui.Driver_LineEdit.text()
        driven_text = self.ui.Driven_LineEdit.text()
        driver_channel = self.ui.Driver_ComboBox.currentText().lower()
        driven_channel = self.ui.Driven_ComboBox.currentText().lower()
        driverSetup = self.ui.DriverSetup_ComboBox.currentText()
        drivenSetup = self.ui.DrivenSetup_ComboBox.currentText()
        setup_index = self.getSetupIndex(driverSetup, drivenSetup)
        json_path = self.ui.FilePath_LineEdit.text()
        kernel_index = self.ui.Kernel_ComboBox.currentIndex() + 1

        # Disconnect all current inputs and outputs
        self.disconnectNode()

        # Set the Data Path and Data Id on the node
        cmds.setAttr(f"{nodeName}.RBF_DataPath", json_path, type="string")
        cmds.setAttr(f"{nodeName}.RBF_DataId", ID, type="string")
        cmds.setAttr(f"{nodeName}.RBF_Settings", setup_index)
        cmds.setAttr(f"{nodeName}.RBF_Kernel", kernel_index)

        # Data to help handle the driver hookups
        iInput = 0
        iOutput = 0
        coords = ["X", "Y", "Z"]

        # Hookup Driver to Input Attributes
        if "x" in driverSetup:
            cmds.connectAttr(
                f"{driver_text}.{driver_channel}X", f"{nodeName}.Input{coords[iInput]}"
            )
            iInput += 1
        if "y" in driverSetup:
            cmds.connectAttr(
                f"{driver_text}.{driver_channel}Y", f"{nodeName}.Input{coords[iInput]}"
            )
            iInput += 1
        if "z" in driverSetup:
            cmds.connectAttr(
                f"{driver_text}.{driver_channel}Z", f"{nodeName}.Input{coords[iInput]}"
            )
            iInput += 1

        # Hookup Output to Driven Attributes
        if "x" in drivenSetup:
            cmds.connectAttr(
                f"{nodeName}.Output{driven_channel.title()}{coords[iOutput]}",
                f"{driven_text}.{driven_channel}X",
            )
            iOutput += 1
        if "y" in drivenSetup:
            cmds.connectAttr(
                f"{nodeName}.Output{driven_channel.title()}{coords[iOutput]}",
                f"{driven_text}.{driven_channel}Y",
            )
            iOutput += 1
        if "z" in drivenSetup:
            cmds.connectAttr(
                f"{nodeName}.Output{driven_channel.title()}{coords[iOutput]}",
                f"{driven_text}.{driven_channel}Z",
            )
            iOutput += 1


class RBFCalc:
    # Calculate the Weight matrix
    @staticmethod
    def calculate_weights_matrix(input_mtrx, output_mtrx, beta):
        dist_mtrx = RBFCalc.calc_distance_matrix(input_mtrx)
        phi = RBFCalc.rbf(dist_mtrx, beta)
        weight_mtrx = np.linalg.solve(phi, output_mtrx)

        return weight_mtrx

    # Distance
    @staticmethod
    def distance(p1, p2):
        return math.sqrt(sum([(a - b) ** 2 for a, b in zip(p1, p2)]))

    # RBF Solver
    @staticmethod
    def rbf(r, beta):
        return r**beta

    # Training
    @staticmethod
    def calc_distance_matrix(p_matrix):
        dist_matrix = np.zeros([len(p_matrix), len(p_matrix)])

        for x in range(len(p_matrix)):
            for y in range(len(p_matrix)):
                dist_matrix[x][y] = RBFCalc.distance(p_matrix[x], p_matrix[y])

        return dist_matrix

    # Evaluation
    @staticmethod
    def evaluate_rbf(q, pos_mtrx, weight_mtrx):
        q_phi = np.zeros(len(pos_mtrx))

        for i in range(len(q_phi)):
            dist = RBFCalc.distance(q, pos_mtrx[i])
            q_phi[i] = RBFCalc.rbf(dist)

        result = np.dot(q_phi, weight_mtrx)
        return result

    @staticmethod
    def format_RBF_string(input_mtrx, output_mtrx, weight_mtrx, unique_id):
        # format strings
        p_array_string = np.array2string(input_mtrx, separator=",")
        p_formatted_string = (
            p_array_string.replace("\n", "")
            .replace(" ", "")
            .replace("0.", "0.0")
            .replace("1.", "1.0")
        )
        o_array_string = np.array2string(output_mtrx, separator=",")
        o_formatted_string = (
            o_array_string.replace("\n", "")
            .replace(" ", "")
            .replace("0.", "0.0")
            .replace("1.", "1.0")
        )
        w_array_string = np.array2string(weight_mtrx, separator=",")
        w_formatted_string = (
            w_array_string.replace("\n", "").replace(" ", "").replace("0.", "0.0")
        )

        out = f'"i_{unique_id}":{p_formatted_string},"o_{unique_id}":{o_formatted_string},"w_{unique_id}":{w_formatted_string}'

        out_dict = {
            f"i_{unique_id}": input_mtrx.tolist(),
            f"o_{unique_id}": output_mtrx.tolist(),
            f"w_{unique_id}": weight_mtrx.tolist(),
        }

        return out_dict


if __name__ == "__main__":
    myWidget = RBFManager()
    myWidget.show()
