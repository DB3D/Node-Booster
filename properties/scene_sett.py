# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
#
# SPDX-License-Identifier: GPL-2.0-or-later


import bpy

from ..operators.search import search_upd
from ..operators.palette import palette_active_upd


class NODEBOOSTER_PR_scene_favorites_data(bpy.types.PropertyGroup):
    """favorites_data = bpy.context.scene.nodebooster.favorites_data"""

    name : bpy.props.StringProperty(
        )
    nodetree_reference : bpy.props.PointerProperty(
        type=bpy.types.NodeTree,
        )
    material_reference : bpy.props.PointerProperty(
        type=bpy.types.Material, #NOTE we need this in case user place a favorite to a material.node_tree, material.node_tree are special for some reasons.. can't put them in a Pointer.. 
        )
    active : bpy.props.BoolProperty(
        default=False, #TODO replace index system with active system
        description="Informal read-only property to track the current active favorite",
        )

    def get_ng(self):
        if (self.nodetree_reference):
            return self.nodetree_reference
        if (self.material_reference):
            return self.material_reference.node_tree
        return None

    def get_node(self):
        ng = self.get_ng()
        if (ng is None):
            return None
        return ng.nodes.get(self.name)

    def get_label(self):
        nd = self.get_node()
        if (nd is None):
            return 'Deleted?'
        return nd.label

