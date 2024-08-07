import maya.cmds as cmds
import functools

def main():
    create_ui("MyWindowName")

####################################################################################################################################

def create_ui(pWindowTitle):

    windowID = 'hello'
    
    # Check if the window exists
    if cmds.window( windowID, exists=True ):
        cmds.deleteUI( windowID )

    window = cmds.window( windowID, title=pWindowTitle, sizeable=True )
    cmds.columnLayout( adj=True )

    # First row ####################
    cmds.text( label='EXISTING JOINT CHAIN', font='boldLabelFont' )

    # Second row ####################
    cmds.rowLayout( adj=2, numberOfColumns=3 )
    cmds.text( label='first' )
    originParentField = cmds.textField( pht='Origin Parent Joint', ed=True )
    cmds.button( label='Select', command=functools.partial( get_selection, originParentField, 'joint' ) )

    cmds.setParent( '..' )

    # Third row ####################
    cmds.rowLayout( adj=2, numberOfColumns=3 )
    cmds.text( label='last' )
    insertionParentField = cmds.textField( pht='Insertion Parent Joint', ed=True )
    cmds.button( label='Select', command=functools.partial( get_selection, insertionParentField, 'joint' ) )
    
    cmds.setParent( '..' )
    
    # Fourth row ####################
    cmds.button( label='Generate', command=functools.partial( create_stretchy_system, 
                                                              originParentField, insertionParentField ) ) #change this after create_stretchy_system edits
    #cmds.button( label='Help', command=functools.partial( display_Help_UI ) )

        # NEW JOINT CHAIN ---------------------------------------------
    # ROW 01 ---------------------------
    cmds.separator( height=10 )

    # ROW 02 ---------------------------
    cmds.text( label='CREATE NEW STRETCHY JOINT CHAIN', font='boldLabelFont' )

    # ROW 03 ---------------------------
    cmds.separator( style='none', height=10 )
    
    # ROW 04 ---------------------------
    cmds.text( label='1. Parameters')
    
    # ROW 05 ---------------------------
    cmds.rowLayout( adj=3, numberOfColumns=4 )
    cmds.separator( style='none', height=10, width=30 )
    cmds.text( label= 'Name:' )
    genNameTextField = cmds.textField( pht="Joint Names", editable=True, aie=True )
    cmds.separator( style='none', height=10, width=30 )
    
    # ROW 06 --------------------------
    cmds.setParent( '..' )
    cmds.rowLayout( adj=3, numberOfColumns=6 )
    cmds.text( label='Segment Count:')
    genJointCountField = cmds.textField( pht="#", editable=True, aie=True )
    cmds.separator( style='none', height=10 )
    cmds.text( label= 'Parent Joint:' )
    genJointParentField = cmds.textField( pht="Parent Joint", editable=True, aie=True )
    cmds.button(label='Select', command=functools.partial( get_selection,
                                                           genJointParentField, 'joint' ) )
    
    # ROW 07 --------------------------
    cmds.setParent( '..' )
    cmds.separator( style='none', height=10 )
    
    # ROW 08 --------------------------
    cmds.text( label='2. Placement Locators')
    
    # ROW 09 --------------------------
    cmds.button( label='Create and Set Placement Locators', command=functools.partial( create_placement_locators,
                                                                                       genNameTextField, genJointCountField, genJointParentField ) )

    # ROW 10 --------------------------
    cmds.separator( style='none', height=10 )
    
    # ROW 11 --------------------------
    cmds.text(label='3. Create System')

    # ROW 12 --------------------------
    cmds.button( label='Generate', command=functools.partial( create_jointchain_at_locators,
                                                              genNameTextField, genJointCountField, genJointParentField ) )
                                                           
    # ROW 13 ---------------------------
    cmds.separator( style='none', height=10 )
    
    # ROW 14 ---------------------------
    cmds.separator( height=10 )  
                                                              
    cmds.showWindow( window )

####################################################################################################################################

def get_selection( pField, objType, *pArgs):
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

    firstJoint = cmds.textField( pTextField1, query=True, text=True )
    lastJoint = cmds.textField( pTextField2, query=True, text=True )
    
    pJointList = []
    
    cmds.select( firstJoint, hi=True )
    pJointList = cmds.ls( sl=True, type='joint' )
    print( pJointList )

    if not (len(pJointList) >= 3): #if there arent at least 3 joints in the pre existing group
        cmds.error("not enough joints in chain (at least 3 required)", n=True)
        return 0
        
    #if the grp already exists, delete it
    if cmds.objExists( 'stretchy_grp' ):
        cmds.delete( 'stretchy_grp' )
        
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
        newControl = cmds.spaceLocator( name=(jnt + '_ctrl') )
        controlCurveList.append( newControl[0] ) #newControl will return a dictionary containing the transform and the shape node, you just want the name, hence [0]
        cmds.move( jntTranslation[0], jntTranslation[1], jntTranslation[2], newControl )
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
    
    '''    
    #PARENT CONSTRAIN THE MIDDLE CONTROLLER OFFSET GROUP TO THE START AND END CONTROLLERS
    cmds.parentConstraint( controlCurveList[0], controlCurveList[-1], pJointList[1]+'_offset' )
    '''
    
    #PARENT CONSTRAIN THE MIDDLE CONTROLLER OFFSET GROUPS TO THEIR ADJACENT CONTROLLERS
    for x in range( len( pJointList ) ) :
        if pJointList[x] == firstJoint or pJointList[x] == lastJoint:
            continue
            
        cmds.parentConstraint( controlCurveList[x-1], controlCurveList[x+1], pJointList[x]+'_offset' )
    
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

