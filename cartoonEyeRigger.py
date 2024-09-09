#☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺
#
#    Script:          cartoonEyeRigger.py
#    Author:          Audrey Paransky
#    Last Updated:    09/09/2024
#    Created:         09/09/2024
#    Description:     This script creates a rig for cartoon eyes and mouths using the user's selected vertices as a base.
#                     The rig is MOSTLY 1:1 translatable and scaleable, but distortions are noticeable at extreme values.
#
#☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺☺

from maya import cmds, OpenMaya
import functools

center = 'center'
lowPoints = []

def main():
    create_UI("Cartoon Eye Rigger")    
    
    
################################################################################################################################################################


def create_UI( pWindowTitle ):
    
    center = 'center'
    
    windowID = "tester"

    if cmds.window( windowID, exists = True):
        cmds.deleteUI( windowID )
    
    cmds.window( windowID, title=pWindowTitle, sizeable = True, resizeToFitChildren=True )

    cmds.columnLayout( adj=True )

    
    # FIRST ROW --------------------------------
    cmds.text( label='center eye pivot' )

    # SECOND ROW --------------------------------
    cmds.rowLayout( adj=2, numberOfColumns=3 )
    cmds.text( label='select center radius' )
    eyeMesh = cmds.textField( pht='eye mesh', ed=True )
    cmds.button( label='Select', command=functools.partial( get_selection, eyeMesh ) )

    cmds.setParent( '..' )
    
    # THIRD ROW --------------------------------
    cmds.rowLayout( adj=2, numberOfColumns=2 )

    cmds.text( label='Name')
    sysNameField = cmds.textField( pht='Eyelid, Lip, etc.', ed=True)
    cmds.setParent( '..' )

    # FOURTH ROW --------------------------------
    cmds.rowLayout( adj=1, numberOfColumns=4 )
    cmds.text( label='Position' )

    positionRadioCol = cmds.radioCollection()

    cmds.radioButton( label='Left', collection=positionRadioCol)
    cmds.radioButton( label='Center', collection=positionRadioCol, select=True)
    cmds.radioButton( label='Right', collection=positionRadioCol)
    
    cmds.setParent( '..' )
    

    # FIFTH ROW --------------------------------
    cmds.button( label='create center locator', command=functools.partial( create_center_loc , eyeMesh ) )

    # SIXTH ROW --------------------------------
    cmds.text( label='INDIVIDUALLY select upper eyelid vertices' )

    # SEVENTH ROW --------------------------------
    cmds.button( label='create upper joints', command=functools.partial( create_joints, 'Up', sysNameField, positionRadioCol ) )

    # EIGHTH ROW --------------------------------
    cmds.text( label='adjust low crv to match shape of eye' )
    
    # NINTH ROW --------------------------------
    cmds.text( label='Select eyeball' )
    
    # TENTH ROW --------------------------------
    cmds.button( label='Generate Controllers', command=functools.partial( create_controllers, 'Up', sysNameField, positionRadioCol ) )
    
    # ELEVENTH ROW --------------------------------
    cmds.text( label='INDIVIDUALLY select bottom eyelid vertices' )    
    
    # TWELFTH ROW --------------------------------
    cmds.button( label='create bottom joints', command=functools.partial( create_joints, 'Bot', sysNameField, positionRadioCol ) )
    
    # THIRTEENTH ROW --------------------------------
    cmds.text( label='adjust low crv to match shape of eye' )
    
    # FOURTEENTH ROW --------------------------------
    cmds.text( label='Select eyeball' )
    
    # FIFTEENTH ROW --------------------------------
    cmds.button( label='Generate Controllers', command=functools.partial( create_controllers, 'Bot', sysNameField, positionRadioCol ) )
    
    # SIXTEENTH ROW --------------------------------
    cmds.text( label='Parent & scale constrain rig group to head controller' )

    cmds.showWindow( windowID )
    
    
################################################################################################################################################################


def get_selection( pField, *pArgs ):
    selection = cmds.ls( selection=True )    
    cmds.textField( pField, edit=True, text=selection[0] )
        

################################################################################################################################################################


