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
        
        self.on_text_changed(self.spin_box.text())
        self.on_value_changed(self.spin_box.value())
            
    def create_widgets(self):
        self.spin_box = QtWidgets.QSpinBox()
        self.spin_box.setFixedWidth(60)
        self.spin_box.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spin_box.setSuffix("m")
        self.spin_box.setMinimum(-1000)
        self.spin_box.setMaximum(1000)
        self.spin_box.setSingleStep(10)
        self.spin_box.setValue(99)
        
        self.double_spin_box = QtWidgets.QDoubleSpinBox()
        self.double_spin_box.setFixedWidth(60)
        self.double_spin_box.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.double_spin_box.setValue(0.0)
        
        self.sb_text_label = QtWidgets.QLabel()
        self.sb_value_label = QtWidgets.QLabel()
        
    def create_layout(self):
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("QSpinBox:", self.spin_box)
        form_layout.addRow("QDoubleSpinBox:", self.double_spin_box)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addWidget(self.sb_text_label)
        main_layout.addWidget(self.sb_value_label)
        
    def create_connections(self):
        self.spin_box.editingFinished.connect(self.on_editing_finished)
        self.spin_box.textChanged.connect(self.on_text_changed)
        self.spin_box.valueChanged.connect(self.on_value_changed)
        
    def on_editing_finished(self):
        value = self.spin_box.value()
        print(f"QSpinBox editing finished: {value}")
        
    def on_text_changed(self, text):
        self.sb_text_label.setText(f"QSpinBox Text: {text}")
        
    def on_value_changed(self, i):
        self.sb_value_label.setText(f"QSpinBox Value: {i}")
        
        
if __name__ == "__main__":
    try:
        win.close()        # pylint: disable=E0601
        win.deleteLater()
    except:
        pass
        
    win = ToolDialog()
    win.show()
    
    
    
    
    
    
    
    