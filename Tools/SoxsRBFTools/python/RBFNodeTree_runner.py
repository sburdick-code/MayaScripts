try:
    from Tools.SoxsRBFTools.python.RBFNodeTree import RBFNodeTree
except:
    from SoxsRBFTools.python.RBFNodeTree import RBFNodeTree

if __name__ == "__main__":
    try:
        RBFNodeTreerDialog.close()  # pylint: disable=E0601
        RBFNodeTreerDialog.deleteLater()
    except:
        pass
    RBFNodeTreerDialog = RBFNodeTree()
    RBFNodeTreerDialog.show()
