from mathutils import Vector, Quaternion, Matrix
from .io import unpack, read_string
from .utils import align

class Anim(object):
    def __init__(self):
        # Straight from data
        self.skeleton_count = 0
        self.version = 0 # Either 0 or 8
        self.skeleton_data_pointer = 0
        self.effect_count = 0 # TexMods
        self.effect_pointer = 0
        # Only if unknown_short != 0
        self.psys_count = 0
        self.psys_pointer = 0

        # Scratch Space
        self.current_skeleton_position = 0
        self.current_animation_position = 0
        self.current_animation_data = None
        self.current_skeleton = None

        # Processed
        self.skeletons = []
    # End Def

    def read(self, f):
        self.skeleton_count = unpack('H', f)[0]
        self.version = unpack('H', f)[0]
        self.skeleton_data_pointer = unpack('I', f)[0]
        self.effect_count = unpack('I', f)[0]
        self.effect_pointer = unpack('I', f)[0]

        if self.version != 0:
            self.psys_count = unpack('I', f)[0]
            self.psys_pointer = unpack('I', f)[0]
        # End If

        for _ in range(self.skeleton_count):
            skeleton = self.Skeleton()
            skeleton.read(self, f)
            self.skeletons.append(skeleton)
        # End For

        for skeleton in self.skeletons:
            skeleton.read_data(self, f)

    # End Def

    #
    # Internal Classes
    #

    class Skeleton(object):
        def __init__(self):
            self.name = ""
            self.skeleton_data_pointer = 0

            # Skeleton Data
            self.data = None
        # End Def
        def read(self, model, f):
            self.name = read_string(f)
            f.seek(31 - len(self.name), 1)

            self.skeleton_data_pointer = unpack('I', f)[0]
        # End Def

        def read_data(self, model, f):
            # Hop over to the skeleton pointer
            f.seek(self.skeleton_data_pointer, 0)
            model.current_skeleton_position = f.tell()

            self.data = model.SkeletonData()
            self.data.read(model, f)
        # End Def
    # End Class

    class SkeletonData(object):
        def __init__(self):
            self.animation_header_pointer = 0
            self.animation_data_pointer = 0     # Skeletal Animations
            self.obj_animation_data_pointer = 0 # Vertex Animations
            self.bone_pointer = 0
            self.bone_count = 0
            self.animation_count = 0
            self.name = ""

            # Our skeleton is filled with bones! Wild what they do these days.
            self.bones = []

            self.animation_data = None
            self.animation_headers = []
            self.animations = []
        # End Def

        def read(self, model, f):
            self.animation_header_pointer = unpack('I', f)[0]
            self.animation_data_pointer = unpack('I', f)[0]
            self.unk_pointer = unpack('I', f)[0]
            self.bone_pointer = unpack('I', f)[0]
            self.bone_count = unpack('I', f)[0]
            self.animation_count = unpack('I', f)[0]

            self.name = read_string(f)
            f.seek(31 - len(self.name), 1)

            model.current_skeleton = self

            f.seek( self.animation_data_pointer + model.current_skeleton_position, 0 )
            self.animation_data = model.AnimationData()
            self.animation_data.read(model, f)

            f.seek( self.animation_header_pointer + model.current_skeleton_position, 0 )
            for _ in range(self.animation_count):
                header = model.AnimationHeader()
                header.read(model, f)
                self.animation_headers.append(header)
            # End For

            # From here, it's all relative, and boy that's not fun
            f.seek( self.bone_pointer + model.current_skeleton_position, 0 )
            for _ in range(self.bone_count):
                bone = model.Bone()
                bone.read(model, f)
                self.bones.append(bone)

                bone_position = f.tell()

                print("Getting animation data for %s" % bone.name)

                # Animation Sequences
                f.seek( bone.sequence_pointer + model.current_animation_position, 0 )
                for i in range(model.current_animation_data.sequence_count):
                    sequence = model.AnimationSequence()
                    sequence.read(model, f, i)
                    self.animations.append(sequence)
                # End For

                print("-----------------------------")

                # Reset to our position
                f.seek( bone_position, 0 )
            # End For
        # End Def
    # End Class

    class Bone(object):
        # Bone Type
        BT_EMPTY = 0xFFFFFFFF
        BT_NULL = 0
        BT_SKEL_ANIM = 1
        BT_OBJ_ANIM = 2 # Vertex Animation
        BT_TEX_ANIM = 3
        BT_PSYS_ANIM = 4

        def __init__(self):
            self.name = ""
            self.location = Vector()
            self.type = 0 
            self.flags = 0
            self.mb_flags = 0
            self.sequence_pointer = 0
            self.parent_id = -1

            # Linkage
            self.parent = None
            self.children = []
            self.child_count = 0

            # Transform info
            self.bind_matrix = Matrix()
        # End Def

        def read(self, model, f):
            self.name = read_string(f)
            f.seek(31 - len(self.name), 1)
            
            self.location = Vector(unpack('3f', f))
            self.type = unpack('H', f)[0]
            self.flags = unpack('H', f)[0]
            self.mb_flags = unpack('I', f)[0]
            self.sequence_pointer = unpack('I', f)[0]
            self.parent_id = unpack('i', f)[0]

            # Set a default bind pose
            self.bind_matrix = Matrix.Translation(self.location)
        # End Def

    # End Class

    # More like...a header, except that's already claimed
    class AnimationData(object):
        def __init__(self):
            self.compress_ang_pointer = 0
            self.compress_pos_pointer = 0
            self.compress_unit_pointer = 0
            self.block_pointer = 0
            self.sequence_pointer = 0
            self.sequence_count = 0 # Animations
            self.object_count = 0 # Bones

            self.compress_ang = 0
            self.compress_pos = 0
            self.compress_unit = 0
        # End Def

        def read(self, model, f):
             # This is the basis for a lot of pointers!
            model.current_animation_position = f.tell()
            model.current_animation_data = self

            self.compress_ang_pointer = unpack('I', f)[0]
            self.compress_pos_pointer = unpack('I', f)[0]
            self.compress_unit_pointer = unpack('I', f)[0]
            self.block_pointer = unpack('I', f)[0]
            self.sequence_pointer = unpack('I', f)[0]
            self.sequence_count = unpack('I', f)[0]
            self.object_count = unpack('I', f)[0]



            # Compress Pointers (At least I think they're pointers...)
            # If they're a non-zero value then go to them, and get the value!

            if (self.compress_ang_pointer > 0):
                f.seek(model.current_animation_position + self.compress_ang_pointer, 0)
                self.compress_ang = unpack('I', f)[0]
            # End If

            if (self.compress_pos_pointer > 0):
                f.seek(model.current_animation_position + self.compress_pos_pointer, 0)
                self.compress_pos = unpack('I', f)[0]
            # End If

            if (self.compress_unit_pointer > 0):
                f.seek(model.current_animation_position + self.compress_unit_pointer, 0)
                self.compress_pos = unpack('I', f)[0]
            # End If
        # End Def
    # End Class

    class AnimationHeader(object):
        def __init__(self):
            self.name = ""
            self.frame_count = 0
            self.frame_rate = 0
            self.loop = False
            self.fix_pos = False # This MIGHT not be a bool...
            self.effect_count = 0
            self.flags = 0
            self.effect_pointer = -1
        # End Def

        def read(self, model, f):
            self.name = read_string(f)
            f.seek(31 - len(self.name), 1)

            self.frame_count = unpack('H', f)[0]
            self.frame_rate = unpack('H', f)[0]
            self.loop = bool(unpack('H', f)[0])
            self.fix_pos = bool(unpack('H', f)[0])
            self.effect_count = unpack('H', f)[0]
            self.flags = unpack('H', f)[0]
            self.effect_pointer = unpack('i', f)[0] # Signed int!

            # TODO: map out effects
        # End Def
    # End Class

    class AnimationSequence(object):
        def __init__(self):
            self.type = 0
            self.size = 0
            self.data_pointer = 0

            self.data = [] # Raw Data
            self.transforms = [] # Processed Data
        # End Def

        def read(self, model, f, index):
            self.type = unpack('H', f)[0]
            self.size = unpack('H', f)[0]
            self.data_pointer = unpack('I', f)[0]

            # We'll need to hop back here after we process the data
            sequence_position = f.tell()

            f.seek( self.data_pointer + ( model.current_skeleton.animation_data_pointer + model.current_animation_data.block_pointer ) , 0 )

            # Skip the framecount header bits (this bit is decompiled so uhh yeah.)
            f.seek( (model.current_skeleton.animation_headers[index].frame_count + 0x1f >> 5) * 4 , 1 )

            for _ in range( self.size * model.current_skeleton.animation_headers[index].frame_count ):
                self.data.append(unpack('f', f)[0])
            # End For

            # For now, read everything as a vector
            amount_of_vector_processed = 0
            vector = Vector()
            for i in range( len(self.data) ):
                if amount_of_vector_processed == 0:
                    vector.x = self.data[i]
                elif amount_of_vector_processed == 1:
                    vector.y = self.data[i]
                elif amount_of_vector_processed == 2:
                    vector.z = self.data[i]
                # End If

                amount_of_vector_processed += 1

                if amount_of_vector_processed > 2:
                    self.transforms.append(vector)
                    vector = Vector()
                    amount_of_vector_processed = 0
                # End If
            # End For

            if amount_of_vector_processed > 0:
                print("Amount of vector left hanging ",amount_of_vector_processed)

            # Reset our position, now that we've processed the data
            f.seek( sequence_position, 0 )

        # End Def
    # End Class
