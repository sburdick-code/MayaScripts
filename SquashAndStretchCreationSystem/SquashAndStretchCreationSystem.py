import maya.cmds as cmds
import functools


def main():
    """
    The main function.
    """
    create_ui("SquashAndStretchCreationSystem")


"""
I'd like to turn this file into a class later. For now lets just get it working as is.

class SquashAndStretchCreationSystem():
    WINDOW_NAME = "Stretchy Joint Generator"
    WINDOW_ID = "SquashAndStretchCreationSystem_Window"

    def __init__( self, windowName, windowID ):
"""


def create_ui(pWindowTitle):
    """
    Set the UI Layout and display the UI when called. It will delete any existing window of the same windowID when called.

    Args:
        pWindowTitle (str): The title of the window.

    Returns:
        None: This function does not return a value.
    """

    windowID = "SquashAndStretch_System"

    # Check if the window exists
    if cmds.window(windowID, exists=True):
        cmds.deleteUI(windowID)

    window = cmds.window(windowID, title=pWindowTitle, sizeable=True)
    cmds.columnLayout(adj=True)

    ### EXISTING JOINT CHAIN ---------------------------------------------
    # First row ####################
    cmds.text(label="EXISTING JOINT CHAIN", font="boldLabelFont")

    # Second row ####################
    cmds.separator(height=10)

    # Third row ####################
    cmds.rowLayout(adj=3, numberOfColumns=4)
    cmds.separator(style="none", height=10, width=30)
    cmds.text(label="Name:")
    nameField = cmds.textField(pht="Name", editable=True, aie=True)
    cmds.separator(style="none", height=10, width=30)

    cmds.setParent("..")

    # Fourth row ####################
    cmds.rowLayout(adj=2, numberOfColumns=3)
    cmds.text(label="first")
    originParentField = cmds.textField(pht="Origin Parent Joint", ed=True)
    cmds.button(
        label="Select",
        command=functools.partial(get_selection, originParentField, "joint"),
    )

    cmds.setParent("..")

    # Fifth row ####################
    cmds.rowLayout(adj=2, numberOfColumns=3)
    cmds.text(label="last")
    insertionParentField = cmds.textField(pht="Insertion Parent Joint", ed=True)
    cmds.button(
        label="Select",
        command=functools.partial(get_selection, insertionParentField, "joint"),
    )

    cmds.setParent("..")

    # Sixth row ####################
    cmds.button(
        label="Generate",
        command=functools.partial(
            create_stretchy_system, originParentField, insertionParentField, nameField
        ),
    )  # change this after create_stretchy_system edits
    # cmds.button( label='Help', command=functools.partial( display_Help_UI ) )

    ### NEW JOINT CHAIN ---------------------------------------------
    # ROW 01 ---------------------------
    cmds.separator(height=10)

    # ROW 02 ---------------------------
    cmds.text(label="CREATE NEW STRETCHY JOINT CHAIN", font="boldLabelFont")

    # ROW 03 ---------------------------
    cmds.separator(style="none", height=10)

    # ROW 04 ---------------------------
    cmds.text(label="1. Parameters")

    # ROW 05 ---------------------------
    cmds.rowLayout(adj=3, numberOfColumns=4)
    cmds.separator(style="none", height=10, width=30)
    cmds.text(label="Name:")
    genNameTextField = cmds.textField(pht="Joint Names", editable=True, aie=True)
    cmds.separator(style="none", height=10, width=30)

    # ROW 06 --------------------------
    cmds.setParent("..")
    cmds.rowLayout(adj=3, numberOfColumns=6)
    cmds.text(label="Segment Count:")
    genJointCountField = cmds.textField(pht="#", editable=True, aie=True)
    cmds.separator(style="none", height=10)
    cmds.text(label="Parent Joint:")
    genJointParentField = cmds.textField(pht="Parent Joint", editable=True, aie=True)
    cmds.button(
        label="Select",
        command=functools.partial(get_selection, genJointParentField, "joint"),
    )

    # ROW 07 --------------------------
    cmds.setParent("..")
    cmds.separator(style="none", height=10)

    # ROW 08 --------------------------
    cmds.text(label="2. Placement Locators")

    # ROW 09 --------------------------
    cmds.button(
        label="Create and Set Placement Locators",
        command=functools.partial(
            create_placement_locators,
            genNameTextField,
            genJointCountField,
            genJointParentField,
        ),
    )

    # ROW 10 --------------------------
    cmds.separator(style="none", height=10)

    # ROW 11 --------------------------
    cmds.text(label="3. Create System")

    # ROW 12 --------------------------
    cmds.button(
        label="Generate",
        command=functools.partial(
            create_jointchain_at_locators,
            genNameTextField,
            genJointCountField,
            genJointParentField,
        ),
    )

    ### DELETE FUNCTION ---------------------------------------------
    # ROW 01 ---------------------------
    cmds.separator(height=10)

    # ROW 02 ---------------------------
    cmds.text(label="DELETE SELECTED STRETCHY SYSTEM", font="boldLabelFont")

    # ROW 03 ---------------------------
    cmds.separator(style="none", height=10)

    # ROW 04 ---------------------------
    cmds.rowLayout(adj=2, numberOfColumns=3)
    cmds.text(label="Joint affected by stretchy system")
    deletionField = cmds.textField(pht="Joint Name", ed=True)
    cmds.button(
        label="Select",
        command=functools.partial(get_selection, deletionField, "joint"),
    )

    cmds.setParent("..")

    # ROW 05 ---------------------------
    cmds.button(
        label="Delete",
        command=functools.partial(
            delete_stretchy_system, cmds.textField(deletionField, query=True, text=True)
        ),
    )

    # ROW 06 ---------------------------
    cmds.separator(height=10)

    cmds.showWindow(window)


