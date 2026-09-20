from SoxsRBFTools.python.RBFManager import RBFManager

if __name__ == "__main__":
    try:
        RBFManagerDialog.close()  # pylint: disable=E0601
        RBFManagerDialog.deleteLater()
    except:
        pass
    RBFManagerDialog = RBFManager()
    RBFManagerDialog.show()
