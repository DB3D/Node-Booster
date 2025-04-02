# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
#
# SPDX-License-Identifier: GPL-2.0-or-later

# ---------------------------------------------------------------------------------------------

# TODO v2.0 release
#  - Custom operator shortcuts are not saved, they reset on each blender sessions.
#  - Functions should always check if a value or type isn't already set before setting it. 
#    I believe the tool is currently sending a lot of useless update signals by setting the same values 
#    (see compositor refresh, perhaps it's because of node.update()?? need to investigate)
#  - Finalize NexScript for Shader/compositor. Need to overview functions..
#  - Codebase review for extension.. Ask AI to do a big check.
#  - Sound Sequencer Node: Text property with custom poll. That's it. No sound data.
#  - Velocity Node: Better history calculations just doing last middle first is not precise enough. 

# ---------------------------------------------------------------------------------------------

# TODO v2.1 release
#  - Wait a minute.. we can add custom NodeSocketTypes, with custom Node types? What the heck..???
#    - Check how it behaves when passing default value output????
#    - Check if we can process data from CustomSocketInput to CustomSocketOutput??
#    - Check if cross compatible 4.2 / 4.3 / 4.4
#    - How does it behave in a nodegroup??
#      - problem with nodegroup input evaluation. i believe it is technically impossible to evaluate something from a 
#        nodegroup context, as it is unknown. The evaluation can only be done within the larger context..
#        So in short, we will never be able to toy with CustomSocket NativeSocket within the same nodegroups, 
#        there's will be an evaluation conflict.
#    - Can it creates/remove sockets on the fly? what about label? what about changing socket type on the fly?
#    - Re-Implement most nodes as CustomNodes then.. Start with an easy one.. 
#       node_utils will have some rework to do. need to precise type of operation, if CustomNodeGroup or CustoNode.
#    - How does it behave when the nodegroup is unregistered???
#    - How can we process NativeNodes mixed with CustomSockets? 
#       - What if we wrap a CustomNodeSocket in a CustomNodeGroup? how can we do that via an API? it works manually.
#       -  still, will need to find a solution to convert our CustomNodeSocket to a NativeSocket. Python could just update a Value node default_value..
#    - if possible, then we can cross the todo in  'Change to C blender code' for custom socket types.

# See demo below:

# import bpy
# from bpy.types import Node, NodeSocket

# # Define a custom socket with a custom color property
# class CustomColorSocket(NodeSocket):
#     bl_idname = 'CustomColorSocketType'
#     bl_label = "Custom Color Socket"

#     # Custom property (an RGB color)
#     value: bpy.props.FloatVectorProperty(
#         name="Color Value",
#         subtype='COLOR',
#         default=(0.8, 0.2, 0.2),
#         min=0.0, max=1.0,
#         size=3
#     )

#     def draw(self, context, layout, node, text):
#         # Display the socket property in the node UI
#         layout.prop(self, "value", text=text)
    
#     def draw_color(self, context, node):
#         r, g, b = self.value
#         return (r, g, b, 1.0)

# # Define a custom Geometry Node that uses our custom socket type
# class CustomGeometryNode(Node):
#     bl_idname = 'CustomGeometryNodeType'
#     bl_label = 'Custom Geometry Node'
#     bl_icon = 'NODE'
    
#     def init(self, context):
#         # Create an input and an output using our custom socket type.
#         self.inputs.new('CustomColorSocketType', "Custom Data")
#         self.outputs.new('CustomColorSocketType', "Custom Data")
        
#         # Create a standard Float socket with an initial value.
#         float_socket = self.outputs.new('NodeSocketFloat', "Normal Data")
#         float_socket.default_value = 0.0

#     def update(self):
#         print('update signal')
#         # Find the Float socket and increment its value by 1 on each update.
#         for socket in self.outputs:
#             if socket.bl_idname == 'NodeSocketFloat':
#                 socket.default_value += 1
#                 print(f"Updated {socket.name} to {socket.default_value}")

