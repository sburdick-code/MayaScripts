#################################################################################################################################################
#
#    Library:         Audrey and Simon: Key Function Library
#    Authors:          Audrey Paransky & Simon Burdick
#    Last Updated:    07/18/2024
#    Created:         07/15/2024
#
#    This python library contains all of our common utility functions fo maya scripting. To import into maya, ensure you have the module set up 
#    and then call "import AudreySimon_KFL as kfl" at the start of your code. To call a function simply type " kfl."function_name"() "
#
################################################################################################################################################

import os
import maya.cmds as cmds

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
File Directory Functions
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
###############################################################################################################################################
#   get_script_dir - returns the file path of this modules root folder and prints it.
#
#   Returns:    String of the current directory path
#   Args:       None
#
###############################################################################################################################################
def get_script_dir():
    path = os.path.dirname(__file__)
    print( f"Current Dir: {path}")

    return path


################################################################################################################################################


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Maya GUI Functions
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#################################################################################################################################################
#   create_confirmation_box - displays a confirmation box with the passed message. The box contains one button labeled Close that closes it.
#
#   Returns:    None
#   Args:       A string to be the displayed message
#
#################################################################################################################################################
def create_confirmation_box( pMessage ):
    cmds.confirmDialog( title='Confirm', 
                        message=pMessage, 
                        button=['Close'], 
                        cancelButton='Close', 
                        dismissString='Close' )


################################################################################################################################################
#   get_selection - fills the passed object field with the selected object of a specified type. It is intended to be used called by a button and
#   used with a Maya GUI.
#
#   Returns:    None
#   Args:       A text field to be filled, a string of the object type, *pArgs to catch anything passed
#
################################################################################################################################################
def get_selection( pField, objType, *pArgs):
    selection = cmds.ls( selection=True, type=objType)
        
    if selection:
        cmds.textField( pField, edit=True, text=selection[0] )
    else:
        cmds.error( f"No {objType} selected!", n=True )


#################################################################################################################################################