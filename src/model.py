from .io import unpack
from mathutils import Vector, Quaternion, Matrix
from .utils import align

'''
Every console port is based off the PS2 version.
It seems they just "re-built" some of the PS2 sdk functions for Xbox and Gamecube.
Refer to here for model info: https://psi-rockin.github.io/ps2tek/
Other Resources:
http://lukasz.dk/files/PS2Optimisations.pdf
https://gtamods.com/wiki/Native_Data_PLG_(RW_Section)

This is more of the file format model...it might get moved to an importer...
'''

class Model(object):
    def __init__(self, options):

        # Inherit some import options
        self._log = options._enable_logging

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

        # Not sure what these are, but you should skip the next verts on face gen if >> 7 == 1
        self._skip_vertices = []

        self._vertices = []
        self._uvs = []

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

        # Handle textures
        for _ in range(self._texture_count):
            rom_texture = Texture()
            rom_texture.read(f)
            self._textures.append(rom_texture)

        # Let's load some data!

        for obj_index, obj in enumerate(self._objects):
            if self._log:
                print("------------------------------------------------------")
                print("Reading Object [%d] %s" % (obj_index, self._object_defs[obj_index]._name))

            # Invalid pointer!
            if obj._data_pointer == 0:
                if self._log:
                    print("Invalid object data, skipping!")

                # Hack: Add empty data to our vert array...
                self._vertices.append([])
                self._skip_vertices.append([])
                self._uvs.append([])
                continue

            # Find the next valid object!
            # Sometimes object data is just e m p t y.
            next_obj_index = obj_index + 1
            for obj_index_test in range(next_obj_index, len(self._objects)):
                if self._objects[obj_index_test]._data_pointer == 0:
                    continue
                next_obj_index = obj_index_test
                break
            # End For

            f.seek(obj._data_pointer, 0)

            subobj_count = obj._sub_object_count
            
            # Total vertices for this object
            # An object can be split up into multiple "groups" or batches
            obj_vertices = []
            obj_uv = []
            obj_skip_vertices = []

            if self._log:
                print("Found %d objects to unpack", subobj_count)

            # Loop through the number of sub objects
            # This counter includes the main object!
            while subobj_count > 0:
                subobj_count -= 1

                if self._log:
                    print("Object %d/%d" % (obj._sub_object_count - subobj_count, obj._sub_object_count))

                # We want to include the next 8 bytes
                last_position = f.tell()

                # VU unpack command
                unpack_command = unpack('i', f)[0]

                # Skip two unknown shorts
                f.seek(1 * 4, 1)

                header_unk_x = 0
                header_unk_y = 0

                prev_header_unk_x = 0
                prev_header_unk_y = 0


                current_position = f.tell()
                total_size = 0

                # We can get the size of the entire packet by doing this,
                # We also need to truncate the result to 32-bit!!!
                unpack_size = (unpack_command << 4) & 0xFFFFFFFF

                if self._log and unpack_size > 10000:
                    print("WARNING: Unusually large unpack size at ", f.tell())

                # SubObj Count - 1 is how much extra data we have
                # ---
                # Once we hit unpack size, check if we'll bleed into another object,
                # if not, then check if there's a new "unpack_command". 
                # If there is, mark it as merge with previous then grab that mesh data.

                while total_size < unpack_size:

                    while True: 
                        align(4, f)

                        if self._log:
                            print("Reading Signal at %d" % f.tell())
                        signal = Signal()
                        signal.read(f)

                        # Note: Possible colour data if signal.index == 3 
                        if self._log:
                            print("Signal mode: %s" % signal.get_mode_string())
                        if signal.is_header():
                            f.seek(4 * 2, 1)

                            # Set the previous directionals
                            prev_header_unk_x = header_unk_x
                            prev_header_unk_y = header_unk_y

                            # Not sure, but these might have to do with groupings
                            header_unk_x = unpack('f', f)[0]
                            header_unk_y = unpack('f', f)[0]

                        elif signal.is_vertex():
                            # Unsure as to why this vertices are -1, but it skips the (0,0,0) padding at the end
                            for _ in range(signal._data_count - 1):
                                vertex = Vertex()
                                vertex.read(f, signal._mode)
                                obj_vertices.append(vertex)
                                
                            if signal._mode == SIGNAL_MODE_CHAR_3:
                                f.seek(3, 1)
                            elif signal._mode == SIGNAL_MODE_SHORT_3:
                                f.seek(6, 1)
                            
                        elif signal.is_uv():
                            for _ in range(signal._data_count):
                                uv = UV()
                                uv.read(f, signal._mode)

                                obj_uv.append(uv)
                            
                        elif signal.is_skip_vertex():
                            for _ in range(signal._data_count):
                                skip = SkipVertex()
                                skip.read(f)

                                obj_skip_vertices.append(skip)

                        else:
                            if self._log:
                                print("Unknown signal! Probably misaligned read..breaking!", signal._mode, f.tell())
                            break
                        # End If

                        # If we hit index 4 (UV map),
                        # then quit out!
                        if signal._index >= 4:
                            break
                    # End While
                    align(4, f)

                    # Check for VIF commands
                    vif_command = unpack('i', f)[0]
                    
                    if self._log:
                        if vif_command == VIF_MSCAL:
                            print("MSCAL found. Call microprogram")
                        elif vif_command == VIF_MSCNT:
                            print("MSCNT found. Continue microprogram")
                        else:
                            print("Unknown VIF command found: ", vif_command)

                    current_position = f.tell()
                    total_size = current_position - last_position

                    if self._log:
                        print("Current Total Size/Unpack Size:",total_size, unpack_size)
                # End For
                align(16, f)
            # End While
            self._vertices.append(obj_vertices)
            self._uvs.append(obj_uv)
            self._skip_vertices.append(obj_skip_vertices)
        # End While

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
#define VIF_MSCAL 0x14000000
#define VIF_MSCNT 0x17000000
VIF_MSCAL = 0x14000000
VIF_MSCNT = 0x17000000

