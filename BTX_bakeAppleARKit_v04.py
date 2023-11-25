##############################################################################################################################
#
#    Script:          BTX_bakeAppleARKit_v04.py
#    Author:          Simon Burdick
#    Last Updated:    11/24/2023
#    Created:         10/26/2023
#    Description:     This script receives blendshape and head rotation data from an FBX recorded with the Apple AR Kit. 
#                     It connects this data to a custom BTX rig then allows for baking the animation on.
#
##############################################################################################################################

import maya.cmds as cmds
import functools

############################################################################################
# getSelected - Get the currently selected objects
############################################################################################
def getSelected():
    selectedObjects = cmds.ls(selection=True)
    if selectedObjects:
        # Save the first selected object as a variable
        selected = selectedObjects[0]
        print(f"Selected object: {selected}")

        # Deselect all objects
        cmds.select(clear=True)
        return selected
    else:
        print("No objects are selected.")

############################################################################################
# connectAttr - Add attribute and set up connection to selected object (TESTING PURPOSES)
############################################################################################
def addNewAttr( fSelected, fRigAttr ):
    
    num = 0
    
    for attribute in fRigAttr:
        if cmds.attributeQuery( attribute, node = fSelected, exists=True):
            print ( "MESSAGE: Object Already Contains Attribute: " + attribute )
        else:
            # Add rig Attributes
            cmds.addAttr(fSelected, longName=attribute, attributeType='float', minValue=0, maxValue=1, keyable=True, hidden=False)
            print( "MESSAGE: Added Attribute: " + attribute )
            
        num += 1
        
        # Block Testing
        connection = cmds.listConnections(f'pCube{num}.translateY', source=True, destination=False)
        cmds.delete(connection)
        expressionString = f'pCube{num}.translateY = {fSelected}.{attribute} * 5;'
        cmds.expression( object=( f'pCube{num}' ), string=( expressionString ) )
        
############################################################################################
# disconnectARKit - disconnect AR Kit blendshapes to the attributes
############################################################################################
def disconnectARKit( fSelected, shapeTextField, fRigAttr, fAppleARKitAttr, fObjNamespace, *pArgs ):
    
    fShapeName = cmds.textField(shapeTextField, query=True, text=True)
    
    for num in range(52):
        if ( cmds.listConnections( f'{fObjNamespace}{fSelected[num]}.translateY', source=True, destination=False ) ):
            connection = cmds.listConnections( f'{fObjNamespace}{fSelected[num]}.translateY', source=True, destination=False )
            print( connection )
            cmds.delete( connection )
            
            if ( cmds.listConnections( f'{fObjNamespace}{fSelected[num]}.translateX', source=True, destination=False, type='expression') ):
                connection = cmds.listConnections( f'{fObjNamespace}{fSelected[num]}.translateX', source=True, destination=False )
                print( connection )
                cmds.delete( connection )
                cmds.setAttr(f'{fObjNamespace}{fSelected[num]}.translateX', 0)
        
            cmds.setAttr(f'{fObjNamespace}{fSelected[num]}.translateY', 0)
            
        
