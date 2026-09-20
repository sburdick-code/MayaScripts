import os
import shutil
import logging
import maya.cmds as cmds
import maya.mel as mel

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def onMayaDroppedPythonFile(obj):
    # Get the directory of installer files
    installer_dir = os.path.dirname(__file__)
    print(installer_dir)

    # Get default script directory
    prefs_dir = os.path.dirname(cmds.about(preferences=True))
    scripts_dir = os.path.normpath(os.path.join(prefs_dir, "scripts"))
    print(scripts_dir)
    print("WAHOO")
    # Move the installer directory into the maya scripts dir
    new_dir = os.path.join(scripts_dir, "ControllerToolboxWidget")
    shutil.copytree(installer_dir, new_dir)
    print(new_dir)

    # Create a shelf Icon on the currrent shelf
    current_shelf = mel.eval(
        "string $currentShelf = `tabLayout -query -selectTab $gShelfTopLevel`;"
    )
    icon_path = os.path.join(new_dir, "ControllerToolbox_32x32.png")
    runner_path = os.path.join(new_dir, "python/ControllerToolbox_runner.py")
    with open(runner_path, "r") as f:
        py_command = f.read()

    cmds.shelfButton(
        label="",
        image=icon_path,
        command=py_command,
        annotation="Controller Toolbox",
        parent=current_shelf,
    )
