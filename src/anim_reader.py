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
        pass

    # End Def
