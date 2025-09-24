# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
#
# SPDX-License-Identifier: GPL-2.0-or-later


import bpy 

from bl_ui.properties_paint_common import BrushPanel

from ..__init__ import get_addon_prefs
from ..utils.str_utils import word_wrap


class NODEBOOSTER_PT_active_node(bpy.types.Panel):

    bl_idname = "NODEBOOSTER_PT_active_node"
    bl_label = "Active Node"
    bl_category = "Node Booster"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        if (context.space_data.type!='NODE_EDITOR'):
            return False
        if (context.space_data.node_tree is None):
            return False
        return True

    def draw(self, context):

        layout = self.layout

        ng = context.space_data.edit_tree
        active = ng.nodes.active

        if (not active):
            layout.active = False
            layout.label(text="No Active Nodes")
            return None

        if ('NodeBooster' not in active.bl_idname):
            layout.active = False
            layout.label(text="Select a Booster Node")
            return None

        layout.label(text=active.bl_label, icon='NODE')
        # layout.separator(type='LINE')

        if hasattr(active,'draw_panel'):
              active.draw_panel(layout, context)
        else: layout.label(text="No Interface Defined", icon='GHOST_DISABLED')

        return None


class NODEBOOSTER_PT_tool_search(bpy.types.Panel):
    """search element within your node_tree"""

    bl_idname = "NODEBOOSTER_PT_tool_search"
    bl_label = "Search"
    bl_category = "Node Booster"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return (context.space_data.type=='NODE_EDITOR') and (context.space_data.node_tree is not None)

    def draw(self, context):

        sett_scene = context.scene.nodebooster

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        row.prop(sett_scene,"search_keywords",text="",icon="VIEWZOOM")
        row.prop(sett_scene,"search_center",text="",icon="ZOOM_ALL")

        col = layout.column(heading="Filters")
        col.prop(sett_scene,"search_labels")
        # col.prop(sett_scene,"search_types") #TODO For later. Ideally they should be type enum
        col.prop(sett_scene,"search_socket_names") #TODO Ideally we should have an option to either check sockets or ng info.
        # col.prop(sett_scene,"search_socket_types") #TODO For later. Ideally they should be type enum
        col.prop(sett_scene,"search_names")
        col.prop(sett_scene,"search_input_only")
        col.prop(sett_scene,"search_frame_only")

        s = layout.column()
        s.label(text=f"Found {sett_scene.search_found} Element(s)")
    
        return None


class NODEBOOSTER_PT_tool_color_palette(bpy.types.Panel,BrushPanel):
    #palette api is a bit bad, it is operatiors designed for unified paint tools
    #so we are hijacking the context for us then.

    bl_idname = "NODEBOOSTER_PT_tool_color_palette"
    bl_label = "Assign Color"
    bl_category = "Node Booster"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return (context.space_data.type=='NODE_EDITOR') and (context.space_data.node_tree is not None)

    def draw(self, context):

        layout = self.layout

        sett_scene = context.scene.nodebooster
        if (not sett_scene.palette_assign_ptr):
            op = layout.operator("nodebooster.initalize_palette",text="Create Palette",icon="ADD",)
            op.set_scn_prop = "palette_assign_ptr"
            return None

        row = layout.row(align=True)

        colo = row.row(align=True)
        colo.prop(sett_scene,"palette_older",text="")
        colo.prop(sett_scene,"palette_old",text="")
        colo.prop(sett_scene,"palette_active",text="")

        row.operator("nodebooster.palette_reset_color",text="",icon="LOOP_BACK",)

        layout.template_palette(sett_scene, "palette_assign_ptr", color=True,)

        return None 


class NODEBOOSTER_PT_tool_frame(bpy.types.Panel):

    bl_idname = "NODEBOOSTER_PT_tool_frame"
    bl_label = "Draw Frame"
    bl_category = "Node Booster"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_order = 3

    @classmethod
    def poll(cls, context):
        return (context.space_data.type=='NODE_EDITOR') and (context.space_data.node_tree is not None)

    def draw(self, context):

        sett_scene = context.scene.nodebooster

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.prop(sett_scene,"frame_label")
        col.prop(sett_scene,"frame_label_size")
        col.prop(sett_scene,"frame_use_custom_color")

        col = col.column()
        col.prop(sett_scene,"frame_sync_color")
        col.separator(factor=0.25)
        col.active = sett_scene.frame_use_custom_color
        col.prop(sett_scene,"frame_color")

        return None


