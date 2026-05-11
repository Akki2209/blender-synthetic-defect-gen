import bpy
import math
import os
from mathutils import Vector

def run_automated_render_workflow():

    # =========================================================================
    # CONFIGURATION
    # =========================================================================
    #save_folder = "D:/blender_out/Stain/"
    save_folder = "D:/blender_out/Gouge/"
    #save_folder = "D:/blender_out/Discoloration/"
    #save_folder = "D:/blender_out/Golden/"

    CENTER_X = 1.394644
    CENTER_Y = 5.5145304

    PART_Z_POSITION = 2.4
    CAMERA_TARGET_Z = 0.0  

    DIST_FROM_CENTER = 7.5
    CAM_Z_ROTATION = 0.0
    USER_TILT_ANGLE = 40.0

    LIGHT_POWER = 1200
    LIGHT_Z_OFFSET = -1.5

    # -------------------------------------------------------------------------
    # 🔥 DEFECT 1: Gouge
    # -------------------------------------------------------------------------
    ENABLE_NOISE_BUMP = False
    D1_NOISE_SCALE = 4.0
    D1_NOISE_DETAIL = 2.0
    D1_NOISE_DISTORTION = 0.6
    D1_RAMP_POS_WHITE = 0.3
    D1_BUMP_STRENGTH = 4.3
    D1_BUMP_DISTANCE = 0.3

    # -------------------------------------------------------------------------
    # 🔥 DEFECT 2: BUMP
    # -------------------------------------------------------------------------
    ENABLE_MAGIC_BUMP = False
    D2_MAGIC_SCALE = 3.0
    D2_MAGIC_DISTORTION = 2.0
    D2_NOISE_SCALE = 5.2
    D2_NOISE_DISTORTION = -0.8
    D2_MIX_FACTOR = 0.573
    D2_RAMP_POS_WHITE = 0.2
    D2_BUMP_STRENGTH = 0.2
    D2_BUMP_DISTANCE = 0.2

    # -------------------------------------------------------------------------
    # 🔥 DEFECT 3: Stain/Discoloration
    # -------------------------------------------------------------------------
    ENABLE_PAINT_DEFECT = True
    D3_PAINT_RGB = (1, 1, 1, 1.0) # Base color
    D3_DEFECT_RGB = (0.5, 0.2, 0.2, 1.0) # Defect color
    D3_COUNT = 5
    D3_SIZE = 0.6
    D3_INTENSITY = 0.4
    D3_SEED = 0.3

    # -------------------------------------------------------------------------
    # 🔥 DEFECT 4: Scratch
    # -------------------------------------------------------------------------
    ENABLE_DEFECT_4 = False

    D4_VORONOI_SCALE = 20.0
    D4_VORONOI_RANDOM = 1.0

    D4_BOTTOM_SCALE = 0.1
    D4_BOTTOM_RANDOM = 1.0

    D4_NOISE_SCALE = 4.7
    D4_NOISE_DETAIL = 3.5
    D4_NOISE_ROUGHNESS = 0.0
    D4_NOISE_DISTORTION = 0.4

    D4_SUBTRACT_VALUE = 0.4
    D4_DIVIDE_VALUE = 0.003

    D4_RAMP_BLACK_POS = 0.0
    D4_RAMP_WHITE_POS = 0.8

    # -------------------------------------------------------------------------

    os.makedirs(save_folder, exist_ok=True)

    # -------------------------------------------------------------------------
    # CLEAN SCENE & CREATE PART
    # -------------------------------------------------------------------------
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(0, 0, 0))
    base = bpy.context.active_object
    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(0, 0, 1))
    top = bpy.context.active_object
    top.rotation_euler[0] = math.radians(90)
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()

    obj = base
    obj.rotation_euler = (math.radians(180), math.radians(90), 0)
    obj.location = (CENTER_X, CENTER_Y, PART_Z_POSITION)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
    bpy.ops.object.shade_smooth()

    # -------------------------------------------------------------------------
    # 🛠️ DISTINCT DEFECT MATERIAL SYSTEM
    # -------------------------------------------------------------------------
    mat = bpy.data.materials.new(name="Distinct_Defects_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_tex_coord = nodes.new(type='ShaderNodeTexCoord')
    node_mapping = nodes.new(type='ShaderNodeMapping')
    node_bsdf_base = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    
    node_bsdf_base.inputs['Base Color'].default_value = D3_PAINT_RGB
    links.new(node_tex_coord.outputs['Object'], node_mapping.inputs['Vector'])

    bump_noise = nodes.new(type='ShaderNodeBump')
    bump_magic = nodes.new(type='ShaderNodeBump')

    # Defect 1: Noise Bump Logic
    if ENABLE_NOISE_BUMP:
        node_noise_d1 = nodes.new(type='ShaderNodeTexNoise')
        node_noise_d1.inputs['Scale'].default_value = D1_NOISE_SCALE
        node_noise_d1.inputs['Detail'].default_value = D1_NOISE_DETAIL
        node_noise_d1.inputs['Distortion'].default_value = D1_NOISE_DISTORTION
        node_ramp_d1 = nodes.new(type='ShaderNodeValToRGB')
        node_ramp_d1.color_ramp.elements[1].position = D1_RAMP_POS_WHITE
        bump_noise.inputs['Strength'].default_value = D1_BUMP_STRENGTH
        bump_noise.inputs['Distance'].default_value = D1_BUMP_DISTANCE
        links.new(node_mapping.outputs['Vector'], node_noise_d1.inputs['Vector'])
        links.new(node_noise_d1.outputs['Color'], node_ramp_d1.inputs['Fac'])
        links.new(node_ramp_d1.outputs['Color'], bump_noise.inputs['Height'])

    # Defect 2: Magic Bump Logic
    if ENABLE_MAGIC_BUMP:
        node_noise_d2 = nodes.new(type='ShaderNodeTexNoise')
        node_noise_d2.inputs['Scale'].default_value = D2_NOISE_SCALE
        node_noise_d2.inputs['Distortion'].default_value = D2_NOISE_DISTORTION
        node_mix_d2 = nodes.new(type='ShaderNodeMix')
        node_mix_d2.data_type = 'RGBA'
        node_mix_d2.inputs['Factor'].default_value = D2_MIX_FACTOR
        node_magic_d2 = nodes.new(type='ShaderNodeTexMagic')
        node_magic_d2.inputs['Scale'].default_value = D2_MAGIC_SCALE
        node_magic_d2.inputs['Distortion'].default_value = D2_MAGIC_DISTORTION
        node_ramp_d2 = nodes.new(type='ShaderNodeValToRGB')
        node_ramp_d2.color_ramp.elements[1].position = D2_RAMP_POS_WHITE
        bump_magic.inputs['Strength'].default_value = D2_BUMP_STRENGTH
        bump_magic.inputs['Distance'].default_value = D2_BUMP_DISTANCE
        links.new(node_mapping.outputs['Vector'], node_mix_d2.inputs['A'])
        links.new(node_noise_d2.outputs['Color'], node_mix_d2.inputs['B'])
        links.new(node_mix_d2.outputs['Result'], node_magic_d2.inputs['Vector'])
        links.new(node_magic_d2.outputs['Fac'], node_ramp_d2.inputs['Fac'])
        links.new(node_ramp_d2.outputs['Color'], bump_magic.inputs['Height'])

    # Defect 3: Dynamic Paint Logic
    current_shader_out = node_bsdf_base.outputs['BSDF']
    if ENABLE_PAINT_DEFECT:
        node_bsdf_defect = nodes.new('ShaderNodeBsdfPrincipled')
        node_bsdf_defect.inputs['Base Color'].default_value = D3_DEFECT_RGB
        node_bsdf_defect.inputs['Roughness'].default_value = 0.9

        node_noise_d3 = nodes.new('ShaderNodeTexNoise')
        node_noise_d3.inputs['Scale'].default_value = D3_COUNT
        node_noise_d3.inputs['Detail'].default_value = 15.0
        
        node_map_d3 = nodes.new('ShaderNodeMapping')
        node_map_d3.inputs['Location'].default_value = (D3_SEED, D3_SEED, D3_SEED)
        
        node_ramp_d3 = nodes.new('ShaderNodeValToRGB')
        node_ramp_d3.color_ramp.elements[0].position = D3_SIZE
        node_ramp_d3.color_ramp.elements[1].position = min(D3_SIZE + 0.02, 1.0)
        
        node_math_d3 = nodes.new('ShaderNodeMath')
        node_math_d3.operation = 'MULTIPLY'
        node_math_d3.inputs[1].default_value = D3_INTENSITY
        
        node_mix_shader = nodes.new('ShaderNodeMixShader')
        
        links.new(node_tex_coord.outputs['Object'], node_map_d3.inputs['Vector'])
        links.new(node_map_d3.outputs['Vector'], node_noise_d3.inputs['Vector'])
        links.new(node_noise_d3.outputs['Fac'], node_ramp_d3.inputs['Fac'])
        links.new(node_ramp_d3.outputs['Color'], node_math_d3.inputs[0])
        links.new(node_math_d3.outputs['Value'], node_mix_shader.inputs[0])
        links.new(node_bsdf_base.outputs['BSDF'], node_mix_shader.inputs[1])
        links.new(node_bsdf_defect.outputs['BSDF'], node_mix_shader.inputs[2])
        current_shader_out = node_mix_shader.outputs['Shader']
        
    # ---------------------------------------------------------------------
    # Defect 4 : Voronoi Flow Defect
    # ---------------------------------------------------------------------
    if ENABLE_DEFECT_4:

        # =========================================================
        # VORONOI TOP
        # =========================================================
        node_voronoi_d4_top = nodes.new(type='ShaderNodeTexVoronoi')
        node_voronoi_d4_top.location = (-1200, -900)

        node_voronoi_d4_top.voronoi_dimensions = '3D'
        node_voronoi_d4_top.feature = 'F1'
        node_voronoi_d4_top.distance = 'EUCLIDEAN'

        node_voronoi_d4_top.inputs["Scale"].default_value = D4_VORONOI_SCALE
        node_voronoi_d4_top.inputs["Randomness"].default_value = D4_VORONOI_RANDOM

        # =========================================================
        # VORONOI BOTTOM
        # =========================================================
        node_voronoi_d4_bottom = nodes.new(type='ShaderNodeTexVoronoi')
        node_voronoi_d4_bottom.location = (-1200, -1200)

        node_voronoi_d4_bottom.voronoi_dimensions = '3D'
        node_voronoi_d4_bottom.feature = 'DISTANCE_TO_EDGE'

        node_voronoi_d4_bottom.inputs["Scale"].default_value = D4_BOTTOM_SCALE
        node_voronoi_d4_bottom.inputs["Randomness"].default_value = D4_BOTTOM_RANDOM

        # =========================================================
        # VECTOR SUBTRACT
        # =========================================================
        node_subtract_vec_d4 = nodes.new(type='ShaderNodeVectorMath')
        node_subtract_vec_d4.location = (-900, -900)
        node_subtract_vec_d4.operation = 'SUBTRACT'

        # =========================================================
        # VECTOR ADD
        # =========================================================
        node_add_vec_d4 = nodes.new(type='ShaderNodeVectorMath')
        node_add_vec_d4.location = (-650, -900)
        node_add_vec_d4.operation = 'ADD'

        # =========================================================
        # NOISE
        # =========================================================
        node_noise_d4 = nodes.new(type='ShaderNodeTexNoise')
        node_noise_d4.location = (-400, -900)

        node_noise_d4.noise_dimensions = '3D'

        node_noise_d4.inputs["Scale"].default_value = D4_NOISE_SCALE
        node_noise_d4.inputs["Detail"].default_value = D4_NOISE_DETAIL
        node_noise_d4.inputs["Roughness"].default_value = D4_NOISE_ROUGHNESS
        node_noise_d4.inputs["Distortion"].default_value = D4_NOISE_DISTORTION

        # =========================================================
        # SUBTRACT
        # =========================================================
        node_math_sub_d4 = nodes.new(type='ShaderNodeMath')
        node_math_sub_d4.location = (-150, -900)

        node_math_sub_d4.operation = 'SUBTRACT'
        node_math_sub_d4.inputs[1].default_value = D4_SUBTRACT_VALUE

        # =========================================================
        # ABSOLUTE
        # =========================================================
        node_abs_d4 = nodes.new(type='ShaderNodeMath')
        node_abs_d4.location = (100, -900)

        node_abs_d4.operation = 'ABSOLUTE'

        # =========================================================
        # DIVIDE
        # =========================================================
        node_divide_d4 = nodes.new(type='ShaderNodeMath')
        node_divide_d4.location = (350, -900)

        node_divide_d4.operation = 'DIVIDE'
        node_divide_d4.inputs[1].default_value = D4_DIVIDE_VALUE

        # =========================================================
        # COLOR RAMP
        # =========================================================
        node_ramp_d4 = nodes.new(type='ShaderNodeValToRGB')
        node_ramp_d4.location = (600, -900)

        node_ramp_d4.color_ramp.elements[0].position = D4_RAMP_BLACK_POS
        node_ramp_d4.color_ramp.elements[0].color = (1, 1, 1, 1)

        node_ramp_d4.color_ramp.elements[1].position = D4_RAMP_WHITE_POS
        node_ramp_d4.color_ramp.elements[1].color = (1, 0, 0, 1)

        # =========================================================
        # DEFECT BSDF
        # =========================================================
        node_bsdf_d4 = nodes.new(type='ShaderNodeBsdfPrincipled')
        node_bsdf_d4.location = (900, -900)

        node_bsdf_d4.inputs['Base Color'].default_value = (0.0, 0.0, 0.0, 1)
        node_bsdf_d4.inputs['Roughness'].default_value = 0.95

        # =========================================================
        # MIX SHADER
        # =========================================================
        node_mix_d4 = nodes.new(type='ShaderNodeMixShader')
        node_mix_d4.location = (1200, -700)

        # =========================================================
        # CONNECTIONS
        # =========================================================

        # Texture Coordinate
        links.new(node_tex_coord.outputs['Object'], node_voronoi_d4_top.inputs['Vector'])
        links.new(node_tex_coord.outputs['Object'], node_voronoi_d4_bottom.inputs['Vector'])

        # Updated routing
        links.new(node_tex_coord.outputs['Object'], node_subtract_vec_d4.inputs[0])
        links.new(node_voronoi_d4_top.outputs['Position'], node_subtract_vec_d4.inputs[1])

        links.new(node_subtract_vec_d4.outputs['Vector'], node_add_vec_d4.inputs[0])
        links.new(node_voronoi_d4_top.outputs['Color'], node_add_vec_d4.inputs[1])

        # Flow
        links.new(node_add_vec_d4.outputs['Vector'], node_noise_d4.inputs['Vector'])

        links.new(node_noise_d4.outputs['Fac'], node_math_sub_d4.inputs[0])

        links.new(node_math_sub_d4.outputs['Value'], node_abs_d4.inputs[0])

        links.new(node_abs_d4.outputs['Value'], node_divide_d4.inputs[0])

        links.new(node_divide_d4.outputs['Value'], node_ramp_d4.inputs['Fac'])

        # Mix defect
        links.new(node_ramp_d4.outputs['Color'], node_mix_d4.inputs[0])

        links.new(current_shader_out, node_mix_d4.inputs[1])

        links.new(node_bsdf_d4.outputs['BSDF'], node_mix_d4.inputs[2])

        current_shader_out = node_mix_d4.outputs['Shader']

    # Final Linking (Chaining Normals and Surface)
    links.new(bump_noise.outputs['Normal'], bump_magic.inputs['Normal'])
    links.new(bump_magic.outputs['Normal'], node_bsdf_base.inputs['Normal'])
    # If the defect scuffs also need the bump, link it here:
    if ENABLE_PAINT_DEFECT:
        links.new(bump_magic.outputs['Normal'], node_bsdf_defect.inputs['Normal'])
        
    links.new(current_shader_out, node_output.inputs['Surface'])

    obj.data.materials.append(mat)

    # -------------------------------------------------------------------------
    # TRANSFORMS & RENDER
    # -------------------------------------------------------------------------
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.transform.translate(value=(-0.8, 0, 0), orient_type='GLOBAL') 
    bpy.ops.transform.translate(value=(0, 0, -1.7), orient_type='GLOBAL')
    CENTER_X, CENTER_Y, PART_Z_POSITION = obj.location.x, obj.location.y, obj.location.z

    bpy.ops.mesh.primitive_plane_add(size=44, location=(0, 0, -0.95))
    f_mat = bpy.data.materials.new(name="BlackMat")
    f_mat.use_nodes = True
    f_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0, 0, 0, 1)
    bpy.context.active_object.data.materials.append(f_mat)

    def create_camera_and_light(name, suffix, az_deg, tilt_deg):
        az, tilt = math.radians(az_deg), math.radians(tilt_deg)
        x = CENTER_X + DIST_FROM_CENTER * math.cos(tilt) * math.sin(az)
        y = CENTER_Y - DIST_FROM_CENTER * math.cos(tilt) * math.cos(az)
        z = CAMERA_TARGET_Z + DIST_FROM_CENTER * math.sin(tilt)
        cam_data = bpy.data.cameras.new(f"{name}_data")
        cam_obj = bpy.data.objects.new(name, cam_data)
        bpy.context.collection.objects.link(cam_obj)
        cam_obj.location = (x, y, z)
        cam_obj.rotation_euler = (Vector((CENTER_X, CENTER_Y, CAMERA_TARGET_Z)) - cam_obj.location).to_track_quat('-Z', 'Y').to_euler()
        l_data = bpy.data.lights.new(f"Light_{suffix}", type='AREA')
        l_data.energy, l_data.specular_factor = 1200, 0.0
        l_data.shape, l_data.size, l_data.size_y = 'RECTANGLE', 10, 10
        l_obj = bpy.data.objects.new(f"Light_{suffix}_Obj", l_data)
        bpy.context.collection.objects.link(l_obj)
        l_obj.location = (x, y, z + LIGHT_Z_OFFSET)
        l_obj.rotation_euler = (Vector((CENTER_X, CENTER_Y, PART_Z_POSITION)) - l_obj.location).to_track_quat('-Z', 'Y').to_euler()
        return cam_obj

    cam1 = create_camera_and_light("Camera_1", "1", CAM_Z_ROTATION, USER_TILT_ANGLE)
    cam2 = create_camera_and_light("Camera_2", "2", CAM_Z_ROTATION + 180, USER_TILT_ANGLE)

    def render_step(step_name):
        for i, cam in enumerate([cam1, cam2]):
            bpy.context.scene.camera = cam
            bpy.context.scene.render.filepath = os.path.join(save_folder, f"Cam{i+1}_{step_name}.png")
            bpy.ops.render.render(write_still=True)

    original_rot = obj.rotation_euler.copy()

    obj.rotation_euler = original_rot
    render_step("01_Original")

    obj.rotation_euler = original_rot
    obj.rotation_euler[2] += math.radians(90)
    render_step("02_Rotate_Z_90")

    obj.rotation_euler[2] += math.radians(90)
    obj.rotation_euler[1] += math.radians(180)
    render_step("03_Flip_Y_180")

    obj.rotation_euler[2] += math.radians(90)
    render_step("04_FlipY_Z_90")
    print("\n✔ DONE: All 3 defects applied and rendered.")

run_automated_render_workflow()
