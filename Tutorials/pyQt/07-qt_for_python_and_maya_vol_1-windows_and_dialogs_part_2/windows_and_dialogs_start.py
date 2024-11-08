try:
    # Qt5
    from PySide2 import QtCore
    from PySide2 import QtWidgets
except:
    # Qt6
    from PySide6 import QtCore
    from PySide6 import QtWidgets
    

class MainToolWindow(QtWidgets.QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Windows and Dialogs")
        self.setMinimumSize(400, 300)
        
        
if __name__ == "__main__":
    win = MainToolWindow()
    win.show()
    