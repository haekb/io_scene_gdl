import os
import bpy
import bpy_extras
from bpy.props import StringProperty, BoolProperty, FloatProperty
from .obj_reader import ObjectReader

class ImportOperatorObject(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = 'io_scene_gdl.objects_import'  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = 'Import GDL OBJECTS.PS2'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    # ImportHelper mixin class uses this
    filename_ext = ".PS2"

    filter_glob: StringProperty(
        default="OBJECTS.PS2",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        # Load the model
        model = ObjectReader().read(self.filepath)

        model.name = os.path.splitext(os.path.basename(self.filepath))[0]

        return {'FINISHED'}

    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(ImportOperatorObject.bl_idname, text='GDL OBJECTS.PS2 (.PS2)')
