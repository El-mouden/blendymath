bl_info = {
    "name": "math mesh curves",
    "author": "Abdessamad Elmouden",
    "version": (1, 0),
    "blender": (2, 90, 0),
    "location": "View3D > Add > Mesh > Math Curve",
    "description": "Creats math curve f(x) or parametric equation x(t),y(t),z(t)",
    "warning": "change the equation at the creation",
    "doc_url": "",
    "category": "Add Mesh",
}

import bpy
import bmesh
from math  import *
from bpy_extras.object_utils import AddObjectHelper

from bpy.props import *



def vertices(eq,a, b, n):

    h=(b-a)/(n-1)
    verts=[]
    
    
    for i in range(int(n)):
        x=a+i*h
        y=eval(eq)
        verts.append((x,y,0))
        
    return verts


def verticesP(Xt,Yt,Zt,includZ,a, b, n):

    h=(b-a)/(n-1)
    verts=[]
    
    if not includZ:
        for i in range(int(n)):
            t=a+i*h
            x=eval(Xt)
            y=eval(Yt)
            verts.append((x,y,0))
    else:
        for i in range(int(n)):
            t=a+i*h
            x=eval(Xt)
            y=eval(Yt)
            z=eval(Zt)
            verts.append((x,y,z))
            
    return verts


def convert(a=True,bevel=False,epp=.1, seg=6):
    bpy.ops.object.convert(target='CURVE', keep_original=a)
    if bevel :
        bpy.context.object.data.bevel_depth = epp
        bpy.context.object.data.bevel_resolution = seg/2



class MathCurve(bpy.types.Operator):
    """Add y=f(x) or a parametric Mesh curve"""
    
    bl_idname = "mesh.primitive_math_curve"
    bl_label = "Math curve"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    par:BoolProperty(
        name="parametric?",
        description="if false: y=f(x) or"
         +"true: set of points (x(t),y(t))",
        default=False,
    )

    Xof_t:StringProperty(
        name="x(t)=",
        description="equation (x(t),y(t))",
        default='cos(t)',
    )        
    Yof_t:StringProperty(
        name="y(t)=",
        description="equation (x(t),y(t))",
        default='sin(t)',
    )
    Zof_t:StringProperty(
        name="z(t)=",
        description="",
        default='t/2',
    )
    equation:StringProperty(
        name="y(x)=",
        description="equation y=f(x)",
        default='cos(x)',
    )
    
    
    
    Convert:BoolProperty(
        name="Convert to Curve",
        description="Curve",
        default=False,
    )
    bevel: BoolProperty(
        name="make wire",
        description="bevel ",
        
        default=True,
    )
    epp: FloatProperty(
        name="radius",
        description="the radius ",
        min=0,
        default=0.1,
    )
    segm: IntProperty(
        name="resolusion",
        description="number of segments ",
        min=0,
        default=6,
    )
    
    
    
    a: FloatProperty(
        name="a",
        description="start at ",
        default=0,
    )
    b: FloatProperty(
        name="b",
        description="end at ",
        
        default=6.0,
    )
    n: IntProperty(
        name="n",
        description="number of vertices",
        min=2, 
        default=50,
    )
    layers: BoolVectorProperty(
        name="Layers",
        description="Object Layers",
        size=20,
        options={'HIDDEN', 'SKIP_SAVE'},
    )
    z:BoolProperty(
        name="also z?",
        description="if disabled the curve will be in the plan x,y",
        default=False,
    )

    # generic transform props
    align_items = (
        ('WORLD', "World", "Align the new object to the world"),
        ('VIEW', "View", "Align the new object to the view"),
        ('CURSOR', "3D Cursor", "Use the 3D cursor orientation for the new object")
    )
    align: EnumProperty(
        name="Align",
        items=align_items,
        default='WORLD',
        update=AddObjectHelper.align_update_callback,
    )
    location: FloatVectorProperty(
        name="Location",
        subtype='TRANSLATION',
        
    )
    rotation: FloatVectorProperty(
        name="Rotation",
        subtype='EULER',
    )

    #_____________________________________________________________________________

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.prop(self, 'Convert')
        box.prop(self, 'par')
        
        
        box = layout.box()
        if not self.par:
            box.prop(self, 'equation')
        else:
            box.prop(self, 'z')
            box.prop(self, 'Xof_t')
            box.prop(self, 'Yof_t')
            if self.z :
                box.prop(self, 'Zof_t')
        
        box = layout.box()
        box.prop(self, 'a')
        box.prop(self, 'b')
        box.prop(self, 'n')


        if self.Convert:
            box = layout.box()
            
            box.prop(self, 'bevel')
            
            if self.bevel:
                box.prop(self, 'epp')
                box.prop(self, 'segm')

                


        box = layout.box()
        box.prop(self, 'align')
        box.prop(self, 'location')
        box.prop(self, 'rotation')
    
    def execute(self, context):
        
        if self.par :
            verts_loc = verticesP(
                self.Xof_t,
                self.Yof_t,
                self.Zof_t,
                self.z,
                self.a,
                self.b,
                self.n,
            )
        else:
            verts_loc = vertices(self.equation,
                self.a,
                self.b,
                self.n,
            )
            

        mesh = bpy.data.meshes.new("M_Curve")

        bm = bmesh.new()

        for v_co in verts_loc:
            bm.verts.new(v_co)

        bm.verts.ensure_lookup_table()
        
        for i in range(self.n-1):
            bm.edges.new([bm.verts[i] ,bm.verts[i+1]])

        bm.to_mesh(mesh)
        mesh.update()

        # add the mesh as an object into the scene with this utility module
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=self)
        if self.Convert:
            convert(self.Convert,self.bevel,self.epp, self.segm)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(MathCurve.bl_idname, icon='MOD_SCREW')


def register():
    bpy.utils.register_class(MathCurve)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(MathCurve)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()

