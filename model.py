from .io import unpack
from mathutils import Vector, Quaternion, Matrix


'''
Every console port is based off the PS2 version.
It seems they just "re-built" some of the PS2 sdk functions for Xbox and Gamecube.
Refer to here for model info: https://psi-rockin.github.io/ps2tek/

This is more of the file format model...it might get moved to an importer...
'''

class Model(object):
    def __init__(self):

        # Start Header

        self._dir_name = ""
        self._version = 0

        # Counts
        self._object_count = 0
        self._texture_count = 0
        self._object_def_count = 0
        self._texture_def_count = 0

        # Locations
        self._object_pointer = 0
        self._texture_pointer = 0
        self._object_def_pointer = 0
        self._texture_def_pointer = 0
        self._sub_object_pointer = 0
        self._geometry_pointer = 0
        self._object_end_pointer = 0

        # Unknowns
        self._texture_start = 0
        self._texture_end = 0
        self._texture_bits = 0 # Pointer?
        self._lmtex_first = 0
        self._lmtex_num = 0
        self._texture_info = 0

        self._header_end_position = 0
        # End Header

        # Array of ...name...
        self._object_defs = []
        self._texture_defs = []

        self._objects = []
        self._textures = []
        self._sub_objects = []

        self._vertices = []

    # End Def

    def read(self, f):
        self._dir_name = f.read(32).decode('ascii')

        # Next up is ModelName which isn't filled in data afaik
        f.seek(32, 1)

        self._version = unpack('I', f)[0]

        # Version check!
        if self._version != 0xF00B000D:
            raise Exception('Unsupported file version. ({}).'.format(self._version))

        # Counts
        self._object_count = unpack('I', f)[0]
        self._texture_count = unpack('I', f)[0]
        self._object_def_count = unpack('I', f)[0]
        self._texture_def_count = unpack('I', f)[0]

        # Locations
        self._object_pointer = unpack('I', f)[0]
        self._texture_pointer = unpack('I', f)[0]
        self._object_def_pointer = unpack('I', f)[0]
        self._texture_def_pointer = unpack('I', f)[0]
        self._sub_object_pointer = unpack('I', f)[0]
        self._geometry_pointer = unpack('I', f)[0]
        self._object_end_pointer = unpack('I', f)[0]

        # Unknowns
        self._texture_start = unpack('I', f)[0]
        self._texture_end = unpack('I', f)[0]
        self._texture_bits = unpack('I', f)[0]
        self._lmtex_first = unpack('H', f)[0]
        self._lmtex_end = unpack('H', f)[0]
        self._texture_info = unpack('I', f)[0]

        # Skip past unused
        f.seek(4, 1)

        # Just in case we gotta go back!
        self._header_end_position = f.tell()

        # Handle object defs
        f.seek(self._object_def_pointer, 0)

        for _ in range(self._object_def_count):
            object_def = ObjectDef()
            object_def.read(f)
            self._object_defs.append(object_def)

        f.seek(self._texture_def_pointer, 0)

        # Handle texture defs
        for _ in range(self._texture_def_count):
            texture_def = TextureDef()
            texture_def.read(f)
            self._texture_defs.append(texture_def)

        f.seek(self._object_pointer, 0)

        # Handle objects
        for _ in range(self._object_count):
            rom_object = Object()
            rom_object.read(f)
            self._objects.append(rom_object)

        f.seek(self._texture_pointer, 0)

        # Handle objects
        for _ in range(self._texture_count):
            rom_texture = Texture()
            rom_texture.read(f)
            self._textures.append(rom_texture)

        # Let's load some data!

        for obj in self._objects:
            f.seek(obj._data_pointer, 0)

            print("Current: %d" % f.tell())
            # VU unpack command
            f.seek(2 * 4, 1)
            print("Current: %d" % f.tell())
            base_signal = Signal()
            base_signal.read(f)
            # Unknown data
            f.seek(4 * 4, 1)

            vertex_signal = Signal()
            vertex_signal.read(f)

            for _ in range(obj._vertex_count):
                vertex = Vertex()
                vertex.read(f, vertex_signal._mode)
                self._vertices.append(vertex)

        end = True
    # End Def
# End Class

class ObjectDef(object):
    def __init__(self):
        self._name = ""
        self._bnd_rad = 0.0
        self._index = 0
        self._frame_count = 0

    def read(self, f):
        self._name = f.read(16).decode('ascii')
        self._bnd_rad = unpack('f', f)[0]
        self._index = unpack('H', f)[0]
        self._frame_count = unpack('H', f)[0]

