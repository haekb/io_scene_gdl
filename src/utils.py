'''
Determine the amount of alignment that's needed
'''
def alignment_required(to, f):
    align = f.tell() % to
    if (align == 0):
        return align
    return to - align

'''
Align our file pointer by `to` bytes
'''
def align(to, f):
    align = alignment_required(to, f)

    if align == 0:
        return
    
    f.seek(align, 1)