############################################################################################
# connectARKit - connect AR Kit blendshapes to the attributes
############################################################################################
def connectARKit( fSelected, shapeTextField, fRigAttr, fAppleARKitAttr, fSliderCtrls, fObjNamespace, *pArgs ):

    fShapeName = cmds.textField(shapeTextField, query=True, text=True)
    
    disconnectARKit( fSliderCtrls, shapeTextField, fRigAttr, fAppleARKitAttr, fObjNamespace )
    
    for num in range(52):
        
        sliderCtrl = fObjNamespace + fSliderCtrls[num]
        
        if ( fSliderCtrls[num] == 'eye_R_anim' ):
            if not ( cmds.listConnections(f'{fObjNamespace}eye_R_anim.translateX', source=True, destination=False, type='expression') ):
                cmds.expression( object = sliderCtrl, string = ( "if ( " + fShapeName + ".eyeLookOut_R > 0) {" + sliderCtrl + ".translateX = (" + fShapeName + ".eyeLookOut_R * -1); } else {" + sliderCtrl + ".translateX = (" + fShapeName + ".eyeLookIn_R); }" ) )
                cmds.expression( object = sliderCtrl, string = ( "if ( " + fShapeName + ".eyeLookDown_R > 0) {" + sliderCtrl + ".translateY = (" + fShapeName + ".eyeLookDown_R * -1); } else {" + sliderCtrl + ".translateY = (" + fShapeName + ".eyeLookUp_R); }" ) )
        
        elif( fSliderCtrls[num] == 'eye_L_anim' ):
            if not ( cmds.listConnections(f'{fObjNamespace}eye_L_anim.translateX', source=True, destination=False, type='expression') ):
                cmds.expression( object = sliderCtrl, string = ( "if ( " + fShapeName + ".eyeLookOut_L > 0) {" + sliderCtrl + ".translateX = (" + fShapeName + ".eyeLookOut_L ); } else {" + sliderCtrl + ".translateX = (" + fShapeName + ".eyeLookIn_L * -1); }" ) )
                cmds.expression( object = sliderCtrl, string = ( "if ( " + fShapeName + ".eyeLookDown_L > 0) {" + sliderCtrl + ".translateY = (" + fShapeName + ".eyeLookDown_L * -1); } else {" + sliderCtrl + ".translateY = (" + fShapeName + ".eyeLookUp_L); }" ) )
        
        elif( fSliderCtrls[num] == 'eyeSquintWide_R_anim'):
            if not ( cmds.listConnections(f'{fObjNamespace}eyeSquintWide_R_anim.translateY', source=True, destination=False, type='expression') ):
                cmds.expression( object = sliderCtrl, string = ( "if ( " + fShapeName + ".eyeSquint_R > 0) {" + sliderCtrl + ".translateY = (" + fShapeName + ".eyeSquint_R * -1); } else {" + sliderCtrl + ".translateY = (" + fShapeName + ".eyeWide_R); }" ) )

        elif( fSliderCtrls[num] == 'eyeSquintWide_L_anim'):
            if not ( cmds.listConnections(f'{fObjNamespace}eyeSquintWide_L_anim.translateY', source=True, destination=False, type='expression') ):
                cmds.expression( object = sliderCtrl, string = ( "if ( " + fShapeName + ".eyeSquint_L > 0) {" + sliderCtrl + ".translateY = (" + fShapeName + ".eyeSquint_L * -1); } else {" + sliderCtrl + ".translateY = (" + fShapeName + ".eyeWide_L); }" ) )
        
        elif( fSliderCtrls[num] == 'mouthLeftRight_anim'):
            if not ( cmds.listConnections(f'{fObjNamespace}mouthLeftRight_anim.translateY' , source=True, destination=False, type='expression') ):
                cmds.expression( object = sliderCtrl, string = ( "if ( " + fShapeName + ".mouthLeft > 0) {" + sliderCtrl + ".translateY = (" + fShapeName + ".mouthLeft * -1); } else {" + sliderCtrl + ".translateY = (" + fShapeName + ".mouthRight); }" ) )

        elif( fSliderCtrls[num] == 'jawLeftRight_anim'):
            if not ( cmds.listConnections(f'{fObjNamespace}jawLeftRight_anim.translateY', source=True, destination=False, type='expression') ):
                cmds.expression( object = sliderCtrl, string = ( "if ( " + fShapeName + ".jawLeft > 0) {" + sliderCtrl + ".translateY = (" + fShapeName + ".jawLeft * -1); } else {" + sliderCtrl + ".translateY = (" + fShapeName + ".jawRight); }" ) )   

        else:
            createMultiplyNode( f'{fShapeName}.{fAppleARKitAttr[num]}', f'{fObjNamespace}{fSliderCtrls[num]}.translateY', 1 )

############################################################################################
# disconnectHeadRotation - connect AR Kit Head Rotation
############################################################################################
def disconnectHeadRotation( fSelected, headRotationField, fObjNamespace, *pArgs ):
    
    fHeadGroup = cmds.textField(headRotationTextField, query=True, text=True)
          
    connection = cmds.listConnections( f'{fSelected}.translateX', source=True, destination=False )
    if ( connection ):
        cmds.delete( connection )
        
    connection = cmds.listConnections( f'{fSelected}.rotateX', source=True, destination=False )
    if ( connection ):
        cmds.delete( connection )
        
    cmds.setAttr(f'{fSelected}.rotateX', 0)
    cmds.setAttr(f'{fSelected}.rotateY', 0)
    cmds.setAttr(f'{fSelected}.rotateZ', 0)
       
############################################################################################
# connectHeadRotation - connect AR Kit Head Rotation
############################################################################################
def connectHeadRotation( fSelected, headRotationTextField, fObjNamespace, *pArgs ):

    fHeadGroup = cmds.textField(headRotationTextField, query=True, text=True)    
    disconnectHeadRotation( fSelected, headRotationTextField, fObjNamespace )
        
    cmds.orientConstraint( fHeadGroup, fSelected, maintainOffset = True )
    #cmds.pointConstraint( fHeadGroup, fSelected, maintainOffset = True )

