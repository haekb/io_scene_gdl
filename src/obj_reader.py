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

            # Ok it got a little confusing, but our vertices are stored in groups
            # So loop through those groups, and those vertices, 
            # create them on our mesh, and add them to a new grouped list for face generation!
            for vertex_group in model._vertices[i]:
                new_vertex_group = []
                for vertex in vertex_group:
                    new_vertex = vertex._vector
                    
                    vert_tuple = ()
                        
                    # Scale the model down
                    for vert in new_vertex:
                        # If we've got a bound radius(?), normalize it!
                        # Otherwise the object will be huge (or small)!
                        if object_def._bnd_rad != 0.0:
                            vert *= (1.0/object_def._bnd_rad)
                        vert_tuple += (vert,)
                    
                    new_vertex_group.append(bm.verts.new(vert_tuple))
                vertex_list.append(new_vertex_group)
            # End For

            # Determine face generation via groups
            faces = []
            for vertex_group in vertex_list:
                faces += self.generate_faces(vertex_group)
            

            for vertex_list in faces:
                # Uncomment to skip face generation
                #continue
                # ---------------------------------

                #print("Verts", vertex_list)
                #face = [bm.verts[vertex_offset + vertex.vertex_index] for vertex in face.vertices]

                try:
                    bmface = bm.faces.new(vertex_list)
                except ValueError:
                    '''
                    This face is a duplicate of another face, which is disallowed by Blender.
                    Mark this face for deletion after iteration.
                    '''
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

            glob_uv_index = 0

            uv_texture = mesh.uv_layers[0]

            mesh.validate(clean_customdata=False)
            mesh.update(calc_edges=True)

            # add it to our collection c:
            collection.objects.link(mesh_object)

            # Hide by default
            mesh_object.hide_set(1)
        # End For
    # End Def

    def generate_faces(self, vert_list):
        flip = False
        
        face_list = []
        
        for i in range( len(vert_list) ):
            if i < 2:
                continue
            
            verts = []

            if flip:
                verts.append( vert_list[i - 2] )
                verts.append( vert_list[i    ] )
                verts.append( vert_list[i - 1] )
            else:
                verts.append( vert_list[i - 2] )
                verts.append( vert_list[i - 1] )
                verts.append( vert_list[i    ] )

            flip = not flip
            face_list.append(verts)

        
        return face_list
    # End