def getUParam( pnt =[], crv=None ):
    point=OpenMaya.MPoint( pnt[0], pnt[1], pnt[2] )
    curveFn = OpenMaya.MFnNurbsCurve( getDagPath(crv))
    paramUtil = OpenMaya.MScriptUtil()
    paramPtr = paramUtil.asDoublePtr()
    isOnCurve = curveFn.isPointOnCurve( point )
    if isOnCurve == False:
        
        curveFn.getParamAtPoint ( point, paramPtr, 0.001, OpenMaya.MSpace.kObject )
    else:
        point = curveFn.closestPoint( point, paramPtr, 0.001, OpenMaya.MSpace.kObject )
        curveFn.closestPoint( point, paramPtr, 0.001, OpenMaya.MSpace.kObject )
        
    param = paramUtil.getDouble( paramPtr )
    return param
    
    
################################################################################################################################################################

    
def getDagPath( objectName ):
    if isinstance( objectName, list )==True:
        oNodeList = []
        for o in objectName:
            selectionList = OpenMaya.MSelectionList()
            selectionList.add( o )
            oNode = OpenMaya.MDagPath()
            selectionList.getDathPath( 0, oNode )
            oNodeList.append( oNode )
            
        return oNodeList
        
    else:
        selectionList = OpenMaya.MSelectionList()
        selectionList.add( objectName )
        oNode = OpenMaya.MDagPath()
        selectionList.getDagPath( 0, oNode )
        return oNode 
        
        
################################################################################################################################################################


def create_center_loc( pEyeMesh, *pArgs ):
    global center
    
    selectedObj = cmds.textField( pEyeMesh, query=True, text=True )
    cmds.spaceLocator( n=center ) #create a locator with pCenter name

    
    pCenter = cmds.ls( sl=True )[0] #pCenter = to what is currently selected in case there is another center already

    cmds.matchTransform( pCenter, selectedObj, pos=True ) #match translation selected obj and centerLoc. i think there was something wrong with the match part when selecting the stuff
    #cmds.makeIdentity( pCenter, apply=True )
    
    center = pCenter #update center to new pcenter
    
    
################################################################################################################################################################


def create_name( pUpBot, pNameField, pRadioCol, *pArgs ):
    prefixName = ( cmds.textField( pNameField, query=True, text=True ) )

    radioSelection = cmds.radioCollection( pRadioCol, query=True, select=True ) #assigning whatever selected radio button (will return which radio button is selected)(which is an entire class)
    label = cmds.radioButton( radioSelection, query=True, label=True ) #will return the name of the radio button (a string)
    
    if label == 'Left':
        positionPrefix = 'L_'
    elif label == 'Right':
        positionPrefix = 'R_'
    elif label == 'Center':
        positionPrefix = 'C_'
    else:
        positionPrefix = '0_' #just in case something fails
        
    positionPrefix = positionPrefix + pUpBot + prefixName
    #L_UpEyelid
        
    return positionPrefix


################################################################################################################################################################


def gen_Curve(pPoints, pPosPrefix, pHighLow):
    global lowPoints
    controlPoints = []
    
    for p in pPoints:
        controlPoints.append(cmds.xform(p, q=True, t=True))
    
    if pHighLow == 'High':
        # Create a linear curve (degree 1) with all control points
        genCrv = cmds.curve(p=controlPoints, d=1, name=pPosPrefix + pHighLow + '_CRV')
    else:  # If pHighLow is 'Low'
        lowPoints = []
        
        # Ensure we have at least 5 points
        if len(controlPoints) >= 5:
            # Include the first point
            lowPoints.append(controlPoints[0])
            
            centerPt = len(controlPoints)//2
            step = centerPt//2
            
            lowPoints.append(controlPoints[centerPt-step])
            lowPoints.append(controlPoints[centerPt])
            lowPoints.append(controlPoints[centerPt+step])

            # Include the last point
            lowPoints.append(controlPoints[-1])
        else:
            # If there are fewer than 5 control points, just use all points
            lowPoints = controlPoints
        
        # Create a cubic curve (degree 3) using the selected lowPoints
        genCrv = cmds.curve(p=lowPoints, d=3, name=pPosPrefix + pHighLow + '_CRV')
    
    # Center the pivot of the curve
    cmds.xform(genCrv, cp=True)
    
    return genCrv
        
        
################################################################################################################################################################


