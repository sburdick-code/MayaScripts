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
        self.setMinimumSize(400, 140)
        
        # On macOS make the window a Tool to keep it on top of Maya
        if sys.platform == "darwin":
            self.setWindowFlag(QtCore.Qt.Tool, True)
            
        self.create_widgets()
        self.create_layout()
        self.create_connections()
            
    def create_widgets(self):
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText("This is an <b><i>HTML message</i></b>")

        self.plain_text_edit = QtWidgets.QPlainTextEdit()
        self.plain_text_edit.setPlainText("This is a <b><i>plain text message</i></b>")
        
        self.plain_text_cb = QtWidgets.QCheckBox("Set Plain Text")
        
        self.update_text_btn = QtWidgets.QPushButton("Update Text")
        self.clear_text_btn = QtWidgets.QPushButton("Clear All")
        
    def create_layout(self):
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.plain_text_cb)
        btn_layout.addStretch()
        btn_layout.addWidget(self.clear_text_btn)
        btn_layout.addWidget(self.update_text_btn)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(QtWidgets.QLabel("QTextEdit:"))
        main_layout.addWidget(self.text_edit)
        main_layout.addWidget(QtWidgets.QLabel("QPlainTextEdit:"))
        main_layout.addWidget(self.plain_text_edit)
        main_layout.addLayout(btn_layout)
        
    def create_connections(self):
        self.update_text_btn.clicked.connect(self.update_text)
        
        self.clear_text_btn.clicked.connect(self.text_edit.clear)
        self.clear_text_btn.clicked.connect(self.plain_text_edit.clear)
        
    def update_text(self):
        text = self.plain_text_edit.toPlainText()
        
        if self.plain_text_cb.isChecked():
            self.text_edit.setPlainText(text)
        else:
            self.text_edit.setText(text)
        
    def keyPressEvent(self, event):
        pass
        
        
if __name__ == "__main__":
    try:
        win.close()        # pylint: disable=E0601
        win.deleteLater()
    except:
        pass
        
    win = ToolDialog()
    win.show()
    
    
    
    
    
    
    
    