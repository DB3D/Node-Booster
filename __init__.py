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
#  - Continue with the interpolation nodes for proof of concept of note below.
#    - warning message if the node encounter a user nodegroup. NG can't be evaluated.
#    - Document why it crash on blender reload. Specific to geomtry node not supporting custom NodeSocket. 
#      Report once the proof of concept is done. devs need to see it's worth it.
#    - Why is there a triple update signal when adding a new node?
#    - IMPORTANT: Geometry node seems to ignore evaluation of our custom group. Why? 'Not Logged during evaluation'. Need a report.

# ---------------------------------------------------------------------------------------------

# TODO Custom SocketTypes Experiments.
#  - Wait a minute.. we can add custom NodeSocketTypes, with custom Node types? What the heck..???
#    - Check if cross compatible 4.2 / 4.3 / 4.4????
#    - Can it creates/remove sockets on the fly? what about label? what about changing socket type on the fly?
#      -A: i think yes, but not for NodeCustomGroup in GeometryNode api limitations. NodeCustom should be ok. need to test..
#    - Re-Implement most nodes as CustomNodes then.. Start with an easy one.. 
#       node_utils will have some rework to do. need to precise type of operation, if CustomNodeGroup or CustoNode.
#    - How does it behave when the nodegroup is unregistered???
#    - How can we process NativeNodes mixed with CustomSockets? 
#       - What if we wrap a CustomNodeSocket in a CustomNodeGroup? how can we do that via an API? it works manually.
#       -  still, will need to find a solution to convert our CustomNodeSocket to a NativeSocket. Python could just update a Value node default_value..
#    - if possible, then we can cross the todo in  'Change to C blender code' for custom socket types.
#       - Start with custom interpolation types. See if MapRange can be ported. Could linearmaprange to 01 then use the FloatMapCurve then map range to custom values. 
#         The final nodes would simply do the evaluation. would not be nodegroup compatible tho. Problem:

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
#  - BugFix when adding a lot of nodes while animation is playing. Quite random, can't reproduce. must be related to depsgraph implementation?
#    seems that all_3d_viewports trigger this but it might be a coincidence..
#    ConsolePrints:
#        RecursionError: maximum recursion depth exceeded
#        Error in bpy.app.handlers.depsgraph_update_post[1]:
#        Traceback (most recent call last):
#          File "D:\Work\NodeBooster\nodebooster\handlers.py", line 106, in nodebooster_handler_depspost
#          File "D:\Work\NodeBooster\nodebooster\handlers.py", line 32, in upd_all_custom_nodes
#          File "D:\Work\NodeBooster\nodebooster\utils\node_utils.py", line 72, in get_all_nodes
#        RecursionError: maximum recursion depth exceeded while calling a Python object
#    It seems to trigger a depsgraph chain reaction with other addons.
#        Error in bpy.app.handlers.depsgraph_update_post[0]:
#        Traceback (most recent call last):
#          File "D:\Work\Geo-Scatter\vLatest\geo_scatter\gpl_script\handlers\handlers.py", line 118, in scatter5_depsgraph
#          File "D:\Work\Geo-Scatter\vLatest\geo_scatter\gpl_script\handlers\handlers.py", line 540, in shading_type_callback
#          File "D:\Work\Geo-Scatter\vLatest\geo_scatter\gpl_script\utils\extra_utils.py", line 156, in is_rendered_view
#          File "D:\Work\Geo-Scatter\vLatest\geo_scatter\gpl_script\utils\extra_utils.py", line 150, in all_3d_viewports_shading_type
#        RecursionError: maximum recursion depth exceeded
#        Error in bpy.app.handlers.depsgraph_update_post[1]:
#        Traceback (most recent call last):
#          File "D:\Work\NodeBooster\nodebooster\handlers.py", line 106, in nodebooster_handler_depspost
#          File "D:\Work\NodeBooster\nodebooster\handlers.py", line 32, in upd_all_custom_nodes
#          File "D:\Work\NodeBooster\nodebooster\utils\node_utils.py", line 72, in get_all_nodes
#        RecursionError: maximum recursion depth exceeded while calling a Python object
#        Error in bpy.app.handlers.depsgraph_update_post[0]:
#        Traceback (most recent call last):
#          File "D:\Work\Geo-Scatter\vLatest\geo_scatter\gpl_script\handlers\handlers.py", line 118, in scatter5_depsgraph
#            shading_type_callback()
#          File "D:\Work\Geo-Scatter\vLatest\geo_scatter\gpl_script\handlers\handlers.py", line 540, in shading_type_callback
#            is_rdr = is_rendered_view()
#                     ^^^^^^^^^^^^^^^^^^
#          File "D:\Work\Geo-Scatter\vLatest\geo_scatter\gpl_script\utils\extra_utils.py", line 156, in is_rendered_view
#            return 'RENDERED' in all_3d_viewports_shading_type()
#                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#          File "D:\Work\Geo-Scatter\vLatest\geo_scatter\gpl_script\utils\extra_utils.py", line 150, in all_3d_viewports_shading_type
#            for space in all_3d_viewports():
#          File "D:\Work\Geo-Scatter\vLatest\geo_scatter\gpl_script\utils\extra_utils.py", line 140, in all_3d_viewports
#            for window in bpy.context.window_manager.windows:
#                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
