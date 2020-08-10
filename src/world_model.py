from .io import unpack
from mathutils import Vector, Quaternion, Matrix
from .utils import align

class World(object):
    def __init__(self):
        self._object_count = 0
        self._world_object_offset = 0
        self._triangle_count = 0
        self._triangle_offset = 0
        # Grid
        self._grid_entry_count = 0
        self._grid_entry_offset = 0
        self._grid_list_values = 0
        self._grid_list_offet = 0
        self._grid_row_offset = 0
        # Bounds
        self._world_min = Vector()
        self._world_max = Vector()
        self._grid_size = 0.0
        self._grid_x_count = 0
        self._grid_z_count = 0
        self._grid_item_info_count = 0
        self._grid_item_instance_count = 0
        self._locator_count = 0
        self._locator_offset = 0
        self._world_format = 0
        self._anim_header_offset = 0
        self._world_anim_count = 0
        self._world_psys = 0 #?
        self._world_psys_offset = 0

        # 
        self._world_objects = []
    # End Def

    def read(self, f):
        self._object_count = unpack('I', f)[0]
        self._world_object_offset = unpack('I', f)[0]
        self._triangle_count = unpack('I', f)[0]
        self._triangle_offset = unpack('I', f)[0]
        # Grid
        self._grid_entry_count = unpack('I', f)[0]
        self._grid_entry_offset = unpack('I', f)[0]
        self._grid_list_values = unpack('I', f)[0]
        self._grid_list_offet = unpack('I', f)[0]
        self._grid_row_offset = unpack('I', f)[0]
        # Bounds
        self._world_min = Vector(unpack('3f', f))
        self._world_max = Vector(unpack('3f', f))
        self._grid_size = unpack('f', f)[0]
        self._grid_x_count = unpack('I', f)[0]
        self._grid_z_count = unpack('I', f)[0]
        self._grid_item_info_count = unpack('I', f)[0]
        self._grid_item_instance_count = unpack('I', f)[0]
        self._locator_count = unpack('I', f)[0]
        self._locator_offset = unpack('I', f)[0]
        self._world_format = unpack('I', f)[0]
        self._anim_header_offset = unpack('I', f)[0]
        self._world_anim_count = unpack('I', f)[0]
        self._world_psys = unpack('I', f)[0] #?
        self._world_psys_offset = unpack('I', f)[0]

        # Okay read the data
        f.seek(self._world_object_offset, 0)
        for _ in range(self._object_count):
            world_object = WorldObject()
            world_object.read(f)
            self._world_objects.append(world_object)
        # End For

    # End Def
# End Class

class WorldObject(object):
    def __init__(self):
        self._name = ""
        self._flags = 0
        self._trigger_type = 0
        self._trigger_state = 0
        self._previous_trigger_state = 0 # ...or pointer
        self._parent_pointer = 0
        self._position = Vector()
        self._node_pointer = 0
        self._next_index = 0
        self._child_index = 0
        self._rad = 0.0
        self._checked = 0
        self._no_col = 0 # Column? Colour? We just don't know!
        self._triangle_count = 0
        self._triangle_index = 0

    def read(self, f):
        self._name = f.read(16).decode('ascii')
        self._flags = unpack('I', f)[0]
        self._trigger_type = unpack('h', f)[0]
        self._trigger_state = unpack('b', f)[0]
        self._previous_trigger_state = unpack('b', f)[0] # ...or pointer
        self._parent_pointer = unpack('I', f)[0]
        self._position = Vector(unpack('3f', f))
        self._node_pointer = unpack('I', f)[0]
        self._next_index = unpack('h', f)[0]
        self._child_index = unpack('h', f)[0]
        self._rad = unpack('f', f)[0]
        self._checked = unpack('b', f)[0]
        self._no_col = unpack('b', f)[0] # Column? Colour? We just don't know!
        self._triangle_count = unpack('h', f)[0]
        self._triangle_index = unpack('I', f)[0]