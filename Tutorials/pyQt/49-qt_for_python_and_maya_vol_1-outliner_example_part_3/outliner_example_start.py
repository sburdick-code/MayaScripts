try:
    # Qt5
    from PySide2 import QtCore
    from PySide2 import QtGui
    from PySide2 import QtWidgets
    from shiboken2 import wrapInstance
except:
    # Qt6
    from PySide6 import QtCore
    from PySide6 import QtGui
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance
    
import sys
import maya.OpenMayaUI as omui
import maya.cmds as cmds


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class OutlinerDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(OutlinerDialog, self).__init__(parent)

        self.setWindowTitle("Outliner")
        self.setMinimumSize(300, 400)

        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        

    def create_layout(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_btn)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.addWidget(self.tree_widget)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.refresh_btn.clicked.connect(self.refresh_tree_widget)
        
    def refresh_tree_widget(self):
        print("TODO: refresh_tree_widget")
        
        self.tree_widget.clear()
        
        top_level_item = QtWidgets.QTreeWidgetItem(["Top Level 1"])
        self.tree_widget.addTopLevelItem(top_level_item)
        
        child_item = QtWidgets.QTreeWidgetItem(["Child 1"])
        top_level_item.addChild(child_item)
        
        gc_item = QtWidgets.QTreeWidgetItem(["Grandchild 1"])
        child_item.addChild(gc_item)
        
        top_level_item = QtWidgets.QTreeWidgetItem(["Top Level 2"])
        self.tree_widget.addTopLevelItem(top_level_item)


if __name__ == "__main__":

    try:
        outliner_dialog.close() # pylint: disable=E0601
        outliner_dialog.deleteLater()
    except:
        pass

    outliner_dialog = OutlinerDialog()
    outliner_dialog.show()










