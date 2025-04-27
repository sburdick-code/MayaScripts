try:
    from PySide2 import QtCore, QtWidgets, QtUiTools, QtGui
    from shiboken2 import wrapInstance
except:
    from PySide6 import QtCore, QtWidgets, QtUiTools, QtGui
    from shiboken6 import wrapInstance

import sys
import os
import maya.cmds as cmds
import json

from Tools.ControllerToolboxWidget.Const import Const
from Tools.ControllerToolboxWidget import curveTools


class CreateNewCurveDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(CreateNewCurveDialog, self).__init__(parent)

        self.parent = parent
        self.setWindowTitle("Create New Curve")
        self.setMinimumSize(172, 300)
        self.setMaximumSize(172, 300)

        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)

        self.initUI()
        self.createConnections()

    def initUI(self):
        """
        Load up the widget UI from the .ui file
        """
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(
            (Const.UI_DIR + "CreateNewCurveDialog.ui"), parentWidget=self
        )
        self.setLayout(self.ui.layout())

    def createConnections(self):
        """
        Create necessary connections for the ui
        """
        self.ui.snapshotButton.clicked.connect(self.capture_viewport)
        self.ui.saveCancelButtons.accepted.connect(self.on_accepted)
        self.ui.saveCancelButtons.rejected.connect(self.close)

    def on_accepted(self):
        """
        When the Save button is pressed, check that all required
        info is present, then save the curve and capture to a
        json and png.
        """

        curve_name = self.ui.nameLineEdit.text()

        # Check if a temp capture was created
        if not os.path.exists(Const.TEMP_IMAGE_PATH):
            cmds.error("Please take a snapshot of the curve.")
            return

        # Check if the user has added a name for the curve
        if not self.ui.nameLineEdit.text():
            cmds.error("Please add a name for the curve.")
            return

        # Check if curve data of the same name already exists
        print(Const.CTRL_DATA_DIR + curve_name + ".json")
        if os.path.exists(Const.CTRL_DATA_DIR + curve_name + ".json"):
            qm = QtWidgets.QMessageBox
            message = f"{curve_name} already exists.\nOverwrite this data?"
            user_input = qm.question(
                self,
                "",
                message,
                qm.Yes | qm.No,
            )
            if user_input == qm.No:
                return
            else:
                os.remove(Const.CTRL_DATA_DIR + curve_name + ".png")
                os.remove(Const.CTRL_DATA_DIR + curve_name + ".json")

        # Validate the selection
        selection = cmds.ls(selection=True)

        if len(selection) == 1:
            if cmds.objectType(selection[0]) == "transform":
                children = cmds.listRelatives(c=True)

                for child in children:
                    if (
                        cmds.objectType(child) == "nurbsCurve"
                        or cmds.objectType(child) == "bezierCurve"
                    ):
                        curveTools.save_curve(child, curve_name, self.parent)
                        # Re-populate the table
                        self.parent.populate_table()
                        # Re-enable the parent widget
                        self.parent.setEnabled(True)
                        # Close this dialog
                        self.close()

                    # Error if the selection has no curves
                    else:
                        cmds.error(
                            "Invalid object. Object must be of type nurbsCurve or bezierCurve",
                            n=True,
                        )
                        return

            elif (
                cmds.objectType(selection) == "nurbsCurve"
                or cmds.objectType(selection) == "bezierCurve"
            ):
                curveTools.save_curve(
                    selection[0], self.ui.nameLineEdit.text(), self.parent
                )
                # Re-populate the table
                self.parent.populate_table()
                # Re-enable the parent widget
                self.parent.setEnabled(True)
                # Close this dialog
                self.close()

            else:
                cmds.error(
                    "Invalid object. Object must be of type nurbsCurve or bezierCurve",
                    n=True,
                )
        else:
            cmds.error("Please select one object", n=True)
            return

    def capture_viewport(self):
        """
        Take a playblast of the viewport and save it as a temp png file
        """
        # Capture the viewport as a 128x128 png named tempCapture.png
        curFrame = int(cmds.currentTime(query=True))
        cmds.playblast(
            fr=curFrame,
            v=False,
            fmt="image",
            c="png",
            orn=False,
            cf=Const.TEMP_IMAGE_PATH,
            wh=[128, 128],
            p=100,
        )
        print(f"Snapshot saved as: {Const.TEMP_IMAGE_PATH}")

        # Set the playblast as the image for the imageFrame
        pixmap = QtGui.QPixmap(Const.TEMP_IMAGE_PATH)
        pixmap = pixmap.scaled(150, 150, QtCore.Qt.IgnoreAspectRatio)
        self.ui.imageFrame.setPixmap(pixmap)

    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        Override the close event so the parent widget can be re-enabled
        """
        # Delete the temp image if it exists
        if os.path.exists(Const.TEMP_IMAGE_PATH):
            os.remove(Const.TEMP_IMAGE_PATH)

        # Re-enable the parent widget
        self.parent.setEnabled(True)

        # Close this dialog
        self.close()


class RenameDialog(QtWidgets.QDialog):

    def __init__(self, parent, curve_name):
        super(RenameDialog, self).__init__(parent)

        self.curve_name = curve_name
        self.parent = parent
        self.setWindowTitle(f"Rename {curve_name}")
        self.setMinimumSize(172, 100)

        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)

        self.initUI()
        self.createConnections()

    def initUI(self):
        """
        Load up the widget UI from the .ui file
        """
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load((Const.UI_DIR + "RenameDialog.ui"), parentWidget=self)
        self.setLayout(self.ui.layout())

    def createConnections(self):
        """
        Create necessary connections for the ui
        """
        self.ui.renameLineEdit.returnPressed.connect(self.on_accepted)
        self.ui.okCancelButtons.accepted.connect(self.on_accepted)
        self.ui.okCancelButtons.rejected.connect(self.close)

    def on_accepted(self):
        new_name = self.ui.renameLineEdit.text()

        # Rename the curve data
        src_json = Const.CTRL_DATA_DIR + self.curve_name + ".json"
        src_png = Const.CTRL_DATA_DIR + self.curve_name + ".png"
        dst_json = Const.CTRL_DATA_DIR + new_name + ".json"
        dst_png = Const.CTRL_DATA_DIR + new_name + ".png"

        try:
            os.rename(src_json, dst_json)
            os.rename(src_png, dst_png)

            with open(dst_json, "r") as curve_file:
                data = json.load(curve_file)

            data["name"] = new_name

            with open(dst_json, "w") as curve_file:
                json.dump(data, curve_file)

            # Reload the table
            self.parent.populate_table()

            # Notify the user of success
            qm = QtWidgets.QMessageBox
            message = f"{self.curve_name} renamed to {new_name}"
            qm.information(self, "Success", message)

        except:
            # Notify the user of failure
            qm = QtWidgets.QMessageBox
            message = f"Could not rename {self.curve_name}!"
            qm.information(self, "Failure", message)
            cmds.warning(message)

        # Close this dialog
        self.close()

    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        Override the close event so the parent widget can be re-enabled
        """
        # Re-enable the parent widget
        self.parent.setEnabled(True)

        # Close this dialog
        self.close()
