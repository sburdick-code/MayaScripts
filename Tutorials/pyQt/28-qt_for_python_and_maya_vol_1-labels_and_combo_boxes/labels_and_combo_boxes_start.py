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
        self.setMinimumSize(300, 120)
        
        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)
            
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        
        self.update_text("<none>")
        self.update_index(-1)
            
    def create_widgets(self):
        self.combo_box = QtWidgets.QComboBox()
        
        self.selected_text_label = QtWidgets.QLabel()
        self.selected_index_label = QtWidgets.QLabel()
        self.selected_data_label = QtWidgets.QLabel()
        
    def create_layout(self):
        combo_box_layout = QtWidgets.QHBoxLayout()
        combo_box_layout.setContentsMargins(0, 0, 0, 0)
        combo_box_layout.addWidget(QtWidgets.QLabel("Item Select:"))
        combo_box_layout.addWidget(self.combo_box)
        combo_box_layout.addStretch()
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(combo_box_layout)
        main_layout.addStretch()
        main_layout.addWidget(self.selected_text_label)
        main_layout.addWidget(self.selected_index_label)   
        main_layout.addWidget(self.selected_data_label)   
        
    def create_connections(self):
        pass
        
    def update_text(self, text):
        self.selected_text_label.setText(f"Selected Text: {text}")
        
        data = "<none>"
        self.selected_data_label.setText(f"Selected Data: {data}")
        
    def update_index(self, index):
        self.selected_index_label.setText(f"Selected Index: {index}")
        
        
if __name__ == "__main__":
    try:
        win.close()        # pylint: disable=E0601
        win.deleteLater()
    except:
        pass
        
    win = ToolDialog()
    win.show()
    
    
    
    
    
    
    
    