def get_selection(pField, objType, *pArgs):
    """
    Populate a textfield with the name of a selected object.

    Args:
        pField (cmds.textField) : The field to be populated with the name of the selected object
        objType (str) : The data type the selected object must match

    Returns:
        None: This function does not return a value.

    Raises:
        MayaError: If the selection does not match the object type.
            - "No {objType} selected!"
    """

    selection = cmds.ls(selection=True, type=objType)

    if selection:
        cmds.textField(pField, edit=True, text=selection[0])
    else:
        cmds.error(f"No {objType} selected!", n=True)


def delete_stretchy_system(pStretchyComponent, *pArgs):
    """
    Deletes all nodes that are associated with the stretchy system from this script.

    Args:
        pStretchyComponent (cmds.joint): A joint of the stretchy system that contains a reference to its parent stretchy system
                                         group. It should have the string attribute, parentSystem as the group name.

    Returns:
        None: This function does not return a value.

    Raises:
        MayaError: If the selected joint does not have a stretchy system.
            - "Selected joint is not part of a stretchy system!"
    """

    if cmds.getAttr(f"{pStretchyComponent}.parentSystem"):
        groupName = cmds.getAttr(f"{pStretchyComponent}.parentSystem")
        jointsAffected = cmds.getAttr(f"{groupName}.jointsAffected")
        systemToDelete = cmds.getAttr(f"{groupName}.stretchySystem")

        for jnt in jointsAffected:
            cmds.deleteAttr(f"{jnt}.parentSystem")
        cmds.delete(systemToDelete)

        helper1 = groupName + "_helper1_jnt"
        helper2 = groupName + "_helper2_jnt"

        cmds.removeJoint(helper1)
        cmds.removeJoint(helper2)

        print("\n\n### Stretchy System Deleted ###\n\n")

    else:
        cmds.error("Selected joint is not part of a stretchy system!", n=True)


