import maya.cmds as cmds
import functools

def main():
    create_ui("MyWindowName")

####################################################################################################################################

def create_ui( pWindowName ):
    windowID = 'squashStretchSystemGenerator'


    if cmds.window( windowID, exists=True ):
        cmds.deleteUI( windowID )

    window = cmds.window( windowID, title=pWindowName, widthHeight=(320, 410) )

    cmds.columnLayout( adjustableColumn=True )


    # NEW JOINT CHAIN ---------------------------------------------
    # FIRST ROW ---------------------------
    cmds.separator( height=10 )

    # SECOND ROW --------------------------
    cmds.text( label='CREATE NEW STRETCHY JOINT CHAIN', font='boldLabelFont' )

    # THIRD ROW ---------------------------
    cmds.separator( style='none', height=10 )
    cmds.text( label='1. Placement Locator')
    

    # FOURTH ROW --------------------------
    cmds.button( label='Create and Set Placement Locators', command = functools.partial(create_placement_locators,
                                                                                        'JOINT_NAMES')  )

    # FIFTH ROW ---------------------------
    cmds.separator( style='none', height=10 )
    cmds.text( label='2. How Many Segments?')
    

    # SIXTH ROW ---------------------------
    cmds.setParent( '..' )
    cmds.rowLayout( adj=3, numberOfColumns=6 )
    cmds.text( label='Segment Count:')
    genJointCount = cmds.textField( pht="#", editable=True, aie=True )
    cmds.separator( style='none', height=10 )
    cmds.text( label= 'Parent Joint:' )
    genJointParent = cmds.textField( pht="Parent Joint", editable=True, aie=True )
    cmds.button(label='Select', command = functools.partial(select_object,
                                                            genJointParent))
    
    # SEVENTH ROW -------------------------
    cmds.setParent( '..' )
    cmds.separator( style='none', height=10 )
    cmds.text(label='3. Create System')

    # EIGHTH ROW --------------------------
    cmds.button( label='Generate', command= functools.partial (create_jointchain_at_locators,
                                                               'arg1', 'arg2', 'arg3' ))
                                                           
    # NINTH ROW ---------------------------
    cmds.separator( style='none', height=10 )
    cmds.separator( height=10 ) 
                                                              
    cmds.showWindow( window )

####################################################################################################################################

def get_selection(*pArgs):
    selection = cmds.ls( selection=True, type=objType)
        
    if selection:
        cmds.textField( pField, edit=True, text=selection[0] )
    else:
        cmds.error( f"No {objType} selected!", n=True )

####################################################################################################################################

def delete_stretchy_system( pStretchyGroup ):
    print('hello')
    # This function will create the formatted GUI for our script