def create_joints( pUpBot, pNameField, pRadioCol, *pArgs ):
    global center
    positionPrefix = create_name( pUpBot, pNameField, pRadioCol )
     
    #fl flattens the returned list of objects so that each component is identified individualy
    selectedVerts = cmds.ls( os=True, fl=True ) #have the user select all the joints they want
    
    crv = gen_Curve( selectedVerts, positionPrefix, 'High' )
    
    centerPos = cmds.xform( center, q=True, t=True, ws=True) #query the center position of center 
    cmds.select( deselect = True ) #clear selection
    
    if cmds.objExists( create_name('', pNameField, pRadioCol )+'_LOC' ): #if the up loc already exists, just reuse it
        posLoc = create_name('', pNameField, pRadioCol )+'_LOC'
    else:
        posLoc = cmds.spaceLocator( n=create_name('', pNameField, pRadioCol )+'_LOC' )[0] #create the up loc
    
    cmds.move( centerPos[0], centerPos[1]+3, centerPos[2], posLoc ) #move the posLoc up 3 units
        
    locGrp = cmds.group( empty=True,  n = positionPrefix + '_loc_GRP' )
    jntGrp = cmds.group( empty=True,  n = positionPrefix + '_jnt_GRP' )
        
    jnts = []

    jntCnt =0
    
    for vert in selectedVerts: 
        #create a joint at every vertex
        cmds.select( deselect = True ) #clear selection
        jnt = cmds.joint( n=positionPrefix+str(jntCnt)+'_JNT' ) #create joint
        jntCnt+=1
        pos = cmds.xform( vert, q=True, t=True, ws=True ) #query the location
        cmds.xform( jnt, t=pos, ws=True ) #move the joints to the location
        cmds.select( deselect = True ) #clear selection
        centerJnt = cmds.joint() #create the center joint
        cmds.xform( centerJnt, t=centerPos, ws=True ) #move centerjoint to center location
        cmds.parent( jnt, centerJnt ) #parent the joint under center joint
        cmds.joint( centerJnt, e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True ) #orient joints
        
        #create locators
        loc = cmds.spaceLocator( n=positionPrefix+'Aim'+str(jntCnt)+'_LOC' )[0] #create a locator at the location of the vertex as well. we just want the transform component
        #pos = cmds.xform( jnt, q=True, t=True, ws=True ) #query the location
        cmds.xform( loc, ws=True, t=pos ) #move loc to jnt location
        par = cmds.listRelatives( jnt, p=True )[0] 
        cmds.aimConstraint( loc, par, mo=True, weight=True, aimVector=(1,0,0), upVector=(0,1,0), worldUpType='object', worldUpObject= posLoc )
        
        
        #create pci nodes
        u = getUParam ( pos, crv ) #get the uParam of all the locators in relation to the curve
        pci = cmds.createNode( 'pointOnCurveInfo', n=positionPrefix+'Aim_PCI0' ) #point on curve info node
        cmds.connectAttr( crv + '.worldSpace', pci + '.inputCurve' )
        cmds.setAttr( pci + '.parameter', u )
        cmds.connectAttr( pci + '.position', loc+'.t' )
                
        cmds.parent( loc, locGrp )
        cmds.setAttr( locGrp+'.inheritsTransform', 0)
        cmds.parent( centerJnt, jntGrp )
    
    
                
    lowCrv = gen_Curve( selectedVerts, positionPrefix, 'Low' )
    
    
