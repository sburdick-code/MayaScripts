try:
    from PySide2 import QtCore, QtWidgets, QtUiTools, QtGui
    from shiboken2 import wrapInstance
except:
    from PySide6 import QtCore, QtWidgets, QtUiTools, QtGui
    from shiboken6 import wrapInstance

import sys
import os
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import json


def mayaMainWindow():
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mainWindowPtr), QtWidgets.QWidget)


class CreateNewCurveDialog(QtWidgets.QDialog):
    WORKING_DIR = "Z:\Projects\MayaScripts\Tools\ControllerToolboxWidget"  # TODO Switch with this: os.path.dirname(__file__)
    TEMP_IMAGE_PATH = WORKING_DIR + "\controller_data\\tempCapture.png"
    UI_PATH = WORKING_DIR + "\\ui\\CreateNewCurveDialog.ui"

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
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(self.UI_PATH, parentWidget=self)
        self.setLayout(self.ui.layout())

    def createConnections(self):
        self.ui.snapshotButton.clicked.connect(self.capture_viewport)
        self.ui.saveCancelButtons.accepted.connect(self.on_accepted)
        self.ui.saveCancelButtons.rejected.connect(self.close)

    def on_accepted(self):

        # Check if a temp capture was created
        if not os.path.exists(self.TEMP_IMAGE_PATH):
            cmds.error("Please take a snapshot of the curve.")
            return

        # Check if the user has added a name for the curve
        if not self.ui.nameLineEdit.text():
            cmds.error("Please add a name for the curve.")
            return

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
                        self.save_curve(child, self.ui.nameLineEdit.text())
                        # Re-enable the parent widget
                        self.parent.setEnabled(True)
                        # Close this dialog
                        self.close()
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
                self.save_curve(selection[0], self.ui.nameLineEdit.text())
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
        # Capture the viewport as a 128x128 png named tempCapture.png
        curFrame = int(cmds.currentTime(query=True))
        cmds.playblast(
            fr=curFrame,
            v=False,
            fmt="image",
            c="png",
            orn=False,
            cf=self.TEMP_IMAGE_PATH,
            wh=[128, 128],
            p=100,
        )
        print(f"Snapshot saved as: {self.TEMP_IMAGE_PATH}")

        # Set the playblast as the image for the imageFrame
        pixmap = QtGui.QPixmap(self.TEMP_IMAGE_PATH)
        pixmap = pixmap.scaled(150, 150, QtCore.Qt.IgnoreAspectRatio)
        self.ui.imageFrame.setPixmap(pixmap)

    def save_curve(self, obj, curve_name):
        # Rename the temp capture to the curve name
        png_path = f"{self.WORKING_DIR}\\controller_data\\{curve_name}.png"
        os.rename(self.TEMP_IMAGE_PATH, png_path)

        cv_data = []
        cv_count = cmds.getAttr(f"{obj}.spans") + cmds.getAttr(f"{obj}.degree")
        degree = cmds.getAttr(f"{obj}.degree")

        for i in range(cv_count):
            cv_data.append(cmds.getAttr(f"{obj}.cv[{i}]")[0])

        json_data = {"name": curve_name, "degree": degree, "CVs": cv_data}

        try:
            with open(
                self.WORKING_DIR + "\\controller_data\\" + curve_name + ".json", "w"
            ) as curve_file:
                json.dump(json_data, curve_file)
            print(f"Saved to : {self.WORKING_DIR}\\controller_data\\{curve_name}.json")

            self.parent.populate_table()
        except:
            cmds.error(f"Could not save : {curve_name}.json")
            os.remove(png_path)

    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        Override the close event so the parent widget can be re-enabled
        """
        # Delete the temp image if it exists
        if os.path.exists(self.TEMP_IMAGE_PATH):
            os.remove(self.TEMP_IMAGE_PATH)

        # Re-enable the parent widget
        self.parent.setEnabled(True)

        # Close this dialog
        self.close()


class ControllerToolbox(QtWidgets.QDialog):
    WORKING_DIR = "Z:\Projects\MayaScripts\Tools\ControllerToolboxWidget"  # TODO Switch with this: os.path.dirname(__file__)
    CONTROLLER_DATA_DIR = WORKING_DIR + "\controller_data"
    UI_PATH = WORKING_DIR + "\\ui\\ControllerToolbox.ui"
    dlgInstance = None

    @classmethod
    def showDialog(cls):
        if not cls.dlgInstance:
            cls.dlgInstance = ControllerToolbox()

        if cls.dlgInstance.isHidden():
            cls.dlgInstance.show()
        else:
            cls.dlgInstance.raise_()
            cls.dlgInstance.activateWindow()

    def __init__(self, parent=mayaMainWindow()):
        super(ControllerToolbox, self).__init__(parent)

        self.setWindowTitle("Controller Toolbox")
        self.setMinimumSize(620, 450)
        self.resize(620, 450)

        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)

        self.initUI()
        self.createConnections()

    def initUI(self):
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(self.UI_PATH, parentWidget=self)
        self.setLayout(self.ui.layout())
        self.populate_table()

    def createConnections(self):
        # Create Button
        self.ui.createButton.clicked.connect(self.on_createButton_clicked)

        # Swap Button
        self.ui.swapButton.clicked.connect(self.on_swapButton_clicked)

        # Color Section
        self.ui.colorPickerButton.clicked.connect(self.on_color_changed)
        self.ui.rSpinBox.valueChanged.connect(self.on_color_changed)
        self.ui.gSpinBox.valueChanged.connect(self.on_color_changed)
        self.ui.bSpinBox.valueChanged.connect(self.on_color_changed)
        self.ui.hexLineEdit.textEdited.connect(self.on_color_changed)

        # Scale Buttons
        self.ui.scaleDownButton.clicked.connect(self.on_scaleButton_clicked)
        self.ui.scaleUpButton.clicked.connect(self.on_scaleButton_clicked)
        self.ui.scaleLineEdit.editingFinished.connect(self.on_scaleButton_clicked)

        # Rotate Buttons
        self.ui.rotateXDownButton.clicked.connect(self.on_rotateButton_clicked)
        self.ui.rotateXUpButton.clicked.connect(self.on_rotateButton_clicked)
        self.ui.rotateXLineEdit.returnPressed.connect(self.on_rotateButton_clicked)
        self.ui.rotateYDownButton.clicked.connect(self.on_rotateButton_clicked)
        self.ui.rotateYUpButton.clicked.connect(self.on_rotateButton_clicked)
        self.ui.rotateYLineEdit.returnPressed.connect(self.on_rotateButton_clicked)
        self.ui.rotateZDownButton.clicked.connect(self.on_rotateButton_clicked)
        self.ui.rotateZUpButton.clicked.connect(self.on_rotateButton_clicked)
        self.ui.rotateZLineEdit.returnPressed.connect(self.on_rotateButton_clicked)

        # Search Functionality
        self.ui.searchButton.clicked.connect(self.on_searchButton_clicked)
        self.ui.searchLineEdit.returnPressed.connect(self.on_searchButton_clicked)

    def populate_table(self, is_searching=False):
        """
        Populates the table widget with names and images of the existing curve JSONs and PNGs
        """

        # Clear the current model
        if self.ui.imageTable.model():
            for row in reversed(range(self.model.rowCount())):
                self.model.removeRow(row)
        else:
            self.model = QtGui.QStandardItemModel()

        # Set empty indexes at 0, 0
        i = 0
        j = 0

        # Populate the table with data from the controller data directory
        for fn in os.listdir(self.CONTROLLER_DATA_DIR):
            if fn.endswith(".json"):

                # Get the display name
                name = fn.replace(".json", "")

                # If you are searching the table, only populate it with text in the search query
                if is_searching:
                    print("CHECK 04")
                    if not (self.ui.searchLineEdit.text() in name):
                        print("CHECK 05")
                        continue

                # Check if there is an image for the controller if not, don't set an icon
                try:
                    image_path = f"{self.CONTROLLER_DATA_DIR}\\{name}.png"
                    pixmap = QtGui.QPixmap(image_path)
                    pixmap = pixmap.scaled(128, 128, QtCore.Qt.IgnoreAspectRatio)
                    icon = QtGui.QBrush(pixmap)
                    item = QtGui.QStandardItem(name)
                    item.setBackground(icon)
                except:
                    item = QtGui.QStandardItem(name)
                    cmds.warning(f"No image found for {name}")

                font = QtGui.QFont("Arial", 12, QtGui.QFont.Bold)

                item.setTextAlignment(QtCore.Qt.AlignCenter)
                item.setFont(font)

                self.model.setItem(i, j, item)

                # Increment the indexes. Keep the columns to 3 total. Rows can be infinite.
                if j == 2:
                    i += 1
                    j = 0

                else:
                    j += 1

        # Add a final QStandardItem for the add button to populate
        self.model.setItem(i, j, QtGui.QStandardItem())

        # Set the model and selection model for the table
        self.ui.imageTable.setModel(self.model)
        self.ui.imageTable.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.ui.imageTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Add the add button to the table as the final item
        add_button = QtWidgets.QPushButton("+")
        font = QtGui.QFont("Arial", 26, QtGui.QFont.Bold)
        add_button.setFont(font)
        index = self.model.index(i, j)
        self.ui.imageTable.setIndexWidget(index, add_button)

        # Connect the add button to the save_curve method
        add_button.clicked.connect(self.on_addButton_clicked)

    def on_createButton_clicked(self):
        selection_model = self.ui.imageTable.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        selected_curve = selected_indexes[0].data(QtCore.Qt.DisplayRole)
        new_curve = self.load_curve(selected_curve)

        # Set the new curve's color
        cmds.setAttr(f"{new_curve}.overrideEnabled", 1)
        cmds.setAttr(f"{new_curve}.overrideRGBColors", 1)
        cmds.setAttr(
            f"{new_curve}.overrideColorRGB",
            self.ui.rSpinBox.value() / 255,
            self.ui.gSpinBox.value() / 255,
            self.ui.bSpinBox.value() / 255,
        )

        # Set the new curve's scale
        # TODO setup appropriate checks!
        cmds.setAttr(
            f"{new_curve}.scale",
            float(self.ui.scaleLineEdit.text()),
            float(self.ui.scaleLineEdit.text()),
            float(self.ui.scaleLineEdit.text()),
        )

        # Set the new curve's rotation
        # TODO setup appropriate checks!
        cmds.setAttr(
            f"{new_curve}.rotate",
            float(self.ui.rotateXLineEdit.text()),
            float(self.ui.rotateYLineEdit.text()),
            float(self.ui.rotateZLineEdit.text()),
        )
        cmds.makeIdentity(new_curve, apply=True)

        # Add custom attributes
        cmds.addAttr(
            new_curve,
            longName="defaultScale",
            shortName="dScale",
            attributeType="double",
            dv=1,
        )

    def on_swapButton_clicked(self):
        print("TODO Swap Button")
        # Get the selection
        # For Loop iterate thru the selection
        #   Get the attributes from the curve (Name, Trans, Rot, Scale)
        #   Get the parent and children of the curve
        #   Delete the curve
        #   Create the new curve while maintaining the hierarchy (Think offset groups parents or children)
        #   Apply the attributes (Name, Trans, Rot, Scale)

    def on_color_changed(self):

        # Check if the sender was the colorPickerButton
        if self.sender() == self.ui.colorPickerButton:
            cmds.colorEditor()

            # If color editor exited with Accept, else don't run the code
            if cmds.colorEditor(result=True, q=True):
                color = cmds.colorEditor(rgb=True, q=True)
                r = int(color[0] * 255)
                g = int(color[1] * 255)
                b = int(color[2] * 255)

                print(r, g, b)

                self.ui.rSpinBox.setValue(r)
                self.ui.gSpinBox.setValue(g)
                self.ui.bSpinBox.setValue(b)
                self.ui.hexLineEdit.setText("{:02x}{:02x}{:02x}".format(r, g, b))
                self.ui.colorPickerButton.setStyleSheet(
                    f"background-color: rgb({r}, {g}, {b})"
                )

            else:
                return
        # Check if the sender was any of the RGB Spin Boxes
        elif (
            self.sender() == self.ui.rSpinBox
            or self.sender() == self.ui.gSpinBox
            or self.sender() == self.ui.bSpinBox
        ):
            r = self.ui.rSpinBox.value()
            g = self.ui.gSpinBox.value()
            b = self.ui.bSpinBox.value()
            self.ui.hexLineEdit.setText("{:02x}{:02x}{:02x}".format(r, g, b))
            self.ui.colorPickerButton.setStyleSheet(
                f"background-color: rgb({r}, {g}, {b})"
            )
        # Check if the sender was the hexLineEdit
        elif self.sender() == self.ui.hexLineEdit:
            hex_string = self.ui.hexLineEdit.text()
            hex_list = list(hex_string)
            rgb = []

            if len(hex_string) == 6:
                for i in range(3):
                    first = hex_list.pop(0)
                    second = hex_list.pop(0)
                    rgb.append(int(f"{first}{second}", 16))

                self.ui.rSpinBox.setValue(rgb[0])
                self.ui.gSpinBox.setValue(rgb[1])
                self.ui.bSpinBox.setValue(rgb[2])
                self.ui.colorPickerButton.setStyleSheet(
                    f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
                )

        # Check if there is a selected curve, then change its color
        selection = cmds.ls(selection=True)

        # Filter the selection so only nurbsCurves will be edited
        for curve_transform in selection:
            children = cmds.listRelatives(
                curve_transform, children=True, type="nurbsCurve"
            )
            if children is not None:
                cmds.setAttr(f"{curve_transform}.overrideEnabled", 1)
                cmds.setAttr(f"{curve_transform}.overrideRGBColors", 1)
                cmds.setAttr(
                    f"{curve_transform}.overrideColorRGB",
                    self.ui.rSpinBox.value() / 255,
                    self.ui.gSpinBox.value() / 255,
                    self.ui.bSpinBox.value() / 255,
                )

    def on_scaleButton_clicked(self):
        """
        Scales all items in the selection list up or down
        """
        selection = cmds.ls(selection=True)

        # Filter the selection so only nurbsCurves will be edited
        for curve_transform in selection:
            children = cmds.listRelatives(
                curve_transform, children=True, type="nurbsCurve"
            )
            if children is not None:
                current_scale = cmds.getAttr(f"{curve_transform}.scale")

                # All objects edited/created by this tool should have an attribute defaultScale to track their initial starting size
                try:
                    scale_mod = cmds.getAttr(f"{curve_transform}.defaultScale")
                except:
                    cmds.addAttr(
                        curve_transform,
                        longName="defaultScale",
                        shortName="dScale",
                        attributeType="double",
                        dv=1,
                    )
                    scale_mod = cmds.getAttr(f"{curve_transform}.defaultScale")

                # Check if the sender was the scaleUpButton
                if self.sender() == self.ui.scaleUpButton:
                    cmds.setAttr(
                        f"{curve_transform}.scale",
                        current_scale[0][0] + 0.1,
                        current_scale[0][1] + 0.1,
                        current_scale[0][2] + 0.1,
                    )
                    cmds.makeIdentity(curve_transform, apply=True)

                # Check if the sender was the scaleDownButton
                elif self.sender() == self.ui.scaleDownButton:
                    cmds.setAttr(
                        f"{curve_transform}.scale",
                        current_scale[0][0] - 0.1,
                        current_scale[0][1] - 0.1,
                        current_scale[0][2] - 0.1,
                    )
                    cmds.makeIdentity(curve_transform, apply=True)

                # Check if the sender was the scaleLineEdit
                elif self.sender() == self.ui.scaleLineEdit:

                    user_scale = float(self.ui.scaleLineEdit.text())

                    cmds.setAttr(
                        f"{curve_transform}.scale",
                        current_scale[0][0] * (user_scale / scale_mod),
                        current_scale[0][1] * (user_scale / scale_mod),
                        current_scale[0][2] * (user_scale / scale_mod),
                    )
                    cmds.makeIdentity(curve_transform, apply=True)
                    cmds.setAttr(f"{curve_transform}.defaultScale", user_scale)

    def on_rotateButton_clicked(self):
        """
        Rotates all items in the selection list up or down
        """
        selection = cmds.ls(selection=True)
        rot_value = 5

        # Filter the selection so only nurbsCurves will be edited
        for curve_transform in selection:
            children = cmds.listRelatives(
                curve_transform, children=True, type="nurbsCurve"
            )

            if children is not None:

                # Check if the sender was the rotateXDownButton
                if self.sender() == self.ui.rotateXDownButton:
                    cmds.setAttr(f"{curve_transform}.rotateX", -1 * rot_value)
                # Check if the sender was the rotateXUpButton
                elif self.sender() == self.ui.rotateXUpButton:
                    cmds.setAttr(f"{curve_transform}.rotateX", rot_value)
                # Check if the sender was the rotateXLineEdit
                elif self.sender() == self.ui.rotateXLineEdit:
                    cmds.setAttr(
                        f"{curve_transform}.rotateX",
                        float(self.ui.rotateXLineEdit.text()),
                    )

                # Check if the sender was the rotateYDownButton
                elif self.sender() == self.ui.rotateYDownButton:
                    cmds.setAttr(f"{curve_transform}.rotateY", -1 * rot_value)
                # Check if the sender was the rotateYUpButton
                elif self.sender() == self.ui.rotateYUpButton:
                    cmds.setAttr(f"{curve_transform}.rotateY", rot_value)
                # Check if the sender was the rotateYLineEdit
                elif self.sender() == self.ui.rotateXLineEdit:
                    cmds.setAttr(
                        f"{curve_transform}.rotateY",
                        float(self.ui.rotateYLineEdit.text()),
                    )

                # Check if the sender was the rotateZDownButton
                elif self.sender() == self.ui.rotateZDownButton:
                    cmds.setAttr(f"{curve_transform}.rotateZ", -1 * rot_value)
                # Check if the sender was the rotateZUpButton
                elif self.sender() == self.ui.rotateZUpButton:
                    cmds.setAttr(f"{curve_transform}.rotateZ", rot_value)
                # Check if the sender was the rotateZLineEdit
                elif self.sender() == self.ui.rotateZLineEdit:
                    cmds.setAttr(
                        f"{curve_transform}.rotateZ",
                        float(self.ui.rotateZLineEdit.text()),
                    )

                cmds.makeIdentity(curve_transform, apply=True)

    def on_searchButton_clicked(self):
        """
        Repopulates the table with the queried control name
        """

        # Passing in True to make the table searchable
        self.populate_table(True)

    def on_addButton_clicked(self):
        self.setEnabled(False)
        self.CreateDialog = CreateNewCurveDialog(self)
        self.CreateDialog.show()

    def load_curve(self, file_name):
        """
        Opens the JSON file passed in and creates a curve based on its data
        :param file_name: file path for the JSON being opened
        :return: returns a reference to the curve created
        """
        curve_name = ""
        cv_data = []

        try:
            with open(
                self.CONTROLLER_DATA_DIR + "\\" + file_name + ".json", "r"
            ) as curve_file:
                data = json.load(curve_file)
                curve_name = data["name"]
                cv_data = data["CVs"]
                degree = data["degree"]

            my_curve = cmds.curve(p=cv_data, d=degree, name=curve_name)
        except:
            cmds.error(
                f"Could not load data from {self.CONTROLLER_DATA_DIR}\\{file_name}.json"
            )

        return my_curve


if __name__ == "__main__":
    try:
        controllerToolboxDialog.close()  # pylint: disable=E0601
        controllerToolboxDialog.deleteLater()
    except:
        pass
    controllerToolboxDialog = ControllerToolbox()
    controllerToolboxDialog.show()
