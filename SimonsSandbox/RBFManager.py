from PySide2 import QtWidgets, QtCore, QtUiTools
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