class NODEBOOSTER_PT_minimap(bpy.types.Panel):

    bl_idname = "NODEBOOSTER_PT_minimap"
    bl_label = ""
    bl_category = "Node Booster"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return (context.space_data.type=='NODE_EDITOR') and (context.space_data.node_tree is not None)

    def draw_header(self, context):
        self.layout.prop(context.scene.nodebooster,"minimap_show", text="Minimap",)
        return None

    def draw(self, context):
        sett_addon = get_addon_prefs()
        sett_win = context.window_manager.nodebooster
        sett_scene = context.scene.nodebooster

        layout = self.layout
        layout.active = sett_scene.minimap_show

        header, panel = layout.panel("minimap_sh_params", default_closed=False,)
        header.label(text="Shape",)
        if (panel):

            col = panel.column()
            col.use_property_split = True
            col.use_property_decorate = False

            subcol = col.column()
            subcol.prop(sett_scene,"minimap_width_percentage", slider=True, text="Size")
            subcol.prop(sett_scene,"minimap_auto_aspect_ratio", text="Auto Crop",)

            col.separator(factor=1.55, type='LINE')

            subcol = col.column(heading="T Panel",)
            subcol.prop(sett_scene,"minimap_auto_tool_panel_collapse", text="Auto Collapse",)

        header, panel = layout.panel("minimap_map_params", default_closed=True,)
        header.label(text="Theme",)
        if (panel):

            col = panel.column()
            col.use_property_split = True
            col.use_property_decorate = False

            col.prop(sett_scene,"minimap_fill_color", text="Fill",)
            
            col.separator(factor=1.55, type='LINE')
            
            col.prop(sett_scene,"minimap_outline_width", text="Outline",)
            col.prop(sett_scene,"minimap_outline_color", text=" ",)
            # col.prop(sett_scene,"minimap_border_radius", text="Bevel",)
            
            col.separator(factor=1.55, type='LINE')

            col.prop(sett_scene,"minimap_padding", text="Padding",)
            # col.prop(sett_scene,"minimap_draw_type", text="Draw Type",)

            col.separator(factor=1.55, type='LINE')

            col = panel.column(heading='View',)
            col.use_property_split = True
            col.use_property_decorate = False
            col.prop(sett_scene,"minimap_view_enable", text="Show",)
            subcol = col.column()
            subcol.active = sett_scene.minimap_view_enable
            subcol.prop(sett_scene,"minimap_view_fill_color", text="Fill",)
            subcol.prop(sett_scene,"minimap_view_outline_color", text="Outline",)
            subcol.prop(sett_scene,"minimap_view_outline_width", text="Width",)
            # col.prop(sett_scene,"minimap_view_border_radius", text="Bevel",)

        header, panel = layout.panel("minimap_node_params", default_closed=True,)
        header.label(text="Node Detail",)
        if (panel):

            col = panel.column()
            col.use_property_split = True
            col.use_property_decorate = False
            
            subcol = col.column(heading='Color')
            subcol.prop(sett_scene,"minimap_node_draw_typecolor", text="Type",)
            subcol.prop(sett_scene,"minimap_node_draw_nodecustomcolor", text="Custom",)
            
            col.separator(factor=1.55, type='LINE')

            subcol = col.column(heading='Selection')
            subcol.prop(sett_scene,"minimap_node_draw_selection", text="Show",)

            col.prop(sett_scene,"minimap_node_outline_width", text="Outline",)
            # col.prop(sett_scene,"minimap_node_border_radius", text="Bevel",)

            col.separator(factor=1.55, type='LINE')

            subcol = col.column(heading='Header')
            subcol.prop(sett_scene,"minimap_node_draw_header", text="Show",)
            childcol = subcol.column()
            childcol.active = sett_scene.minimap_node_draw_header
            childcol.prop(sett_scene,"minimap_node_header_height", text="Height",)
            childcol.prop(sett_scene,"minimap_node_header_minheight", text="Min Height",)
            
            col.separator(factor=1.55, type='LINE')
            
            subcol = col.column(heading='Frames')
            subcol.prop(sett_scene,"minimap_node_draw_frames", text="Show",)
            childcol = subcol.column()
            childcol.active = sett_scene.minimap_node_draw_frames
            childcol.prop(sett_scene,"minimap_node_draw_framecustomcolor", text="Color",)
            childcol.prop(sett_scene,"minimap_node_draw_frames_detail", text="Detail",)
            
            col.separator(factor=1.55, type='LINE')
            
            col.prop(sett_scene,"minimap_node_body_color", text="Body",)


        header, panel = layout.panel("minimap_nav_params", default_closed=False,)
        header.prop(sett_win,"minimap_modal_operator_is_active", text="Use Navigation",)
        if (panel):

            col = panel.column()
            col.use_property_split = True
            col.use_property_decorate = False
            
            subcol = col.column(heading="Startup",)
            subcol.prop(sett_addon,"auto_launch_minimap_navigation",)

            subcol = col.column(heading="Shortcuts",)
            subcol.prop(sett_scene,"minimap_triple_click_dezoom", text="Frame All",)

        header, panel = layout.panel("minimap_star_params", default_closed=True,)
        header.prop(sett_scene,"minimap_fav_show", text="Show Favorites",)
        if (panel):

            col = panel.column()
            col.active = sett_scene.minimap_fav_show
            col.use_property_split = True
            col.use_property_decorate = False

            subcol = col.column(heading="Star")
            subcol.prop(sett_scene,"minimap_fav_size", text="Size",)

        header, panel = layout.panel("minimap_cursor_params", default_closed=True,)
        header.prop(sett_scene,"minimap_cursor_show", text="Show Cursor",)
        if (panel):

            col = panel.column()
            col.active = sett_scene.minimap_cursor_show
            col.use_property_split = True
            col.use_property_decorate = False

            subcol = col.column(heading="Cursor")
            subcol.prop(sett_scene,"minimap_cursor_radius", text="Radius",)
            subcol.prop(sett_scene,"minimap_cursor_color", text="Color",)

        return None


