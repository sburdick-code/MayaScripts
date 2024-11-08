try:
    # Qt5
    from PySide2 import QtCore
    from PySide2 import QtGui
    from PySide2 import QtWidgets
    from shiboken2 import wrapInstance
    from shiboken2 import getCppPointer
    
    from PySide2.QtWidgets import QAction
except:
    # Qt6
    from PySide6 import QtCore
    from PySide6 import QtGui
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance
    from shiboken6 import getCppPointer
    
    from PySide6.QtGui import QAction
    
import sys

from functools import partial

import maya.OpenMayaUI as omui
import maya.cmds as cmds

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


class OutlinerWidget(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    
    OBJECT_NAME = "OutlinerWidget"
    
    @classmethod
    def workspace_control_name(cls):
        return "{0}WorkspaceControl".format(cls.OBJECT_NAME)
        
    @classmethod
    def workspace_ui_script(cls):
        return "from outliner_example import OutlinerWidget\noutliner_widget = OutlinerWidget()"

    def __init__(self):
        super().__init__()
        
        self.setObjectName(self.OBJECT_NAME)

        self.setWindowTitle("Outliner")
        self.setMinimumSize(300, 400)
            
        self.script_job_number = -1
        
        self.add_to_workspace_control()

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        
        self.create_icons()
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        self.refresh_tree_widget()
        
    def add_to_workspace_control(self):
        workspace_control = omui.MQtUtil.findControl(self.workspace_control_name())
        if workspace_control:
            workspace_control_ptr = int(workspace_control)
            widget_ptr = int(getCppPointer(self)[0])
            
            omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)

    def create_actions(self):
        self.shape_nodes_visible_action = QAction("Shapes", self)
        self.shape_nodes_visible_action.setCheckable(True)
        self.shape_nodes_visible_action.setChecked(True)
        self.shape_nodes_visible_action.setShortcut(QtGui.QKeySequence("Ctrl+Shift+H"))
        
        self.about_action = QAction("About", self)

    def create_widgets(self):
        self.menu_bar = QtWidgets.QMenuBar()
        display_menu = self.menu_bar.addMenu("Display")
        display_menu.addAction(self.shape_nodes_visible_action)
        
        help_menu = self.menu_bar.addMenu("Help")
        help_menu.addAction(self.about_action)
        
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
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addWidget(self.tree_widget)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.shape_nodes_visible_action.toggled.connect(self.set_shape_nodes_visible)
        self.about_action.triggered.connect(self.show_about)
        
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
        
    def set_shape_nodes_visible(self, visible):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tree_widget)
        while iterator.value():
            item = iterator.value()
            is_shape = item.data(0, QtCore.Qt.UserRole)
            if is_shape:
                item.setHidden(not visible)
                
            iterator += 1
        
    def show_about(self):
        QtWidgets.QMessageBox.about(self, "About Outliner", "Add About Text Here")
        
    def show_context_menu(self, point):
        context_menu = QtWidgets.QMenu()
        
        context_menu.addAction(self.shape_nodes_visible_action)
        context_menu.addSeparator()
        context_menu.addAction(self.about_action)
        
        context_menu.exec_(self.mapToGlobal(point))
        
    def update_selection(self):
        selection = cmds.ls(selection=True)
        
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tree_widget)
        while iterator.value():
            item = iterator.value()
            is_selected = item.text(0) in selection
            item.setSelected(is_selected)
            
            iterator += 1
        
    def set_script_job_enabled(self, enabled):
        if enabled and self.script_job_number < 0:
            self.script_job_number = cmds.scriptJob(event=["SelectionChanged", partial(self.update_selection)], protected=True)
        elif not enabled and self.script_job_number >= 0:
            cmds.scriptJob(kill=self.script_job_number, force=True)
            self.script_job_number = -1
            
    def showEvent(self, e):
        self.set_script_job_enabled(True)
        
    def closeEvent(self, e):
        self.set_script_job_enabled(False)


if __name__ == "__main__":

    workspace_control_name = OutlinerWidget.workspace_control_name()
    
    if cmds.workspaceControl(workspace_control_name, exists=True):
        cmds.workspaceControl(workspace_control_name, e=True, close=True)
        cmds.deleteUI(workspace_control_name)

    outliner = OutlinerWidget()
    outliner.show(dockable=True, uiScript=OutlinerWidget.workspace_ui_script())