####################################################################################################################################

def create_placement_locators( pNameField, pNumberField, pParentJoint, *pArgs ):

    # Check if all parameters are filled
    if not( ( cmds.textField(pNameField, query=True, text=True) )and( int(cmds.textField( pNumberField, query=True, text=True )) > 0 )and( cmds.textField(pParentJoint, query=True, text=True) ) ):
        cmds.error("Parameters not valid", n=True)
        return 0
    elif not( cmds.objExists( cmds.textField(pParentJoint, query=True, text=True) ) ):
        cmds.error("No valid parent joint parameter", n=True)
        return 0

    # Set the scale of the locators and the translation of the last locator
    scaleValue = 1
    translateValue = [ 0, 100, 0 ]
    number = int(cmds.textField( pNumberField, query=True, text=True ))
    pName = cmds.textField( pNameField, query=True, text=True )

    # Create the locator system and scale them up
    firstPL = cmds.spaceLocator( name = pName + "_firstPlacement" ) 
    cmds.scale( scaleValue, scaleValue, scaleValue, firstPL )
    firstGroup = cmds.group( name = pName + "_first_off" )
    middlePLList=[]
    middleGroup = cmds.group( name = pName + "_middle_off" )
    lastPL = cmds.spaceLocator( name = pName + "_lastPlacement" )
    cmds.scale( scaleValue, scaleValue, scaleValue, lastPL )
    lastGroup = cmds.group( name = pName + "_last_off" )



    if number > 0:
        for i in range( number ):
            middlePL = cmds.spaceLocator( name = pName + "_middlePlacement_" + str(i).zfill(2) )
            cmds.scale( scaleValue, scaleValue, scaleValue, middlePL )
            middlePLList.append( middlePL )
            cmds.parent( middlePL, middleGroup )
    else:
        cmds.error( "Invalid number of joints to create!", n=True )
        return 0

    print( middlePLList )


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

    cmds.select(clear=True)
    successGroup = cmds.group( name= pName + "_SuccessGroup", empty=True )
    cmds.parent( successGroup, locatorGroup )

####################################################################################################################################

def create_jointchain_at_locators( pNameField, pNumberField, pParentJoint, *pArgs ):

    if not( cmds.objExists( (cmds.textField( pNameField, query=True, text=True )) + "_SuccessGroup" ) ):
        cmds.error("Locators Not Created!", n=True)
        return 0

    pName = cmds.textField( pNameField, query=True, text=True )
    number = int(cmds.textField( pNumberField, query=True, text=True ))
    parentJoint = cmds.textField( pParentJoint, query=True, text=True )

    pFirstPL = pName + "_firstPlacement"
    pLastPL = pName + "_lastPlacement"
    pMiddleList = cmds.listRelatives( pName + "_middle_off")

    # Get the location of locators
    firstLoc = cmds.xform( pFirstPL, query=True, translation=True, ws=True )
    lastLoc = cmds.xform( pLastPL, query=True, translation=True, ws=True )

    middleLocList = []
    translationList = [ firstLoc ]
    for i in range( number ):
        translationList.append( cmds.xform( pMiddleList[i], query=True, translation=True, ws=True ) )

    translationList.append( lastLoc )

    # Get the rotation of locators
    firstRot = cmds.xform( pFirstPL, query=True, rotation=True, ws=True )
    lastRot = cmds.xform( pLastPL, query=True, rotation=True, ws=True )

    middleRotList = []
    rotationList = [ firstRot ]
    for i in range( number ):
        rotationList.append( cmds.xform( pMiddleList[i], query=True, rotation=True, ws=True ) )

    rotationList.append( lastRot )

    # Create the joints
    cmds.select( cl=True )
    middleJointList = []

    firstJoint = cmds.joint( name=pName + "_01" )
    jointList = [ firstJoint ]

    for i in range( number ):
        jointList.append( cmds.joint( name=pName + "_" + str(i+2).zfill(2) ) )

    lastJoint = cmds.joint( name=pName + "_" + str(number + 2).zfill(2) )

    jointList.append( lastJoint )

    # Move the joints to the proper location
    for num in range( len(jointList) ):
        cmds.xform( jointList[num], ws=True, translation=translationList[num], rotation=rotationList[num] )
        
    # Get the parent group of the locators and delete it
    parentGroup = cmds.listRelatives( cmds.listRelatives( pFirstPL, parent=True ), parent=True ) 
    
    print( f"deleting {parentGroup[0]}" )
    cmds.delete( parentGroup[0] )

    cmds.parent( firstJoint, parentJoint )

    #create_stretchy_system( jointList )

####################################################################################################################################
# MAIN
####################################################################################################################################

main()