import struct
# From io_scene_lithtech

'''
Utility functions for reading from the file.

fmt reference:
https://docs.python.org/3/library/struct.html#format-characters

'''
def unpack(fmt, f):
    return struct.unpack(fmt, f.read(struct.calcsize(fmt)))


def pack(fmt, f, values):
    f.write(struct.pack(fmt, values))

# Reads null terminated string
# Returns string
def read_string(f):
    return ''.join(iter(lambda: f.read(1).decode('ascii'), '\x00'))
    # chars = []
    # while True:
    #     c = f.read(1)
    #     if c == b'\x00':#chr(0):
    #         return "".join(chars)
    #     chars.append(c)
    