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

import sys


def mayaMainWindow():
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mainWindowPtr), QtWidgets.QWidget)


class RBFNodeTree(QtWidgets.QDialog):

    def __init__(self, parent=mayaMainWindow()):
        super(RBFNodeTree, self).__init__(parent)

        self.setWindowTitle("RBF Node Tree")
        self.setMinimumSize(300, 400)

        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)

        self.createWidgets()
        self.createLayouts()
        self.createConnections()
        self.createIcons()

        self.refreshTreeWidget()

    def createWidgets(self):
        self.rbfTree_Tree = QtWidgets.QTreeWidget()
        self.rbfTree_Tree.setSelectionMode(QtWidgets.QTreeWidget.ExtendedSelection)
        self.rbfTree_Tree.setHeaderHidden(True)

        self.refresh_Button = QtWidgets.QPushButton("Refresh")

    def createLayouts(self):
        main_Layout = QtWidgets.QVBoxLayout(self)
        main_Layout.setContentsMargins(2, 2, 2, 2)
        main_Layout.setSpacing(2)
        main_Layout.addWidget(self.rbfTree_Tree)
        main_Layout.addWidget(self.refresh_Button)

    def createConnections(self):
        self.refresh_Button.clicked.connect(self.refreshTreeWidget)

    def createIcons(self):
        self.item_Icon = QtGui.QIcon(":cube.png")
        self.node_Icon = QtGui.QIcon(":dollyCursor.png")

        self.rootClosed_Icon = QtGui.QIcon(":branch-root-closed.svg")
        self.rootOpen_Icon = QtGui.QIcon(":branch-root-open.svg")
        self.branchMore_Icon = QtGui.QIcon(":branch-more.svg")
        self.branchEnd_Icon = QtGui.QIcon(":branch-end.svg")

    def refreshTreeWidget(self):
        self.rbfTree_Tree.clear()

        self.rbfNodes = cmds.ls(exactType="SoxsRBFNode")

        for node in self.rbfNodes:
            item = self.createItem(node.replace("_RBF", ""))
            self.rbfTree_Tree.addTopLevelItem(item)

    def createItem(self, text):
        item = QtWidgets.QTreeWidgetItem([text])
        self.addChildren(item)
        self.updateIcon(item)

        return item

    def addChildren(self, item):

        if not cmds.objExists(f"{item.text(0)}_RBF"):
            return

        node = item.text(0) + "_RBF"
        driver = cmds.listConnections(node, source=True, destination=False)
        driven = cmds.listConnections(node, source=False, destination=True)
        driverAttribs = cmds.listConnections(node, s=True, d=False, plugs=True)
        drivenAttribs = cmds.listConnections(node, s=False, d=True, plugs=True)

        # No driver or driven were attached
        if driverAttribs == None:
            return
        if drivenAttribs == None:
            return

        driverMainAttrib = (
            driverAttribs[0]
            .replace(driver[0] + ".", "")
            .replace("X", "")
            .replace("Y", "")
            .replace("Z", "")
        )
        drivenMainAttrib = (
            drivenAttribs[0]
            .replace(driven[0] + ".", "")
            .replace("X", "")
            .replace("Y", "")
            .replace("Z", "")
        )

        driverAttribsStr = ["_", "_", "_"]
        drivenAttribsStr = ["_", "_", "_"]

        for attrib in driverAttribs:
            if "X" in attrib.replace(driver[0], ""):
                driverAttribsStr[0] = "x"
            elif "Y" in attrib.replace(driver[0], ""):
                driverAttribsStr[1] = "y"
            elif "Z" in attrib.replace(driver[0], ""):
                driverAttribsStr[2] = "z"
            else:
                driverAttribsStr = ["x", "y", "z"]

        for attrib in drivenAttribs:
            if "X" in attrib.replace(driven[0], ""):
                drivenAttribsStr[0] = "x"
            elif "Y" in attrib.replace(driven[0], ""):
                drivenAttribsStr[1] = "y"
            elif "Z" in attrib.replace(driven[0], ""):
                drivenAttribsStr[2] = "z"
            else:
                drivenAttribsStr = ["x", "y", "z"]

        driverStr = f"{driver[0]} | {driverMainAttrib} | {''.join(driverAttribsStr)}"
        drivenStr = f"{driven[0]} | {drivenMainAttrib} | {''.join(drivenAttribsStr)}"

        driverItem = self.createItem(driverStr)
        drivenItem = self.createItem(drivenStr)
        nodeItem = self.createItem(node)

        item.addChild(driverItem)
        item.addChild(nodeItem)
        item.addChild(drivenItem)

    def updateIcon(self, item):

        # Check if it is the title
        if cmds.objExists(f"{item.text(0)}_RBF"):
            return

        if cmds.objExists(item.text(0)):
            item.setIcon(0, self.node_Icon)
        else:
            item.setIcon(0, self.item_Icon)


if __name__ == "__main__":
    myWidget = RBFNodeTree()
    myWidget.show()