####################################################################################################################################
def create_stretchy_system( pTextField1, pTextField2, *pArgs ):

    firstJoint = cmds.textField( pTextField, query=True, text=True )
    lastJoint = cmds.textField( pTextField, query=True, text=True )

    pJointList = # find every joint btwn

    if (len(pJointList) >= 3):
        #if the grp already exists, delete it
        if cmds.objExists( 'stretchy_grp' ):
            cmds.delete( stretchy_grp )
            
        #CREATE CONTROLLERS
        controlCurveList = []
            
        for jnt in pJointList:
            ## Joint Information
            # Get parent of current joint
            jntParent = cmds.listRelatives( jnt, parent=True )
            if( jntParent ):
                jntParentName = jntParent[0]
            else:
                jntParentName = "GARBAGE" #this is for the first joint in the heirarchy since it has no parent. there needs to be something
                
            # Get Radius of current joint
            jntRadius = cmds.getAttr( jnt + '.radius' )
            
            # Get translation and rotation of current joint
            jntTranslation = cmds.xform( jnt, query=True, translation=True, worldSpace=True )
            jntRotation = cmds.xform( jnt, query=True, rotation=True, worldSpace=True )
            
            ## Controller Manipulation
            # Create new controller
            newControl = cmds.circle( c=(0, 0, 0), name=(jnt + '_ctrl') ) #c changes the shape of the cirlce, 0,0,0 ensures that it's a full circle
            controlCurveList.append( newControl[0] ) #newControl will return a dictionary containing the transform and the shape node, you just want the name, hence [0]
            cmds.move( jntTranslation[0], jntTranslation[1], jntTranslation[2], newControl )
            cmds.rotate( 90, 0, 90, newControl )
            cmds.scale( ( 1*jntRadius ), ( 1*jntRadius ), ( 1*jntRadius ), newControl )
            cmds.makeIdentity( newControl, apply=True )
            
            # Create the offset group for our new controller
            newGroup = cmds.group( empty=True, name=(jnt + '_offset') )
            cmds.move( jntTranslation[0], jntTranslation[1], jntTranslation[2], newGroup ) #the group and the cntrl are at the same place
            cmds.makeIdentity( newGroup, apply=True ) #freeze transformations
            
            # Make new control a child of new group
            cmds.parent( newControl, newGroup )
            
            # Rotate offset group to match the rotations of the joint
            cmds.rotate( jntRotation[0], jntRotation[1], jntRotation[2], newGroup )
            
            '''
            ## Place group in the right hierarchy
            if ( jntParentName + '_ctrl' ) in controlCurveList:
                cmds.parent( newGroup, (jntParentName + '_ctrl') )
                print( newGroup + ' parented under ' + jntParentName + '_ctrl' )
            else:
                print( 'No parent found' )
                print( jntParentName ) 
                print( controlCurveList )
            '''
                
            ## Parent constrain joint under control
            cmds.parentConstraint( newControl, jnt )
            
        #PARENT CONSTRAIN THE MIDDLE CONTROLLER OFFSET GROUP TO THE START AND END CONTROLLERS
        cmds.parentConstraint( controlCurveList[0], controlCurveList[-1], pJointList[1]+'_offset' )
        
        #BUILD HELPER JOINTS
        jointRotList = []
        jointTransList = []
            
        jointRotList.append(cmds.xform( pJointList[0], rotation = True, worldSpace = True, q = True, )) #the first elemeent in the joint list
        jointRotList.append(cmds.xform( pJointList[-1], rotation = True, worldSpace = True, q = True, )) #the first elemeent in the joint list
        jointTransList.append(cmds.xform( pJointList[0], translation = True, worldSpace = True, q = True, )) #the last element in the joint list
        jointTransList.append(cmds.xform( pJointList[-1], translation = True, worldSpace = True, q = True, )) #the last element in the joint list
        
        helperJoints = []
        
        cmds.select( deselect = True )
        helperJoints.append( cmds.joint( position = jointTransList[0], orientation = jointRotList[0], name = pJointList[0]+'_helper' ) )
        cmds.select( deselect = True )
        helperJoints.append( cmds.joint( position = jointTransList[-1], orientation = jointRotList[-1], name = pJointList[-1]+'_helper' ) )
        
        cmds.parent( helperJoints[-1], helperJoints[0] ) #parent the current joint to the previous joint
        
        #parent constrain the helper joints to the controllers
        cmds.parentConstraint( controlCurveList[0], helperJoints[0] )
        cmds.parentConstraint( controlCurveList[-1], helperJoints[-1] )
        
        #CREATE THE SCALE EXPRESSIONS
        
        middleOffCtrl = pJointList[1]+'_offset'
        statement = "$peak / pow(1 + $blend * $dist, 2)"
        
        cmds.expression( object = middleOffCtrl, string = f" float $dist = abs({helperJoints[-1]}.translateX) + abs({helperJoints[-1]}.translateY) + abs({helperJoints[-1]}.translateZ); float $peak = 6; float $blend = .6; {middleOffCtrl}.scaleX = {statement}; {middleOffCtrl}.scaleY = {statement}; {middleOffCtrl}.scaleZ = {statement};" )
        
        #scale constraint the middle joint to the controller
        cmds.scaleConstraint( pJointList[1]+"_ctrl", pJointList[1], mo = True)
        
        #GROUP EVERYTHING INTO stretchy_grp
        #create group
        stretchy_grp = cmds.group( f"{pJointList[0]}_helper" , n='stretchy_grp' )
        
        #add the controllers into it
        for jnt in pJointList:
            cmds.parent( jnt + '_offset', stretchy_grp )
            
    else:
        print("not enough joints selected (3 required)")

####################################################################################################################################

def create_placement_locators( pName, *pArgs ):
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

def create_jointchain_at_locators( pName, pFirstPL, pLastPL, pMiddlePL, *pArgs ):

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

    create_stretchy_system( jointList )

####################################################################################################################################
# MAIN
####################################################################################################################################

main()