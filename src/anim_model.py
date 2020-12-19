from mathutils import Vector, Quaternion, Matrix
from .io import unpack, read_string
from .utils import align

class Anim(object):
    def __init__(self):
        # Straight from data
        self._skeleton_count = 0
        self._unknown_short = 0 # Some sort of flag
        self._skeleton_data_pointer = 0
        self._effect_count = 0
        self._effect_pointer = 0
        # Only if unknown_short != 0
        self._unknown_count = 0
        self._unknown_pointer = 0

        # Scratch Space
        self._current_skeleton_position = 0

        # Processed
        self._skeletons = []
    # End Def

    def read(self, f):
        self._skeleton_count = unpack('H', f)[0]
        self._unknown_short = unpack('H', f)[0]
        self._skeleton_data_pointer = unpack('I', f)[0]
        self._effect_count = unpack('I', f)[0]
        self._effect_pointer = unpack('I', f)[0]

        if self._unknown_short != 0:
            self._unknown_count = unpack('I', f)[0]
            self._unknown_pointer = unpack('I', f)[0]
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
            f.seek(31, - len(self._name), 1)
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
            self._unk_float = 0.0
            self._location = Vector()
            self._unk_1 = 0
            self._unk_2 = 0
            self._unk_3 = 0
            self._parent_id = -1
        # End Def

        def read(self, model, f):
            self._name = f.read(28).decode('ascii')
            self._unk_float = unpack('f', f)[0]
            self._location = Vector(unpack('3f', f))
            self._unk_1 = unpack('I', f)[0]
            self._unk_2 = unpack('I', f)[0]
            self._unk_3 = unpack('I', f)[0]
            self._parent_id = unpack('i', f)[0]
        # End Def

    # End Class
