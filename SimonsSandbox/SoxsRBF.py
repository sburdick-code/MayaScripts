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
    position_obj = None
    pos_x_obj = None
    pos_y_obj = None
    pos_z_obj = None

    output_obj = None
    out_x_obj = None
    out_y_obj = None
    out_z_obj = None

    rbf_data_path_obj = None
    rbf_id_obj = None

    def __init__(self):
        super(SoxsRBFNode, self).__init__()

    def compute(self, plug, data):

        if plug == SoxsRBFNode.output_obj:

            print("updating")

            postion = None
            dist_matrix = None
            weight_matrix = None
            output = None

            # Get Attributes
            position_handle = data.inputValue(SoxsRBFNode.position_obj)
            pos_x = position_handle.child(SoxsRBFNode.pos_x_obj).asDouble()
            pos_y = position_handle.child(SoxsRBFNode.pos_y_obj).asDouble()
            pos_z = position_handle.child(SoxsRBFNode.pos_z_obj).asDouble()
            position = [pos_x, pos_y, pos_z]

            dist_matrix_path = data.inputValue(SoxsRBFNode.rbf_data_path_obj).asString()
            rbf_id = data.inputValue(SoxsRBFNode.rbf_id_obj).asString()

            try:
                with open(dist_matrix_path, "r") as f:
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

                    dist_matrix = np.array(rbf_data[dist_key])
                    weight_matrix = np.array(rbf_data[weight_key])

            except Exception as e:
                om.MGlobal.displayError(f"Failed to read JSON: {e}")
                return

            output_handle = data.outputValue(SoxsRBFNode.output_obj)
            out_x = output_handle.child(SoxsRBFNode.out_x_obj)
            out_y = output_handle.child(SoxsRBFNode.out_y_obj)
            out_z = output_handle.child(SoxsRBFNode.out_z_obj)

            print(dist_matrix)
            print(weight_matrix)

            # Calculate RBF
            solve_result = self.evaluate_rbf(position, dist_matrix, weight_matrix)
            print(solve_result)

            out_x.setDouble(solve_result[0])
            out_y.setDouble(solve_result[1])
            out_z.setDouble(solve_result[2])

            data.setClean(plug)

    # RBF Solver
    def evaluate_rbf(self, pos, dist_matrix, weight_matrix):
        beta = 2
        pos_phi = np.zeros(len(dist_matrix))

        for i in range(len(pos_phi)):
            dist = self.squared_distance(pos, dist_matrix[i])
            pos_phi[i] = dist**beta

        result = np.dot(pos_phi, weight_matrix)
        print(result)
        return result

    @staticmethod
    def squared_distance(p1, p2):
        return math.sqrt(sum([(a - b) ** 2 for a, b in zip(p1, p2)]))

    @classmethod
    def creator(cls):
        return SoxsRBFNode()

    @classmethod
    def initialize(cls):
        nAttr = om.MFnNumericAttribute()
        cAttr = om.MFnCompoundAttribute()
        uAttr = om.MFnUnitAttribute()
        tAttr = om.MFnTypedAttribute()
        mAttr = om.MFnMatrixAttribute()
        stringData = om.MFnStringData()

        cls.pos_x_obj = nAttr.create("positionX", "pX", om.MFnNumericData.kDouble, 0.0)
        cls.pos_y_obj = nAttr.create("positionY", "pY", om.MFnNumericData.kDouble, 0.0)
        cls.pos_z_obj = nAttr.create("positionZ", "pZ", om.MFnNumericData.kDouble, 0.0)

        cls.position_obj = cAttr.create("position", "pos")
        cAttr.keyable = True
        cAttr.addChild(cls.pos_x_obj)
        cAttr.addChild(cls.pos_y_obj)
        cAttr.addChild(cls.pos_z_obj)

        cls.out_x_obj = nAttr.create("outputX", "oX", om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = False
        nAttr.storable = False
        cls.out_y_obj = nAttr.create("outputY", "oY", om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = False
        nAttr.storable = False
        cls.out_z_obj = nAttr.create("outputZ", "oZ", om.MFnNumericData.kDouble, 0.0)
        nAttr.writable = False
        nAttr.storable = False

        cls.output_obj = cAttr.create("output", "out")
        cAttr.writable = False
        cAttr.addChild(cls.out_x_obj)
        cAttr.addChild(cls.out_y_obj)
        cAttr.addChild(cls.out_z_obj)

        cls.rbf_data_path_obj = tAttr.create(
            "RbfDataPath", "path", om.MFnData.kString, stringData.create("")
        )
        tAttr.keyable = True

        cls.rbf_id_obj = tAttr.create(
            "RbfId", "id", om.MFnData.kString, stringData.create("")
        )
        tAttr.keyable = True

        cls.addAttribute(cls.position_obj)
        cls.addAttribute(cls.output_obj)
        cls.addAttribute(cls.rbf_data_path_obj)
        cls.addAttribute(cls.rbf_id_obj)

        cls.attributeAffects(cls.pos_x_obj, cls.output_obj)
        cls.attributeAffects(cls.pos_y_obj, cls.output_obj)
        cls.attributeAffects(cls.pos_z_obj, cls.output_obj)
        cls.attributeAffects(cls.rbf_data_path_obj, cls.output_obj)
        cls.attributeAffects(cls.rbf_id_obj, cls.output_obj)


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
