import maya.api.OpenMaya as om2
import maya.cmds as cmds
import pymel.core as pm

# Create UI
window = cmds.window(title= "Test Window")
layout = cmds.columnLayout(adjustableColumn=True)
sliderGrp1 = cmds.intSliderGrp(label="Step2: Arm Length", min=3, max=20, field=True)
button = cmds.button(label="create_arms", command='arms(pm.intSliderGrp(sliderGrp1, q=True, value=True))')

maya.cmds.separator(h=10)
sliderGrp2 = cmds.intSliderGrp(label="Step1: Spine Length", min=3, max = 7, field=True)
button = cmds.button(label="Step1: create_spine", command='spine(pm.intSliderGrp(sliderGrp2, q=True, value=True), pm.intSliderGrp(sliderGrp2, q=True, value=True))')
button = cmds.button(label="create_hips", command='legs()')
button = cmds.button(label="create_IKcontrol", command='createIK(joints, contrl)')
button = cmds.button(label="create_armIK", command='createarmIK()')
button = cmds.button(label="create_rig", command='createrig()')

pm.showWindow( window )

def legs():
pm.select( d=True )
pm.joint( name='hip', p=(0, 27, 0) )
pm.joint( name='left_leg', p=(8, 20, 0) )
pm.joint( name='left_knee', p=(8, 10, 0) )
pm.joint( name='left_foot', p=(8, 0, 0) )

pm.select( d=True )
pm.joint( name='right_leg', p=(-8, 20, 0) )
pm.joint( name='right_knee', p=(-8, 10, 0)  )
pm.joint( name='right_foot', p=(-8, 0, 0) )

pm.select('right_foot', replace=True)
k = 3
for i in range(0, 3):
    k = k + 2
    pm.joint(name='right_foot{0}'.format(i+1), p=(-8, 0, -k))

k = 3
pm.select('left_foot', replace=True)
for i in range(0, 3):
    k = k + 2
    pm.joint(name='left_foot{0}'.format(i+1), p=(8, 0, -k))

pm.parent('right_leg', 'hip')
pm.parent('hip', 'spine1')
def spine(joints, tweenspinelength):
pm.select( d=True )
k = 27
for i in range(0, joints):
k = k + tweenspinelength
pm.joint(name='spine{0}'.format(i+1), p=(0, k, 0))

spine(pm.intSliderGrp(sliderGrp2, q=True, value=True), pm.intSliderGrp(sliderGrp2, q=True, value=True))

def arms(armlength):
pm.select('spine3', replace=True)
x = 0
y = 45
for i in range(0, 3):
x = x - armlength
y = y - 3
pm.joint(name='left_arm{0}'.format(i+1), p=(x, y, 0))

pm.select('spine3', replace=True)
x = 0
y = 45
for i in range(0, 3):
    x = x - armlength
    y = y - 3
    pm.joint(name='right_arm{0}'.format(i+1), p=(-x, y, 0))
arms(pm.intSliderGrp(sliderGrp1, q=True, value=True))

#selectedJoint = pm.select('spine1', replace=True)
#joints = pm.ls(type='joint')
#pm.select(joints, replace=True)

#for item in joints:

#contrl = pm.circle(n='ctrl ' + item.name())
#pm.scale(3, 3, 3)
#pm.rotate(0, 90, 0)

#if item.name()[:-1].endswith("arm"):
    #pm.rotate(0, 0, 90)
#if item.name()[:-1].endswith("foot"):
    #pm.rotate(0, 0, 0)

#pm.makeIdentity(contrl, apply=True)   
#contrlcurve = pm.listRelatives(contrl, shapes=True)[0]
#pm.parent(contrlcurve, item, s=True, r=True)
def createIK(joints, contrl):
joints = cmds.ls(type='joint')
for item in joints:
contrl = cmds.circle(n='ctrl_' + item.name())
cmds.matchTransform(contrl, item, pos=True)
cmds.scale(3, 3, 3)
cmds.rotate(0, 90, 0)

    if item.name()[:-1].endswith("arm"):
        cmds.rotate(0, 0, 90)
    if item.name()[:-1].endswith("foot"):
        cmds.rotate(0, 0, 0)
    cmds.makeIdentity(contrl, apply=True)
#pm.matchTransform('ctrl_' + item.name(), item.name())  
#contrlcurve = pm.listRelatives(contrl, shapes=True)[0]
cmds.parent(contrlcurve, item, s=True, r=True)
def createarmIK():

pm.select( 'right_arm3', r=True )
pm.select( 'left_arm3', add=True )
selection_arm3 = pm.ls(selection=True)
for item in selection_arm3:
    IKcontrol = pm.polyCube(name='IKcontrol_' + item.name(), h=5, w=5, d=5)
    pm.makeIdentity(IKcontrol, apply=True)
    pm.matchTransform('IKcontrol_' + item.name(), item.name())
createarmIK()

def createrig():
pm.select('right_arm1', replace=True)
pm.duplicate(rc=True)
pm.makeIdentity('right_arm4', apply=True)
pm.rename('right_arm4', 'IK_right_arm1')
pm.rename('right_arm5', 'IK_right_arm2')
pm.rename('right_arm6', 'IK_right_arm3')

pm.select('left_arm1', replace=True)
pm.duplicate(rc=True)
pm.makeIdentity('left_arm4', apply=True)
pm.rename('left_arm4', 'IK_left_arm1')
pm.rename('left_arm5', 'IK_left_arm2')
pm.rename('left_arm6', 'IK_left_arm3')


