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
        
        self.setWindowTitle("Organizing the Code")
        self.setMinimumWidth(300)
        
        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)
            
        self.create_widgets()
        self.create_layout()
        self.create_connections()
            
    def create_widgets(self):
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
        
    def create_layout(self):
        rb_layout = QtWidgets.QHBoxLayout()
        rb_layout.setContentsMargins(0, 0, 0, 0)
        rb_layout.addWidget(self.rb1)
        rb_layout.addWidget(self.rb2)
        rb_layout.addWidget(self.rb3)
        
        cb_layout = QtWidgets.QGridLayout()
        cb_layout.setContentsMargins(0, 0, 0, 0)
        cb_layout.addWidget(self.cb1, 0, 0)
        cb_layout.addWidget(self.cb2, 0, 1)
        cb_layout.addWidget(self.cb3, 1, 0)
        cb_layout.addWidget(self.cb4, 1, 1)
        
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(6)
        form_layout.addRow("Name:", self.name_le)
        form_layout.addRow("Address:", self.address_le)
        form_layout.addRow("", rb_layout)
        form_layout.addRow("", cb_layout)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(btn_layout)
        
    def create_connections(self):
        self.name_le.editingFinished.connect(self.print_name)
        self.cancel_btn.clicked.connect(self.close)
        
        self.cb1.toggled.connect(self.print_cb)
        self.cb2.toggled.connect(self.print_cb)
        self.cb3.toggled.connect(self.print_cb)
        self.cb4.toggled.connect(self.print_cb)
        
    def print_name(self, name):
        print(name)
        
    def print_cb(self, checked):
        cb = self.sender()
        if cb == self.cb1:
            cb_name = "Option 1"
        elif cb == self.cb2:
            cb_name = "Option 2"
        elif cb == self.cb3:
            cb_name = "Option 3"
        elif cb == self.cb4:
            cb_name = "Option 4"
        else:
            return
        
        if checked:
            print(f"{cb_name} is checked")
        else:
            print(f"{cb_name} is not checked")
        
        
        
        
if __name__ == "__main__":
    try:
        win.close()        # pylint: disable=E0601
        win.deleteLater()
    except:
        pass
        
    win = MainToolWindow()
    win.show()
    
    
    
    
    
    
    
    