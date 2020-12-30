from .anim_model import Anim
from mathutils import Vector, Quaternion, Matrix
import bpy
import bmesh

class AnimReader(object):
    def __init__(self):
        pass

    def read(self, path):
        anim = Anim()
        with open(path, 'rb') as f:
            anim.read(f)
            self.setup_anim(anim)
            
        return anim
    # End Def

    def setup_anim(self, anim):
        for skeleton in anim.skeletons:

            # Link 'em up!
            for bone in skeleton.data.bones:
                # Skip root
                if bone.parent_id == -1:
                    continue

                bone.parent = skeleton.data.bones[bone.parent_id]
                skeleton.data.bones[bone.parent_id].children.append(bone)
                skeleton.data.bones[bone.parent_id].child_count += 1
            # End For

            # Okay make the bind poses relative
            for bone in skeleton.data.bones:
                if bone.child_count == 0:
                    continue

                for child_bone in bone.children:
                    child_bone.bind_matrix = bone.bind_matrix @ child_bone.bind_matrix
                # End For
        # End For
    # End Def