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
        for skeleton in anim._skeletons:

            # Link 'em up!
            for bone in skeleton._data._bones:
                # Skip root
                if bone._parent_id == -1:
                    continue

                bone._parent = skeleton._data._bones[bone._parent_id]
                skeleton._data._bones[bone._parent_id]._children.append(bone)
                skeleton._data._bones[bone._parent_id]._child_count += 1
            # End For

            # Okay make the bind poses relative
            for bone in skeleton._data._bones:
                if bone._child_count == 0:
                    continue

                for child_bone in bone._children:
                    child_bone._bind_matrix = bone._bind_matrix @ child_bone._bind_matrix
                # End For
        # End For
    # End Def