############################################################################################
# bakeARKit - bake the incoming inputs from the apple AR Kit to the rig
############################################################################################
def bakeARKit( fSelected, fRigAttr, fRigHeadTransformGroup, fObjNamespace, *pArgs ):

    startFrame = cmds.playbackOptions(query=True, minTime=True)
    endFrame = cmds.playbackOptions(query=True, maxTime=True)
    
    bakedSliderCtrls = []
    for ctrl in fSelected:
        bakedSliderCtrls.append( fObjNamespace + ctrl )

    connection = cmds.listConnections( f'{bakedSliderCtrls[0]}.translateY', source=True, destination=False )
    if ( connection ):
        cmds.bakeResults( bakedSliderCtrls, # Object
                          sm=True,  # Simulation
                          t=(startFrame, endFrame),  # Time range
                          sb=1,  # Sample by frame
                          ral=True,  ) # Remove all locked attributes after baking
    else:
        print("MESSAGE: No Blendshapes to Bake!!!")
    
    connection = cmds.listConnections(fRigHeadTransformGroup, source=True, destination=False, connections=True)
    if ( connection ):
        cmds.bakeResults( fRigHeadTransformGroup, # Object
                          sm=True,  # Simulation
                          t=(startFrame, endFrame),  # Time range
                          sb=1,  # Sample by frame
                          ral=True,  ) # Remove all locked attributes after baking
    else:
        print("MESSAGE: No Head Rotations to Bake!!!")    
  
############################################################################################
# getNamespace - find the namespace of the entered object
############################################################################################    
def getNamespace( fObject ):

    for obj in fObject:
        # Split the object name by the colon
        parts = obj.split(":")

        # The namespace is everything before the last part (the object's name)
        # Join back with ':' in case of nested namespaces
        namespace = ":".join(parts[:-1]) if len(parts) > 1 else ""
        
    namespace = namespace + ":"
    
    return namespace

############################################################################################
# MAIN
############################################################################################

# Variables

if cmds.ls("*:ctrlARKit_M_anim"):
    selected = cmds.ls("*:ctrlARKit_M_anim")
    objNamespace = getNamespace(selected)
else:
    selected = "ctrlARKit_M_anim"
    objNamespace = ""

rigHeadTransformGroup = objNamespace + 'head_M_head_anim'

# Custom Rig variables
rigAttr = [ 'eyeBlinkLeft',      'eyeLookDownLeft', 'eyeLookInLeft',  'eyeLookOutLeft',  'eyeLookUpLeft',   'eyeSquintLeft',    'eyeWideLeft',     'eyeBlinkRight',      'eyeLookDownRight',    'eyeLookInRight',
            'eyeLookOutRight',   'eyeLookUpRight',  'eyeSquintRight', 'eyeWideRight',    'jawForward',      'jawLeft',          'jawRight',        'jawOpen',            'mouthClose',          'mouthFunnel',
            'mouthPucker',       'mouthLeft',       'mouthRight',     'mouthSmileLeft',  'mouthSmileRight', 'mouthFrownLeft',   'mouthFrownRight', 'mouthDimpleLeft',    'mouthDimpleRight',    'mouthStretchLeft',
            'mouthStretchRight', 'mouthRollLower',  'mouthRollUpper', 'mouthShrugLower', 'mouthShrugUpper', 'mouthPressLeft',   'mouthPressRight', 'mouthLowerDownLeft', 'mouthLowerDownRight', 'mouthUpperUpLeft', 
            'mouthUpperUpRight', 'browDownLeft',    'browDownRight',  'browInnerUp',     'browOuterUpLeft', 'browOuterUpRight', 'cheekPuff',       'cheekSquintLeft',    'cheekSquintRight',    'noseSneerLeft',
            'noseSneerRight',    'tongueOut']

