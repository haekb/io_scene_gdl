from .model import Model
import bpy
import bmesh
from enum import Enum

class ObjectFlag(Enum):
    ALPHA = 1
    VNORMS = 2
    VCOLORS = 4
    MESH = 8
    TEX2 = 16
    LMAP = 32
    SHARP = 64
    BLUR = 128
    CHROME = 256
    ERROR = 512
    SORTA = 1024
    SORT =  2048
    # ?
    FMT_BASIC = 0
    FMT_MASK = 61440
    # ?
    LIT_MASK = 983040
    # Lighting settings
    NON_LIT = 0
    PRE_LIT = 65536
    LMAP_LIT = 131072
    NORM_LIT = 196608
    DYN_LIGHT = 1048576
    END = 1048577

    # TODO: Can this be done better?
    # Returns a list of flags
    @staticmethod
    def get_flag_strings(value):
        to_string_dict = {
            ObjectFlag.ALPHA.value: "Alpha",
            ObjectFlag.VNORMS.value: "Vertex Normals",
            ObjectFlag.VCOLORS.value: "Vertex Colours",
            ObjectFlag.MESH.value: "Mesh",
            ObjectFlag.TEX2.value: "Tex2", # Second set of UVs?
            ObjectFlag.LMAP.value: "LMap", # Light map?
            ObjectFlag.SHARP.value: "Sharp",
            ObjectFlag.BLUR.value: "Blur",
            ObjectFlag.CHROME.value: "Chrome",
            ObjectFlag.ERROR.value: "Error",
            ObjectFlag.SORTA.value: "Sort A", # Alpha?
            ObjectFlag.SORT.value: "Sort",
            ObjectFlag.FMT_BASIC.value: "Format Basic", #?
            ObjectFlag.FMT_MASK.value: "Format Mask", #?
            ObjectFlag.LIT_MASK.value: "Lit Mask", #?
            ObjectFlag.NON_LIT.value: "Non Lit",
            ObjectFlag.PRE_LIT.value: "Pre Lit",
            ObjectFlag.LMAP_LIT.value: "LMap Lit",
            ObjectFlag.NORM_LIT.value: "Normal Lit",
            ObjectFlag.DYN_LIGHT.value: "Dynamic Lit",
            ObjectFlag.END.value: "End"
        }
        flags = []
        for flag, string in to_string_dict.items():
            if (flag & value):
                flags.append(string)

        return flags

# End Enum

class ObjectReader(object):
    def __init__(self):
        self._log = False
        pass

    def read(self, path, options):
        # Set options
        self._log = options._should_log

        model = Model(options)
        with open(path, 'rb') as f:
            model.read(f)
            self.import_mesh(model)
            

        return model

    def import_mesh(self, model):
        
        # This seems to be the rage these days
        Context = bpy.context
        Data = bpy.data
        Ops = bpy.ops
        
        collection = Data.collections.new("Objects.ps2")
        # Add our collection to the scene
        Context.scene.collection.children.link(collection)

        material = Data.materials.new("test")

        ''' Populate the actual mesh data. '''
        for i in range(model._object_count):
            object_def = model._object_defs[i]

            if self._log:
                print("Setting up object: %s" % object_def._name)
                print("Object flags: ",flags)

            flags = ObjectFlag.get_flag_strings(model._objects[i]._flags)

            ''' Create the object and mesh. '''
            mesh_name = object_def._name

            mesh = Data.meshes.new(mesh_name)

            mesh_object = Data.objects.new(mesh_name, mesh)

            ''' Add materials to mesh. '''
            #for material in materials:
            ''' Create UV map. '''
            '''
            uv_texture = mesh.uv_textures.new()
            mesh.materials.append(material)
            material.texture_slots[0].uv_layer = uv_texture.name
            '''
            uv_texture = mesh.uv_layers.new()
            mesh.materials.append(material)

            bm = bmesh.new()
            bm.from_mesh(mesh)

            vertex_list = []

            # Loop through our vertex data, scale if needed, and generate some vertices!
            for vertex in model._vertices[i]:
                new_vertex = vertex._vector

                vert_tuple = ()
                    
                # Scale the model down
                for vert in new_vertex:
                    # If we've got a bound radius(?), normalize it!
                    # Otherwise the object will be huge (or small)!
                    if object_def._bnd_rad != 0.0:
                        vert *= (1.0/object_def._bnd_rad)
                    vert_tuple += (vert,)

                # If we want to swap up to z!
                #vert_tuple = (new_vertex.x, new_vertex.z, new_vertex.y)
                
                vertex_list.append(bm.verts.new(vert_tuple))
            # End For

            # Generate some faces!
            faces = self.generate_faces(vertex_list, model._skip_vertices[i])

            # Sanity check
            if self._log:
                print("Generated face count: ", len(faces))
                if len(faces) != model._objects[i]._triangle_count:
                    print("WARNING: Face count was expected to be ", model._objects[i]._triangle_count, "!!!")

            for vertex_list in faces:
                try:
                    bmface = bm.faces.new(vertex_list)
                except ValueError:
                    '''
                    This face is a duplicate of another face, which is disallowed by Blender.
                    Mark this face for deletion after iteration.
                    '''
                    if self._log:
                        print("Dupe found!")
                    #duplicate_face_indices.append(face_index)
                    continue
                '''
                Assign the material index of face based on the piece's material index.
                '''
                bmface.material_index = 0
                bmface.smooth = True
            # End For

            bm.faces.ensure_lookup_table()

            bm.to_mesh(mesh)

            uv_texture = mesh.uv_layers[0]

            mesh.validate(clean_customdata=False)
            mesh.update(calc_edges=True)

            # add it to our collection c:
            collection.objects.link(mesh_object)

            # Hide by default
            mesh_object.hide_set(1)
        # End For
    # End Def

    def generate_faces(self, vert_list, flip_face_list):
        flip = True
        
        face_list = []

        p1 = 0
        p2 = 1

        for p3 in range(2, len(vert_list)):
            if flip_face_list[p3]._skip == False:
                verts = []

                if flip:
                    verts.append( vert_list[p1] )
                    verts.append( vert_list[p3] )
                    verts.append( vert_list[p2] )
                else:
                    verts.append( vert_list[p1] )
                    verts.append( vert_list[p2] )
                    verts.append( vert_list[p3] )
                    
                flip = not flip
                face_list.append(verts)

            p1 = p2
            p2 = p3
        
        return face_list
    # End