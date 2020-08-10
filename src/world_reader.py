from .world_model import World
from mathutils import Vector, Quaternion, Matrix
import bpy
import bmesh

class WorldReader(object):
    def __init__(self):
        pass

    def read(self, path):
        world = World()
        with open(path, 'rb') as f:
            world.read(f)
            self.setup_world(world)
            

        return world
    # End Def

    def setup_world(self, world):
        
        # This seems to be the rage these days
        Context = bpy.context
        Data = bpy.data
        Ops = bpy.ops

        our_collection = Data.collections["Objects.ps2"]

        assert(our_collection != None)

        for obj in our_collection.objects:
            obj.hide_set(1)

        for world_object_index, world_object in enumerate(world._world_objects):

            try:
                our_obj = our_collection.objects[world_object._name]
            except Exception as identifier:
                #print("Missing object %s, skipping!" % world_object._name)
                continue

            assert(our_obj != None)

            print("Found object %s" % world_object._name)

            obj.hide_set(0)
            our_obj.location = world_object._position

            scale_vector = Vector( (1.0, 1.0, 1.0) )
            scale_vector *= (1.0 / world_object._rad)

            our_obj.scale = scale_vector
            

    # End Def
