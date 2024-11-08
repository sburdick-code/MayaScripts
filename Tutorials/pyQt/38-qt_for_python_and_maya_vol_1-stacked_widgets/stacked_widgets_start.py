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
    
    
class CustomWidget01(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.cb_01 = QtWidgets.QCheckBox("Checkbox 01")
        self.cb_02 = QtWidgets.QCheckBox("Checkbox 02")
        self.cb_03 = QtWidgets.QCheckBox("Checkbox 03")
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.cb_01)
        main_layout.addWidget(self.cb_02)
        main_layout.addWidget(self.cb_03)
        main_layout.addStretch()
        
        
class CustomWidget02(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.btn_01 = QtWidgets.QPushButton("Button 01")
        self.btn_02 = QtWidgets.QPushButton("Button 02")
        self.btn_03 = QtWidgets.QPushButton("Button 03")
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.btn_01)
        main_layout.addWidget(self.btn_02)
        main_layout.addWidget(self.btn_03)
        main_layout.addStretch()
        

class ToolDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)
        
        self.setWindowTitle("Common Widgets")
        self.setMinimumSize(600, 140)
        
        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)
            
        self.create_widgets()
        self.create_layout()
        self.create_connections()
            
    def create_widgets(self):
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setFixedWidth(120)
        self.list_widget.addItem("Page 1")
        self.list_widget.addItem("Page 2")
        self.list_widget.addItem("Page 3")
        self.list_widget.setCurrentRow(0)
        
        self.stacked_widget = QtWidgets.QStackedWidget()
        
    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(self.list_widget)
        main_layout.addWidget(self.stacked_widget)
        
    def create_connections(self):
        pass
        
    def keyPressEvent(self, event):
        # Capture any unhandled key presses so they
        # are not passed to Maya's main window
        pass
        
        
if __name__ == "__main__":
    try:
        win.close()        # pylint: disable=E0601
        win.deleteLater()
    except:
        pass
        
    win = ToolDialog()
    win.show()
    
    
    
    
    
    
    
    