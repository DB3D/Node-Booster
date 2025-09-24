# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
#
# SPDX-License-Identifier: GPL-2.0-or-later


import bpy


from mathutils import Color

from ..utils.node_utils import (
    create_new_nodegroup,
    set_ng_socket_defvalue,
    set_ng_socket_type,
    set_ng_socket_label,
    cache_booster_nodes_parent_tree,
)


def gamma_correct(color):
    rgb, alpha = color[:3], color[3] if (len(color)>3) else 1.0
    rgb = Color(rgb).from_srgb_to_scene_linear()
    return [*rgb, alpha]

class Base():

    bl_idname = "NodeBoosterColorPalette"
    bl_label = "Color Palette"
    bl_description = "Output the active palette color. Shows a palette UI and a Create Palette button."
    auto_upd_flags = {'DEPS_POST','LOAD_POST',}
    tree_type = "*ChildrenDefined*"

    def update_signal(self,context):
        self.sync_palette_to_outputs()
        return None 

    def update_colors(self,context):
        ng = self.node_tree
        if (self.gamma_correction):
            set_ng_socket_defvalue(ng, 0, value=gamma_correct(self.color_active),)
            set_ng_socket_defvalue(ng, 1, value=gamma_correct(self.color_after1),)
            set_ng_socket_defvalue(ng, 2, value=gamma_correct(self.color_after2),)
            set_ng_socket_defvalue(ng, 3, value=gamma_correct(self.color_after3),)
            set_ng_socket_defvalue(ng, 4, value=gamma_correct(self.color_after4),)
            set_ng_socket_defvalue(ng, 5, value=gamma_correct(self.color_after5),)
        else:
            set_ng_socket_defvalue(ng, 0, value=self.color_active)
            set_ng_socket_defvalue(ng, 1, value=self.color_after1)
            set_ng_socket_defvalue(ng, 2, value=self.color_after2)
            set_ng_socket_defvalue(ng, 3, value=self.color_after3)
            set_ng_socket_defvalue(ng, 4, value=self.color_after4)
            set_ng_socket_defvalue(ng, 5, value=self.color_after5)
        return None

    palette_ptr : bpy.props.PointerProperty(type=bpy.types.Palette, update=update_signal)
    
    color_active : bpy.props.FloatVectorProperty(
        subtype='COLOR',
        default=(0,0,0,0),
        min=0, max=1,
        size=4,
        update=update_colors,
        )
    color_active_viewer : bpy.props.FloatVectorProperty(
        subtype='COLOR_GAMMA', size=4, get=lambda s: s.color_active, set=lambda s,v: setattr(s, 'color_active', v),)
    color_after1 : bpy.props.FloatVectorProperty(
        subtype='COLOR',
        default=(0,0,0,0),
        min=0, max=1,
        size=4,
        update=update_colors,
        )
    color_after1_viewer : bpy.props.FloatVectorProperty(
        subtype='COLOR_GAMMA', size=4, get=lambda s: s.color_after1, set=lambda s,v: setattr(s, 'color_after1', v),)
    color_after2 : bpy.props.FloatVectorProperty(
        subtype='COLOR',
        default=(0,0,0,0),
        min=0, max=1,
        size=4,
        update=update_colors,
        )
    color_after2_viewer : bpy.props.FloatVectorProperty(
        subtype='COLOR_GAMMA', size=4, get=lambda s: s.color_after2, set=lambda s,v: setattr(s, 'color_after2', v),)
    color_after3 : bpy.props.FloatVectorProperty(
        subtype='COLOR',
        default=(0,0,0,0),
        min=0, max=1,
        size=4,
        update=update_colors,
        )
    color_after3_viewer : bpy.props.FloatVectorProperty(
        subtype='COLOR_GAMMA', size=4, get=lambda s: s.color_after3, set=lambda s,v: setattr(s, 'color_after3', v),)
    color_after4 : bpy.props.FloatVectorProperty(
        subtype='COLOR',
        default=(0,0,0,0),
        min=0, max=1,
        size=4,
        update=update_colors,
        )
    color_after4_viewer : bpy.props.FloatVectorProperty(
        subtype='COLOR_GAMMA', size=4, get=lambda s: s.color_after4, set=lambda s,v: setattr(s, 'color_after4', v),)
    color_after5 : bpy.props.FloatVectorProperty(
        subtype='COLOR',
        default=(0,0,0,0),
        min=0, max=1,
        size=4,
        update=update_colors,
        )
    color_after5_viewer : bpy.props.FloatVectorProperty(
        subtype='COLOR_GAMMA', size=4, get=lambda s: s.color_after5, set=lambda s,v: setattr(s, 'color_after5', v),)
    gamma_correction : bpy.props.BoolProperty(
        default=True,
        name="Gamma Correction",
        description="Apply gamma correction to the color",
        update=update_colors,
        )

    # deprecated: palette_pointer_name (use palette_ptr instead)

    # Alias used by the operator to assign the created palette name
    palette_name : bpy.props.StringProperty(
        default="",
        options={'SKIP_SAVE'},
        # kept for operator wiring; not used otherwise
        )

    @classmethod
    def poll(cls, context):
        """mandatory poll"""
        return True

    def init(self, context,):        
        """this fct run when appending the node for the first time"""

        name = f".{self.bl_idname}"

        ng = bpy.data.node_groups.get(name)
        if (ng is None):
            ng = create_new_nodegroup(name,
                tree_type=self.tree_type,
                out_sockets={
                    "Color Active" : "NodeSocketColor",
                    "Color Neighbor 1" : "NodeSocketColor",
                    "Color Neighbor 2" : "NodeSocketColor",
                    "Color Neighbor 3" : "NodeSocketColor",
                    "Color Neighbor 4" : "NodeSocketColor",
                    "Color Neighbor 5" : "NodeSocketColor",
                    },
                )

        ng = ng.copy() #always using a copy of the original ng
        self.node_tree = ng

        # initialize value to current palette (or black)
        self.color_active, self.color_after1, self.color_after2, self.color_after3, self.color_after4, self.color_after5 = self.get_active_palette_colors()

        self.width = 190

        return None 

    def copy(self,node,):
        """fct run when dupplicating the node"""

        #NOTE: copy/paste can cause crashes, we use a timer to delay the action
        def delayed_copy():
            self.node_tree = node.node_tree.copy()
        bpy.app.timers.register(delayed_copy, first_interval=0.01)

        return None 

    def update(self):
        """generic update function"""

        cache_booster_nodes_parent_tree(self.id_data)

        return None

    def get_active_palette_colors(self) -> tuple:
        """Return the active palette color followed by five subsequent colors (RGBA).
        Wrap to the start if there are not enough colors after the active one.
        """
        pal = self.palette_ptr
        if (pal is not None) and (pal.colors):
            colors = pal.colors

            # Find the active color and its index
            active_idx = 0
            active_color = None
            for i, color in enumerate(colors):
                if color == colors.active:
                    active_idx = i
                    active_color = color
                    break

            # Fallback: if active not found use first
            if (active_color is None):
                active_idx = 0
                active_color = colors[0]

            def to_rgba(pcol):
                r, g, b = pcol.color[:]
                return (float(r), float(g), float(b), 1.0)

            result = [to_rgba(active_color)]
            total = len(colors)
            for step in range(1, 6):
                idx = (active_idx + step) % total
                result.append(to_rgba(colors[idx]))
            return tuple(result)

        # Fallback: return six black colors
        black = (0.0, 0.0, 0.0, 1.0)
        return black, black, black, black, black, black

    def sync_palette_to_outputs(self) -> None:
        """Read active palette color and assign it to the output socket."""

        ng = self.node_tree
        if (ng is None):
            return None
        self.color_active, self.color_after1, self.color_after2, self.color_after3, self.color_after4, self.color_after5 = self.get_active_palette_colors()

        return None

    def draw_label(self,):
        """node label"""
        if (self.label==''):
            return 'Color Palette'
        return self.label

    def draw_buttons(self, context, layout,):
        """node interface drawing"""

        # Palette pointer row (always visible)
        row = layout.row(align=True)
        row.prop(self, "palette_ptr", text="")

        is_valid = bool(self.palette_ptr)
        if (not is_valid):
            op = row.operator("nodebooster.initalize_palette", text="", icon="ADD")
            op.palette_name = self.name
            op.set_node_prop = f"{self.id_data.name}_#_{self.name}"

        # Show Blender palette template from the pointer directly
        layout.template_palette(self, "palette_ptr", color=True)
        
        row = layout.row(align=True)
        addend = '_viewer' if self.gamma_correction else ''
        row.prop(self, f"color_active{addend}", text="")
        row.prop(self, f"color_after1{addend}", text="")
        row.prop(self, f"color_after2{addend}", text="")
        row.prop(self, f"color_after3{addend}", text="")
        row.prop(self, f"color_after4{addend}", text="")
        row.prop(self, f"color_after5{addend}", text="")
        
        row = layout.row(align=True)
        row.prop(self, "gamma_correction",)

        return None

    def draw_panel(self, layout, context):
        """draw in the nodebooster N panel 'Active Node'"""

        header, panel = layout.panel("palette_panelid", default_closed=False,)
        header.label(text="Palette",)
        if (panel):
            row = panel.row(align=True)
            row.prop(self, "palette_ptr", text="")

            is_valid = bool(self.palette_ptr)
            if (not is_valid):
                op = row.operator("nodebooster.initalize_palette", text="", icon="ADD")
                op.palette_name = self.name
                op.set_node_prop = f"{self.id_data.name}_#_{self.name}"
            # Always show Blender palette template below, using the pointer
            panel.template_palette(self, "palette_ptr", color=True)

            row = layout.row(align=True)
            addend = '_viewer' if self.gamma_correction else ''
            row.prop(self, f"color_active{addend}", text="")
            row.prop(self, f"color_after1{addend}", text="")
            row.prop(self, f"color_after2{addend}", text="")
            row.prop(self, f"color_after3{addend}", text="")
            row.prop(self, f"color_after4{addend}", text="")
            row.prop(self, f"color_after5{addend}", text="")
            
            row = layout.row(align=True)
            row.prop(self, "gamma_correction",)
        
        return None

    def _draw_palette_swatches(self, layout, pal):
        """Draw a compact grid of palette color swatches editable in-place."""
        if (pal is None) or (not pal.colors):
            return None
        columns = 8
        col = layout.column(align=True)
        row = None
        for i, pcol in enumerate(pal.colors):
            if (i % columns) == 0:
                row = col.row(align=True)
            cell = row.column(align=True)
            cell.scale_x = 0.6
            cell.scale_y = 0.7
            cell.prop(pcol, "color", text="")
        return None

    @classmethod
    def update_all(cls, using_nodes=None, signal_from_handlers=False,):
        """Refresh all nodes outputs with current active palette color."""

        # defer import to avoid circular issues
        from ..utils.node_utils import get_booster_nodes

        if (using_nodes is None):
              nodes = get_booster_nodes(by_idnames={cls.bl_idname},)
        else: nodes = [n for n in using_nodes if (n.bl_idname==cls.bl_idname)]

        for n in nodes:
            if (n.mute):
                continue
            n.sync_palette_to_outputs()
            continue

        return None


#Per Node-Editor Children:
#Respect _NG_ + _GN_/_SH_/_CP_ nomenclature

class NODEBOOSTER_NG_GN_ColorPalette(Base, bpy.types.GeometryNodeCustomGroup):
    tree_type = "GeometryNodeTree"
    bl_idname = "GeometryNode" + Base.bl_idname

class NODEBOOSTER_NG_SH_ColorPalette(Base, bpy.types.ShaderNodeCustomGroup):
    tree_type = "ShaderNodeTree"
    bl_idname = "ShaderNode" + Base.bl_idname

class NODEBOOSTER_NG_CP_ColorPalette(Base, bpy.types.CompositorNodeCustomGroup):
    tree_type = "CompositorNodeTree"
    bl_idname = "CompositorNode" + Base.bl_idname


