from mathutils import Vector, Quaternion, Matrix
from .io import unpack, read_string
from .utils import align

class Anim(object):
    def __init__(self):
        # Straight from data
        self._skeleton_count = 0
        self._version = 0 # Either 0 or 0x8000
        self._skeleton_data_pointer = 0
        self._effect_count = 0 # TexMods
        self._effect_pointer = 0
        # Only if unknown_short != 0
        self._psys_count = 0
        self._psys_pointer = 0

        # Scratch Space
        self._current_skeleton_position = 0

        # Processed
        self._skeletons = []
    # End Def

    def read(self, f):
        self._skeleton_count = unpack('H', f)[0]
        self._version = unpack('H', f)[0]
        self._skeleton_data_pointer = unpack('I', f)[0]
        self._effect_count = unpack('I', f)[0]
        self._effect_pointer = unpack('I', f)[0]

        if self._version != 0:
            self._psys_count = unpack('I', f)[0]
            self._psys_pointer = unpack('I', f)[0]
        # End If

        print(f.tell())

        for _ in range(self._skeleton_count):
            skeleton = self.Skeleton()
            skeleton.read(self, f)
            self._skeletons.append(skeleton)
        # End For

        for skeleton in self._skeletons:
            skeleton.read_data(self, f)

    # End Def

    #
    # Internal Classes
    #

    class Skeleton(object):
        def __init__(self):
            self._name = ""
            self._skeleton_data_pointer = 0

            # Skeleton Data
            self._data = None
        # End Def
        def read(self, model, f):
            self._name = read_string(f)
            f.seek(31 - len(self._name), 1)
            self._skeleton_data_pointer = unpack('I', f)[0]
        # End Def

        def read_data(self, model, f):
            # Hop over to the skeleton pointer
            f.seek(self._skeleton_data_pointer, 0)
            model._current_skeleton_position = f.tell()

            self._data = model.SkeletonData()
            self._data.read(model, f)
        # End Def
    # End Class

    class SkeletonData(object):
        def __init__(self):
            self._animation_header_pointer = 0
            self._animation_data_pointer = 0
            self._unk_pointer = 0
            self._bone_pointer = 0
            self._bone_count = 0
            self._animation_count = 0
            self._name = ""

            # Our skeleton is filled with bones! Wild what they do these days.
            self._bones = []
        # End Def

        def read(self, model, f):
            self._animation_header_pointer = unpack('I', f)[0]
            self._animation_data_pointer = unpack('I', f)[0]
            self._unk_pointer = unpack('I', f)[0]
            self._bone_pointer = unpack('I', f)[0]
            self._bone_count = unpack('I', f)[0]
            self._animation_count = unpack('I', f)[0]
            self._name = f.read(32).decode('ascii')

            # From here, it's all relative, and boy that's not fun
            f.seek( self._bone_pointer + model._current_skeleton_position, 0 )
            for _ in range(self._bone_count):
                bone = model.Bone()
                bone.read(model, f)
                self._bones.append(bone)
            # End For

        # End Def
    # End Class

    class Bone(object):
        def __init__(self):
            self._name = ""
            self._location = Vector()
            self._type = 0
            self._flags = 0
            self._mbflags = 0
            self._parent_id = -1

            # Linkage
            self._parent = None
            self._children = []
            self._child_count = 0

            # Transform info
            self._bind_pose = Matrix()
        # End Def

        def read(self, model, f):
            self._name = read_string(f)
            f.seek(31 - len(self._name), 1)
            
            self._location = Vector(unpack('3f', f))
            self._type = unpack('I', f)[0]
            self._flags = unpack('I', f)[0]
            self._mbflags = unpack('I', f)[0]
            self._parent_id = unpack('i', f)[0]

            # Set a default bind pose
            self._bind_pose = Matrix.Translation(self._location)
        # End Def

    # End Class
