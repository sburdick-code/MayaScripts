import maya.cmds as cmds
import json
from CurveLibraryBox.CurveData_class import CurveData
import AudreySimon_KFL 

def main():

    curveName = 'myCurve'

    selectedNode = cmds.ls( selection=True )
    
    # To get the current working directory   
    path = ( AudreySimon_KFL.get_script_dir() + "\CurveLibraryBox\curveLibrary\\" + curveName + ".json" )
    print( path )
    
    # Print a curves data
    create_curve_from_json( path )
    
    if not(selectedNode):
        print( "No Curve Selected!" )
        return 0

    # Get the coordinates for the control points
    count = cmds.getAttr(f"{selectedNode[0]}.controlPoints", size=True)
    controlPoints = []

    for num in range(count):
        currentPoint = cmds.getAttr( f'{selectedNode[0]}.controlPoints[{num}]' )
        controlPoints.append( currentPoint[0] )
    print( controlPoints )

    # create a new variable of the simple curve class
    newCurve = CurveData( curveName, controlPoints )
    print( newCurve.formatted() )

    #write_json( path, newCurve.formatted() )
    
    

def read_json( pFileName ):
    
    data = {}

    with open( pFileName, 'r' ) as input:
        data = json.load(input)
        cmds.inViewMessage(amg=f'JSON read successfully', pos='topCenter', fade=True)
        return data

    cmds.error( "JSON read failed", noContext=True)
    return 0

def write_json( pFileName, pData ):

    with open( pFileName, 'w' ) as output:
        json.dump( pData, output )
        cmds.inViewMessage(amg=f'JSON written to: {pFileName}', pos='topCenter', fade=True)
        return 1
    
    cmds.error( "JSON write failed", noContext=True )
    return 0

def create_curve_from_json( pFileName ):
    tempCurve = CurveData( False, False ) 
    tempCurve.deformatted( read_json( pFileName ) )
    
    print( tempCurve.name )
    print( tempCurve.controlPoints )
    

main()