class NODEBOOSTER_PT_shortcuts_memo(bpy.types.Panel):

    bl_idname = "NODEBOOSTER_PT_shortcuts_memo"
    bl_label = "Shortcuts"
    bl_category = "Node Booster"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_order = 5
    bl_options = {'DEFAULT_CLOSED'} 

    @classmethod
    def poll(cls, context):
        return (context.space_data.type=='NODE_EDITOR') and (context.space_data.node_tree is not None)

    def draw(self, context):

        from ..operators import ADDON_KEYMAPS
        layout = self.layout

        for i, (km, kmi, name, icon) in enumerate(ADDON_KEYMAPS):
            
            if (i!=0):
                layout.separator(type='LINE')

            col = layout.box()

            titlename = name.replace('Select','Sel.')
            mainrow = col.row(align=True)
            row = mainrow.row(align=True)
            row.alignment = 'LEFT'
            row.prop(kmi, "active", text=titlename,emboss=False,)
            row = mainrow.row(align=True)
            row.alignment = 'RIGHT'
            row.label(text='',icon=icon)

            col = col.column()
            col.active = kmi.active

            header, panel = col.panel(f'geobuilder_shortcut_layoutpanel_defaults_{i}', default_closed=False,)
            header.label(text="Default Shortcut",)
            if (panel):
                panel.separator(factor=0.5)
                row = panel.row(align=True)
                row.separator(factor=0.5)

                match name:
                    case "Add Favorite":
                        row.label(text='', icon='EVENT_CTRL',)
                        row.separator(factor=2.35)
                        row.label(text='', icon='EVENT_Y',)

                    case "Loop Favorites":
                        row.label(text='', icon='EVENT_Y',)

                    case "Draw Frame":
                        row.label(text='', icon='IMPORT',)
                        row.label(text='', icon='EVENT_J',)

                    case "Draw Route":
                        row.label(text='', icon='EVENT_E',)

                    case "Reroute Chamfer":
                        row.label(text='', icon='EVENT_CTRL',)
                        row.separator(factor=2.35)
                        row.label(text='', icon='EVENT_B',)

                panel.separator(factor=0.5)

            col.separator(factor=0.5)

            header, panel = col.panel(f'geobuilder_shortcut_layoutpanel_custom_{i}', default_closed=True,)
            header.label(text="Customize",)
            if (panel):
                panel.use_property_split = True

                sub = panel.column()
                subrow = sub.row(align=True)
                subrow.prop(kmi, "type", text='Key', event=True)

                sub = panel.column(heading='Modifiers:')
                sub.use_property_split = True
                sub.prop(kmi, "shift_ui",)
                sub.prop(kmi, "ctrl_ui",)
                sub.prop(kmi, "alt_ui",)

            continue

        return None