# Apple AR Kit variables
appleARKitAttr = [ 'eyeBlink_L',      'eyeLookDown_L',  'eyeLookIn_L',    'eyeLookOut_L',    'eyeLookUp_L',     'eyeSquint_L',   'eyeWide_L',    'eyeBlink_R',       'eyeLookDown_R',    'eyeLookIn_R',
                   'eyeLookOut_R',    'eyeLookUp_R',    'eyeSquint_R',    'eyeWide_R',       'jawForward',      'jawLeft',       'jawRight',     'jawOpen',          'mouthClose',       'mouthFunnel',
                   'mouthPucker',     'mouthLeft',      'mouthRight',     'mouthSmile_L',    'mouthSmile_R',    'mouthFrown_L',  'mouthFrown_R', 'mouthDimple_L',    'mouthDimple_R',    'mouthStretch_L',
                   'mouthStretch_R',  'mouthRollLower', 'mouthRollUpper', 'mouthShrugLower', 'mouthShrugUpper', 'mouthPress_L',  'mouthPress_R', 'mouthLowerDown_L', 'mouthLowerDown_R', 'mouthUpperUp_L', 
                   'mouthUpperUp_R',  'browDown_L',     'browDown_R',     'browInnerUp',     'browOuterUp_L',   'browOuterUp_R', 'cheekPuff',    'cheekSquint_L',    'cheekSquint_R',    'noseSneer_L',
                   'noseSneer_R',     'tongueOut']

# Slider controls
sliderCtrls = [ 'eyeBlink_L_anim',     'eye_L_anim',           'eye_L_anim',           'eye_L_anim',                'eye_L_anim',           'eyeSquintWide_L_anim', 'eyeSquintWide_L_anim', 'eyeBlink_R_anim',       'eye_R_anim',            'eye_R_anim',
                'eye_R_anim',          'eye_R_anim',           'eyeSquintWide_R_anim', 'eyeSquintWide_R_anim',      'jawForward_anim',      'jawLeftRight_anim',    'jawLeftRight_anim',    'jawOpen_anim',          'mouthClose_anim',       'mouthFunnel_anim',
                'mouthPucker_anim',    'mouthLeftRight_anim',  'mouthLeftRight_anim',  'mouthSmile_L_anim',         'mouthSmile_R_anim',    'mouthFrown_L_anim',    'mouthFrown_R_anim',    'mouthDimple_L_anim',    'mouthDimple_R_anim',    'mouthStretch_L_anim',
                'mouthStretch_R_anim', 'mouthRollLower__anim', 'mouthRollUpper_anim',  'mouthShrugLower_anim',      'mouthShrugUpper_anim', 'mouthPress_L_anim',    'mouthPress_R_anim',    'mouthLowerDown_L_anim', 'mouthLowerDown_R_anim', 'mouthUpperUp_L_anim', 
                'mouthUpperUp_R_anim', 'browInnerDown_L_anim', 'browInnerDown_R_anim', 'browInnerUp_L_anim',        'browOuterUp_L_anim',   'browOuterUp_R_anim',   'cheekPuff_anim',       'cheekSquint_L_anim',    'cheekSquint_R_anim',    'noseSneer_L_anim',
                'noseSneer_R_anim',    'tongueOut_anim']


# Make a new window
window = cmds.window( title="Connect Face MoCap", iconName='Connect Face MoCap', widthHeight=(300, 280) )
cmds.columnLayout( adjustableColumn=True )

cmds.separator( h = 25)

cmds.text( label = 'Bake Apple AR Kit MoCap to custom BTX Rig' )

cmds.separator( h = 25)

cmds.rowLayout( adj = 1, numberOfColumns = 2 )
cmds.text( label='Blend Shape Input:' )
shapeTextField = cmds.textField( text = 'shapes', editable = True, aie = True)

cmds.setParent( '..' )
cmds.button( label='Connect', command = functools.partial(connectARKit,
                                                          selected,
                                                          shapeTextField,
                                                          rigAttr,
                                                          appleARKitAttr,
                                                          sliderCtrls,
                                                          objNamespace ) )
cmds.button( label='Disconnect', command = functools.partial(disconnectARKit,
                                                             sliderCtrls,
                                                             shapeTextField,
                                                             rigAttr,
                                                             appleARKitAttr,
                                                             objNamespace ) )

cmds.separator( h = 25)

cmds.rowLayout( adj = 1, numberOfColumns = 2 )
cmds.text( label='Head Rotation Input:' )
headRotationTextField = cmds.textField( text = 'grp_transform', editable = True, aie = True)

cmds.setParent( '..' )
cmds.button( label='Connect', command=functools.partial(connectHeadRotation, 
                                                        rigHeadTransformGroup, 
                                                        headRotationTextField,
                                                        objNamespace ) )
cmds.button( label='Disconnect', command=functools.partial(disconnectHeadRotation, 
                                                           rigHeadTransformGroup, 
                                                           headRotationTextField,
                                                           objNamespace ) )

cmds.separator( h = 25)

cmds.button( label='Bake To Keys', command=functools.partial(bakeARKit, 
                                                             sliderCtrls, 
                                                             rigAttr,
                                                             rigHeadTransformGroup,
                                                             objNamespace ) )

cmds.showWindow( window )