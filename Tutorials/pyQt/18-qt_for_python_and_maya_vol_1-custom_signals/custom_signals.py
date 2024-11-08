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
    
    
class CustomLineEdit(QtWidgets.QLineEdit):
    
    enter_pressed = QtCore.Signal(str)
    return_pressed = QtCore.Signal(str)
    
    def keyPressEvent(self, e):
        super().keyPressEvent(e)
        
        if e.key() == QtCore.Qt.Key_Enter:
            self.enter_pressed.emit(self.text())
        elif e.key() == QtCore.Qt.Key_Return:
            self.return_pressed.emit(self.text())
    
    
class MainToolWindow(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)
        
        self.setWindowTitle("Layouts")
        self.setMinimumWidth(300)
        
        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)
            
        self.create_widgets()
        self.create_layout()
        self.create_connections()
            
    def create_widgets(self):
        self.name_le = CustomLineEdit()

        self.ok_btn = QtWidgets.QPushButton("OK")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        
    def create_layout(self):
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(6)
        form_layout.addRow("Name:", self.name_le)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(btn_layout)
        
    def create_connections(self):
        self.name_le.enter_pressed.connect(self.on_enter_pressed)
        self.name_le.return_pressed.connect(self.on_return_pressed)
        
    def on_enter_pressed(self, text):
        print(f"Enter key pressed: {text}")
      
    def on_return_pressed(self, text):
        print(f"Return key pressed: {text}")
        
        
if __name__ == "__main__":
    try:
        win.close()        # pylint: disable=E0601
        win.deleteLater()
    except:
        pass
        
    win = MainToolWindow()
    win.show()
    
    
    
    
    
    
    
    