import maya.cmds as cmds
import functools


def main():
    """
    The main function.
    """
    create_ui("MyWindowName")


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
    cmds.rowLayout(adj=2, numberOfColumns=3)
    cmds.text(label="first")
    originParentField = cmds.textField(pht="Origin Parent Joint", ed=True)
    cmds.button(
        label="Select",
        command=functools.partial(get_selection, originParentField, "joint"),
    )

    cmds.setParent("..")

    # Third row ####################
    cmds.rowLayout(adj=2, numberOfColumns=3)
    cmds.text(label="last")
    insertionParentField = cmds.textField(pht="Insertion Parent Joint", ed=True)
    cmds.button(
        label="Select",
        command=functools.partial(get_selection, insertionParentField, "joint"),
    )

    cmds.setParent("..")

    # Fourth row ####################
    cmds.button(
        label="Generate",
        command=functools.partial(
            create_stretchy_system, originParentField, insertionParentField
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

    # ROW 13 ---------------------------
    cmds.separator(style="none", height=10)

    # ROW 14 ---------------------------
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


def delete_stretchy_system(pStretchyComponent):
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

        print("\n\n### Stretchy System Deleted ###\n\n")

    else:
        cmds.error("Selected joint is not part of a stretchy system!", n=True)


def create_stretchy_system(pTextField1, pTextField2, *pArgs):
    """
    Receives the start and end joints in a chain and then produces a stretchy rigging system for them.

    Args:
        pTextField1 (cmds.textField): A text field containing the name of the joint structure.
        pTextField2 (cmds.textField): A textfield containing the number of locators/joints to be created.

    Returns:
        None: This function does not return a value.

    Raises:
        MayaError: If any textfields are improperly filled.
            - "Not enough joints in chain (at least 3 required)" If no joints are detectable with the data from the text fields
    """

    # Add any nodes created for the stretchy system to this variable, do not add skin joints
    StretchySystem = ["stretchy_grp"]

    firstJoint = cmds.textField(pTextField1, query=True, text=True)
    lastJoint = cmds.textField(pTextField2, query=True, text=True)

    pJointList = []

    # select the hierarchy and append it to pJointList
    cmds.select(firstJoint, hi=True)
    pJointList = cmds.ls(sl=True, type="joint")
    print(pJointList)

    if not (
        len(pJointList) >= 3
    ):  # if there arent at least 3 joints in the pre existing group
        cmds.error("Not enough joints in chain (at least 3 required)", n=True)
        return 0

    # if the grp already exists, delete it
    if cmds.objExists("stretchy_grp"):
        cmds.delete("stretchy_grp")

    # CREATE CONTROLLERS
    controlCurveList = []

    for jnt in pJointList:
        ## Joint Information
        # Get parent of current joint
        jntParent = cmds.listRelatives(jnt, parent=True)
        if jntParent:
            jntParentName = jntParent[0]
        else:
            jntParentName = "GARBAGE"  # this is for the first joint in the heirarchy since it has no parent. there needs to be something

        # Get Radius of current joint
        jntRadius = cmds.getAttr(jnt + ".radius")

        # Get translation and rotation of current joint
        jntTranslation = cmds.xform(jnt, query=True, translation=True, worldSpace=True)
        jntRotation = cmds.xform(jnt, query=True, rotation=True, worldSpace=True)

        ## Controller Manipulation
        # Create new controller
        newControl = cmds.spaceLocator(name=(jnt + "_ctrl"))
        controlCurveList.append(
            newControl[0]
        )  # newControl will return a dictionary containing the transform and the shape node, you just want the name, hence [0]
        cmds.move(jntTranslation[0], jntTranslation[1], jntTranslation[2], newControl)
        cmds.makeIdentity(newControl, apply=True)

        # Create the offset group for our new controller
        newGroup = cmds.group(empty=True, name=(jnt + "_offset"))
        cmds.move(
            jntTranslation[0], jntTranslation[1], jntTranslation[2], newGroup
        )  # the group and the cntrl are at the same place
        cmds.makeIdentity(newGroup, apply=True)  # freeze transformations

        # Make new control a child of new group
        cmds.parent(newControl, newGroup)

        # Rotate offset group to match the rotations of the joint
        cmds.rotate(jntRotation[0], jntRotation[1], jntRotation[2], newGroup)

        """
        ## Place group in the right hierarchy
        if ( jntParentName + '_ctrl' ) in controlCurveList:
            cmds.parent( newGroup, (jntParentName + '_ctrl') )
            print( newGroup + ' parented under ' + jntParentName + '_ctrl' )
        else:
            print( 'No parent found' )
            print( jntParentName ) 
            print( controlCurveList )
        """

        ## Parent constrain joint under control
        cmds.parentConstraint(newControl, jnt)

    # PARENT CONSTRAIN THE MIDDLE CONTROLLER OFFSET GROUPS TO THEIR ADJACENT CONTROLLERS
    for x in range(len(pJointList)):
        if pJointList[x] == firstJoint or pJointList[x] == lastJoint:
            continue

        cmds.parentConstraint(
            controlCurveList[x - 1], controlCurveList[x + 1], pJointList[x] + "_offset"
        )

    # BUILD HELPER JOINTS
    jointRotList = []
    jointTransList = []

    jointRotList.append(
        cmds.xform(
            pJointList[0],
            rotation=True,
            worldSpace=True,
            q=True,
        )
    )  # the first elemeent in the joint list
    jointRotList.append(
        cmds.xform(
            pJointList[-1],
            rotation=True,
            worldSpace=True,
            q=True,
        )
    )  # the first elemeent in the joint list
    jointTransList.append(
        cmds.xform(
            pJointList[0],
            translation=True,
            worldSpace=True,
            q=True,
        )
    )  # the last element in the joint list
    jointTransList.append(
        cmds.xform(
            pJointList[-1],
            translation=True,
            worldSpace=True,
            q=True,
        )
    )  # the last element in the joint list

    helperJoints = []

    cmds.select(deselect=True)
    helperJoints.append(
        cmds.joint(
            position=jointTransList[0],
            orientation=jointRotList[0],
            name=pJointList[0] + "_helper",
        )
    )
    cmds.select(deselect=True)
    helperJoints.append(
        cmds.joint(
            position=jointTransList[-1],
            orientation=jointRotList[-1],
            name=pJointList[-1] + "_helper",
        )
    )

    cmds.parent(
        helperJoints[-1], helperJoints[0]
    )  # parent the current joint to the previous joint

    # parent constrain the helper joints to the controllers
    cmds.parentConstraint(controlCurveList[0], helperJoints[0])
    cmds.parentConstraint(controlCurveList[-1], helperJoints[-1])

    # CREATE MIDDLE DRIVER LOC
    # place a locator between the first and last joint
    cmds.spaceLocator(n="Loc_M")  # create locator
    cmds.group("Loc_M", n="Loc_M_offset")
    cmds.parentConstraint(firstJoint, lastJoint, "Loc_M_offset")

    # CREATE THE SCALE EXPRESSIONS

    statement = "$peak / pow(1 + $blend * $dist, 2)"

    cmds.expression(
        object="Loc_M_offset",
        string=f" float $dist = abs({helperJoints[-1]}.translateX) + abs({helperJoints[-1]}.translateY) + abs({helperJoints[-1]}.translateZ); float $peak = 6; float $blend = .6; Loc_M_offset.scaleX = {statement}; Loc_M_offset.scaleY = {statement}; Loc_M_offset.scaleZ = {statement};",
    )

    # scale constraint the middle joints to their controller
    for jnt in pJointList:
        if jnt == firstJoint or jnt == lastJoint:
            continue
        cmds.scaleConstraint(jnt + "_ctrl", jnt, mo=True)

    centerJoint = []

    for jnt in pJointList:  # scale constrain all the joints to their controllers
        cmds.scaleConstraint(jnt + "_ctrl", jnt, mo=True)

    # determine if there is odd or even amount of joints
    if len(pJointList) % 2 == 0:  # if even
        centerIndex = [(len(pJointList) // 2) - 1, len(pJointList) // 2]

        # scale constraint the offset groups of the controllers to locM and start/end controller
        for x in range(len(controlCurveList)):
            weight = 100 / centerIndex[0] * x
            opWeight = abs(100 - weight)

            if (
                x == 0 or x == len(controlCurveList) - 1
            ):  # skip the first and last controllers
                continue
            elif x < centerIndex[0]:  # if to the left of the center
                cmds.scaleConstraint(
                    pJointList[centerIndex[0]] + "_ctrl",
                    firstJoint + "_ctrl",
                    pJointList[x] + "_offset",
                    mo=True,
                )  # scale constrain the offset ctrl groups to the center controllers and start controller
                cmds.setAttr(
                    pJointList[x]
                    + "_offset_scaleConstraint1."
                    + pJointList[centerIndex[0]]
                    + "_ctrlW0",
                    weight,
                )
                cmds.setAttr(
                    pJointList[x]
                    + "_offset_scaleConstraint1."
                    + firstJoint
                    + "_ctrlW1",
                    opWeight,
                )
            elif x > centerIndex[1]:  # if to the right of the center
                cmds.scaleConstraint(
                    pJointList[centerIndex[1]] + "_ctrl",
                    lastJoint + "_ctrl",
                    pJointList[x] + "_offset",
                    mo=True,
                )
                cmds.setAttr(
                    pJointList[x]
                    + "_offset_scaleConstraint1."
                    + pJointList[centerIndex[1]]
                    + "_ctrlW0",
                    weight,
                )  # this is wrong
                cmds.setAttr(
                    pJointList[x] + "_offset_scaleConstraint1." + lastJoint + "_ctrlW1",
                    opWeight,
                )
            else:  # if we are at the center joints
                cmds.scaleConstraint(
                    "Loc_M", pJointList[centerIndex[0]] + "_offset", mo=True
                )
                cmds.scaleConstraint(
                    "Loc_M", pJointList[centerIndex[1]] + "_offset", mo=True
                )

            # calculate the distance from the center joint and then use that to determine the scale strength

    else:  # if odd
        centerIndex = len(pJointList) // 2

        for x in range(len(controlCurveList)):
            weight = (
                100 / centerIndex * x
            )  # this is wrong after we get to the right side
            opWeight = abs(100 - weight)

            if (
                x == 0 or x == len(controlCurveList) - 1
            ):  # skip the first and last controllers
                continue
            elif x < centerIndex:  # if to the left of the center
                cmds.scaleConstraint(
                    pJointList[centerIndex] + "_ctrl",
                    firstJoint + "_ctrl",
                    pJointList[x] + "_offset",
                    mo=True,
                )
                cmds.setAttr(
                    pJointList[x]
                    + "_offset_scaleConstraint1."
                    + pJointList[centerIndex]
                    + "_ctrlW0",
                    weight,
                )
                cmds.setAttr(
                    pJointList[x]
                    + "_offset_scaleConstraint1."
                    + firstJoint
                    + "_ctrlW1",
                    opWeight,
                )
            elif x > centerIndex:  # if to the right of the center
                cmds.scaleConstraint(
                    pJointList[centerIndex] + "_ctrl",
                    lastJoint + "_ctrl",
                    pJointList[x] + "_offset",
                    mo=True,
                )
                cmds.setAttr(
                    pJointList[x]
                    + "_offset_scaleConstraint1."
                    + pJointList[centerIndex]
                    + "_ctrlW0",
                    weight,
                )  # this is wrong
                cmds.setAttr(
                    pJointList[x] + "_offset_scaleConstraint1." + lastJoint + "_ctrlW1",
                    opWeight,
                )
            else:  # if we are at the center joints, skip
                cmds.scaleConstraint(
                    "Loc_M", pJointList[centerIndex] + "_offset", mo=True
                )

    # the middle has 100 scaling, as the joints get further away, the scaling influence decreases

    # GROUP EVERYTHING INTO stretchy_grp
    # create group
    stretchy_grp = cmds.group(
        f"{pJointList[0]}_helper", "Loc_M_offset", n="stretchy_grp"
    )

    # add the controllers into it
    for jnt in pJointList:
        cmds.parent(jnt + "_offset", stretchy_grp)

    """These next lines are necessary to set up the deletion system"""
    # Add the name of the stretchy group to all joints affected
    for jnt in pJointList:
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
        len(pJointList),
        *pJointList,
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
