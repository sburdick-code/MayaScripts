import maya.cmds as cmds
import maya.mel as mel


def prep_mixamo_rig():
    """
    Prepares the mixamo rig for animation matching by setting it to a T-Pose at frame -1.

    Args:
        None

    Returns:
        mixamoJointList (list):
    """
    cmds.select(clear=True)
    mixamoHipJoint = cmds.ls("*:Hips")[0]

    cmds.select(mixamoHipJoint, hi=True)
    mixamoJointList = cmds.ls(sl=True, type="joint")
    print(f"Mixamo Joints: {mixamoJointList}")

    cmds.currentTime(0)
    cmds.setKeyframe()

    cmds.currentTime(-1)
    for i in range(len(mixamoJointList)):
        cmds.xform(mixamoJointList[i], ro=[0, 0, 0])
    cmds.xform(mixamoHipJoint, t=[0, 104.25, 8.6])
    cmds.setKeyframe()

    return mixamoJointList


def prep_unreal_rig():
    """
    Prepares the UE rig for animation matching by connecting the appropriate IK joints
    via constraints setting it in a T-Pose at frame -1.

    Args:
        None

    Returns:
        unrealJointList (list):
    """
    cmds.currentTime(-1)
    cmds.select(clear=True)
    unrealRootJoint = cmds.ls("*:root")[0]

    cmds.select(unrealRootJoint, hi=True)
    unrealJointList = cmds.ls(sl=True, type="joint")
    print(f"Unreal Joints: {unrealJointList}")

    # parent constrain necessary joints
    jointsToConstrain = [
        {
            "name": "ik_foot_root",
            "index": 152,
            "parentIndex": 0,
            "point": [True, "y"],
            "orient": [False, "none"],
        },
        {
            "name": "ik_foot_l",
            "index": 153,
            "parentIndex": 131,
            "point": [True, "none"],
            "orient": [True, "none"],
        },
        {
            "name": "ik_foot_r",
            "index": 154,
            "parentIndex": 108,
            "point": [True, "none"],
            "orient": [True, "none"],
        },
        {
            "name": "ik_hand_root",
            "index": 155,
            "parentIndex": 0,
            "point": [True, "y"],
            "orient": [False, "none"],
        },
        {
            "name": "ik_hand_gun",
            "index": 156,
            "parentIndex": 66,
            "point": [True, "none"],
            "orient": [True, "none"],
        },
        {
            "name": "ik_hand_l",
            "index": 157,
            "parentIndex": 20,
            "point": [True, "none"],
            "orient": [True, "none"],
        },
        {
            "name": "ik_hand_r",
            "index": 158,
            "parentIndex": 66,
            "point": [True, "none"],
            "orient": [True, "none"],
        },
        {
            "name": "interaction",
            "index": 159,
            "parentIndex": 0,
            "point": [True, "y"],
            "orient": [False, "none"],
        },
        {
            "name": "center_of_mass",
            "index": 160,
            "parentIndex": 0,
            "point": [True, "y"],
            "orient": [False, "none"],
        },
    ]

    pointConstraints = []
    orientConstraints = []

    for joint in jointsToConstrain:
        if joint["point"][0]:
            pointConstraints.append(
                cmds.pointConstraint(
                    unrealJointList[joint["parentIndex"]],
                    unrealJointList[joint["index"]],
                    sk=joint["point"][1],
                    mo=True,
                )
            )
        if joint["orient"][0]:
            orientConstraints.append(
                cmds.orientConstraint(
                    unrealJointList[joint["parentIndex"]],
                    unrealJointList[joint["index"]],
                    sk=joint["orient"][1],
                    mo=True,
                )
            )

    jointsToZero = [
        {
            "name": "upperarm_r",
            "index": 57,
            "ro": [0, -7, 0],
        },
        {
            "name": "lowerarm_r",
            "index": 58,
            "ro": [0, 0, 0],
        },
        {
            "name": "hand_r",
            "index": 66,
            "ro": [-86.179, 0, 0],
        },
        {
            "name": "thumb_01_r",
            "index": 85,
            "ro": [75, 40, 20],
        },
        {
            "name": "upperarm_l",
            "index": 11,
            "ro": [0, -7, 0],
        },
        {
            "name": "lowerarm_l",
            "index": 12,
            "ro": [0, 0, 0],
        },
        {
            "name": "hand_l",
            "index": 20,
            "ro": [-86.179, 0, 0],
        },
        {
            "name": "thumb_01_l",
            "index": 31,
            "ro": [75, 40, 20],
        },
        {
            "name": "thigh_r",
            "index": 106,
            "ro": [0, 0, 180],
        },
        {
            "name": "thigh_l",
            "index": 129,
            "ro": [0, 0, 0],
        },
    ]

    # "zero" out the arm and leg joints
    for joint in jointsToZero:
        cmds.xform(unrealJointList[joint["index"]], ro=joint["ro"])

    # zero out the fingers, but not the metacarpals
    for i in range(24, 41):
        if (
            "metacarpal" not in unrealJointList[i]
            and "thumb_01" not in unrealJointList[i]
        ):
            cmds.xform(unrealJointList[i], ro=[0, 0, 0])
    for i in range(70, 87):
        if (
            "metacarpal" not in unrealJointList[i]
            and "thumb_01" not in unrealJointList[i]
        ):
            cmds.xform(unrealJointList[i], ro=[0, 0, 0])

    return unrealJointList


