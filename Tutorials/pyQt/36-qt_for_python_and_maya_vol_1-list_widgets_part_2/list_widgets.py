try:
    # Qt5
    from PySide2 import QtCore
    from PySide2 import QtWidgets
    from shiboken2 import wrapInstance
except:
    # Qt6
    from PySide6 import QtCore
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance
    
import sys
import maya.OpenMayaUI as omui
import maya.cmds as cmds
    
    
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    

class ToolDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)
        
        self.setWindowTitle("Common Widgets")
        self.setMinimumSize(300, 140)
        
        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)
            
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        
        self.refresh_list()
            
    def create_widgets(self):
        self.list_widget = QtWidgets.QListWidget()
        
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        
    def create_layout(self):
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_btn)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.list_widget)
        main_layout.addLayout(btn_layout)
        
    def create_connections(self):
        self.list_widget.currentItemChanged.connect(self.on_current_item_changed)
        
        self.refresh_btn.clicked.connect(self.refresh_list)
        
    def keyPressEvent(self, event):
        # Capture any unhandled key presses so they
        # are not passed to Maya's main window
        pass
        
    def refresh_list(self):
        self.list_widget.clear()
        
        mesh_nodes = cmds.ls(type="mesh")
        for mesh_name in mesh_nodes:
            transform_name = cmds.listRelatives(mesh_name, parent=True)[0]
            text = f"{transform_name} ({mesh_name})"
            
            self.add_item(text, transform_name)
            
            
    def add_item(self, text, transform_name):
        item = QtWidgets.QListWidgetItem(text)
        item.setData(QtCore.Qt.ItemDataRole.UserRole, transform_name)
        
        self.list_widget.addItem(item)
        
    def on_current_item_changed(self, item):
        if item:
            transform_name = item.data(QtCore.Qt.ItemDataRole.UserRole)
            cmds.select(transform_name)
        
        
if __name__ == "__main__":
    try:
        win.close()        # pylint: disable=E0601
        win.deleteLater()
    except:
        pass
        
    win = ToolDialog()
    win.show()
    
    
    
    
    
    
    
    