#     def draw_buttons(self, context, layout):
#         # You can add custom buttons here if desired.
#         pass
    
#     def draw_label(self):
#         return "Custom Geometry Node"

# # Append the custom node to the Geometry Node Editor's "Add" menu.
# def custom_nodes_menu_draw(self, context):
#     if context.space_data.tree_type == 'GeometryNodeTree':
#         self.layout.operator("node.add_node", text="Custom Geometry Node", icon="NODE").type = "CustomGeometryNodeType"

# def register():
#     bpy.utils.register_class(CustomColorSocket)
#     bpy.utils.register_class(CustomGeometryNode)
#     bpy.types.NODE_MT_add.append(custom_nodes_menu_draw)

# def unregister():
#     bpy.types.NODE_MT_add.remove(custom_nodes_menu_draw)
#     bpy.utils.unregister_class(CustomGeometryNode)
#     bpy.utils.unregister_class(CustomColorSocket)

# if __name__ == "__main__":
#     register()

# ---------------------------------------------------------------------------------------------

# NOTE Ideas for changes of blender C source code:
#  - Would be great to display error messages for context nodes who use them like the native node. 
#    API is not exposed th
#  - Color of some nodes should'nt be red. sometimes blue for converter (math expression) or script color..
#    Unfortunately the API si not Exposed. It would be nice to have custom colors for our nodes.. Or at least choose in existing colortype list.
#  - Eval socket_value API??? ex `my_node.inputs[0].eval_value()` would return a single value, or a numpy array (if possible?)
#    So far in this plugin we can only pass information to a socket, or arrange nodes.
#    What would be an extremely useful functionality, woould be to sample a socket value from a socket.evaluate_value()
#    integrated directly in blender. Unfortunately there are no plans to implement such API.
#  - CustomSocketTypes API? (NOTE it seems that this one is possible).
#    If we could create custom SocketTypes, we could create nodes that process specific data before sending it 
#    to the native blender SocketTypes. A lot of new CustomNodes could be implemented that way for each editors.
#    It would greatly improve how extensible existing editors are. A lot of nodes from Animation nodes for example
#    could be implemented on for all editors types, and be directly use within these native editors without the need
#    of a separate nodetree interface.
#  - Nodes Consistencies: Generally speaking, nodes are not consistent from one editor to another.
#    For example ShaderNodeValue becomes CompositorNodeValue. Ect.. a lot of Native socket types could be ported to 
#    all editors as well. For example, SocketBool can be in the compositor.
#  - NodeSocket position should definitely be exposed for custom noodle drawing. or socket overdrawings.

# ---------------------------------------------------------------------------------------------

# TODO Ideas:
#
# Generic Functionalities Ideas:
#  - Maybe copy some nodewrangler functionality such as quick mix so user stick to our extrusion style workflow?
#  - Could have an operator for quickly editing a frame description?  Either full custom python editor, or popup a new small window.
#  - Could implement background reference image. there's even a special drawing method for that in the API.
#  - could implement a tab switch in the header for quickly switching between different the big 3 editors?
# Nodes Ideas:
# - Could design portal node. There are ways to hide sockets, even from user CTRL+H, this node could simply pass hidden sockets around? 
#   Do some tests. Note: would only be nice if we draw a heavy 'portal line' effect from node A to node B. Bonus: animation of the direction.
# - Material Info node? gather informations about the material? if so, what?
# - Color Palette Node? easily swap between color palettes?
# - Armature/Bone nodes? Will need to learn about rigging to do that tho..
# - File IO: For geometry node, could create a mesh on the fly from a file and set up as field attributes.
# - View3D Info node: Like camera info, but for the 3d view (location/rotation/fov/clip/)
#   Problem: what if there are many? Perhaps should use context.
# - MetaBall Info node?
# - Evaluate sequencer images? Possible to feed the sequencer render to the nodes? Hmm
# - SoundData Info Node: Sample the sound? Generate a sound geometry curve? Evaluate Sound at time? If we work based on sound, perhaps it's for the best isn't it?
# - See if it's possible to imitate a multi-socket like the geometry join node, in customNode, and in customNodegroup. multi math ect would be nice.
# - IF CustomSocketTypes works with NativeSockets:
#     - we could port the interpolation nodes from AnimationNodes?
#       problem is: how do apply the interpolation, to what kind of data, and how?
#         we could use Float/Vector Curve.
#         for geometry node we can even make a curve. 
#         problem is, what about map range?? see how it's internally calculated.
#     - we could have some sort of gamelogic nodes?
# - See inspirations from other softs: AnimationNodes/Svershock/Houdini/Ue5/MayaFrost/ect.. see what can be extending GeoNode/Shader/Compositor.
# - MaterialMaker/ SubstanceDesigner import/livelink would be nice. 

