
BONE_TAIL = (0, 0, 1)

MATS = {"s": "SkinDmg_Skin",
        "g": "GlassDmgCrack_Glass",
        "d": "DetailsDmgNormal_Details",
        "w": "DetailsDmgNormal_Wheels"}

SOCKETS = ["LightFProj", 
           "LightFL1", 
           "LightFR1", 
           "LightRL", 
           "LightRR", 
           "FLLight",
           "FRLight",
           "RLLight",
           "RRLight",
           "ProjShad",
           "Exhaust1",
           "Exhaust2",
           "Exhaust3",
           "Exhaust4"]

EXTRA_JOINTS = ["Exhaust",
                "PilHead",
                "PilHead2",
                "PlayerSeat_Pilot01",
                "FLArmDir",
                "FRArmDir",
                "RLArmDir",
                "RRArmDir",
                "Hood",
                "Trunk",
                "LDoor",
                "RDoor",
                "FLCardan",
                "FRCardan",
                "FWShieldGlass",
                "LDoorGlass",
                "RDoorGlass",
                "TrunkGlass"]

CAR_SKEL = ["Body", ["FLHub", ["FLGuard", "FLWheel"],
                               "FLReactor",
                               "FLArmBot",
                               "FLArmTop",
                               "FLSusp"],
                    ["FRHub", ["FRGuard", "FRWheel"],
                               "FRReactor",
                               "FRArmBot",
                               "FRArmTop",
                               "FRSusp"],
                    ["RLHub", ["RLGuard", ["RLCardan", "RLWheel"]],
                               "RLReactor",
                               "RLSusp",
                               "RLCardan",
                               "RLArmBot",
                               "RLArmTop"],
                    ["RRHub", ["RRGuard", ["RRCardan", "RRWheel"]],
                               "RRReactor",
                               "RRSusp",
                               "RRCardanB",
                               "RRArmBot",
                               "RRArmTop"]]

def add_bones(arm, bones, parent=None):
    bones = iter(bones)
    new_parent = arm.edit_bones.new(next(bones))
    new_parent.tail = BONE_TAIL
    new_parent.parent = parent
    for b in bones:
        if type(b) is list:
            add_bones(arm, b, new_parent)
        else:
            new_bone = arm.edit_bones.new(b)
            new_bone.parent = new_parent
            new_bone.tail = BONE_TAIL


parts = list(D.objects)

arm = bpy.data.armatures.new("Hips")
arm_obj = bpy.data.objects.new("Hips", arm)
bpy.context.scene.collection.objects.link(arm_obj)

bpy.context.view_layer.objects.active = arm_obj

bpy.ops.object.mode_set(mode='EDIT')
add_bones(arm, CAR_SKEL)


for part in parts:
   
    bpy.ops.object.mode_set(mode='EDIT')
    
    if part.name[0].islower():
        mat_letter = part.name[0]
        part_name = part.name[1:-5]
    else:
        mat_letter = "s"
        part_name = part.name[:-5]
    
    print(part.name, part_name) 
    
    if part_name == "FakeShad":
        D.objects.remove(part)
        continue
    
    part_mesh = part.data
    
    is_socket = False
    move_bone = False

    
    if part_name in (EXTRA_JOINTS + SOCKETS):
        is_socket = part_name in SOCKETS
        part_name = ["", "_"][is_socket] + part_name
        
        if not part_name in arm.edit_bones:
            new_bone = arm.edit_bones.new(part_name)
            new_bone.tail = BONE_TAIL
            move_bone = True    
    

    if part_name in map(lambda b: b.name, arm.edit_bones):
        move_bone = True
        
    if move_bone:
        bone = arm.edit_bones[part_name]
        bone.matrix = part.matrix_world @ Matrix.Rotation(radians(90.0), 4, 'X')
        
        if part_name[2:] == "Wheel":
            reactor_name = part_name[:2] + "Reactor"
            bone = arm.edit_bones[reactor_name]
            bone.matrix = part.matrix_world @ Matrix.Rotation(radians(90.0), 4, 'X')
    
    if is_socket:
        D.objects.remove(part)
        continue
    
    
    if part_mesh and not is_socket:
        bpy.ops.object.mode_set(mode='OBJECT')
        
        if mat_letter in MATS:
            mat_name = MATS[mat_letter]
            mat = D.materials.get(mat_name, D.materials.new(name=mat_name))
            part_mesh.materials.clear()
            part_mesh.materials.append(mat)
        
        bpy.ops.object.select_all(action='DESELECT')
        part.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.parent_set(type='ARMATURE_NAME')
        
        if part_name in part.vertex_groups:
            vert_group = part.vertex_groups[part_name]
        else:
            vert_group = part.vertex_groups["Body"]
        
        all_verts = range(len(part_mesh.vertices))
        vert_group.add(all_verts, 1.0, "REPLACE")
    