#bug
pm.ikHandle( n='IKhandleleft', sol='ikRPsolver', sj='IK_left_arm1', ee='IK_left_arm3', snc=True)
pm.parent('IKhandleleft', 'IKcontrol_left_arm3', s=True, r=True)
pm.ikHandle( n='IKhandleright', sol='ikRPsolver', sj='IK_right_arm1', ee='IK_right_arm3', snc=True)
pm.parent('IKhandleright', 'IKcontrol_right_arm3', s=True, r=True)

pm.select('right_arm1', replace=True)
pm.duplicate(rc=True)
pm.makeIdentity('right_arm4', apply=True)
pm.rename('right_arm4', 'FK_right_arm1')
pm.rename('right_arm5', 'FK_right_arm2')
pm.rename('right_arm6', 'FK_right_arm3')


pm.select('left_arm1', replace=True)
pm.duplicate(rc=True)
pm.makeIdentity('left_arm4', apply=True)
pm.rename('left_arm4', 'FK_left_arm1')
pm.rename('left_arm5', 'FK_left_arm2')
pm.rename('left_arm6', 'FK_left_arm3')

pm.select( 'right_arm2', r=True )
pm.select( 'left_arm2', add=True )
selection_arm2 = pm.ls(selection=True)
for item in selection_arm2:
    pvLoc = pm.spaceLocator(name='pv1_local_loc_' + item.name())
    pm.matchTransform('pv1_local_loc_' + item.name(), item.name())
    pm.move(pvLoc, 5, z=True)
    pm.group('pv1_local_loc_' + item.name(), n='pv1_local_loc_' + item.name() + 'null')
    pm.matchTransform('pv1_local_loc_' + item.name() + 'null', item.name(), piv=True)
#pm.matchTransform('pv1_local_loc_' + item.name() + 'null', item.name(), piv=True)
pm.poleVectorConstraint('pv1_local_loc_left_arm2null', 'IKhandleleft')
pm.poleVectorConstraint('pv1_local_loc_right_arm2null', 'IKhandleright')

pm.select( 'FK_right_arm3', r=True )
pm.select( 'FK_left_arm3', add=True )
selection_arm3 = pm.ls(selection=True)
for item in selection_arm3:
    ctrl = pm.circle(name='hand_ctrl_' + item.name())
    pm.matchTransform('hand_ctrl_' + item.name(), item.name())
    pm.scale(ctrl, 7, 4, 5)
    pm.rotate(ctrl, 90, x=True)
    pm.makeIdentity(ctrl, apply=True)

    pm.addAttr(ctrl, longName='FK', at='bool' , k=True, h=False)
    pm.addAttr(ctrl, longName='IK', at='bool', k=True, h=False)
pm.parent('hand_ctrl_FK_right_arm3', 'IKcontrol_right_arm3')
pm.parent('hand_ctrl_FK_left_arm3', 'IKcontrol_left_arm3')
    
pm.orientConstraint('FK_left_arm1', 'IK_left_arm1', 'left_arm1', w=1)
pm.orientConstraint('FK_left_arm2', 'IK_left_arm2', 'left_arm2', w=1)
pm.orientConstraint('FK_left_arm3', 'IK_left_arm3', 'left_arm3', w=1)

pm.orientConstraint('FK_right_arm1', 'IK_right_arm1', 'right_arm1', w=1)
pm.orientConstraint('FK_right_arm2', 'IK_right_arm2', 'right_arm2', w=1)
pm.orientConstraint('FK_right_arm3', 'IK_right_arm3', 'right_arm3', w=1)

pm.connectAttr('hand_ctrl_FK_left_arm3.FK', 'left_arm3_orientConstraint1.FK_left_arm3W0')
pm.connectAttr('hand_ctrl_FK_left_arm3.IK', 'left_arm3_orientConstraint1.IK_left_arm3W1')
pm.connectAttr('hand_ctrl_FK_left_arm3.FK', 'left_arm2_orientConstraint1.FK_left_arm2W0')
pm.connectAttr('hand_ctrl_FK_left_arm3.IK', 'left_arm2_orientConstraint1.IK_left_arm2W1')
pm.connectAttr('hand_ctrl_FK_left_arm3.FK', 'left_arm1_orientConstraint1.FK_left_arm1W0')
pm.connectAttr('hand_ctrl_FK_left_arm3.IK', 'left_arm1_orientConstraint1.IK_left_arm1W1')

pm.connectAttr('hand_ctrl_FK_right_arm3.FK', 'right_arm3_orientConstraint1.FK_right_arm3W0')
pm.connectAttr('hand_ctrl_FK_right_arm3.IK', 'right_arm3_orientConstraint1.IK_right_arm3W1')
pm.connectAttr('hand_ctrl_FK_right_arm3.FK', 'right_arm2_orientConstraint1.FK_right_arm2W0')
pm.connectAttr('hand_ctrl_FK_right_arm3.IK', 'right_arm2_orientConstraint1.IK_right_arm2W1')
pm.connectAttr('hand_ctrl_FK_right_arm3.FK', 'right_arm1_orientConstraint1.FK_right_arm1W0')
pm.connectAttr('hand_ctrl_FK_right_arm3.IK', 'right_arm1_orientConstraint1.IK_right_arm1W1')


    
#IK is movable, main rig snaps to either FK or IK
pm.connectAttr('hand_ctrl_FK_right_arm3.IK', 'IKcontrol_right_arm3.visibility')

pm.connectAttr('hand_ctrl_FK_left_arm3.IK', 'IKcontrol_left_arm3.visibility')
createrig()
