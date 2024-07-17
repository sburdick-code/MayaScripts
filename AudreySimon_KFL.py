import os
import maya.cmds as cmds
# prints the current directory of this file then returns it
def get_script_dir():
    path = os.path.dirname(__file__)
    print( f"Current Dir: {path}")

    return path

# creates a confirmation dialogue box with whatever string the user passed
def create_confirmation_box( pMessage ):
    cmds.confirmDialog( title='Confirm', 
                        message=pMessage, 
                        button=['Close'], 
                        cancelButton='Close', 
                        dismissString='Close' )