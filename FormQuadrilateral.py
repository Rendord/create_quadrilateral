bl_info = {
    "name": "Form Quadrilateral",
    "blender": (2, 80, 0),
    "category": "Mesh",
    "author": "Abraham Oosterhuis",
    "version": (1, 0, 1),
}

import bpy
from bpy.types import Operator, Panel

class FormQuadrilateralOperator(Operator):
    bl_idname = "mesh.form_quadrilateral"
    bl_label = "Form Quadrilateral"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Start of Form Quadrilateral Operator")
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Check if there are 2 edges selected
        shared_vert, vert1, vert2 = self.check_selected_edges(context)
        if shared_vert is None:
            print("Exiting Form Quadrilateral Operator")
            return {'CANCELLED'}

        print("Selected Edges Check Passed")

        # Get original pivot point and cursor position
        original_pivot_point = context.scene.tool_settings.transform_pivot_point
        original_cursor_location = context.scene.cursor.location.copy()

        print("Original Pivot Point:", original_pivot_point)
        print("Original Cursor Location:", original_cursor_location)

        # Set pivot point to 3D cursor and move cursor to the middle of the selected vertices
        context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        # Place the cursor inbetween the 2 vertices that are in the middle of the quadrilateral
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        context.active_object.data.vertices[vert1].select = True
        context.active_object.data.vertices[vert2].select = True      
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.view3d.snap_cursor_to_selected()

        print("Set Pivot Point to Cursor")
        
        # Select the shared vertex and duplicate it
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        context.active_object.data.vertices[shared_vert].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        
        bpy.ops.mesh.duplicate()

        print("Duplicated Vertex")

        #we need to override the context of our operator    
        override = self.get_override(context, 'VIEW_3D', 'WINDOW')
        # Mirror the duplicate on x, y, and z axes
        
        bpy.ops.transform.mirror(orient_type='GLOBAL', constraint_axis=(True, True, True))
        
        #save mirrored vertex for future reference
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        selected_verts = [vert for vert in context.edit_object.data.vertices if vert.select]
        duplicate_vert = selected_verts[0].index
        
        print(context.active_object.data.vertices[duplicate_vert].co)    

        print("Mirrored Duplicate")

        bpy.ops.mesh.select_mode(type="VERT")  
        # Add edges from the new vertex to the unique vertices
        bpy.ops.object.mode_set(mode='OBJECT')
        context.active_object.data.vertices[vert1].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        context.active_object.data.vertices[duplicate_vert].select = True
        context.active_object.data.vertices[vert2].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.select_all(action='DESELECT')

        print("Added Edges")

        # Restore pivot point and cursor position
        context.scene.tool_settings.transform_pivot_point = original_pivot_point
        context.scene.cursor.location = original_cursor_location

        print("Restored Pivot Point and Cursor")

        print("End of Form Quadrilateral Operator")
        return {'FINISHED'}

    def check_selected_edges(self, context):
        # Get selected edges
        selected_edges = [edge for edge in context.edit_object.data.edges if edge.select]

        if len(selected_edges) != 2:
            self.report({'ERROR'}, "Please select exactly 2 edges.")
            return None, None, None

        # Check if there are 3 unique vertices
        selected_verts = set()
        shared_vert = None

        for edge in selected_edges:
            for vert_index in edge.vertices:
                if vert_index in selected_verts:
                    shared_vert = vert_index
                else:
                    selected_verts.add(vert_index)

        if len(selected_verts) != 3 or shared_vert is None:
            self.report({'ERROR'}, "Selected edges do not share a common vertex or have more than 3 unique vertices.")
            return None, None, None

        return shared_vert, list(selected_verts - {shared_vert})[0], list(selected_verts - {shared_vert})[1]

    def get_override(self, context, area_type, region_type):
        for area in context.screen.areas: 
            if area.type == area_type:             
                for region in area.regions:                 
                    if region.type == region_type:                    
                        override = {'area': area, 'region': region} 
                        return override
        #error message if the area or region wasn't found
        raise RuntimeError("Wasn't able to find", region_type," in area ", area_type,
                            "\n Make sure it's open while executing script.")

class FormQuadrilateralPanel(Panel):
    bl_label = "Form Quadrilateral"
    bl_idname = "PT_FormQuadrilateralPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("mesh.form_quadrilateral", text="Form Quadrilateral")

classes = [FormQuadrilateralOperator, FormQuadrilateralPanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
