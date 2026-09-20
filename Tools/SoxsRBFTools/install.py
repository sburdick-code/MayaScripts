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

    # Move the installer directory into the maya scripts dir
    new_dir = os.path.join(scripts_dir, "SoxsRBFTools")
    if os.path.exists(new_dir):
        shutil.rmtree(new_dir)
    shutil.copytree(installer_dir, new_dir)
    # Remove the plugin dir from the scripts

    app_dir = cmds.internalVar(userAppDir=True)
    plugins_dir = os.path.normpath(os.path.join(app_dir, "plug-ins"))
    plugin_target_path = plugins_dir + r"\SoxsRBF.py"
    temp_plugin_dir = new_dir + r"\plug-in"
    installed_package_dir = new_dir + r"\package"
    rbf_plugin = temp_plugin_dir + r"\SoxsRBF.py"

    if os.path.exists(plugin_target_path):
        os.remove(plugin_target_path)
    shutil.move(rbf_plugin, plugins_dir)

    # Load the Plugin
    plugin_name = "SoxsRBF.py"

    cmds.evalDeferred(
        'if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(
            plugin_name
        )
    )
    cmds.evalDeferred(
        'if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(
            plugin_name
        )
    )

    cmds.evalDeferred(
        'if not cmds.pluginInfo("{0}", query=True, autoload=True): cmds.pluginInfo("{0}", edit=True, autoload=True)'.format(
            plugin_name
        )
    )

    # Cleanup unused dirs
    if os.path.exists(temp_plugin_dir):
        shutil.rmtree(temp_plugin_dir)
    if os.path.exists(installed_package_dir):
        shutil.rmtree(installed_package_dir)
    if os.path.exists(new_dir + r"\install.py"):
        os.remove(new_dir + r"\install.py")

    # Delete any existing shelf icons
    current_shelf = mel.eval(
        "string $currentShelf = `tabLayout -query -selectTab $gShelfTopLevel`;"
    )

    gShelfTopLevel = mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;")
    current_shelf = cmds.tabLayout(gShelfTopLevel, query=True, selectTab=True)

    shelf_buttons = cmds.shelfLayout(current_shelf, query=True, childArray=True) or []

    for btn in shelf_buttons:
        if cmds.shelfButton(btn, exists=True):
            annotation = cmds.shelfButton(btn, query=True, annotation=True)

            if annotation == "Sox's RBF Manager" or annotation == "Sox's RBF Node Tree":
                cmds.deleteUI(btn)

    # Create new shelf Icons on the currrent shelf
    icon_path = os.path.join(new_dir, "RBFManager_32x32.png")
    runner_path = os.path.join(new_dir, "python/RBFManager_runner.py")
    with open(runner_path, "r") as f:
        py_command = f.read()

    cmds.shelfButton(
        label="Sox's RBF Manager",
        image=icon_path,
        command=py_command,
        annotation="Sox's RBF Manager",
        parent=current_shelf,
    )

    icon_path = os.path.join(new_dir, "RBFNodeTree_32x32.png")
    runner_path = os.path.join(new_dir, "python/RBFNodeTree_runner.py")
    with open(runner_path, "r") as f:
        py_command = f.read()

    cmds.shelfButton(
        label="Sox's RBF Node Tree",
        image=icon_path,
        command=py_command,
        annotation="Sox's RBF Node Tree",
        parent=current_shelf,
    )
