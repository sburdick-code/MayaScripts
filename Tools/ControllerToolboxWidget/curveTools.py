import os
import maya.api.OpenMaya as om
import maya.cmds as cmds
import json

from Tools.ControllerToolboxWidget.Const import Const


def save_curve(obj, curve_name, parent_widget):
    """
    This function processes the passed in curve to a json file with all necessary data.
    :param curve_name: name of the curve being saved
    """

    # Rename the temp capture to the curve name
    try:
        png_path = f"{Const.CTRL_DATA_DIR}{curve_name}.png"
        os.rename(Const.TEMP_IMAGE_PATH, png_path)
    except:
        cmds.warning("No PNG found.")

    # Create a selection list
    sel = om.MSelectionList()
    sel.add(obj)
    dagPath = sel.getDagPath(0)

    # Get the data for the curve
    curve_fn = om.MFnNurbsCurve(dagPath)

    ## Get the degree
    degree = curve_fn.degree

    ## Get the form
    form = curve_fn.form

    ## Get the knots
    knot_vector = curve_fn.knots()
    knot_list = list(knot_vector)

    ## Get CV data and degree
    num_cvs = curve_fn.numCVs
    cv_data = []

    for i in range(num_cvs):
        point = curve_fn.cvPosition(i)
        cv_data.append((point.x, point.y, point.z))

    # create a dictionary with all the data to be writted
    json_data = {
        "name": curve_name,
        "degree": degree,
        "form": form,
        "knots": knot_list,
        "CVs": cv_data,
    }

    try:
        with open(Const.CTRL_DATA_DIR + curve_name + ".json", "w") as curve_file:
            json.dump(json_data, curve_file)
        print(f"Saved to : {Const.CTRL_DATA_DIR}{curve_name}.json")
        parent_widget.populate_table()

    except:
        cmds.error(f"Could not save : {curve_name}.json")
        os.remove(png_path)


def load_curve(file_name):
    """
    Opens the JSON file passed in and creates a curve based on its data.
    :param file_name: file path for the JSON being opened
    :return: returns a reference to the curve created
    """
    curve_name = ""
    cv_data = []

    try:
        with open(Const.CTRL_DATA_DIR + file_name + ".json", "r") as curve_file:
            data = json.load(curve_file)
            curve_name = data["name"]
            degree = data["degree"]
            form = data["form"]
            cv_data = data["CVs"]

            try:
                knots = data["knots"]
            except KeyError:
                knots = None
                print("Knots not found in json data.")

        if form == 3 and knots:
            periodic = True
            my_curve = cmds.curve(
                p=cv_data, d=degree, name=curve_name, per=periodic, k=knots
            )
        else:
            periodic = False
            my_curve = cmds.curve(p=cv_data, d=degree, name=curve_name)
    except:
        cmds.warning(f"Could not load data from {Const.CTRL_DATA_DIR}{file_name}.json")
        return None

    return my_curve
