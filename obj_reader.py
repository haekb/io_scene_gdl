from .model import Model
import bpy
import bmesh

class ObjectReader(object):
    def __init__(self):
        pass

    def read(self, path):
        model = Model()
        with open(path, 'rb') as f:
            model.read(f)
            self.importMesh(model)
            

        return model

    def importMesh(self, model):
        
        # This seems to be the rage these days
        Context = bpy.context
        Data = bpy.data
        Ops = bpy.ops

        collection = Data.collections.new("vert test")
        # Add our collection to the scene
        Context.scene.collection.children.link(collection)

        material = Data.materials.new("test")

        ''' Create the object and mesh. '''
        mesh_name = "test"

        mesh = Data.meshes.new("test")

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
        # material.uv_layers[0].name = uv_texture.name

        # TODO: these need to be reset for each mesh
        vertex_offset = 0
        face_offset = 0

        ''' Populate the actual mesh data. '''
        bm = bmesh.new()
        bm.from_mesh(mesh)

        for vertex in model._vertices:#unique_vert_list:
    
            new_vertex = vertex._vector
            
            vert_tuple = ()
                
            # Scale the model down
            for vert in new_vertex:
                #vert *= 0.01
                vert_tuple += (vert,)
                
            #print(vert_tuple)
            
            new_vertex = vert_tuple#tuple([i * 0.01 for i in vertex])
            bm.verts.new(new_vertex)
    

        bm.faces.ensure_lookup_table()

        bm.to_mesh(mesh)

        glob_uv_index = 0

        uv_texture = mesh.uv_layers[0]

        mesh.validate(clean_customdata=False)
        mesh.update(calc_edges=True)

        # add it to our collection c:
        collection.objects.link(mesh_object)

