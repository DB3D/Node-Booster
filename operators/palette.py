# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
#
# SPDX-License-Identifier: GPL-2.0-or-later


import bpy


#NOTE this functionality is implemented on an property update and msgbus callback level
#NOTE about palettes: https://blender.stackexchange.com/questions/73122/how-do-i-create-palette-ui-object



def palette_active_upd(self, context):
    """update when user is changing the scene 'palette_active' property, for assigning color to nodes"""

    if (context.space_data is None):
        return None
    if (context.space_data.type!='NODE_EDITOR'):
        return None 

    ng = context.space_data.edit_tree
    for n in [n for n in ng.nodes if (n.select)]:
        if (not n.use_custom_color):
            n.use_custom_color = True
        n.color = self.palette_active

    return None

def msgbus_palette_callback(context):
    """get notified when user is changing a palette color"""
    
    # NOTE: msgbus context is very bad, even bpy.context from here is None..
    # so we use an operator instead.. i don't like this, but there's no choice.
    # not my fault if most handlers and msgbus context parameters are broken!
    try:
        bpy.ops.nodebooster.palette_msg_bus_actions(('INVOKE_DEFAULT'))
    except Exception as e:
        print(f"Error updating Color Palette custom nodes: {e}")

    return None


class NODEBOOSTER_OT_palette_msg_bus_actions(bpy.types.Operator):

    bl_idname = "nodebooster.palette_msg_bus_actions"
    bl_label = ""
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        # This operator will be called from a msgbus, and context will be crap
        # So we need to find back the space from mouse
        space = None
        region = None
        for a in bpy.context.window.screen.areas:
            if (a.x<event.mouse_x<a.x+a.width) and (a.y<event.mouse_y<a.y+a.height):
                space = a.spaces[0]
                # Find which region the mouse is in
                for r in a.regions:
                    if (r.x<event.mouse_x<r.x+r.width) and (r.y<event.mouse_y<r.y+r.height):
                        region = r
                        break
                break

        if (space is None) or (space.type!='NODE_EDITOR'):
            print('ERROR: NODEBOOSTER_OT_palette_msg_bus_actions: space invalid')
            return {'CANCELLED'}
        ng = space.edit_tree
        if (not ng):
            print('ERROR: NODEBOOSTER_OT_palette_msg_bus_actions: ng invalid')
            return {'CANCELLED'}

        sett_scene = context.scene.nodebooster
        
        #panel assignation operator from N panel
        if (region is not None) or (region.type=='UI'):
            pal = sett_scene.palette_assign_ptr
            if (pal):
                palactive = pal.colors.active
                if (palactive):
                    palcol = palactive.color[:]
                    # Create a nice History
                    sett_scene.palette_older = sett_scene.palette_old
                    sett_scene.palette_old = sett_scene.palette_active
                    # Will trigger palette_active_upd
                    sett_scene.palette_active = palcol
                    if (sett_scene.frame_sync_color):
                        sett_scene.frame_color = palcol
                    for n in [n for n in ng.nodes if (n.select)]:
                        if (not n.use_custom_color):
                            n.use_custom_color = True
                        n.color = palcol

        #palette sync operator for specific node
        for n in [n for n in ng.nodes if ('NodeBoosterColorPalette' in n.bl_idname)]:
            n.sync_palette_to_outputs()

        return {'FINISHED'}



class NODEBOOSTER_OT_palette_reset_color(bpy.types.Operator, ):

    bl_idname = "nodebooster.palette_reset_color"
    bl_label = "Reset Color"
    bl_description = "Reset Color"

    @classmethod
    def poll(cls, context):
        return (context.space_data.type=='NODE_EDITOR') and (context.space_data.node_tree is not None)

    def execute(self, context,):
        
        ng = context.space_data.edit_tree
        for n in ng.nodes:
            if n.select:
                n.use_custom_color = False

        return {'FINISHED'}