def createController(pName, pJoint):
    """
    Receives a name and the joint to be constrained/controlled and then creates a controller and offset group

    Args:
        pName (string): A string to name the controller
        pJoint (cmds.joint): The joint to be constrained/controlled

    Returns:
        newControl (string): the name of the generated controller
    """

    loc = cmds.xform(pJoint, q=True, t=True, ws=True)
    rot = cmds.xform(pJoint, q=True, ro=True, ws=True)

    newControl = cmds.circle(
        c=(0, 0, 0), name=(pName + "_ctrl")
    )  # c changes the shape of the cirlce, 0,0,0 ensures that it's a full circle
    cmds.rotate(0, 90, 0, newControl)
    offGrp = cmds.group(newControl, n=newControl[0] + "_offset")
    cmds.move(loc[0], loc[1], loc[2], offGrp)
    cmds.makeIdentity(newControl, apply=True)
    cmds.rotate(rot[0], rot[1], rot[2], offGrp)
    return newControl


def create_stretchy_system(pTextField1, pTextField2, pNameField, *pArgs):
    """
    Receives the start and end joints in a chain and then produces a stretchy rigging system for them.

    Args:
        pTextField1 (cmds.textField): A text field containing the name of the joint structure.
        pTextField2 (cmds.textField): A textfield containing the number of locators/joints to be created.
        pNameField (cmds.textField): A textfield containing the name of the system to be created

    Returns:
        None: This function does not return a value.

    Raises:
        MayaError: If any textfields are improperly filled.
            - "Not enough joints in chain (at least 3 required)" If there are less than three joints in the joint chain detectable with the data from the text fields
            - "{joint} and {joint} don't exist!" If the selected joints from the text field don't exist
    """

    # Add any nodes created for the stretchy system to this variable, do not add skin joints
    StretchySystem = []
    systemName = cmds.textField(pNameField, query=True, text=True)

    firstJnt = cmds.textField(pTextField1, query=True, text=True)
    lastJnt = cmds.textField(pTextField2, query=True, text=True)

    if not cmds.objExists(firstJnt) or not cmds.objExists(lastJnt):
        cmds.error(f"{firstJnt} and {lastJnt} don't exist!", n=True)
        return

    # if a stretchy group for either of the selected joints already exists, delete the related one and create a new one
    if cmds.objExists("stretchy_grp"):
        delete_stretchy_system(firstJnt)

    cmds.select(firstJnt, hi=True)
    jointList = cmds.ls(sl=True, type="joint")
    for j in range(len(jointList)):
        if jointList[j] == lastJnt:
            lastIndex = j
    jointList = jointList[:lastIndex]

    if len(jointList) < 3:
        cmds.error("Not enough joints in chain (at least 3 required)", n=True)

    secondJnt = jointList[1]

    firstJntLoc = cmds.xform(firstJnt, q=True, t=True, ws=True)
    lastJntLoc = cmds.xform(lastJnt, q=True, t=True, ws=True)

    cmds.select(clear=True)
    helper1 = cmds.joint(p=firstJntLoc, n=systemName + "_helper1_jnt")
    cmds.joint(helper1, e=True, zso=True, oj="xyz")
    cmds.select(clear=True)
    helper2 = cmds.joint(p=lastJntLoc, n=systemName + "_helper2_jnt")

    firstController = createController(firstJnt, firstJnt)[0]
    lastController = createController(lastJnt, lastJnt)[0]

    cmds.pointConstraint(firstController, firstJnt)
    cmds.pointConstraint(lastController, lastJnt)
    cmds.parentConstraint(lastController, helper2)

    cmds.parent(helper1, firstJnt)
    cmds.parent(helper2, firstJnt)
    cmds.parent(secondJnt, helper1)
    cmds.parent(lastController + "_offset", firstController)

    distanceNode = cmds.shadingNode(
        "distanceBetween", asUtility=True, n=systemName + "_distanceBetween"
    )
    cmds.connectAttr(helper2 + ".translate", distanceNode + ".point1")
    defaultDistance = cmds.getAttr(distanceNode + ".distance")

    distanceFactor = cmds.shadingNode(
        "multiplyDivide", asUtility=True, n=systemName + "_distanceFactor"
    )
    cmds.setAttr(distanceFactor + ".input2X", defaultDistance)
    cmds.setAttr(distanceFactor + ".operation", 2)
    cmds.connectAttr(distanceNode + ".distance", distanceFactor + ".input1X")

    invertIt = cmds.shadingNode(
        "multiplyDivide", asUtility=True, n=systemName + "_invertIt"
    )
    cmds.setAttr(invertIt + ".input1X", 1)
    cmds.setAttr(invertIt + ".operation", 2)
    cmds.connectAttr(distanceFactor + ".outputX", invertIt + ".input2X")

    for jnt in jointList[1:]:  # iterate thru all the joints except the first joint
        cmds.aimConstraint(lastController, jnt)
        cmds.connectAttr(distanceFactor + ".outputX", jnt + ".scaleX")

    cmds.connectAttr(distanceFactor + ".outputX", helper1 + ".scaleX")
    cmds.aimConstraint(lastController, helper1)

    if len(jointList) % 2 == 0:  # if even
        centerIndex = [len(jointList) // 2, -1, len(jointList) // 2]
        j = 3

    else:  # if odd
        centerIndex = [len(jointList) // 2, len(jointList) // 2]
        j = 2

    for i in range(
        1, len(jointList) - 1
    ):  # only iterate thru the middle joints, not the end joints
        if (
            i <= centerIndex[0] or i <= centerIndex[1]
        ):  # we are to the left or center of the chain
            if i <= centerIndex[0]:  # if we are to the left of the chain
                posFactor = i / centerIndex[0]
            else:  # we are at the center of the chain
                posFactor = 1

            uniScale = 2  # arbitrary number

            multDiv = cmds.shadingNode(
                "multiplyDivide", asUtility=True, n=systemName + "_multDiv"
            )
            cmds.setAttr(multDiv + ".input2X", posFactor)
            cmds.connectAttr(invertIt + ".outputX", multDiv + ".input1X")
            plusMinusAvg = cmds.shadingNode(
                "plusMinusAverage", asUtility=True, n=systemName + "_plusMinusAvg"
            )
            cmds.setAttr(plusMinusAvg + ".operation", 2)
            cmds.setAttr(plusMinusAvg + ".input2D[1].input2Dx", posFactor)
            cmds.connectAttr(
                multDiv + ".outputX", plusMinusAvg + ".input2D[0].input2Dx"
            )
            exponent = cmds.shadingNode(
                "floatMath", asUtility=True, n=systemName + "_exponent1"
            )
            cmds.setAttr(exponent + ".floatA", uniScale)
            cmds.setAttr(exponent + ".operation", 6)
            cmds.connectAttr(plusMinusAvg + ".output2Dx", exponent + ".floatB")
            cmds.connectAttr(exponent + ".outFloat", jointList[i] + ".scaleY")
            cmds.connectAttr(exponent + ".outFloat", jointList[i] + ".scaleZ")

            StretchySystem.append(exponent)
            StretchySystem.append(plusMinusAvg)
            StretchySystem.append(multDiv)

        else:  # we are to the right of the chain
            exponent = systemName + "_exponent" + str(i - j)
            j = j + 2
            cmds.connectAttr(exponent + ".outFloat", jointList[i] + ".scaleY")
            cmds.connectAttr(exponent + ".outFloat", jointList[i] + ".scaleZ")

    StretchySystem.append(invertIt)
    StretchySystem.append(distanceFactor)
    StretchySystem.append(distanceNode)

    """These next lines are necessary to set up the deletion system"""
    # Add the name of the stretchy group to all joints affected

    StretchySystem.append(firstController + "_offset")
    # StretchySystem.append(helper2)
    # StretchySystem.append(helper1)

    stretchy_grp = cmds.group(n=systemName, empty=True)
    StretchySystem.append(stretchy_grp)

    for jnt in jointList:
        cmds.addAttr(jnt, ln="parentSystem", dt="string")
        cmds.setAttr(f"{jnt}.parentSystem", stretchy_grp, type="string")

    # Add a the names of all stretchy system nodes to the local stretchySystemGroup
    cmds.addAttr(stretchy_grp, ln="stretchySystem", dt="stringArray")
    cmds.setAttr(
        f"{stretchy_grp}.stretchySystem",
        len(StretchySystem),
        *StretchySystem,
        type="stringArray",
    )
    print(cmds.getAttr(f"{stretchy_grp}.stretchySystem"))

    # Add the names of all the joints affected by the stretchySystemGroup
    cmds.addAttr(stretchy_grp, ln="jointsAffected", dt="stringArray")
    cmds.setAttr(
        f"{stretchy_grp}.jointsAffected",
        len(jointList),
        *jointList,
        type="stringArray",
    )
    print(cmds.getAttr(f"{stretchy_grp}.jointsAffected"))


def create_placement_locators(pNameField, pNumberField, pParentJoint, *pArgs):
    """
    Create an interactive set of locators allowing the rigging artist to set them in space. These locators are used to help place
    the joints in the function create_jointchain_at_locators().

    Args:
        pNameField (cmds.textField): A text field containing the name of the joint structure.
        pNumberField (cmds.textField): A textfield containing the number of locators/joints to be created.
        pParentJoint (cmds.textField): A textfield containing the name of the parent joint.

    Returns:
        None: This function does not return a value.

    Raises:
        MayaError: If any textfields are improperly filled.
            - "Parameters not valid" If pNameField or pParentJoint are left empty.
            - "Must have at least 2 joints!" If pNumberField has less than 2 joints.
            - "No valid parent joint parameter" If pParentJoint is not filled with a joint value.
    """

    # Check if all parameters are filled properly
    if not (
        (cmds.textField(pNameField, query=True, text=True))
        and (cmds.textField(pParentJoint, query=True, text=True))
    ):
        cmds.error("Parameters not valid", n=True)
        return 0
    elif not (int(cmds.textField(pNumberField, query=True, text=True)) > 1):
        cmds.error("Must have at least 2 joints!", n=True)
        return 0
    elif not (cmds.objExists(cmds.textField(pParentJoint, query=True, text=True))):
        cmds.error("No valid parent joint parameter", n=True)
        return 0

    # Set the scale of the locators and the translation of the last locator
    scaleValue = 1
    translateValue = [0, 100, 0]
    number = int(cmds.textField(pNumberField, query=True, text=True))
    pName = cmds.textField(pNameField, query=True, text=True)

    # Create the locator system and scale them up
    firstPL = cmds.spaceLocator(name=pName + "_firstPlacement")
    cmds.scale(scaleValue, scaleValue, scaleValue, firstPL)
    firstGroup = cmds.group(name=pName + "_first_off")
    middlePLList = []
    middleGroupList = []
    lastPL = cmds.spaceLocator(name=pName + "_lastPlacement")
    cmds.scale(scaleValue, scaleValue, scaleValue, lastPL)
    lastGroup = cmds.group(name=pName + "_last_off")
    cmds.xform(lastGroup, ws=True, translation=translateValue)

    locatorList = [firstPL]
    locatorGroupList = [firstGroup]

    # Group the system under the group placementLocators_grp
    locatorGroup = cmds.group(em=True, name=pName + "_placementLocators_grp")
    cmds.parent(firstGroup, locatorGroup)
    cmds.parent(lastGroup, locatorGroup)

    # Divide the distance of the translate value in half and place each locator in the list at that point
    distance = translateValue[1] / (number - 1)
    incDistance = distance

    cmds.select(clear=True)
    middleGroupHead = cmds.group(em=True, name=pName + "_middle_off")

    # Create each locator even distance apart
    if number > 1:
        for i in range(number - 2):
            middlePL = cmds.spaceLocator(
                name=pName + "_middlePlacement_" + str(i).zfill(2)
            )
            cmds.scale(scaleValue, scaleValue, scaleValue, middlePL)
            cmds.makeIdentity(middlePL, apply=True)
            middleGroup = cmds.group(name=pName + "_middle_off_" + str(i).zfill(2))
            print(incDistance)
            cmds.xform(middleGroup, ws=True, translation=[0, incDistance, 0])

            locatorList.append(middlePL)
            locatorGroupList.append(middleGroup)

            incDistance = incDistance + distance

        locatorList.append(lastPL)
        locatorGroupList.append(lastGroup)

        for i in range(number):
            if (i != 0) and (i != (len(locatorGroupList) - 1)):
                cmds.parentConstraint(locatorList[i - 1], locatorGroupList[i])
                cmds.parentConstraint(locatorList[i + 1], locatorGroupList[i])
                cmds.parent(locatorGroupList[i], middleGroupHead)

    cmds.parent(middleGroupHead, locatorGroup)
    cmds.select(clear=True)
    successGroup = cmds.group(name=pName + "_SuccessGroup", empty=True)
    cmds.parent(successGroup, locatorGroup)


def create_jointchain_at_locators(pNameField, pNumberField, pParentJoint, *pArgs):
    """
    From a set of locators, this function creates a joint chain at their locations. The name of the joints are determined by pNameField.

    Args:
        pNameField (cmds.textField): A text field containing the name of the joint structure.
        pNumberField (cmds.textField): A textfield containing the number of locators/joints to be created.
        pParentJoint (cmds.textField): A textfield containing the name of the parent joint.

    Returns:
        None: This function does not return a value.

    Raises:
        MayaError: If there is an issue creating the joints.
            - "Locators Not Created!" If the locators do not exist.
    """

    if not (
        cmds.objExists(
            (cmds.textField(pNameField, query=True, text=True)) + "_SuccessGroup"
        )
    ):
        cmds.error("Locators Not Created!", n=True)
        return 0

    pName = cmds.textField(pNameField, query=True, text=True)
    number = int(cmds.textField(pNumberField, query=True, text=True))
    parentJoint = cmds.textField(pParentJoint, query=True, text=True)

    pFirstPL = pName + "_firstPlacement"
    pLastPL = pName + "_lastPlacement"
    pMiddleList = cmds.listRelatives(pName + "_middle_off")
    print(pMiddleList)
    print(cmds.listRelatives(pMiddleList[0]))

    # Get the location of locators
    firstLoc = cmds.xform(pFirstPL, query=True, translation=True, ws=True)
    lastLoc = cmds.xform(pLastPL, query=True, translation=True, ws=True)

    middleLocList = []
    translationList = [firstLoc]
    for i in range(number):
        locator = cmds.listRelatives(pMiddleList[i])
        print(locator[0])
        translationList.append(
            cmds.xform(locator[0], query=True, translation=True, ws=True)
        )

    translationList.append(lastLoc)

    # Get the rotation of locators
    firstRot = cmds.xform(pFirstPL, query=True, rotation=True, ws=True)
    lastRot = cmds.xform(pLastPL, query=True, rotation=True, ws=True)

    middleRotList = []
    rotationList = [firstRot]
    for i in range(number):
        rotationList.append(
            cmds.xform(
                cmds.listRelatives(pMiddleList[i]), query=True, rotation=True, ws=True
            )
        )

    rotationList.append(lastRot)

    # Create the joints
    cmds.select(cl=True)
    middleJointList = []

    firstJoint = cmds.joint(name=pName + "_01")
    jointList = [firstJoint]

    for i in range(number):
        jointList.append(cmds.joint(name=pName + "_" + str(i + 2).zfill(2)))

    lastJoint = cmds.joint(name=pName + "_" + str(number + 2).zfill(2))

    jointList.append(lastJoint)

    # Move the joints to the proper location
    for num in range(len(jointList)):
        cmds.xform(
            jointList[num],
            ws=True,
            translation=translationList[num],
            rotation=rotationList[num],
        )

    # Get the parent group of the locators and delete it
    parentGroup = cmds.listRelatives(
        cmds.listRelatives(pFirstPL, parent=True), parent=True
    )

    print(f"deleting {parentGroup[0]}")
    cmds.delete(parentGroup[0])

    cmds.parent(firstJoint, parentJoint)

    # create_stretchy_system( jointList )


### MAIN ###
main()