# Constants for various things
OBJ_START_SIGNATURE = 0x6C018000

# Else 12 byte vertex
# UV?
SIGNAL_MODE_UV = 0x6F # V4-5 - 4 Items packed in 5 bytes
# Datamined unknowns
SIGNAL_MODE_UNK_8BYTE = 0x6D # V4-16 (4 items, 16 bytes) # Possibly level-based
SIGNAL_MODE_UNK_2BYTE = 0x66 # V2-8 (2 items, 8 bytes)

# Confirmed
# Header?
SIGNAL_MODE_HEADER = 0x6C # V4-32 (4 items, 32 bytes) (Doesn't quite line up..)
# Vertex
SIGNAL_MODE_CHAR_3 = 0x6A
SIGNAL_MODE_SHORT_3 = 0x69
# UV
SIGNAL_MODE_CHAR_2 = 0x66
SIGNAL_MODE_SHORT_2 = 0x65
# Flip Vert related
SIGNAL_MODE_INT_4 = 0x6F

'''
Vertex data can either be stored in shorts or chars
'''
class Vertex(object):
    def __init__(self):
        self._x = 0
        self._y = 0
        self._z = 0
        self._vector = Vector()

    def read(self, f, mode = SIGNAL_MODE_CHAR_3):
        if mode == SIGNAL_MODE_CHAR_3:
            fmt = '3b'
        elif mode == SIGNAL_MODE_SHORT_3:
            fmt = '3h'
        else: # UNKNOWN!
            fmt = '3b'
        
        [ self._x, self._y, self._z ] = unpack(fmt, f)
        self._vector = Vector( ( self._x, self._y, self._z ) )

class UV(object):
    def __init__(self):
        self._u = 0.0
        self._v = 0.0
        self._vector = Vector()

    def read(self, f, mode = SIGNAL_MODE_CHAR_2):
        if mode == SIGNAL_MODE_CHAR_2:
            fmt = '2b'
            div = 128.0 # Max Char
        elif mode == SIGNAL_MODE_SHORT_2:
            fmt = '2h'
            div = 32768.0 # Max Short
        else: # UNKNOWN!
            fmt = '2b'
            div = 128.0
        
        [ self._u, self._v ] = unpack(fmt, f)

        # Process them into floats
        self._u = float(self._u) / div
        self._v = float(self._v) / div

        self._vector = Vector( ( self._u, self._v, 0.0 ) )

# This is a hack class
class SkipVertex(object):
    def __init__(self):
        self._byte_1 = 0
        self._byte_2 = 0

        self._skip = False
    
    def read(self, f):
        [ self._byte_1, self._byte_2 ] = unpack('2B', f)

        self._skip = bool(( self._byte_2 >> 7 ))

class Signal(object):
    def __init__(self):
        self._index = 0
        self._constant = 0
        self._data_count = 0
        self._mode = 0

        self._signature = 0x0
    
    def read(self, f):
        # Read in the signature, and then reverse, so we can get individual components
        self._signature = unpack('i', f)[0]
        f.seek(-4, 1)

        self._index = unpack('B', f)[0]
        self._constant = unpack('B', f)[0]
        self._data_count = unpack('B', f)[0]
        self._mode = unpack('B', f)[0]

    def get_mode_string(self):
        if self.is_header():
            return "Header"
        elif self.is_vertex():
            return "Vertex"
        elif self.is_uv():
            return "UV"
        elif self.is_skip_vertex():
            return "Skip Vertex"
        return "Unknown"

    def is_header(self):
        return self._mode in [SIGNAL_MODE_HEADER]

    def is_vertex(self):
        return self._mode in [SIGNAL_MODE_CHAR_3, SIGNAL_MODE_SHORT_3]
    
    def is_uv(self):
        return self._mode in [SIGNAL_MODE_CHAR_2, SIGNAL_MODE_SHORT_2]

    def is_skip_vertex(self):
        return self._mode in [SIGNAL_MODE_INT_4]

# Good reference: https://github.com/ps2dev/ps2sdk/blob/8b7579979db87ace4b0aa5693a8a560d15224a96/common/include/vif_codes.h
class VUCommand(object):
    def __init__(self):
        self._command = 0

    def read(self, f):
        f.seek(3, 1)
        self._command = unpack('B', f)[0]

    def get_command_string(self):
        if self._command == 0x14:
            return "MSCAL (0x14)"
        elif self._command == 0x17:
            return "MSCNT (0x17)"
        return "Unknown %d" % self._command
