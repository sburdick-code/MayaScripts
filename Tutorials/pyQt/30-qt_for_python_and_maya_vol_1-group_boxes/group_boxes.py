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
    
    
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    

class ToolDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)
        
        self.setWindowTitle("Common Widgets")
        self.setMinimumSize(400, 240)
        
        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)
            
        self.create_widgets()
        self.create_layout()
        self.create_connections()
            
    def create_widgets(self):
        self.directory_le = QtWidgets.QLineEdit()
        self.filename_le = QtWidgets.QLineEdit()
        
        self.option01_cb = QtWidgets.QCheckBox("Option 01")
        self.option02_cb = QtWidgets.QCheckBox("Option 02")
        self.option03_cb = QtWidgets.QCheckBox("Option 03")
        
        self.ok_btn = QtWidgets.QPushButton("OK")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        
    def create_layout(self):
        path_layout = QtWidgets.QFormLayout()
        path_layout.addRow("Directory:", self.directory_le)
        path_layout.addRow("Filename:", self.filename_le)
        
        path_grp = QtWidgets.QGroupBox("File Path")
        path_grp.setLayout(path_layout)
        
        options_layout = QtWidgets.QHBoxLayout()
        options_layout.addWidget(self.option01_cb)
        options_layout.addWidget(self.option02_cb)
        options_layout.addWidget(self.option03_cb)
        options_layout.addStretch()
        
        options_grp = QtWidgets.QGroupBox("Options")
        options_grp.setLayout(options_layout)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(path_grp)
        main_layout.addWidget(options_grp)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        
    def create_connections(self):
        pass
        
        
if __name__ == "__main__":
    try:
        win.close()        # pylint: disable=E0601
        win.deleteLater()
    except:
        pass
        
    win = ToolDialog()
    win.show()
    
    
    
    
    
    
    
    