# ROMOBJECT in the bt
class Object(object):
    def __init__(self):
        self._inv_rad = 0.0
        self._bnd_rad = 0.0
        self._flags = 0
        self._sub_object_count = 0
        self._sub_object_0_qwc = 0
        self._sub_object_0_texture_index = 0
        self._sub_object_0_lm_index = 0
        self._sub_object_0_lodk = 0
        self._sub_object_pointer = 0
        self._data_pointer = 0
        self._vertex_count = 0
        self._triangle_count = 0
        self._index = 0
        self._object_def_pointer = 0

    def read(self, f):
        self._inv_rad = unpack('f', f)[0]
        self._bnd_rad = unpack('f', f)[0]
        self._flags = unpack('I', f)[0]
        self._sub_object_count = unpack('I', f)[0]
        self._sub_object_0_qwc = unpack('H', f)[0]
        self._sub_object_0_texture_index = unpack('H', f)[0]
        self._sub_object_0_lm_index = unpack('H', f)[0]
        self._sub_object_0_lodk = unpack('h', f)[0] # Signed
        self._sub_object_pointer = unpack('I', f)[0]
        self._data_pointer = unpack('I', f)[0]
        self._vertex_count = unpack('I', f)[0]
        self._triangle_count = unpack('I', f)[0]
        self._index = unpack('I', f)[0]
        self._object_def_pointer = unpack('I', f)[0]
        f.seek(4*4, 1)

class TextureDef(object):
    def __init__(self):
        self._name = ""
        self._index = 0
        self._width = 0
        self._height = 0

    def read(self, f):
        self._name = f.read(30).decode('ascii')
        self._index = unpack('H', f)[0]
        self._width = unpack('H', f)[0]
        self._height = unpack('H', f)[0]

class Texture(object):
    def __init__(self):
        self._format = 0
        self._lodk = 0
        self._mipmaps = 0
        self._width64 = 0
        self._width_log2 = 0
        self._height_log2 = 0
        self._flags = 0
        self._texture_palette_index = 0
        self._texture_base_pointer = 0
        self._texture_palette_count = 0
        self._texture_shift_index = 0
        self._frame_count = 0
        self._width = 0
        self._height = 0
        self._size = 0
        self._texture_def_pointer = 0

        # Not used?
        # uint Tex0[2]
        # uint64 MIPTBP1
        # uint64 MIPTBP2
        # uint vram_addr
        # uint clut_addr
    
    def read(self, f):
        self._format = unpack('B', f)[0]
        self._lodk = unpack('B', f)[0]
        self._mipmaps = unpack('B', f)[0]
        self._width64 = unpack('B', f)[0]
        self._width_log2 = unpack('H', f)[0]
        self._height_log2 = unpack('H', f)[0]
        self._flags = unpack('H', f)[0]
        self._texture_palette_index = unpack('H', f)[0]
        self._texture_base_pointer = unpack('I', f)[0]
        self._texture_palette_count = unpack('H', f)[0]
        self._texture_shift_index = unpack('H', f)[0]
        self._frame_count = unpack('H', f)[0]
        self._width = unpack('H', f)[0]
        self._height = unpack('H', f)[0]
        self._size = unpack('H', f)[0]
        self._texture_def_pointer = unpack('I', f)[0]

        f.seek(8 * 4, 1)

class SubObject(object):
    def __init__(self):
        # Quadword count
        self._qwc = 0
        self._texture_index = 0
        self._lm_index = 0
        # Level of Detail - K parameter (signed fixed-point, 7 bits whole, 4 bits fractional)
        self._lodk = 0

    def read(self, f):
        self._qwc = unpack('H', f)[0]
        self._texture_index = unpack('H', f)[0]
        self._lm_index = unpack('H', f)[0]
        self._lodk = unpack('H', f)[0]

'''
PS2 related geometry
Geometry data seems to be formatted for PS2
'''

# Constants for various things
# Header?
SIGNAL_MODE_HEADER = 0x6C
# Vertex
SIGNAL_MODE_CHAR = 0x6A
SIGNAL_MODE_SHORT = 0x69
# UV?
SIGNAL_MODE_UV = 0x6F

'''
Vertex data can either be stored in shorts or chars
'''
class Vertex(object):
    def __init__(self):
        self._x = 0
        self._y = 0
        self._z = 0
        self._vector = Vector()

    def read(self, f, mode = SIGNAL_MODE_CHAR):
        if mode == SIGNAL_MODE_CHAR:
            fmt = '3b'
        elif mode == SIGNAL_MODE_SHORT:
            fmt = '3h'
        else: # UNKNOWN!
            fmt = '3b'
        
        [ self._x, self._y, self._z ] = unpack(fmt, f)
        self._vector = Vector( ( self._x, self._y, self._z ) )

class Signal(object):
    def __init__(self):
        self._count = 0
        self._constant = 0
        self._data_count = 0
        self._mode = 0
    
    def read(self, f):
        self._count = unpack('B', f)[0]
        self._constant = unpack('B', f)[0]
        self._data_count = unpack('B', f)[0]
        self._mode = unpack('B', f)[0]