class NODEBOOSTER_PR_scene(bpy.types.PropertyGroup): 
    """sett_scene = bpy.context.scene.nodebooster"""

    #frame tool
    frame_use_custom_color : bpy.props.BoolProperty(
        default=False,
        name="Frame Color")
    frame_color : bpy.props.FloatVectorProperty(
        default=(0,0,0),
        subtype="COLOR",
        name="Color",
        min=0,
        max=1,
        )
    frame_sync_color : bpy.props.BoolProperty(
        default=True,
        name="Sync Palette",
        description="Synchronize with palette",
        )
    frame_label : bpy.props.StringProperty(
        default=" ",
        name="Label",
        )
    frame_label_size : bpy.props.IntProperty(
        default=16,min=0,
        name="Label Size",
        )

    #palette tool
    palette_active : bpy.props.FloatVectorProperty(
        default=(0,0,0),
        subtype='COLOR',
        name="Color",
        min=0,
        max=1,
        update=palette_active_upd,
        )
    palette_assign_ptr: bpy.props.PointerProperty(
        type=bpy.types.Palette,
        name="Palette",
        )
    palette_old : bpy.props.FloatVectorProperty(
        default=(0,0,0),
        subtype='COLOR',
        name="Color",
        min=0,
        max=1,
        )
    palette_older : bpy.props.FloatVectorProperty(
        default=(0,0,0),
        subtype='COLOR',
        name="Color",
        min=0,
        max=1,
        )

    #search tool
    search_keywords : bpy.props.StringProperty(
        default=" ",
        name="Keywords",
        update=search_upd,
        )
    search_center : bpy.props.BoolProperty(
        default=True,
        name="Recenter View",
        update=search_upd,
        )
    search_labels : bpy.props.BoolProperty(
        default=True,
        name="Label",
        update=search_upd,
        )
    search_types : bpy.props.BoolProperty(
        default=True,
        name="Type",
        update=search_upd,
        )
    search_names : bpy.props.BoolProperty(
        default=False,
        name="Internal Name",
        update=search_upd,
        )
    search_socket_names : bpy.props.BoolProperty(
        default=False,
        name="Socket Names",
        update=search_upd,
        )
    search_socket_types : bpy.props.BoolProperty(
        default=False,
        name="Socket Types",
        update=search_upd,
        )
    search_input_only : bpy.props.BoolProperty(
        default=False,
        name="Input Nodes Only",
        update=search_upd,
        )
    search_frame_only : bpy.props.BoolProperty(
        default=False,
        name="Frame Only",
        update=search_upd,
        )
    search_found : bpy.props.IntProperty(
        default=0,
        )

    #favorite tool
    favorites_data : bpy.props.CollectionProperty(
        type=NODEBOOSTER_PR_scene_favorites_data,
        name="Favorites Data",
        )
    favorite_show_filter : bpy.props.EnumProperty(
        items=[
            ("GEOMETRY,SHADER,COMPOSITOR","All","All",'SORTALPHA',0),
            None,
            ("GEOMETRY","Geometry","Geometry",'GEOMETRY_NODES',1),
            ("SHADER","Shader","Shader",'NODE_MATERIAL',2),
            ("COMPOSITOR","Compositor","Compositor",'NODE_COMPOSITING',3),
            ],
        default="GEOMETRY,SHADER,COMPOSITOR",
        name="Show Filter",
        )
    
    #minimap
    minimap_show : bpy.props.BoolProperty(
        default=True,
        name="Show",
        )
    minimap_auto_tool_panel_collapse : bpy.props.BoolProperty(
        default=True,
        name="Auto Collapse",
        description="Automatically collapse the Tool panel when the minimap is enabled.",
        )
    minimap_auto_aspect_ratio : bpy.props.BoolProperty(
        default=True,
        name="Auto Aspect Ratio",
        description="Automatically adjust the aspect ratio of the minimap to fit all nodes. If disabled, use Size X/Y percentages directly.",
        )
    minimap_draw_type : bpy.props.EnumProperty(
        name="DrawType",
        description="Choose whenever this drawing is done on the background or on the foreground of the node editor space, either as an underlay or an overlay.",
        items=( ("UNDERLAY","Back",""), ("OVERLAY","Front",""),),
        default="OVERLAY",
        )
    # minimap_emplacement : bpy.props.EnumProperty(
    #     items=[("BOTTOM_LEFT","Bottom Left","Bottom Left"),("TOP_LEFT","Top Left","Top Left"),("TOP_RIGHT","Top Right","Top Right"),("BOTTOM_RIGHT","Bottom Right","Bottom Right")],
    #     name="Emplacement",
    #     )
    # minimap_width_pixels : bpy.props.IntVectorProperty(
    minimap_width_percentage : bpy.props.FloatVectorProperty(
        default=(0.25,0.50),
        name="Minimap Size",
        description="Set the max size of your minimap, in width/height percentage of the editor area. The ratio will automatically adjust itself to fit within these max percentages.",
        min=0.01,
        max=1,
        size=2,
        )
    minimap_fill_color : bpy.props.FloatVectorProperty(
        default=(0.120647, 0.120647, 0.120647, 0.990),
        subtype="COLOR",
        name="Fill Color",
        min=0,
        max=1,
        size=4,
        )
    minimap_outline_width : bpy.props.FloatProperty(
        default=1.5,
        name="Outline Width",
        min=0,
        soft_max=5,
        )
    minimap_outline_color : bpy.props.FloatVectorProperty(
        default=(0.180751, 0.180751, 0.180751, 0.891667),
        subtype="COLOR",
        name="Outline Color",
        min=0,
        max=1,
        size=4,
        )
    minimap_border_radius : bpy.props.FloatProperty(
        default=10,
        name="Border Radius",
        min=0,
        soft_max=50,
        )
    minimap_padding : bpy.props.IntVectorProperty(
        default=(14,19),
        name="Padding",
        min=0,
        size=2,
        soft_max=50,
        )
    #minimap node
    minimap_node_draw_typecolor : bpy.props.BoolProperty(
        default=True,
        name="Draw TypeColor",
        )
    minimap_node_draw_nodecustomcolor : bpy.props.BoolProperty(
        default=False,
        name="Draw Custom Color",
        )
    minimap_node_draw_selection : bpy.props.BoolProperty(
        default=True,
        name="Draw Selection",
        )
    minimap_node_outline_width : bpy.props.FloatProperty(
        default=1.5,
        name="Outline Width",
        min=0,
        )
    minimap_node_border_radius : bpy.props.FloatProperty(
        default=3,
        name="Border Radius",
        min=0,
        soft_max=20,
        )
    minimap_node_draw_header : bpy.props.BoolProperty(
        default=True,
        name="Draw Header",
        )
    minimap_node_draw_frames : bpy.props.BoolProperty(
        default=True,
        name="Draw Frames",
        )
    minimap_node_draw_framecustomcolor : bpy.props.BoolProperty(
        default=True,
        name="Draw Frame Custom Color",
        )
    minimap_node_draw_frames_detail : bpy.props.BoolProperty(
        default=False,
        name="Draw Frames within Frames",
        )
    minimap_node_header_height : bpy.props.FloatProperty(
        default=12,
        name="Header Height",
        min=0,
        )
    minimap_node_header_minheight : bpy.props.FloatProperty(
        default=6,
        name="Header Min Height when zoomed out",
        min=0,
        )
    minimap_node_body_color : bpy.props.FloatVectorProperty(
        default=(0.172937, 0.172937, 0.172937, 1.000000),
        subtype="COLOR",
        name="Body Color",
        min=0,
        max=1,
        size=4,
        )
    #view outline
    minimap_view_enable : bpy.props.BoolProperty(
        default=True,
        name="Enable",
        )
    minimap_view_fill_color : bpy.props.FloatVectorProperty(
        default=(0.296174, 0.040511, 0.027817, 0.0),
        subtype="COLOR",
        name="Fill Color",
        min=0,
        max=1,
        size=4,
        )
    minimap_view_outline_color : bpy.props.FloatVectorProperty(
        default=(1.0, 0.180751, 0.180751, 0.395833),
        subtype="COLOR",
        name="Outline Color",
        min=0,
        max=1,
        size=4,
        )
    minimap_view_outline_width : bpy.props.FloatProperty(
        default=4.0,
        name="Outline Width",
        min=0,
        )
    minimap_view_border_radius : bpy.props.FloatProperty(
        default=4,
        name="Border Radius",
        min=0,
        )
    #cursor
    minimap_cursor_show : bpy.props.BoolProperty(
        default=False,
        name="Show",
        )
    minimap_cursor_radius : bpy.props.FloatProperty(
        default=1.5,
        name="Radius",
        min=0.5,
        soft_max=25,
        )
    minimap_cursor_color : bpy.props.FloatVectorProperty(
        default=(1.0, 0.180751, 0.180751, 1.0),
        subtype="COLOR",
        name="Color",
        min=0,
        max=1,
        size=4,
        )
    #favorites
    minimap_fav_show : bpy.props.BoolProperty(
        default=True,
        name="Show",
        )
    minimap_fav_size : bpy.props.FloatProperty(
        default=20,
        name="Size",
        )
    #navigation shortcuts
    minimap_triple_click_dezoom : bpy.props.BoolProperty(
        default=True,
        name="Quick Dezoom",
        description="Quickly dezoom the node editor view to fit the integrity of the nodes by clicking 3 times on the minimap.",
        )
    


