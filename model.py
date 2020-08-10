from .io import unpack

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

        # End Header

        # Array of ObjectDef()
        self._object_defs = []

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
        self._object_def_count = unpack('I', f)[0]
        self._texture_def_count = unpack('I', f)[0]
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

    # End Def
# End Class

class ObjectDef(object):
    def __init__(self):
        self._name = ""
        self._bndrad = 0.0
        self._index = 0
        self._frame_count = 0

    def read(self, f):
        self._name = f.read(16).decode('ascii')
        self._bndrad = unpack('f', f)[0]
        self._index = unpack('H', f)[0]
        self._frame_count = unpack('H', f)[0]

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