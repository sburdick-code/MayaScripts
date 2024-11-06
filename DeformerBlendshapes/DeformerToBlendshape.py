#################################################################################################################################################
#
#    Script:          DeformerToBlendshape.py
#    Authors:         Audrey Paransky
#    Last Updated:    11/05/2024
#    Created:         11/05/2024
#
#    This python script converts deformer animation into baked blendshape animation by creating a blendshape for every frame in the timeline
#    and setting a keyframe. Users must first select the animated mesh before running the code.
#
################################################################################################################################################

"""
    1) Duplicates the selected mesh and creates a new target mesh and a blendshape mesh for every frame in the active timeline.
    2) Each frame, the weights of the blendshapes will alternate between 0 and 1 and will be keyframed such that only one blendshape is active at a time.
    3) Then it bakes the blendshape animation to the new target mesh and deletes the blendshape meshes.
"""

import maya.cmds as cmds
import maya.mel as mel

targetMesh = cmds.ls(selection=True)[0]
newTarget = cmds.duplicate(targetMesh, n=targetMesh + "_Target")[0]

start_frame = int(cmds.playbackOptions(query=True, min=True))
end_frame = int(cmds.playbackOptions(query=True, max=True))

blendList = []

# Loop through each frame in the active time slider range
for frame in range(start_frame, end_frame + 1):
    # Set the current time to this frame
    cmds.currentTime(frame)
    blendshape = cmds.duplicate(targetMesh, n="source" + str(frame))[0]
    blendList.append(blendshape)

cmds.select(blendList)
cmds.select(newTarget, add=True)
convertedBlendshape = cmds.blendShape(n=targetMesh + "_Converted")[0]

for frame in range(start_frame, end_frame + 1):
    cmds.currentTime(frame)
    for bn in blendList:
        if bn == blendList[frame]:
            cmds.setAttr(convertedBlendshape + "." + bn, 1)
        else:
            cmds.setAttr(convertedBlendshape + "." + bn, 0)
        cmds.setKeyframe(convertedBlendshape + "." + bn)

cmds.select(newTarget)
mel.eval("BakeTopologyToTargets;")

cmds.delete(blendList)
