# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.), Ted Milker
#
# SPDX-License-Identifier: GPL-2.0-or-later


import bpy

from ..__init__ import get_addon_prefs
from ..utils.str_utils import word_wrap
from ..utils.node_utils import (
    create_new_nodegroup,
    set_socket_defvalue,
    get_all_nodes,
)


# ooooo      ooo                 .o8            
# `888b.     `8'                "888            
#  8 `88b.    8   .ooooo.   .oooo888   .ooooo.  
#  8   `88b.  8  d88' `88b d88' `888  d88' `88b 
#  8     `88b.8  888   888 888   888  888ooo888 
#  8       `888  888   888 888   888  888    .o 
# o8o        `8  `Y8bod8P' `Y8bod88P" `Y8bod8P' 

class Base():

    bl_idname = "NodeBoosterLightInfo"
    bl_label = "Light Info"
    bl_description = """Custom Nodegroup: Gather informations about any lights.
    • Expect updates on each depsgraph post and frame_pre update signals"""
    auto_update = {'FRAME_PRE','DEPS_POST',}
    tree_type = "*ChildrenDefined*"

    def update_signal(self,context):
        self.sync_out_values()
        return None 

    light_type : bpy.props.EnumProperty(
        name="Light Type",
        default='ANY',
        items=[
            ('ANY',   "Any Lights"        ,"", 'LIGHT',       0,),
            ('POINT', "Point Types Only"  ,"", 'LIGHT_POINT', 1,),
            ('SUN',   "Sun Types Only"    ,"", 'LIGHT_SUN',   2,),
            ('SPOT',  "Spot Types Only"   ,"", 'LIGHT_SPOT',  3,),
            ('AREA',  "Area Types Only"   ,"", 'LIGHT_AREA',  4,),
            ],
        update=update_signal,
        )

    def light_obj_poll(self, obj):
        if (self.light_type=='ANY'):
            return obj.type == 'LIGHT'
        return obj.type == 'LIGHT' and obj.data.type == self.light_type

    light_obj: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=light_obj_poll,
        update=update_signal,
        )

    @classmethod
    def poll(cls, context):
        """mandatory poll"""
        return True

    def init(self, context):
        """this fct run when appending the node for the first time"""

        name = f".{self.bl_idname}"

        match self.tree_type:
            case "GeometryNodeTree":
                sockets = {
                    "Object":       "NodeSocketObject", #{'POINT','SUN','SPOT','AREA',},
                    "Type":         "NodeSocketString", #{'POINT','SUN','SPOT','AREA',},
                    "Color":        "NodeSocketColor", #{'POINT','SUN','SPOT','AREA',},
                    "Power":        "NodeSocketFloat", #{'POINT','SUN','SPOT','AREA',},
                    "Shape":        "NodeSocketString", #{'AREA',},
                    "Size X":       "NodeSocketFloat", #{'AREA',},
                    "Size Y":       "NodeSocketFloat", #{'AREA',},
                    "Spread":       "NodeSocketFloat", #{'AREA',},
                    "Soft Falloff": "NodeSocketBool", #{'SPOT','POINT'},
                    "Radius":       "NodeSocketFloat", #{'SPOT','POINT'},
                    "Angle":        "NodeSocketFloat", #{'SUN',},
                    "Size":         "NodeSocketFloat", #{'SPOT',},
                    "Blend":        "NodeSocketFloat", #{'SPOT',},
                    "Show Cone":    "NodeSocketBool", #{'SPOT',},
                    }

            case "ShaderNodeTree" | "CompositorNodeTree":
                sockets = {
                    "Location":     "NodeSocketVector", #object transforms instead.
                    "Rotation":     "NodeSocketVector", #object transforms instead.
                    "Scale":        "NodeSocketVector", #object transforms instead.
                    "Type":         "NodeSocketInt", #int instead
                    "Color":        "NodeSocketColor",
                    "Power":        "NodeSocketFloat",
                    "Shape":        "NodeSocketInt", #int instead
                    "Size X":       "NodeSocketFloat",
                    "Size Y":       "NodeSocketFloat",
                    "Spread":       "NodeSocketFloat",
                    "Soft Falloff": "NodeSocketBool",
                    "Radius":       "NodeSocketFloat",
                    "Angle":        "NodeSocketFloat",
                    "Size":         "NodeSocketFloat",
                    "Blend":        "NodeSocketFloat",
                    "Show Cone":    "NodeSocketBool",
                    }

        ng = bpy.data.node_groups.get(name)
        if (ng is None):
            ng = create_new_nodegroup(name,
                tree_type=self.tree_type,
                out_sockets=sockets,
                )

        ng = ng.copy() #always using a copy of the original ng

        self.node_tree = ng
        self.label = self.bl_label

        return None

    def copy(self, node):
        """fct run when dupplicating the node"""

        self.node_tree = node.node_tree.copy()

        return None

    def update(self):
        """generic update function"""

        return None

    def sync_out_values(self):
        """sync output socket values with data"""

        ng = self.node_tree
        lo = self.light_obj
        ld = lo.data if lo and (lo.type=='LIGHT') else None
        is_geonode = (self.tree_type=='GeometryNodeTree')
        valid = (lo and ld)

        #different behavior and sockets depending on editor type and light type

        if (not valid):
            ltype = "" if is_geonode else 0
            if (not is_geonode):
                  set_socket_defvalue(ng, socket_name="Location", value=(0,0,0))
                  set_socket_defvalue(ng, socket_name="Rotation", value=(0,0,0))
                  set_socket_defvalue(ng, socket_name="Scale", value=(0,0,0))
            else: set_socket_defvalue(ng, socket_name="Object", value=None)
            set_socket_defvalue(ng, socket_name="Type", value=ltype)
            set_socket_defvalue(ng, socket_name="Color", value=[0.0, 0.0, 0.0, 0.0])
            set_socket_defvalue(ng, socket_name="Power", value=0.0)
            self.outputs["Shape"].enabled = False
            self.outputs["Size X"].enabled = False
            self.outputs["Size Y"].enabled = False
            self.outputs["Spread"].enabled = False
            self.outputs["Soft Falloff"].enabled = False
            self.outputs["Radius"].enabled = False
            self.outputs["Angle"].enabled = False
            self.outputs["Size"].enabled = False
            self.outputs["Blend"].enabled = False
            self.outputs["Show Cone"].enabled = False
            return None

        if (ld.type not in {'POINT','SUN','SPOT','AREA',}):
            raise Exception(f'Was not expecting a light of type "{ld.type}"')

        #These are always on and shared across all
        ltype = ld.type  if is_geonode else 0 if (ld.type=='POINT')   else 1 if (ld.type=='SUN')        else 2 if (ld.type=='SPOT')  else 3
        if (not is_geonode):
              set_socket_defvalue(ng, socket_name="Location", value=lo.location)
              set_socket_defvalue(ng, socket_name="Rotation", value=lo.rotation_euler)
              set_socket_defvalue(ng, socket_name="Scale", value=lo.scale)
        else: set_socket_defvalue(ng, socket_name="Object", value=lo)
        set_socket_defvalue(ng, socket_name="Type", value=ltype)
        set_socket_defvalue(ng, socket_name="Color", value=[ld.color[0], ld.color[1], ld.color[2], 1.0])
        set_socket_defvalue(ng, socket_name="Power", value=ld.energy)

        #below depends on lught type
        match ld.type:
            case 'POINT':
                self.outputs["Shape"].enabled = False
                self.outputs["Size X"].enabled = False
                self.outputs["Size Y"].enabled = False
                self.outputs["Spread"].enabled = False
                set_socket_defvalue(ng, socket_name="Soft Falloff", value=ld.use_soft_falloff)
                set_socket_defvalue(ng, socket_name="Radius", value=ld.shadow_soft_size)
                self.outputs["Angle"].enabled = False
                self.outputs["Size"].enabled = False
                self.outputs["Blend"].enabled = False
                self.outputs["Show Cone"].enabled = False

            case 'SUN':
                self.outputs["Shape"].enabled = False
                self.outputs["Size X"].enabled = False
                self.outputs["Size Y"].enabled = False
                self.outputs["Spread"].enabled = False
                self.outputs["Soft Falloff"].enabled = False
                self.outputs["Radius"].enabled = False
                set_socket_defvalue(ng, socket_name="Angle", value=ld.angle)
                self.outputs["Size"].enabled = False
                self.outputs["Blend"].enabled = False
                self.outputs["Show Cone"].enabled = False

            case 'SPOT':
                self.outputs["Shape"].enabled = False
                self.outputs["Size X"].enabled = False
                self.outputs["Size Y"].enabled = False
                self.outputs["Spread"].enabled = False
                set_socket_defvalue(ng, socket_name="Soft Falloff", value=ld.use_soft_falloff)
                set_socket_defvalue(ng, socket_name="Radius", value=ld.shadow_soft_size)
                self.outputs["Angle"].enabled = False
                self.outputs["Size"].enabled = False
                self.outputs["Blend"].enabled = False
                self.outputs["Show Cone"].enabled = False

            case 'AREA':
                lshape = ld.shape if is_geonode else 0 if (ld.shape=='SQUARE') else 1 if (ld.shape=='RECTANGLE') else 2 if (ld.shape=='DISK') else 3
                set_socket_defvalue(ng, socket_name="Shape", value=lshape)
                set_socket_defvalue(ng, socket_name="Size X", value=ld.size)
                set_socket_defvalue(ng, socket_name="Size Y", value=ld.size_y)
                set_socket_defvalue(ng, socket_name="Spread", value=ld.spread)
                self.outputs["Soft Falloff"].enabled = False
                self.outputs["Radius"].enabled = False
                self.outputs["Angle"].enabled = False
                self.outputs["Size"].enabled = False
                self.outputs["Blend"].enabled = False
                self.outputs["Show Cone"].enabled = False

        return None

    def draw_label(self,):
        """node label"""

        return self.bl_label

    def draw_buttons(self, context, layout):
        """node interface drawing"""

        row = layout.row(align=True)
        
        sub = row.row(align=True)
        ptr = sub.row(align=True)
        if (self.light_type!='ANY' and self.light_obj):
            ptr.alert = self.light_obj.data.type!=self.light_type
        ptr.prop(self, "light_obj", text="", 
            icon='LIGHT' if (self.light_obj is None) else f"LIGHT_{self.light_obj.data.type}" if self.light_obj.data else 'ERROR'
            )
        sub.prop(self, "light_type", text="", icon_only=True,)

        return None

    def draw_panel(self, layout, context):
        """draw in the nodebooster N panel 'Active Node'"""

        n = self

        header, panel = layout.panel("params_panelid", default_closed=False,)
        header.label(text="Parameters",)
        if (panel):

            row = panel.row(align=True)
            sub = row.row(align=True)
            sub.prop(n, "light_obj", text="",)
            sub.prop(n, "light_type", text="", icon_only=True,)

        header, panel = layout.panel("doc_panelid", default_closed=True,)
        header.label(text="Documentation",)
        if (panel):
            word_wrap(layout=panel, alert=False, active=True, max_char='auto',
                char_auto_sidepadding=0.9, context=context, string=n.bl_description,
                )
            panel.operator("wm.url_open", text="Documentation",).url = "https://blenderartists.org/t/nodebooster-new-nodes-and-functionalities-for-node-wizards-for-free"

        header, panel = layout.panel("dev_panelid", default_closed=True,)
        header.label(text="Development",)
        if (panel):
            panel.active = False

            col = panel.column(align=True)
            col.label(text="NodeTree:")
            col.template_ID(n, "node_tree")
        
        return None

    @classmethod
    def update_all(cls, using_nodes=None, signal_from_handlers=False,):
        """search for all node instances of this type and refresh them. Will be called automatically if .auto_update's are defined"""

        if (using_nodes is None):
              nodes = get_all_nodes(exactmatch_idnames={cls.bl_idname},)
        else: nodes = [n for n in using_nodes if (n.bl_idname==cls.bl_idname)]

        for n in nodes: 
            n.sync_out_values()

        return None

#Per Node-Editor Children:
#Respect _NG_ + _GN_/_SH_/_CP_ nomenclature

class NODEBOOSTER_NG_GN_LightInfo(Base, bpy.types.GeometryNodeCustomGroup):
    tree_type = "GeometryNodeTree"
    bl_idname = "GeometryNode" + Base.bl_idname

class NODEBOOSTER_NG_SH_LightInfo(Base, bpy.types.ShaderNodeCustomGroup):
    tree_type = "ShaderNodeTree"
    bl_idname = "ShaderNode" + Base.bl_idname

class NODEBOOSTER_NG_CP_LightInfo(Base, bpy.types.CompositorNodeCustomGroup):
    tree_type = "CompositorNodeTree"
    bl_idname = "CompositorNode" + Base.bl_idname
