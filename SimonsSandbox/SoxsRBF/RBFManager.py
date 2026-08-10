from PySide2 import QtWidgets, QtCore, QtUiTools, QtGui
from shiboken2 import wrapInstance

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

    UI_FILE = "Z:\Projects\MayaScripts\SimonsSandbox\RBFManagerWidget.ui"

    FILE_FILTERS = "JSON (*.json)"
    selected_filter = "JSON (*.json)"

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

    def removeFromTable(self, model, row):
        model.removeRow(row)

    def getDataFromTable(self, model, row, col=-1):

        dataOut = []

        if col == -1:
            for i in range(model.columnCount()):
                if self.isNumber(model.item(row, i).text()):
                    dataOut.append(float(model.item(row, i).text()))
        else:
            dataOut.append(float(model.item(row, col).text()))

        return dataOut

    def getAllDataFromTable(self, model):

        dataOut = []

        for i in range(model.rowCount()):
            dataOut.append(self.getDataFromTable(model, i))

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
            print(item.row(), item.data())

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
            print(item.row(), item.data())

            if item.row() == -1:  # Nothing is selected
                self.add_context_menu.exec_(self.ui.Driven_Table.mapToGlobal(cPosition))

            else:
                self.curRow = item.row()

                self.edit_context_menu.exec_(
                    self.ui.Driven_Table.mapToGlobal(cPosition)
                )

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

            # Write to the Json
            driverData = self.getAllDataFromTable(self.Driver_Table_Model)
            drivenData = self.getAllDataFromTable(self.Driven_Table_Model)
            driverMtrx = np.array(driverData)
            drivenMtrx = np.array(drivenData)
            weights = RBFCalc.calculate_weights_matrix(
                driverMtrx, drivenMtrx, kernel_index
            )

            dKey = f"d_{ID}"
            oKey = f"o_{ID}"
            wKey = f"w_{ID}"

            writeData = {
                dKey: driverData,
                oKey: drivenData,
                wKey: weights.tolist(),
            }

            if not os.path.isfile(json_path):
                try:
                    with open(json_path, "w") as f:
                        pass
                except:
                    cmds.error(f"Could not write json to : {json_path}")
                    return

            with open(json_path, "r+") as f:

                try:
                    fileData = json.load(f)
                    fileData[dKey] = driverData
                    fileData[oKey] = drivenData
                    fileData[wKey] = weights.tolist()
                    f.seek(0)

                except:
                    fileData = writeData

                json.dump(fileData, f)
                f.truncate()

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
        print("Load Driven")

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
        file_path, self.selected_filter = QtWidgets.QFileDialog.getSaveFileName(
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

    def onAddNew(self):

        DriverName = self.ui.Driver_LineEdit.text()
        DrivenName = self.ui.Driven_LineEdit.text()
        DriverAttr = self.ui.Driver_ComboBox.currentText().lower()
        DrivenAttr = self.ui.Driven_ComboBox.currentText().lower()

        if cmds.objExists(DriverName) and cmds.objExists(DrivenName):
            try:
                DriverPos = cmds.getAttr(f"{DriverName}.{DriverAttr}")[0]
                DrivenPos = cmds.getAttr(f"{DrivenName}.{DrivenAttr}")[0]
                DriverPos = [f"{item:.3f}" for item in DriverPos]
                DrivenPos = [f"{item:.3f}" for item in DrivenPos]

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
        setup = self.ui.Setup_ComboBox.currentText()
        DriverName = self.ui.Driver_LineEdit.text()
        DrivenName = self.ui.Driven_LineEdit.text()
        DriverAttr = self.ui.Driver_ComboBox.currentText().lower()
        DrivenAttr = self.ui.Driven_ComboBox.currentText().lower()

        DriverPos = self.getDataFromTable(self.Driver_Table_Model, self.curRow)
        DrivenPos = self.getDataFromTable(self.Driven_Table_Model, self.curRow)

        if cmds.objExists(DriverName) and cmds.objExists(DrivenName):
            try:
                for i in range(3):
                    if self.isNumber(DriverPos[i]):
                        coord = self.getXYZ(i)
                        attr = f"{DriverName}.{DriverAttr}{coord}"
                        pos = float(DriverPos[i])
                        cmds.setAttr(attr, pos)
            except:
                cmds.warning("Error setting Driver Position")

            try:
                for i in range(3):
                    if self.isNumber(DrivenPos[i]):
                        coord = self.getXYZ(i)
                        attr = f"{DrivenName}.{DrivenAttr}{coord}"
                        pos = float(DrivenPos[i])
                        cmds.setAttr(attr, pos)
            except:
                pass

        else:
            cmds.warning(
                "Please select a valid Driver and Driven before adding positions!"
            )


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

        out = f'"d_{unique_id}":{p_formatted_string},"o_{unique_id}":{o_formatted_string},"w_{unique_id}":{w_formatted_string}'

        out_dict = {
            f"d_{unique_id}": input_mtrx.tolist(),
            f"o_{unique_id}": output_mtrx.tolist(),
            f"w_{unique_id}": weight_mtrx.tolist(),
        }

        return out_dict


if __name__ == "__main__":
    myWidget = RBFManager()
    myWidget.show()