# ---------------------------------------------------------------------------------------------

# TODO Bugs:
# To Fix:
#  - copy/pasting a node with ctrlc/v is not working, even crashing. Unsure it's us tho. Maybe it's blender bug.
# Known:
#  - You might stumble into this crash when hot-reloading (enable/disable) the plugin on blender 4.2/4.2
#    https://projects.blender.org/blender/blender/issues/134669 Has been fixed in 4.4. 
#    Only impacts developers hotreloading.

# ---------------------------------------------------------------------------------------------

import bpy

#This is only here for supporting blender 4.1
bl_info = {
    "name": "Node Booster (Experimental 4.1+)",
    "author": "BD3D DIGITAL DESIGN (Dorian B.)",
    "version": (0, 0, 0),
    "blender": (4, 1, 0),
    "location": "Node Editor",
    "description": "Please install this addon as a blender extension instead of a legacy addon!",
    "warning": "",
    "doc_url": "https://blenderartists.org/t/nodebooster-new-nodes-and-functionalities-for-node-wizards-for-free",
    "category": "Node",
}

def get_addon_prefs():
    """get preferences path from base_package, __package__ path change from submodules"""
    return bpy.context.preferences.addons[__package__].preferences

def isdebug():
    return get_addon_prefs().debug

def dprint(thing):
    if isdebug():
        print(thing)

def cleanse_modules():
    """remove all plugin modules from sys.modules for a clean uninstall (dev hotreload solution)"""
    # See https://devtalk.blender.org/t/plugin-hot-reload-by-cleaning-sys-modules/20040 fore more details.

    import sys

    all_modules = sys.modules
    all_modules = dict(sorted(all_modules.items(),key= lambda x:x[0])) #sort them

    for k,v in all_modules.items():
        if k.startswith(__package__):
            del sys.modules[k]

    return None


def get_addon_classes(revert=False):
    """gather all classes of this plugin that have to be reg/unreg"""

    from .properties import classes as sett_classes
    from .operators import classes as ope_classes
    from .customnodes import classes as nodes_classes
    from .ui import classes as ui_classes

    classes = sett_classes + ope_classes + nodes_classes + ui_classes

    if (revert):
        return reversed(classes)

    return classes


def register():
    """main addon register"""

    from .resources import load_icons
    load_icons() 
    
    #register every single addon classes here
    for cls in get_addon_classes():
        bpy.utils.register_class(cls)

    from .properties import load_properties
    load_properties()

    from .customnodes.deviceinput import register_listener
    register_listener()

    from .handlers import load_handlers    
    load_handlers()

    from .ui import load_ui
    load_ui()

    from .operators import load_operators_keymaps
    load_operators_keymaps()
    

    return None


def unregister():
    """main addon un-register"""

    from .operators import unload_operators_keymaps
    unload_operators_keymaps()

    from .ui import unload_ui
    unload_ui()

    from .handlers import unload_handlers  
    unload_handlers()

    from .properties import unload_properties
    unload_properties()

    #unregister every single addon classes here
    for cls in get_addon_classes(revert=True):
        bpy.utils.unregister_class(cls)
        
    from .customnodes.deviceinput import unregister_listener
    unregister_listener()
    
    from .resources import unload_icons
    unload_icons() 

    cleanse_modules()

    return None
