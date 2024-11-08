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
        self.setMinimumWidth(300)
        
        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)
            
        # Create widgets
        self.name_le = QtWidgets.QLineEdit()
        self.address_le = QtWidgets.QLineEdit()
        self.rb1 = QtWidgets.QRadioButton("RB 1")
        self.rb1.setChecked(True)
        self.rb2 = QtWidgets.QRadioButton("RB 2")
        self.rb3 = QtWidgets.QRadioButton("RB 3")
        self.cb1 = QtWidgets.QCheckBox("Option 1")
        self.cb2 = QtWidgets.QCheckBox("Option 2")
        self.cb3 = QtWidgets.QCheckBox("Option 3")
        self.cb4 = QtWidgets.QCheckBox("Option 4")
        
        self.ok_btn = QtWidgets.QPushButton("OK")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        
        # Create layout
        form_layout = QtWidgets.QFormLayout(self)
        form_layout.setSpacing(6)
        form_layout.addRow("Name:", self.name_le)
        form_layout.addRow("Address:", self.address_le)

        
        
        
if __name__ == "__main__":
    win = MainToolWindow()
    win.show()
    
    
    
    
    
    
    
    