################################################################################################################################################################ 
    
    
def create_controllers( pUpBot, pNameField, pRadioCol, *pArgs ):
    global lowPoints
    global center
    
    eyeBall = cmds.ls( sl=True )
    #eyeBallPos = cmds.xform( eyeBall, q=True, t=True, ws=True )    
    
    #CONNECT LOW AND HIGH CRV
    #grab the low and the high curves
    positionPrefix = create_name( pUpBot, pNameField, pRadioCol )
    lowCrv = positionPrefix+'Low'+'_CRV'
    highCrv = positionPrefix+'High'+'_CRV'
    
    #use the wire deformer to connect the high to low
    highCrvWireNode = cmds.wire( highCrv, w=lowCrv )
    #cmds.setAttr( highCrvWireNode+'.scale[0]', 0 )
    cmds.setAttr( highCrvWireNode[0]+'.dropoffDistance[0]', 100 )


    #CREATE THE CONTROLLERS
    if cmds.objExists( create_name( '', pNameField, pRadioCol ) + '_DriverGrp' ): #if the driver group already exists
        driverGrp = create_name( '', pNameField, pRadioCol ) + '_DriverGrp'
        controllerGrp = create_name( '', pNameField, pRadioCol ) + '_ControllerGrp'
    
    else:
        driverGrp = cmds.group( empty=True,  n = create_name( '', pNameField, pRadioCol ) + '_DriverGrp' )
        controllerGrp = cmds.group( empty=True,  n = create_name( '', pNameField, pRadioCol ) + '_ControllerGrp' )
    
    controllerList = []
    jointList = []
    jntCnt = 0
    
    for pos in lowPoints: #create a joint and a controller at that location
        if pos == lowPoints[0] or pos == lowPoints[-1]: #if we are at the first or last vert, then the naming shouldn't have the up or bot in the name
            positionPrefix = create_name( '', pNameField, pRadioCol )
            
        else:
            positionPrefix = create_name( pUpBot, pNameField, pRadioCol )
            
        if cmds.objExists( positionPrefix + str(jntCnt) + '_DRIVER' ): #if the joint we are making already exists, dont create another joint or controller. this only applies to the eye corners
            jointList.append( positionPrefix + str(jntCnt) + '_DRIVER' )
            controllerList.append( positionPrefix + str(jntCnt) + '_DRIVER' + '_CTRL' )
            jntCnt+=1
            
        else:
                
            #create a joint at every vertex
            cmds.select( deselect = True ) #clear selection
            jnt = cmds.joint( n=positionPrefix + str(jntCnt) + '_DRIVER' ) #create joint
            jntCnt+=1
            cmds.xform( jnt, t=pos, ws=True ) #move the joints to the location
            jointList.append(jnt)
            
            #CREATE CONTROLLERS
            newControl = cmds.circle( c=(0, 0, 0), name=(jnt + '_CTRL') )
            cmds.move( pos[0], pos[1], pos[2], newControl )
            cmds.scale( .1, .1, .1, newControl )
            cmds.makeIdentity( newControl, apply=True )
            controllerList.append(newControl)
            
            # Create the offset group for our new controller
            newGroup = cmds.group( empty=True, name=(jnt + '_OFFSET') )
            cmds.move( pos[0], pos[1], pos[2], newGroup ) #the group and the cntrl are at the same place
            cmds.makeIdentity( newGroup, apply=True ) #freeze transformations
            
            cmds.parent( newControl, newGroup )
    
            #bind the joints to their controllers
            cmds.parentConstraint( newControl, jnt )
            
            cmds.parent( jnt, driverGrp )
            cmds.parent( newGroup, controllerGrp )
            
    #BIND THE LOW CRV TO THE JOINTS
    cmds.skinCluster( jointList, lowCrv, tsb=True)
    
    #parent constrain the 2nd and the 4th controllers' offsets to their adjacent controllers. index 1 and index 3
    offsetGrp1 = jointList[1] + '_OFFSET'
    offsetGrp3 = jointList[3] + '_OFFSET'
    cmds.parentConstraint( controllerList[0], controllerList[2], offsetGrp1, mo=True )
    cmds.parentConstraint( controllerList[2], controllerList[4], offsetGrp3, mo=True )
    
    #check to make sure there is a top and a bot low crv
    upCrv = create_name( 'Up', pNameField, pRadioCol ) + 'Low_CRV'
    botCrv = create_name( 'Bot', pNameField, pRadioCol ) + 'Low_CRV'
    
    highUpCrv = create_name( 'Up', pNameField, pRadioCol ) + 'High_CRV'
    highBotCrv = create_name( 'Bot', pNameField, pRadioCol ) + 'High_CRV'
    
    if cmds.objExists( upCrv ) and cmds.objExists( botCrv ): #if both a bottom and an upper curve exist
        #create a master controller that moves the necessary eye controllers
        positionPrefix = create_name( '', pNameField, pRadioCol )
        masterControl = cmds.circle( c=(0, 0, 0), name=(positionPrefix + '_MASTER_CTRL') )
        masterControlOff = cmds.group( empty=True, name=(masterControl[0] + '_OFFSET') )
        cmds.parent( masterControl, masterControlOff )
        cmds.matchTransform( masterControlOff, eyeBall, pos=True )
        cmds.move( 0, 0, 1, masterControl, r=True )
        cmds.makeIdentity( masterControlOff, apply=True )
        
        cmds.aimConstraint( center, masterControl, mo=True, weight=True, aimVector=(1,0,0), upVector=(0,1,0), worldUpType='object', worldUpObject= positionPrefix+'_LOC' )
        
        cmds.parent( controllerGrp, masterControl )
        
        #CREATE SMART BLINK
        #create target blink using low crvs
        smartCloseCrv = cmds.duplicate( lowCrv, n=create_name( '', pNameField, pRadioCol )+'_Closed_CRV' )
        bnsName = positionPrefix+'_targetSmartClosed'
        blendshapeNode = cmds.blendShape( upCrv, botCrv, smartCloseCrv, n=bnsName, o='local' )[0]
        prefixName = ( cmds.textField( pNameField, query=True, text=True ) )
        closedName = 'Closed_Height'
        cmds.addAttr( masterControl, shortName = closedName, longName = closedName, defaultValue=0, minValue=0, maxValue=1, keyable = True)
        cmds.connectAttr( masterControl[0]+'.'+closedName, blendshapeNode+'.weight[0]' ) #connect the closed attr to the blendshape
        reverseNode = cmds.createNode( 'reverse', n=bnsName+'_reverse' ) #create reverse node
        cmds.connectAttr( masterControl[0]+'.'+closedName, reverseNode+'.inputX' ) #connect closedName attr to reverse node
        cmds.connectAttr( reverseNode+'.outputX', blendshapeNode+'.weight[1]' ) #connect the closed attr to the reverse node
        
        #create create high crv blendshapes
        upNaming = create_name( 'Up', pNameField, pRadioCol ) 
        botNaming = create_name( 'Bot', pNameField, pRadioCol )
        upClosed = cmds.duplicate( highUpCrv, n=upNaming+'_Closed_CRV' ) #duplicate the high crvs and rename them
        botClosed = cmds.duplicate( highBotCrv, n=botNaming+'_Closed_CRV' )
        #set up wire deformer
        cmds.setAttr( masterControl[0]+'.'+closedName, 1 ) #set the blink height to 1
        wireNodeUp = cmds.wire( upClosed, w=smartCloseCrv, n=upNaming+'_Closed_WR' )[0] #create a wire deformer, the duplicates are driven by the target blink crv
        cmds.setAttr( wireNodeUp+'.scale[0]', 0 ) #set the scale of the wire deformers to 0 so that the duplicates follow the target blink crv perfectly
        cmds.setAttr( wireNodeUp+'.dropoffDistance[0]', 10 )
        cmds.setAttr( masterControl[0]+'.'+closedName, 0 ) #set the blink height to 0
        wireNodeBot = cmds.wire( botClosed, w=smartCloseCrv, n=botNaming+'_Closed_WR' )[0]
        cmds.setAttr( wireNodeBot+'.scale[0]', 0 )
        cmds.setAttr( wireNodeBot+'.dropoffDistance[0]', 10 )
        cmds.setAttr( masterControl[0]+'.'+closedName, 0.5 ) #set the blink height to 0.5
        #create blendshape 
        upBlendshape = cmds.blendShape( upClosed, highUpCrv, n=upNaming+'_targetSmartClosed', o='local' )[0] #use the duplicates as blendshapes for the high crvs
        botBlendshape = cmds.blendShape( botClosed, highBotCrv, n=botNaming+'_targetSmartClosed', o='local' )[0]

        #create attribute in master controller to control up or down blink
        cmds.addAttr( masterControl, shortName = 'Smart_Close_Up', longName = 'Smart_Close_Up', defaultValue=0, minValue=0, maxValue=1, keyable = True)
        cmds.addAttr( masterControl, shortName = 'Smart_Close_Down', longName = 'Smart_Close_Down', defaultValue=0, minValue=0, maxValue=1, keyable = True)
        cmds.connectAttr( masterControl[0]+'.Smart_Close_Up', upBlendshape+'.weight[0]' )
        cmds.connectAttr( masterControl[0]+'.Smart_Close_Down', botBlendshape+'.weight[0]' )
        
        #GROUP IN OUTLINER
        #make a group for the eye rig and a world_null group
        cmds.group( highUpCrv, highBotCrv, upClosed, botClosed, upCrv, botCrv, smartCloseCrv, upNaming+'Low_CRVBaseWire', botNaming+'Low_CRVBaseWire', smartCloseCrv[0]+'BaseWire', smartCloseCrv[0]+'BaseWire1', n='world_null_GRP' )
        #group the rest of the stuff
        positionPrefix = create_name( '', pNameField, pRadioCol )
        eyeRig = cmds.group( upNaming+'_loc_GRP', upNaming+'_jnt_GRP', botNaming+'_loc_GRP', botNaming+'_jnt_GRP', positionPrefix+'_LOC', center, driverGrp, n=positionPrefix+'_rig_GRP')
        cmds.group( masterControlOff, eyeRig, n=positionPrefix+'RIG' ) #controllerGrp masterControlOff
                
    
################################################################################################################################################################
# MAIN
################################################################################################################################################################ 

main()