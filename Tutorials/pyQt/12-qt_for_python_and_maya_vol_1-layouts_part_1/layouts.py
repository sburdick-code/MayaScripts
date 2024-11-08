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
        self.button_a = QtWidgets.QPushButton("Button A")
        self.button_b = QtWidgets.QPushButton("Button B")
        self.button_c = QtWidgets.QPushButton("Button C")
        self.button_d = QtWidgets.QPushButton("Button D")
        
        # Create layout
        main_layout = QtWidgets.QGridLayout(self)
        main_layout.setContentsMargins(2, 10, 2, 10)
        main_layout.setSpacing(2)
        main_layout.addWidget(self.button_a, 0, 0)
        main_layout.addWidget(self.button_b, 0, 1)
        main_layout.addWidget(self.button_c, 1, 0)
        main_layout.addWidget(self.button_d, 1, 1)
        
        
        
if __name__ == "__main__":
    win = MainToolWindow()
    win.show()
    
    
    
    
    
    
    
    