def initialize_palette(palette_name:str="MyPalette"):
    """create a new palette data with new colors"""

    colors = [
        (1.0, 1.0, 1.0),
        (0.9490196704864502, 0.9490196704864502, 0.9490196704864502),
        (0.9019608497619629, 0.9019608497619629, 0.9019608497619629),
        (0.8509804606437683, 0.8509804606437683, 0.8509804606437683),
        (0.8000000715255737, 0.8000000715255737, 0.8000000715255737),
        (0.7490196228027344, 0.7490196228027344, 0.7490196228027344),
        (0.6980392336845398, 0.6980392336845398, 0.6980392336845398),
        (0.6509804129600525, 0.6509804129600525, 0.6509804129600525),
        (0.6000000238418579, 0.6000000238418579, 0.6000000238418579),
        (0.5490196347236633, 0.5490196347236633, 0.5490196347236633),
        (0.501960813999176, 0.501960813999176, 0.501960813999176),
        (0.45098042488098145, 0.45098042488098145, 0.45098042488098145),
        (0.40000003576278687, 0.40000003576278687, 0.40000003576278687),
        (0.3490196168422699, 0.3490196168422699, 0.3490196168422699),
        (0.2980392277240753, 0.2980392277240753, 0.2980392277240753),
        (0.250980406999588, 0.250980406999588, 0.250980406999588),
        (0.20000001788139343, 0.20000001788139343, 0.20000001788139343),
        (0.14901961386203766, 0.14901961386203766, 0.14901961386203766),
        (0.10196079313755035, 0.10196079313755035, 0.10196079313755035),
        (0.0, 0.0, 0.0),
        (0.9490196704864502, 0.988235354423523, 0.1411764770746231),
        (1.0, 0.917647123336792, 0.0),
        (0.9960784912109375, 0.6549019813537598, 0.06666667014360428),
        (0.9960784912109375, 0.545098066329956, 0.4078431725502014),
        (0.9843137860298157, 0.23137256503105164, 0.007843137718737125),
        (0.9960784912109375, 0.20784315466880798, 0.12941177189350128),
        (0.8156863451004028, 0.0, 0.0),
        (0.658823549747467, 0.12156863510608673, 0.2392157018184662),
        (0.4705882668495178, 0.01568627543747425, 0.13333334028720856),
        (0.16862745583057404, 0.0, 0.0),
        (0.9450981020927429, 0.8862745761871338, 0.7725490927696228),
        (0.9960784912109375, 0.8941177129745483, 0.7019608020782471),
        (0.9960784912109375, 0.8549020290374756, 0.7333333492279053),
        (0.9960784912109375, 0.760784387588501, 0.5568627715110779),
        (0.847058892250061, 0.5607843399047852, 0.34117648005485535),
        (0.7411764860153198, 0.38823533058166504, 0.250980406999588),
        (0.6352941393852234, 0.250980406999588, 0.16862745583057404),
        (0.38823533058166504, 0.20784315466880798, 0.1764705926179886),
        (0.41960787773132324, 0.1568627506494522, 0.20000001788139343),
        (0.2039215862751007, 0.07058823853731155, 0.0470588281750679),
        (0.9058824181556702, 0.7960785031318665, 0.5607843399047852),
        (0.8196079134941101, 0.7019608020782471, 0.545098066329956),
        (0.7568628191947937, 0.6941176652908325, 0.49803924560546875),
        (0.8431373238563538, 0.5960784554481506, 0.04313725605607033),
        (1.0, 0.6941176652908325, 0.0),
        (0.9960784912109375, 0.545098066329956, 0.0),
        (1.0, 0.41568630933761597, 0.0),
        (0.7176470756530762, 0.2549019753932953, 0.0),
        (0.37254902720451355, 0.24313727021217346, 0.11372549831867218),
        (0.23137256503105164, 0.13725490868091583, 0.0),
        (0.9960784912109375, 0.7921569347381592, 0.8549020290374756),
        (0.9960784912109375, 0.3960784673690796, 0.7960785031318665),
        (0.9960784912109375, 0.07450980693101883, 0.572549045085907),
        (0.8666667342185974, 0.1882353127002716, 0.38431376218795776),
        (0.7529412508010864, 0.29019609093666077, 0.4274510145187378),
        (0.5372549295425415, 0.08627451211214066, 0.5333333611488342),
        (0.3019607961177826, 0.14901961386203766, 0.5372549295425415),
        (0.2666666805744171, 0.08235294371843338, 0.12941177189350128),
        (0.1725490242242813, 0.06666667014360428, 0.22352942824363708),
        (0.1411764770746231, 0.0784313753247261, 0.13333334028720856),
        (1.0, 1.0, 0.4901961088180542),
        (1.0, 1.0, 0.0),
        (1.0, 0.49803924560546875, 0.0),
        (1.0, 0.4901961088180542, 0.4901961088180542),
        (1.0, 0.4901961088180542, 1.0),
        (1.0, 0.0, 0.9960784912109375),
        (1.0, 0.0, 0.49803924560546875),
        (1.0, 0.0, 0.0),
        (0.49803924560546875, 0.0, 0.0),
        (0.03921568766236305, 0.03921568766236305, 0.0),
        (0.9647059440612793, 0.9921569228172302, 1.0),
        (0.9137255549430847, 0.9686275124549866, 1.0),
        (0.8117647767066956, 0.9019608497619629, 0.9960784912109375),
        (0.6666666865348816, 0.7803922295570374, 0.9960784912109375),
        (0.46666669845581055, 0.7019608020782471, 0.9960784912109375),
        (0.11764706671237946, 0.4549019932746887, 0.9921569228172302),
        (0.0, 0.27450981736183167, 0.6666666865348816),
        (0.18431372940540314, 0.2666666805744171, 0.46274513006210327),
        (0.0, 0.1882353127002716, 0.32156863808631897),
        (0.05490196496248245, 0.05490196496248245, 0.14509804546833038),
        (0.9333333969116211, 0.960784375667572, 0.9411765336990356),
        (0.8392157554626465, 0.8980392813682556, 0.8705883026123047),
        (0.6745098233222961, 0.847058892250061, 0.7254902124404907),
        (0.4235294461250305, 0.6784313917160034, 0.7764706611633301),
        (0.25882354378700256, 0.6627451181411743, 0.686274528503418),
        (0.0, 0.49803924560546875, 0.49803924560546875),
        (0.2862745225429535, 0.40392160415649414, 0.3607843220233917),
        (0.18039216101169586, 0.30588236451148987, 0.30588236451148987),
        (0.11372549831867218, 0.19607844948768616, 0.22352942824363708),
        (0.05882353335618973, 0.1098039299249649, 0.12941177189350128),
        (0.847058892250061, 1.0, 0.9568628072738647),
        (0.7215686440467834, 0.9568628072738647, 0.960784375667572),
        (0.6823529601097107, 0.8000000715255737, 0.7098039388656616),
        (0.46274513006210327, 0.7725490927696228, 0.4705882668495178),
        (0.20784315466880798, 0.529411792755127, 0.34117648005485535),
        (0.250980406999588, 0.6078431606292725, 0.4078431725502014),
        (0.27450981736183167, 0.529411792755127, 0.4078431725502014),
        (0.12156863510608673, 0.3176470696926117, 0.16862745583057404),
        (0.16470588743686676, 0.2352941334247589, 0.21568629145622253),
        (0.07058823853731155, 0.18039216101169586, 0.11372549831867218),
        (0.9372549653053284, 1.0, 0.7882353663444519),
        (0.9019608497619629, 0.9529412388801575, 0.5215686559677124),
        (0.7372549176216125, 0.960784375667572, 0.1098039299249649),
        (0.8313726186752319, 0.8627451658248901, 0.0941176563501358),
        (0.5098039507865906, 0.8274510502815247, 0.13333334028720856),
        (0.3607843220233917, 0.49803924560546875, 0.0),
        (0.3490196168422699, 0.5764706134796143, 0.16862745583057404),
        (0.16078431904315948, 0.49803924560546875, 0.0),
        (0.0, 0.26274511218070984, 0.125490203499794),
        (0.1098039299249649, 0.20000001788139343, 0.13333334028720856),
        (0.0, 1.0, 0.49803924560546875),
        (0.0, 1.0, 0.0),
        (0.4901961088180542, 1.0, 0.4901961088180542),
        (0.4901961088180542, 1.0, 1.0),
        (0.0, 1.0, 1.0),
        (0.4901961088180542, 0.4901961088180542, 1.0),
        (0.49803924560546875, 0.0, 1.0),
        (0.0, 0.0, 1.0),
        (0.24705883860588074, 0.0, 0.49803924560546875),
        (0.0, 0.0, 0.49803924560546875),
    ]

    pal = bpy.data.palettes.get(palette_name)
    if (pal is None):
        pal = bpy.data.palettes.new(palette_name)

        for col in colors:
            palcol = pal.colors.new()
            palcol.color = col
            palcol.weight = 1.0
    
    return pal


class NODEBOOSTER_OT_initalize_palette(bpy.types.Operator, ):

    bl_idname = "nodebooster.initalize_palette"
    bl_label = "Create Palette"
    bl_description = "Create Palette"

    palette_name : bpy.props.StringProperty(default="MyPalette", options={'SKIP_SAVE'},)
    set_node_prop : bpy.props.StringProperty(default="", options={'SKIP_SAVE'},)
    set_scn_prop : bpy.props.StringProperty(default="", options={'SKIP_SAVE'},)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type=='NODE_EDITOR') and (context.space_data.node_tree is not None)

    def execute(self, context,):
        pal = initialize_palette(palette_name=self.palette_name)
        #set a scene property on creation..
        if (self.set_scn_prop):
            setattr(context.scene.nodebooster, self.set_scn_prop, pal)
        #option to set a node property on creation..
        if (self.set_node_prop):
            ng, ndname = self.set_node_prop.split('_#_')
            ng = bpy.data.node_groups.get(ng)
            nd = ng.nodes.get(ndname)
            nd.palette_ptr = pal

        return {'FINISHED'}
