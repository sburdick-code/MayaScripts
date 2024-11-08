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
        self.setMinimumSize(300, 140)
        
        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)
            
        self.create_widgets()
        self.create_layout()
        self.create_connections()
            
    def create_widgets(self):
        self.a_01 = QtWidgets.QRadioButton("A 01")
        self.a_02 = QtWidgets.QRadioButton("A 02")
        self.a_03 = QtWidgets.QRadioButton("A 03")
        
        self.a_btn_grp = QtWidgets.QButtonGroup()
        self.a_btn_grp.addButton(self.a_01)
        self.a_btn_grp.addButton(self.a_02)
        self.a_btn_grp.addButton(self.a_03)
        
        self.b_01 = QtWidgets.QRadioButton("B 01")
        self.b_02 = QtWidgets.QRadioButton("B 02")
        self.b_03 = QtWidgets.QRadioButton("B 03")
        
        self.b_btn_grp = QtWidgets.QButtonGroup()
        self.b_btn_grp.addButton(self.b_01)
        self.b_btn_grp.addButton(self.b_02)
        self.b_btn_grp.addButton(self.b_03)
        
        self.a_01.setChecked(True)
        self.b_01.setChecked(True)
        
    def create_layout(self):
        grp_a_layout = QtWidgets.QHBoxLayout()
        grp_a_layout.addWidget(self.a_01)
        grp_a_layout.addWidget(self.a_02)
        grp_a_layout.addWidget(self.a_03)
        grp_a_layout.addStretch()
        
        grp_b_layout = QtWidgets.QHBoxLayout()
        grp_b_layout.addWidget(self.b_01)
        grp_b_layout.addWidget(self.b_02)
        grp_b_layout.addWidget(self.b_03)
        grp_b_layout.addStretch()
        
        main_layout = QtWidgets.QFormLayout(self)
        main_layout.setSpacing(14)
        main_layout.addRow("Group A:", grp_a_layout)
        main_layout.addRow("Group B:", grp_b_layout)
        
        
    def create_connections(self):
        self.a_btn_grp.buttonClicked.connect(self.on_button_clicked)
        
        self.b_btn_grp.buttonToggled.connect(self.on_button_toggled)
        
    def on_button_clicked(self, btn):
        print(f"Button clicked: {btn.text()}")
        
    def on_button_toggled(self, btn, checked):
        print(f"{btn.text()} toggled: {checked}")
        
        
if __name__ == "__main__":
    try:
        win.close()        # pylint: disable=E0601
        win.deleteLater()
    except:
        pass
        
    win = ToolDialog()
    win.show()
    
    
    
    
    
    
    
    