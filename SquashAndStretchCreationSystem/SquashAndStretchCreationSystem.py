import maya.cmds as cmds

def main():
    #MAIN BODY CODE GOES HERE!

####################################################################################################################################

def create_placement_locators( pName ):
    # Set the scale of the locators and the translation of the last locator
    scaleValue = 10
    translateValue = [ 0, 100, 0 ]

    # Create the locator system and scale them up
    firstPL = cmds.spaceLocator( name = pName + "_firstPlacement" ) 
    cmds.scale( scaleValue, scaleValue, scaleValue, firstPL )
    firstGroup = cmds.group( name = pName + "_first_off" )
    middlePL = cmds.spaceLocator( name = pName + "_middlePlacement" )
    cmds.scale( scaleValue, scaleValue, scaleValue, middlePL )
    middleGroup = cmds.group( name = pName + "_middle_off" )
    lastPL = cmds.spaceLocator( name = pName + "_lastPlacement" )
    cmds.scale( scaleValue, scaleValue, scaleValue, lastPL )
    lastGroup = cmds.group( name = pName + "_last_off" )

    # Constrain the middle locator's offset group to follow in between the origin and insertion locators
    cmds.parentConstraint( firstPL, middleGroup)
    cmds.parentConstraint( lastPL, middleGroup)

    #Move the system to translate value
    cmds.xform( lastGroup, ws = True, translation = translateValue )

    #Group the system under the group placementLocators_grp
    locatorGroup = cmds.group( em = True, name = pName + "_placementLocators_grp" )
    cmds.parent( firstGroup, locatorGroup )
    cmds.parent( lastGroup, locatorGroup )
    cmds.parent( middleGroup, locatorGroup )

    #Return the locators
    return firstPL, lastPL, middlePL

####################################################################################################################################

def create_jointchain_at_locators( pName, pFirstPL, pLastPL, pMiddlePL ):

    # Get the location and rotation of the locators
    firstLoc = cmds.xform( pFirstPL, query=True, translation=True, ws=True )
    middleLoc = cmds.xform( pMiddlePL, query=True, translation=True, ws=True )
    lastLoc = cmds.xform( pLastPL, query=True, translation=True, ws=True )

    translationList = [ firstLoc, middleLoc, lastLoc ]

    firstRot = cmds.xform( pFirstPL, query=True, rotation=True, ws=True )
    middleRot = cmds.xform( pMiddlePL, query=True, rotation=True, ws=True )
    lastRot = cmds.xform( pLastPL, query=True, rotation=True, ws=True )

    rotationList = [ firstRot, middleRot, lastRot ]

    # Create the joints
    cmds.select( cl=True )
    firstJoint = cmds.joint( name=pName + "_01")
    middleJoint = cmds.joint( name=pName + "_02")
    lastJoint = cmds.joint( name=pName + "_03")

    jointList = [ firstJoint, middleJoint, lastJoint ]

    # Move the joints to the proper location
    for num in range( len(jointList) ):
        cmds.xform( jointList[num], ws=True, translation=translationList[num], rotation=rotationList[num] )
        
    # Get the parent group of the locators and delete it
    parentGroup = cmds.listRelatives( cmds.listRelatives( pFirstPL, parent=True ), parent=True ) 
    
    print( f"deleting {parentGroup[0]}" )
    cmds.delete( parentGroup[0] )

####################################################################################################################################
# MAIN
####################################################################################################################################

main()