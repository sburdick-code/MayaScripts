import maya.api.OpenMaya as om
import maya.cmds
import numpy as np
import json
import math


# Indicates to maya that the new API should be used. Leave it as an empty function call.
def maya_useNewAPI():
    pass


class SoxsRBFNode(om.MPxNode):

    TYPE_NAME = "SoxsRBFNode"
    TYPE_ID = om.MTypeId(0x0007F9F9)

    # Attribute Objects
    input_obj = None
    in_x_obj = None
    in_y_obj = None
    in_z_obj = None

    output_obj = None
    out_x_obj = None
    out_y_obj = None
    out_z_obj = None

    rbf_data_path_obj = None
    rbf_id_obj = None

    eval_settings_obj = None
    kernel_obj = None

    SETTINGS_ENUMS = [
        "1In -> 1Out",
        "1In -> 2Out",
        "1In -> 3Out",
        "2In -> 1Out",
        "2In -> 2Out",
        "2In -> 3Out",
        "3In -> 1Out",
        "3In -> 2Out",
        "3In -> 3Out",
    ]

    KERNEL_ENUMS = ["Linear", "Quadratic", "Cubic"]

    def __init__(self):
        super(SoxsRBFNode, self).__init__()

    def compute(self, plug, data):

        if (
            plug == SoxsRBFNode.output_obj
            or plug == SoxsRBFNode.out_x_obj
            or plug == SoxsRBFNode.out_y_obj
            or plug == SoxsRBFNode.out_z_obj
        ):

            postion = None
            in_matrix = None
            weight_matrix = None
            output = None

            # Get Attributes
            input_handle = data.inputValue(SoxsRBFNode.input_obj)
            in_x = input_handle.child(SoxsRBFNode.in_x_obj).asDouble()
            in_y = input_handle.child(SoxsRBFNode.in_y_obj).asDouble()
            in_z = input_handle.child(SoxsRBFNode.in_z_obj).asDouble()
            position = [in_x, in_y, in_z]

            in_matrix_path = data.inputValue(SoxsRBFNode.rbf_data_path_obj).asString()
            rbf_id = data.inputValue(SoxsRBFNode.rbf_id_obj).asString()

            eval_index = data.inputValue(SoxsRBFNode.eval_settings_obj).asShort()
            eq_index = data.inputValue(SoxsRBFNode.kernel_obj).asShort()

            # Read position matrix and weight matrix form JSON file
            try:
                with open(in_matrix_path, "r") as f:
                    rbf_data = json.load(f)

                    dist_key = f"d_{rbf_id}"
                    weight_key = f"w_{rbf_id}"

                    if dist_key not in rbf_data:
                        om.MGlobal.displayError(
                            f"Failed to find Distance Matrix for {rbf_id}. Key should be labeled as {dist_key}!"
                        )
                        return
                    if weight_key not in rbf_data:
                        om.MGlobal.displayError(
                            f"Failed to find Weight Matrix for {rbf_id}. Key should be labeled as {weight_key}!"
                        )
                        return

                    in_matrix = np.array(rbf_data[dist_key])
                    weight_matrix = np.array(rbf_data[weight_key])

            except Exception as e:
                om.MGlobal.displayError(f"Failed to read JSON: {e}")
                return

            # Switch statement for Evaluation Settings
            if SoxsRBFNode.SETTINGS_ENUMS[eval_index][0:3] == "1In":
                position = [in_x]
            elif SoxsRBFNode.SETTINGS_ENUMS[eval_index][0:3] == "2In":
                position = [in_x, in_y]
            elif SoxsRBFNode.SETTINGS_ENUMS[eval_index][0:3] == "3In":
                position = [in_x, in_y, in_z]

            output_handle = data.outputValue(SoxsRBFNode.output_obj)
            out_x = output_handle.child(SoxsRBFNode.out_x_obj)
            out_y = output_handle.child(SoxsRBFNode.out_y_obj)
            out_z = output_handle.child(SoxsRBFNode.out_z_obj)

            # DEBUG : delete me
            # print(in_matrix)
            # print(weight_matrix)

            # Calculate RBF
            solve_result = self.evaluate_rbf(
                position, in_matrix, weight_matrix, eq_index
            )
            print(solve_result)

            # Set out attributes
            if SoxsRBFNode.SETTINGS_ENUMS[eval_index][-4:] == "1Out":
                out_x.setDouble(solve_result[0])
            if SoxsRBFNode.SETTINGS_ENUMS[eval_index][-4:] == "2Out":
                out_x.setDouble(solve_result[0])
                out_y.setDouble(solve_result[1])
            if SoxsRBFNode.SETTINGS_ENUMS[eval_index][-4:] == "3Out":
                out_x.setDouble(solve_result[0])
                out_y.setDouble(solve_result[1])
                out_z.setDouble(solve_result[2])

            data.setClean(plug)

    # RBF Solver
    def evaluate_rbf(self, pos, in_matrix, weight_matrix, beta):
        in_phi = np.zeros(len(in_matrix))

        for i in range(len(in_phi)):
            dist = self.euclidean_distance(pos, in_matrix[i])
            in_phi[i] = dist**beta

        result = np.dot(in_phi, weight_matrix)

        # HACKY PATCH! Idk why this works :(
        if beta < 3:
            result *= 10

        return result

    @staticmethod
    def euclidean_distance(p1, p2):
        return math.sqrt(sum([(a - b) ** 2 for a, b in zip(p1, p2)]))

    @classmethod
    def creator(cls):
        return SoxsRBFNode()

    @classmethod
    def initialize(cls):
        nAttr = om.MFnNumericAttribute()
        cAttr = om.MFnCompoundAttribute()
        uAttr = om.MFnUnitAttribute()
        eAttr = om.MFnEnumAttribute()
        tAttr = om.MFnTypedAttribute()
        mAttr = om.MFnMatrixAttribute()
        stringData = om.MFnStringData()

        # INPUT - Enums for num inputs and outputs
        cls.eval_settings_obj = eAttr.create("RBF_Settings", "evalSet", 8)
        for i in range(len(cls.SETTINGS_ENUMS)):
            eAttr.addField(cls.SETTINGS_ENUMS[i], i)
        eAttr.keyable = True

        # INPUT - Equation Type
        cls.kernel_obj = eAttr.create("RBF_Kernel", "krnl", 1)
        for i in range(1, len(cls.KERNEL_ENUMS) + 1):
            eAttr.addField(cls.KERNEL_ENUMS[i - 1], i)
        eAttr.keyable = True

        # INPUT - Input Attributes
        cls.in_x_obj = nAttr.create("InputX", "inX", om.MFnNumericData.kDouble, 0.0)
        cls.in_y_obj = nAttr.create("InputY", "inY", om.MFnNumericData.kDouble, 0.0)
        cls.in_z_obj = nAttr.create("InputZ", "inZ", om.MFnNumericData.kDouble, 0.0)

        cls.input_obj = cAttr.create("Input", "in")
        cAttr.keyable = True
        cAttr.addChild(cls.in_x_obj)
        cAttr.addChild(cls.in_y_obj)
        cAttr.addChild(cls.in_z_obj)

        # OUTPUT - Output Attributes
        cls.out_x_obj = nAttr.create("OutputX", "outX", om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = False
        nAttr.storable = False
        cls.out_y_obj = nAttr.create("OutputY", "outY", om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = False
        nAttr.storable = False
        cls.out_z_obj = nAttr.create("OutputZ", "outZ", om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = False
        nAttr.storable = False

        cls.output_obj = cAttr.create("Output", "out")
        cAttr.writable = False
        cAttr.addChild(cls.out_x_obj)
        cAttr.addChild(cls.out_y_obj)
        cAttr.addChild(cls.out_z_obj)

        # INPUT - Json Path
        cls.rbf_data_path_obj = tAttr.create(
            "RBF_DataPath", "path", om.MFnData.kString, stringData.create("")
        )
        tAttr.keyable = True

        # INPUT - Unique ID Path
        cls.rbf_id_obj = tAttr.create(
            "RBF_DataId", "id", om.MFnData.kString, stringData.create("")
        )
        tAttr.keyable = True

        # Add all the attributes
        cls.addAttribute(cls.input_obj)
        cls.addAttribute(cls.output_obj)

        cls.addAttribute(cls.rbf_data_path_obj)
        cls.addAttribute(cls.rbf_id_obj)
        cls.addAttribute(cls.kernel_obj)
        cls.addAttribute(cls.eval_settings_obj)

        # Add attribute affects
        all_outputs = [cls.output_obj, cls.out_x_obj, cls.out_y_obj, cls.out_z_obj]

        for obj in all_outputs:
            cls.attributeAffects(cls.in_x_obj, obj)
            cls.attributeAffects(cls.in_y_obj, obj)
            cls.attributeAffects(cls.in_z_obj, obj)
            cls.attributeAffects(cls.rbf_data_path_obj, obj)
            cls.attributeAffects(cls.rbf_id_obj, obj)
            cls.attributeAffects(cls.eval_settings_obj, obj)
            cls.attributeAffects(cls.kernel_obj, obj)


# Entry Point. Takes in an MObject (plugin)
def initializePlugin(plugin):

    vendor = "Sox"
    version = "1.0.0"

    plugin_fn = om.MFnPlugin(plugin, vendor, version)

    try:
        plugin_fn.registerNode(
            SoxsRBFNode.TYPE_NAME,
            SoxsRBFNode.TYPE_ID,
            SoxsRBFNode.creator,
            SoxsRBFNode.initialize,
            om.MPxNode.kDependNode,
        )

    except:
        om.MGlobal.displayError(
            "Failed to register node: {0}".format(SoxsRBFNode.TYPE_NAME)
        )


# Un-Load the plugin
def uninitializePlugin(plugin):

    plugin_fn = om.MFnPlugin(plugin)

    try:
        plugin_fn.deregisterNode(SoxsRBFNode.TYPE_ID)
    except:
        om.MGlobal.displayError(
            "Failed to deregister node: {0}".format(SoxsRBFNode.TYPE_NAME)
        )


if __name__ == "__main__":

    cmds.file(new=True, force=True)

    plugin_name = "SoxsRBF.py"

    cmds.evalDeferred(
        'if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(
            plugin_name
        )
    )
    cmds.evalDeferred(
        'if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(
            plugin_name
        )
    )

    cmds.evalDeferred('cmds.createNode("SoxsRBFNode")')
