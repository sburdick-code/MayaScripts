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
        
        self.create_icons()
        
        self.refresh_tree_widget()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setSelectionMode(QtWidgets.QTreeWidget.ExtendedSelection)
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
        self.tree_widget.itemSelectionChanged.connect(self.select_items)
        self.tree_widget.itemCollapsed.connect(self.update_icon)
        self.tree_widget.itemExpanded.connect(self.update_icon)
        
        self.refresh_btn.clicked.connect(self.refresh_tree_widget)
        
    def create_icons(self):
        self.transform_icon = QtGui.QIcon(":transform.svg")
        self.camera_icon = QtGui.QIcon(":Camera.png")
        self.mesh_icon = QtGui.QIcon(":mesh.svg")
        
    def refresh_tree_widget(self):
        self.tree_widget.clear()
        
        self.shape_nodes = cmds.ls(shapes=True)
        
        top_level_object_names = cmds.ls(assemblies=True)
        for name in top_level_object_names:
            item = self.create_item(name)
            self.tree_widget.addTopLevelItem(item)
        
    def create_item(self, text):
        item = QtWidgets.QTreeWidgetItem([text])
        self.add_children(item)
        
        self.update_icon(item)
        
        is_shape = text in self.shape_nodes
        item.setData(0, QtCore.Qt.UserRole, is_shape)
        
        return item
        
    def add_children(self, item):
        children = cmds.listRelatives(item.text(0), children=True)
        if children:
            for child in children:
                child_item = self.create_item(child)
                item.addChild(child_item)
                
    def update_icon(self, item):
        object_type = "transform"
        
        if not item.isExpanded():
            child_count = item.childCount()
            
            if child_count == 0:
                object_type = cmds.objectType(item.text(0))
            elif child_count == 1:
                child_item = item.child(0)
                object_type = cmds.objectType(child_item.text(0))
                
        if object_type == "transform":
            item.setIcon(0, self.transform_icon)
        elif object_type == "camera":
            item.setIcon(0, self.camera_icon)
        elif object_type == "mesh":
            item.setIcon(0, self.mesh_icon)
        
    def select_items(self):
        names = []
        items = self.tree_widget.selectedItems()
        for item in items:
            names.append(item.text(0))
            
        cmds.select(names, replace=True)


if __name__ == "__main__":

    try:
        outliner_dialog.close() # pylint: disable=E0601
        outliner_dialog.deleteLater()
    except:
        pass

    outliner_dialog = OutlinerDialog()
    outliner_dialog.show()










