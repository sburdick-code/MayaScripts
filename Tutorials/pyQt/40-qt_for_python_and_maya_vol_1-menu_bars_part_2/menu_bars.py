try:
    # Qt5
    from PySide2 import QtCore
    from PySide2 import QtGui
    from PySide2 import QtWidgets
    from shiboken2 import wrapInstance
    
    from PySide2.QtWidgets import QAction
except:
    # Qt6
    from PySide6 import QtCore
    from PySide6 import QtGui
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance
    
    from PySide6.QtGui import QAction
    
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
            
        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
            
    def create_actions(self):
        self.add_item_action = QAction("Add Item")
        self.add_item_action.setShortcut(QtGui.QKeySequence("Ctrl+Shift+A"))
        
        self.clear_action = QAction("Clear All")
        self.clear_action.setShortcut(QtGui.QKeySequence("Ctrl+Shift+C"))
        
        self.about_action = QAction("About...")
            
    def create_widgets(self):
        self.menu_bar = QtWidgets.QMenuBar()
        edit_menu = self.menu_bar.addMenu("Edit")
        edit_menu.addAction(self.add_item_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.clear_action)
        
        help_menu = self.menu_bar.addMenu("Help")
        help_menu.addAction(self.about_action)
        
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.list_widget.addItem("Item 01")
        self.list_widget.addItem("Item 02")
        self.list_widget.addItem("Item 03")
        self.list_widget.addItem("Item 04")
        self.list_widget.addItem("Item 05")
        self.list_widget.addItem("Item 06")
        self.list_widget.addItem("Item 07")
        self.list_widget.addItem("Item 08")
        self.list_widget.setCurrentRow(0)
        
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        
    def create_layout(self):
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_btn)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addWidget(self.list_widget)
        main_layout.addLayout(btn_layout)
        
    def create_connections(self):
        self.add_item_action.triggered.connect(self.add_item)
        
        self.clear_action.triggered.connect(self.list_widget.clear)
        
    def keyPressEvent(self, event):
        # Capture any unhandled key presses so they
        # are not passed to Maya's main window
        pass
        
    def add_item(self):
        item_number = ("{0}".format(self.list_widget.count() + 1)).zfill(2)
        self.list_widget.addItem(f"Item {item_number}")
        
        
if __name__ == "__main__":
    try:
        win.close()        # pylint: disable=E0601
        win.deleteLater()
    except:
        pass
        
    win = ToolDialog()
    win.show()
    
    
    
    
    
    
    
    