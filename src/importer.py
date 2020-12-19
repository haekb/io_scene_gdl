import os
import bpy
import bpy_extras
from bpy.props import StringProperty, BoolProperty, FloatProperty
from .anim_reader import AnimReader
from .obj_reader import ObjectReader
from .world_reader import WorldReader

class ImportObjectOptions(object):
    def __init__(self):
        # Shoving this in here for now
        self._anim = None

        # Options
        self._should_log = False
        self._should_load_anim = True

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

    should_log: BoolProperty(
        name="Enable Logging",
        description="Enables logging during the object import. (This is slow!)",
        default=False,
    )

    should_load_anim: BoolProperty(
        name="Load Bones/Animations",
        description="Loads the associated ANIM file which contains bone/animation information.",
        default=True,
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Animation')
        box.row().prop(self, 'should_load_anim')

        box = layout.box()
        box.label(text='Misc')
        box.row().prop(self, 'should_log')

    def execute(self, context):
        print("Loading file %s" % self.filepath)

        options = ImportObjectOptions()
        options._should_log = self.should_log
        options._should_load_anim = self.should_load_anim

        if options._should_load_anim:
            anim_path = self.filepath.replace("OBJECTS.PS2", "ANIM.PS2")
            anim_reader = AnimReader()
            options._anim = anim_reader.read(anim_path)

        # Load the model
        model = ObjectReader().read(self.filepath, options)

        model.name = os.path.splitext(os.path.basename(self.filepath))[0]

        return {'FINISHED'}

    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(ImportOperatorObject.bl_idname, text='GDL OBJECTS.PS2 (.PS2)')

class ImportOperatorWorld(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = 'io_scene_gdl.worlds_import'  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = 'Import GDL WORLDS.PS2'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    # ImportHelper mixin class uses this
    filename_ext = ".PS2"

    filter_glob: StringProperty(
        default="WORLDS.PS2",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    should_log: BoolProperty(
        name="Enable Logging",
        description="Enables logging during the object import. (This is slow!)",
        default=False,
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Misc')
        box.row().prop(self, 'should_log')


    def execute(self, context):
        print("Loading file %s" % self.filepath)

        # Haha super hack, it will break if anything else is named WORLDS.PS2...
        objectpath = self.filepath.replace("WORLDS.PS2", "OBJECTS.PS2")

        options = ImportObjectOptions()
        options._should_log = self.should_log

        # Load the model
        model = ObjectReader().read(objectpath, options)
        model.name = os.path.splitext(os.path.basename(objectpath))[0]

        # Okay, now the world!
        world = WorldReader().read(self.filepath)

        return {'FINISHED'}

    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(ImportOperatorWorld.bl_idname, text='GDL WORLDS.PS2 (.PS2)')
