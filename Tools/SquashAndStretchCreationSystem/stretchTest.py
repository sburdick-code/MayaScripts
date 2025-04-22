import maya.cmds as cmds


def createController(
    pName,
    pJoint,
):

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


firstJnt = cmds.ls(sl=True, type="joint")[0]

cmds.select(firstJnt, hi=True)
jointList = cmds.ls(sl=True, type="joint")

lastJnt = jointList[-1]

secondJnt = jointList[1]

firstJntLoc = cmds.xform(firstJnt, q=True, t=True, ws=True)
lastJntLoc = cmds.xform(lastJnt, q=True, t=True, ws=True)

cmds.select(clear=True)
helper1 = cmds.joint(p=firstJntLoc, n="helper1_jnt")
cmds.joint(helper1, e=True, zso=True, oj="xyz")
cmds.select(clear=True)
helper2 = cmds.joint(p=lastJntLoc, n="helper2_jnt")

firstController = createController(firstJnt, firstJnt)[0]
lastController = createController(lastJnt, lastJnt)[0]

cmds.pointConstraint(firstController, firstJnt)
cmds.pointConstraint(lastController, lastJnt)
cmds.parentConstraint(lastController, helper2)

cmds.parent(helper1, firstJnt)
cmds.parent(helper2, firstJnt)
cmds.parent(secondJnt, helper1)
cmds.parent(lastController + "_offset", firstController)

distanceNode = cmds.shadingNode("distanceBetween", asUtility=True, n="distanceBetween")
cmds.connectAttr(helper2 + ".translate", distanceNode + ".point1")
defaultDistance = cmds.getAttr(distanceNode + ".distance")

distanceFactor = cmds.shadingNode("multiplyDivide", asUtility=True, n="distanceFactor")
cmds.setAttr(distanceFactor + ".input2X", defaultDistance)
cmds.setAttr(distanceFactor + ".operation", 2)
cmds.connectAttr(distanceNode + ".distance", distanceFactor + ".input1X")

invertIt = cmds.shadingNode("multiplyDivide", asUtility=True, n="invertIt")
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
    x = 3

else:  # if odd
    centerIndex = [len(jointList) // 2, len(jointList) // 2]
    x = 2

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

        multDiv = cmds.shadingNode("multiplyDivide", asUtility=True, n="multDiv")
        cmds.setAttr(multDiv + ".input2X", posFactor)
        cmds.connectAttr(invertIt + ".outputX", multDiv + ".input1X")
        plusMinusAvg = cmds.shadingNode(
            "plusMinusAverage", asUtility=True, n="plusMinusAvg"
        )
        cmds.setAttr(plusMinusAvg + ".operation", 2)
        cmds.setAttr(plusMinusAvg + ".input2D[1].input2Dx", posFactor)
        cmds.connectAttr(multDiv + ".outputX", plusMinusAvg + ".input2D[0].input2Dx")
        exponent = cmds.shadingNode("floatMath", asUtility=True, n="exponent1")
        cmds.setAttr(exponent + ".floatA", uniScale)
        cmds.setAttr(exponent + ".operation", 6)
        cmds.connectAttr(plusMinusAvg + ".output2Dx", exponent + ".floatB")
        cmds.connectAttr(exponent + ".outFloat", jointList[i] + ".scaleY")
        cmds.connectAttr(exponent + ".outFloat", jointList[i] + ".scaleZ")

    else:  # we are to the right of the chain
        exponent = "exponent" + str(i - x)
        print(str(i) + "-" + str(x) + "=" + str(i - x))
        x = x + 2
        cmds.connectAttr(exponent + ".outFloat", jointList[i] + ".scaleY")
        cmds.connectAttr(exponent + ".outFloat", jointList[i] + ".scaleZ")


# need to know if they already have controllers
# if they have controllers already, then we need to set the constraints accordingly, if not, then we create them ourselves
# we need to know what the last joint in the joint chain is as well, so we know where to limit the stretch
# will need to make the stuff include the proper naming
# delete function will need to delete all the relevant utility nodes and remove hrlper nodes
