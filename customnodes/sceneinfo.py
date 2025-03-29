# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
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

    bl_idname = "NodeBoosteSceneInfo"
    bl_label = "Scene Info"
    bl_description = """Custom Nodgroup: Gather informations about your active scene.
    • Expect updates on each depsgraph post and frame_pre update signals"""
    auto_update = {'FRAME_PRE','DEPS_POST',}
    tree_type = "*ChildrenDefined*"

    @classmethod
    def poll(cls, context):
        """mandatory poll"""
        return True

    def init(self, context):
        """this fct run when appending the node for the first time"""

        name = f".{self.bl_idname}"

        ng = bpy.data.node_groups.get(name)
        if (ng is None):
            ng = create_new_nodegroup(name,
                tree_type=self.tree_type,
                out_sockets={
                    "Use Gravity": "NodeSocketBool",
                    "Gravity": "NodeSocketVector",
                    },
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

        scene = bpy.context.scene

        set_socket_defvalue(self.node_tree, 0, value=scene.use_gravity)
        set_socket_defvalue(self.node_tree, 1, value=scene.gravity)

        return None

    def draw_label(self,):
        """node label"""
        
        return self.bl_label

    def draw_buttons(self, context, layout):
        """node interface drawing"""

        return None

    def draw_panel(self, layout, context):
        """draw in the nodebooster N panel 'Active Node'"""

        n = self

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
    def update_all_instances(cls, from_autoexec=False,):
        """search for all nodes of this type and update them"""

        #TODO we call update_all_instances for a lot of nodes from depsgraph & we need to optimize this, because func below may recur a LOT of nodes
        # could pass a from_nodes arg in this function
        for n in get_all_nodes(
            geometry=True, compositing=True, shader=True, 
            ignore_ng_name="NodeBooster", match_idnames={cls.bl_idname},
            ):
            n.update()
            
        return None 

#Per Node-Editor Children:
#Respect _NG_ + _GN_/_SH_/_CP_ nomenclature

class NODEBOOSTER_NG_GN_SceneInfo(Base, bpy.types.GeometryNodeCustomGroup):
    tree_type = "GeometryNodeTree"
    bl_idname = "GeometryNodeSceneInfo" + Base.bl_idname

class NODEBOOSTER_NG_SH_SceneInfo(Base, bpy.types.ShaderNodeCustomGroup):
    tree_type = "ShaderNodeTree"
    bl_idname = "ShaderNode" + Base.bl_idname

class NODEBOOSTER_NG_CP_SceneInfo(Base, bpy.types.CompositorNodeCustomGroup):
    tree_type = "CompositorNodeTree"
    bl_idname = "CompositorNode" + Base.bl_idname
