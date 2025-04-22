from Tools.ControllerToolbox import ControllerToolbox

if __name__ == "__main__":
    try:
        controllerToolboxDialog.close()  # pylint: disable=E0601
        controllerToolboxDialog.deleteLater()
    except:
        pass
    controllerToolboxDialog = ControllerToolbox()
    controllerToolboxDialog.show()
