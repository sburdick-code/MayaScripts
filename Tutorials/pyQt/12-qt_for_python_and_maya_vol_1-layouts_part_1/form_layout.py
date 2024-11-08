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
    

class MainToolWindow(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)
        
        self.setWindowTitle("Layouts")
        self.setMinimumWidth(200)
        
        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)
            
        # Create widgets
        self.wdg_a = QtWidgets.QLineEdit()
        self.wdg_b = QtWidgets.QLineEdit()
        self.wdg_c = QtWidgets.QCheckBox("Enabled")
        
        # Create layout
        main_layout = QtWidgets.QFormLayout(self)
        main_layout.addRow("Name:", self.wdg_a)
        main_layout.addRow("Address:", self.wdg_b)
        main_layout.addRow("", self.wdg_c)
        
        
        
if __name__ == "__main__":
    win = MainToolWindow()
    win.show()
    
    
    
    
    
    
    
    