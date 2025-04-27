try:
    from PySide2 import QtCore, QtWidgets, QtUiTools, QtGui
    from PySide2.QtWidgets import QAction
    from shiboken2 import wrapInstance
except:
    from PySide6 import QtCore, QtWidgets, QtUiTools, QtGui
    from PySide6.QtGui import QAction
    from shiboken6 import wrapInstance

import sys
import os
import maya.OpenMayaUI as omui
import maya.cmds as cmds

from Tools.ControllerToolboxWidget.Const import Const
from Tools.ControllerToolboxWidget import curveTools
from Tools.ControllerToolboxWidget.HelperDialogs import (
    CreateNewCurveDialog,
    RenameDialog,
)


def mayaMainWindow():
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mainWindowPtr), QtWidgets.QWidget)


class ControllerToolbox(QtWidgets.QDialog):

    # custom resized signal
    resized = QtCore.Signal()

    def __init__(self, parent=mayaMainWindow()):
        super(ControllerToolbox, self).__init__(parent)

        self.setWindowTitle("Controller Toolbox")
        self.setMinimumSize(620, 450)
        self.resize(620, 450)

        self.CreateDialog = None
        self.RenameDialog = None

        # On macOS make the window a Tool to keep it on top of Maya
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
            (Const.UI_DIR + "ControllerToolbox.ui"), parentWidget=self
        )
        self.setLayout(self.ui.layout())
        self.populate_table()

    def createConnections(self):
        """
        Create necessary connections for the ui
        """

        # Search Functionality
        self.ui.searchButton.clicked.connect(self.on_searchButton_clicked)
        self.ui.searchLineEdit.returnPressed.connect(self.on_searchButton_clicked)

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

        # Create Button
        self.ui.createButton.clicked.connect(self.on_createButton_clicked)

        # Swap Button
        self.ui.swapButton.clicked.connect(self.on_swapButton_clicked)

        # Table Widget Context Menu
        self.ui.imageTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.imageTable.customContextMenuRequested.connect(self.show_context_menu)

        # Resize window
        self.resized.connect(self.populate_table)

    def resizeEvent(self, event):
        """
        Override the resize event so any the table repopulates over a certain window sizes
        """
        self.resized.emit()
        return super(ControllerToolbox, self).resizeEvent(event)

    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        Override the close event so any extra child widgets will also close
        """
        # Close any extra widgets if they're open
        if self.CreateDialog is not None:
            self.CreateDialog.close()
        if self.RenameDialog is not None:
            self.RenameDialog.close()

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

        # Calculate the number of columns based on the window's size
        size_tuple = self.size().toTuple()
        size_x = size_tuple[0]
        table_width = size_x - 236
        column_count = (table_width / 128) // 1
        self.model.setColumnCount(column_count)

        # Populate the table with data from the controller data directory
        for fn in os.listdir(Const.CTRL_DATA_DIR):
            if fn.endswith(".json"):

                # Get the display name
                name = fn.replace(".json", "")

                # If you are searching the table, only populate it with text in the search query
                if is_searching:
                    if not (self.ui.searchLineEdit.text() in name):
                        continue

                # Check if there is an image for the controller if not, don't set an icon
                try:
                    image_path = f"{Const.CTRL_DATA_DIR}{name}.png"
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

                # Increment the indexes. Rows can be infinite.
                if j >= (column_count - 1):
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
        """
        Create a new curve from the selection table and add all the attributes selected.
        """
        try:
            selection_model = self.ui.imageTable.selectionModel()
            selected_indexes = selection_model.selectedIndexes()

            selected_curve = selected_indexes[0].data(QtCore.Qt.DisplayRole)
        except:
            cmds.warning("Please select a curve from the table to create.")

        new_curve = curveTools.load_curve(selected_curve)

        if not new_curve:
            cmds.warning("Could not create curve, incorrect data!")
            return

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
        try:
            if float(self.ui.scaleLineEdit.text()) <= 0.0:
                cmds.warning("Cannot create curve : Scale must be greater than 0")
                cmds.delete(new_curve)
                return
            else:
                cmds.setAttr(
                    f"{new_curve}.scale",
                    float(self.ui.scaleLineEdit.text()),
                    float(self.ui.scaleLineEdit.text()),
                    float(self.ui.scaleLineEdit.text()),
                )
                cmds.makeIdentity(new_curve, apply=True)
        except:
            cmds.warning("Cannot create curve : Scale must be a numeric value!")
            cmds.delete(new_curve)
            return

        # Set the new curve's rotation
        try:
            cmds.setAttr(
                f"{new_curve}.rotate",
                float(self.ui.rotateXLineEdit.text()),
                float(self.ui.rotateYLineEdit.text()),
                float(self.ui.rotateZLineEdit.text()),
            )
            cmds.makeIdentity(new_curve, apply=True)
        except:
            cmds.warning("Cannot create curve : Rotation must be a numeric value!")
            cmds.delete(new_curve)
            return

        # Add custom attributes
        ## Scale
        cmds.addAttr(
            new_curve,
            longName="defaultScale",
            shortName="dScale",
            attributeType="double",
            dv=float(self.ui.scaleLineEdit.text()),
        )
        ## Rotate
        cmds.addAttr(
            new_curve,
            longName="defaultRotation",
            shortName="dRot",
            attributeType="float3",
        )
        cmds.addAttr(
            longName="dRotateX",
            attributeType="float",
            parent="defaultRotation",
            dv=float(self.ui.rotateXLineEdit.text()),
        )
        cmds.addAttr(
            longName="dRotateY",
            attributeType="float",
            parent="defaultRotation",
            dv=float(self.ui.rotateYLineEdit.text()),
        )
        cmds.addAttr(
            longName="dRotateZ",
            attributeType="float",
            parent="defaultRotation",
            dv=float(self.ui.rotateZLineEdit.text()),
        )

    def on_swapButton_clicked(self):
        """
        Swap the old curve shape for the selected curve in the selection window.
        """
        # Get the selection
        selection = cmds.ls(selection=True)

        for transform in selection:

            # Create a new curve
            selection_model = self.ui.imageTable.selectionModel()
            selected_indexes = selection_model.selectedIndexes()
            selected_curve = selected_indexes[0].data(QtCore.Qt.DisplayRole)
            new_curve_transform = curveTools.load_curve(selected_curve)

            # Get the curve objects - children of the transforms
            new_curve = cmds.listRelatives(new_curve_transform, children=True)
            old_curve = cmds.listRelatives(transform, children=True)

            # Set the new curve's location
            if cmds.xform(transform, t=True, q=True) == [0, 0, 0]:
                cmds.matchTransform(new_curve_transform, transform, pos=True)

            # Set the new curve's scale
            try:
                scale_mod = cmds.getAttr(f"{transform}.defaultScale")
            except:
                print("No defaultScale attribute on swapped out curve")
                scale_mod = 1
                cmds.addAttr(
                    transform,
                    longName="defaultScale",
                    shortName="dScale",
                    attributeType="double",
                    dv=1,
                )

            cmds.xform(new_curve_transform, scale=[scale_mod, scale_mod, scale_mod])

            # Set the new curve's rotate
            try:
                rot_mod = cmds.getAttr(f"{transform}.defaultRotation")[0]
            except:
                print("No defaultRotation attribute on swapped out curve")
                rot_mod = [0, 0, 0]
                cmds.addAttr(
                    new_curve,
                    longName="defaultRotation",
                    shortName="dRot",
                    attributeType="float3",
                )
                cmds.addAttr(
                    longName="dRotateX",
                    attributeType="float",
                    parent="defaultRotation",
                    dv=0.0,
                )
                cmds.addAttr(
                    longName="dRotateY",
                    attributeType="float",
                    parent="defaultRotation",
                    dv=0.0,
                )
                cmds.addAttr(
                    longName="dRotateZ",
                    attributeType="float",
                    parent="defaultRotation",
                    dv=0.0,
                )

            cmds.xform(new_curve_transform, rotation=rot_mod)

            # Freeze transformations on the new curve
            cmds.makeIdentity(new_curve_transform, a=True)

            # Parent the new curve under the old curve's transform
            cmds.parent(new_curve, transform, r=True, s=True)

            # # Delete the old curve and the new curve transform
            cmds.delete(new_curve_transform)
            cmds.delete(old_curve)

        cmds.select(selection)

    def on_color_changed(self):
        """
        Whenever any change is made to the color, update the UI to reflect
        this change.
        """

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

            try:
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
            except:
                cmds.warning("Invalid Hex value")

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
                        current_scale[0][0] * ((scale_mod + 0.1) / scale_mod),
                        current_scale[0][1] * ((scale_mod + 0.1) / scale_mod),
                        current_scale[0][2] * ((scale_mod + 0.1) / scale_mod),
                    )
                    cmds.makeIdentity(curve_transform, apply=True)
                    cmds.setAttr(
                        f"{curve_transform}.defaultScale",
                        (scale_mod + 0.1),
                    )
                    self.ui.scaleLineEdit.setText(f"{(scale_mod + 0.1):.2f}")

                # Check if the sender was the scaleDownButton
                elif self.sender() == self.ui.scaleDownButton:
                    cmds.setAttr(
                        f"{curve_transform}.scale",
                        current_scale[0][0] * ((scale_mod - 0.1) / scale_mod),
                        current_scale[0][1] * ((scale_mod - 0.1) / scale_mod),
                        current_scale[0][2] * ((scale_mod - 0.1) / scale_mod),
                    )
                    cmds.makeIdentity(curve_transform, apply=True)
                    cmds.setAttr(
                        f"{curve_transform}.defaultScale",
                        (scale_mod - 0.1),
                    )
                    self.ui.scaleLineEdit.setText(f"{(scale_mod - 0.1):.2f}")

                # Check if the sender was the scaleLineEdit
                elif self.sender() == self.ui.scaleLineEdit:
                    try:
                        user_scale = float(self.ui.scaleLineEdit.text())
                    except:
                        cmds.warning("Scale must be a numeric value!")
                        return

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

                # All objects edited/created by this tool should have an attribute defaultRotation to track their initial starting rotation
                try:
                    rot_mod = cmds.getAttr(f"{curve_transform}.defaultRotation")[0]
                except:
                    cmds.addAttr(
                        curve_transform,
                        longName="defaultRotation",
                        shortName="dRot",
                        attributeType="float3",
                    )

                    cmds.addAttr(
                        longName="dRotateX",
                        attributeType="float",
                        parent="defaultRotation",
                    )
                    cmds.addAttr(
                        longName="dRotateY",
                        attributeType="float",
                        parent="defaultRotation",
                    )
                    cmds.addAttr(
                        longName="dRotateZ",
                        attributeType="float",
                        parent="defaultRotation",
                    )
                    rot_mod = cmds.getAttr(f"{curve_transform}.defaultRotation")[0]

                # Rotate X
                if (
                    self.sender() == self.ui.rotateXDownButton
                    or self.sender() == self.ui.rotateXUpButton
                    or self.sender() == self.ui.rotateXLineEdit
                ):
                    # Check if the sender was the rotateXDownButton
                    if self.sender() == self.ui.rotateXDownButton:
                        rotater = -1 * rot_value
                    # Check if the sender was the rotateXUpButton
                    elif self.sender() == self.ui.rotateXUpButton:
                        rotater = rot_value
                    # Check if the sender was the rotateXLineEdit
                    elif self.sender() == self.ui.rotateXLineEdit:
                        try:
                            rotater = float(self.ui.rotateXLineEdit.text()) - rot_mod[0]
                        except:
                            cmds.warning("Rotate X must be a numeric value!")
                            return

                    # Set the rotation
                    cmds.setAttr(f"{curve_transform}.rotateX", rotater)
                    cmds.setAttr(f"{curve_transform}.dRotateX", rotater + rot_mod[0])
                    self.ui.rotateXLineEdit.setText(str(rotater + rot_mod[0]))

                # Rotate Y
                if (
                    self.sender() == self.ui.rotateYDownButton
                    or self.sender() == self.ui.rotateYUpButton
                    or self.sender() == self.ui.rotateYLineEdit
                ):
                    # Check if the sender was the rotateYDownButton
                    if self.sender() == self.ui.rotateYDownButton:
                        rotater = -1 * rot_value
                    # Check if the sender was the rotateYUpButton
                    elif self.sender() == self.ui.rotateYUpButton:
                        rotater = rot_value
                    # Check if the sender was the rotateYLineEdit
                    elif self.sender() == self.ui.rotateYLineEdit:
                        try:
                            rotater = float(self.ui.rotateYLineEdit.text()) - rot_mod[1]
                        except:
                            cmds.warning("Rotate Y must be a numeric value!")
                            return
                    # Set the rotation
                    cmds.setAttr(f"{curve_transform}.rotateY", rotater)
                    cmds.setAttr(f"{curve_transform}.dRotateY", rotater + rot_mod[1])
                    self.ui.rotateYLineEdit.setText(str(rotater + rot_mod[1]))

                # Rotate Z
                if (
                    self.sender() == self.ui.rotateZDownButton
                    or self.sender() == self.ui.rotateZUpButton
                    or self.sender() == self.ui.rotateZLineEdit
                ):
                    # Check if the sender was the rotateZDownButton
                    if self.sender() == self.ui.rotateZDownButton:
                        rotater = -1 * rot_value

                    # Check if the sender was the rotateZUpButton
                    elif self.sender() == self.ui.rotateZUpButton:
                        rotater = rot_value

                    # Check if the sender was the rotateZLineEdit
                    elif self.sender() == self.ui.rotateZLineEdit:
                        try:
                            rotater = float(self.ui.rotateZLineEdit.text()) - rot_mod[2]
                        except:
                            cmds.warning("Rotate X must be a numeric value!")
                            return
                    # Set the rotation
                    cmds.setAttr(f"{curve_transform}.rotateZ", rotater)
                    cmds.setAttr(f"{curve_transform}.dRotateZ", rotater + rot_mod[2])
                    self.ui.rotateZLineEdit.setText(str(rotater + rot_mod[2]))

                # Freeze transformations
                cmds.makeIdentity(curve_transform, apply=True)

    def on_searchButton_clicked(self):
        """
        Repopulates the table with the queried control name
        """
        # Passing in True to make the table searchable
        self.populate_table(True)

    def on_addButton_clicked(self):
        """
        When the addButton is clicked, create a new dialog to handle
        saving the new curve to a json with the proper attributes.
        """
        self.setEnabled(False)
        self.CreateDialog = CreateNewCurveDialog(self)
        self.CreateDialog.show()

    def show_context_menu(self, pos):

        # If the user right-clicks on nothing, don't create the context menu
        selection_model = self.ui.imageTable.selectionModel()
        indexes = selection_model.selectedIndexes()
        if not indexes[0].data(QtCore.Qt.DisplayRole):
            return

        # Create the context menu
        menu = QtWidgets.QMenu()

        rename_action = QAction("Rename Selected", self)
        delete_action = QAction("Delete Selected", self)
        menu.addAction(rename_action)
        menu.addAction(delete_action)

        rename_action.triggered.connect(self.on_rename_action_triggered)
        delete_action.triggered.connect(self.on_delete_action_triggered)

        # Display the context menu
        pos_offset = pos + QtCore.QPoint(226, 15)
        menu.exec_(self.mapToGlobal(pos_offset))

    def on_rename_action_triggered(self):
        # Get the selection from the table
        try:
            selection_model = self.ui.imageTable.selectionModel()
            selected_indexes = selection_model.selectedIndexes()

            curve_name = selected_indexes[0].data(QtCore.Qt.DisplayRole)
        except:
            cmds.warning("Please select a curve from the table to rename.")

        # Query the user for the new name and rename the curve data using
        self.setEnabled(False)
        self.RenameDialog = RenameDialog(self, curve_name)
        self.RenameDialog.show()

    def on_delete_action_triggered(self):
        # Get the selection from the table
        try:
            selection_model = self.ui.imageTable.selectionModel()
            selected_indexes = selection_model.selectedIndexes()

            curve_name = selected_indexes[0].data(QtCore.Qt.DisplayRole)
        except:
            cmds.warning("Please select a curve from the table to delete.")

        # Validate user choice
        json_path = Const.CTRL_DATA_DIR + curve_name + ".json"
        png_path = Const.CTRL_DATA_DIR + curve_name + ".png"

        if os.path.exists(json_path):
            qm = QtWidgets.QMessageBox
            message = f"Are you sure you want\nto delete {curve_name}?"
            user_input = qm.question(
                self,
                f"Delete {curve_name}",
                message,
                qm.Yes | qm.No,
            )
            if user_input == qm.No:
                return
            else:
                # Delete the curve data
                os.remove(json_path)
                try:
                    os.remove(png_path)
                except:
                    cmds.warning("No associated png to delete.")

        # Reload the table
        self.populate_table()


if __name__ == "__main__":
    try:
        controllerToolboxDialog.close()  # pylint: disable=E0601
        controllerToolboxDialog.deleteLater()
    except:
        pass
    controllerToolboxDialog = ControllerToolbox()
    controllerToolboxDialog.show()