def bake_animation():
    """
    Bakes the animation onto the UE rig and hides the mixamo rig

    Args:
        None

    Returns:
        None
    """

    # Populate the joint lists with their respective joints and prep the rigs for baking
    mixamoJoints = prep_mixamo_rig()
    unrealJoints = prep_unreal_rig()

    # These variables will store the joints to be baked and the constraints to be deleted after baking
    toBake = []
    constraints = []

    # This dictionary holds the related joint indexes in the mixamoJoints and unrealJoints
    connectionList = {
        "Root": [0, 0],
        "Hips": [0, 1],
        "Spine1": [1, 3],
        "Spine2": [2, 4],
        "Spine3": [3, 5],
        "Neck": [4, 7],
        "Head": [5, 9],
        "HeadTop_End": [6, -1],
        "RightShoulder": [7, 56],
        "RightArm": [8, 57],
        "RightForeArm": [9, 58],
        "RightHand": [10, 66],
        "LeftShoulder": [31, 10],
        "LeftArm": [32, 11],
        "LeftForeArm": [33, 12],
        "LeftHand": [34, 20],
        "RightUpLeg": [55, 106],
        "RightLeg": [56, 107],
        "RightFoot": [57, 108],
        "RightToe": [59, 109],
        "LeftUpLeg": [60, 129],
        "LeftLeg": [61, 130],
        "LeftFoot": [62, 131],
        "LeftToeBase": [63, 132],
    }

    # Set up the correct constraint per joint
    for joint in connectionList:
        if joint == "Root":
            newC = cmds.pointConstraint(
                mixamoJoints[connectionList[joint][0]],
                unrealJoints[connectionList[joint][1]],
                sk="z",
                mo=True,
            )
            toBake.append(unrealJoints[connectionList[joint][1]])
            constraints += newC
            continue

        elif joint == "Hips" or joint == "RightFoot" or joint == "LeftFoot":
            newC = cmds.pointConstraint(
                mixamoJoints[connectionList[joint][0]],
                unrealJoints[connectionList[joint][1]],
                mo=True,
            )
            constraints += newC

        newC = cmds.orientConstraint(
            mixamoJoints[connectionList[joint][0]],
            unrealJoints[connectionList[joint][1]],
            mo=True,
        )

        toBake.append(unrealJoints[connectionList[joint][1]])
        constraints += newC

    print(f"To Bake: {toBake}")

    # Get the length of the animation to bake
    timeRange = -2 + cmds.keyframe(
        f"{mixamoJoints[0]}.translateX", query=True, keyframeCount=True
    )
    cmds.playbackOptions(
        ast=0, aet=timeRange
    )  # Set the timeline to the animation length

    # Bake the animation from the Mixamo Rig onto the Unreal Rig
    cmds.bakeResults(
        toBake,
        simulation=True,
        t=(0, timeRange),
        sampleBy=1,
        minimizeRotation=True,
        oversamplingRate=1,
        disableImplicitControl=True,
        preserveOutsideKeys=True,
        sparseAnimCurveBake=False,
        removeBakedAttributeFromLayer=False,
        removeBakedAnimFromLayer=False,
        bakeOnOverrideLayer=False,
        controlPoints=False,
        shape=True,
    )

    # Delete Constraints on Unreal Skeleton
    print(f"To Delete: {constraints}")
    cmds.select(clear=True)
    cmds.delete(constraints)

    # Hide the mixamo Rig
    # Currently only works with X Bot Character. Add a way to serch for the skinned mesh
    toHide = [mixamoJoints[0], "Beta_Surface", "Beta_Joints"]
    mixamoGroup = cmds.group(n="MixamoRig", empty=True)
    cmds.parent(toHide, mixamoGroup)
    cmds.hide(mixamoGroup)

    # Open up Game Exporter
    mel.eval("gameFbxExporter;")


cmds.currentUnit(time="ntsc")  # set the time to 30fps (NTSC)
bake_animation()
