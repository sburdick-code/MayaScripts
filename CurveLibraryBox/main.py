import maya.cmds as cmds
import json
from CurveLibraryBox.CurveData_class import CurveData

def main():

    curveName = 'myCurve'

    selectedNode = cmds.ls( selection=True )
    
    if not(selectedNode):
        print( "No Curve Selected!" )
        return 0

    # Get the coordinates for the control points
    count = cmds.getAttr(f"{selectedNode[0]}.controlPoints", size=True)
    controlPoints = []

    for num in range(count):
        currentPoint = cmds.getAttr( f'{selectedNode[0]}.controlPoints[{num}]' )
        #print( currentPoint )
        controlPoints.append( currentPoint )

    # create a new variable of the simple curve class
    newCurve = CurveData( curveName, controlPoints )
    print( newCurve.formatted() )
    

def read_json( pFileName ):
    
    data = {}

    with open( pFileName, 'r' ) as input:
        data = json.load(input)
        cmds.warning( "JSON read successfully", noContext=True )
        return data

    cmds.error( "JSON read failed", noContext=True)
    return 0

def write_json( pFileName, pData ):

    with open( pFileName, 'w' ) as output:
        json.dump( pData, output )
        cmds.warning( "JSON written successfully", noContext=True )
        return 1
    
    cmds.error( "JSON write failed", noContext=True )
    return 0

main()
