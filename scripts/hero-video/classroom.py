#!/usr/bin/env python3
"""Builds the home page classroom scene in Blender and renders it as PNG frames.

An ustazah teaches ten students. Everything is made from simple shapes in this
file, so there are no model files to download or license. The motion repeats
exactly, so the finished video loops without a jump.

    pip install bpy                    # Blender as a Python module
    python3 classroom.py --out frames  # about 20 seconds a frame on 2 CPU cores, 100 frames

Then turn the frames into the files the page uses: see README.md beside this file.
"""

import argparse
import math
import os
import random

import bpy
import bmesh  # only importable after bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument("--out", default="frames")
parser.add_argument("--width", type=int, default=960)
parser.add_argument("--height", type=int, default=540)
parser.add_argument("--samples", type=int, default=16)
parser.add_argument("--fps", type=int, default=20)
parser.add_argument("--seconds", type=float, default=5.0)
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--end", type=int, default=None, help="one past the last frame")
parser.add_argument("--step", type=int, default=1)
args = parser.parse_args()

random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
TAU = math.tau


# Materials ----------------------------------------------------------------


def rgb(hex_color):
    """A web colour such as '#1f5539' as the linear values Blender expects."""
    h = hex_color.lstrip("#")
    srgb = [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*linear, 1.0)


MATERIALS = {}


def material(hex_color, rough=0.7, name=None):
    key = name or f"{hex_color}-{rough}"
    if key in MATERIALS:
        return MATERIALS[key]

    mat = bpy.data.materials.new(key)
    try:
        mat.use_nodes = True
    except Exception:  # newer Blender versions always use nodes
        pass
    tree = mat.node_tree
    bsdf = next((n for n in tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        tree.nodes.clear()
        bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
        out = tree.nodes.new("ShaderNodeOutputMaterial")
        tree.links.new(bsdf.outputs[0], out.inputs[0])
    bsdf.inputs["Base Color"].default_value = rgb(hex_color)
    bsdf.inputs["Roughness"].default_value = rough
    MATERIALS[key] = mat
    return mat


def principled(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def carpet_material():
    mat = material("#0f5f86", 0.95, "carpet")
    tree = mat.node_tree
    try:
        noise = tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 900
        bump = tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.25
        tree.links.new(noise.outputs[0], bump.inputs["Height"])
        tree.links.new(bump.outputs[0], principled(mat).inputs["Normal"])
    except Exception:
        pass
    return mat


def patterned_material(dark, light, name):
    """A two-tone print, like batik, for the ustazah's dress."""
    mat = material(dark, 0.8, name)
    tree = mat.node_tree
    try:
        voronoi = tree.nodes.new("ShaderNodeTexVoronoi")
        voronoi.inputs["Scale"].default_value = 22
        ramp = tree.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.42
        ramp.color_ramp.elements[0].color = rgb(dark)
        ramp.color_ramp.elements[1].position = 0.5
        ramp.color_ramp.elements[1].color = rgb(light)
        tree.links.new(voronoi.outputs["Distance"], ramp.inputs[0])
        tree.links.new(ramp.outputs[0], principled(mat).inputs["Base Color"])
    except Exception:
        pass
    return mat


def glow_material(hex_color, strength, name):
    mat = material(hex_color, 0.5, name)
    bsdf = principled(mat)
    for socket in ("Emission Color", "Emission"):
        if socket in bsdf.inputs:
            bsdf.inputs[socket].default_value = rgb(hex_color)
            break
    bsdf.inputs["Emission Strength"].default_value = strength
    return mat


# Shapes -------------------------------------------------------------------


def add_object(name, mesh_builder, loc, mat, parent=None, rot=(0, 0, 0), bevel=0.0):
    bm = bmesh.new()
    mesh_builder(bm)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    if mat:
        mesh.materials.append(mat)
    if parent:
        obj.parent = parent
    if bevel:
        modifier = obj.modifiers.new("bevel", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    return obj


def box(name, size, loc, mat, parent=None, rot=(0, 0, 0), bevel=0.006):
    def build(bm):
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)

    return add_object(name, build, loc, mat, parent, rot, bevel)


def ball(name, radius, loc, mat, parent=None, scale=(1, 1, 1)):
    def build(bm):
        bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=radius)
        bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)
        for face in bm.faces:
            face.smooth = True

    return add_object(name, build, loc, mat, parent)


def cone(name, r_bottom, r_top, depth, loc, mat, parent=None, rot=(0, 0, 0), scale=(1, 1, 1)):
    def build(bm):
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=28,
            radius1=r_bottom, radius2=r_top, depth=depth,
        )
        bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)
        for face in bm.faces:
            face.smooth = len(face.verts) == 4  # round sides, flat ends

    return add_object(name, build, loc, mat, parent, rot)


def limb(name, start, end, radius, mat, parent=None):
    """A rounded tube between two points: an arm, a leg, a pole."""
    a, b = Vector(start), Vector(end)
    direction = b - a
    tube = cone(name, radius, radius, direction.length, (a + b) / 2, mat, parent)
    tube.rotation_mode = "QUATERNION"
    tube.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(direction.normalized())
    ball(name + "-a", radius, a, mat, parent)
    ball(name + "-b", radius, b, mat, parent)
    return tube


def empty(name, loc, parent=None, rot=(0, 0, 0)):
    obj = bpy.data.objects.new(name, None)
    scene.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    if parent:
        obj.parent = parent
    return obj


# Colours ------------------------------------------------------------------

WALL = material("#f3efe6", 0.9)
SKIN = [material(c, 0.55) for c in ("#c98f6b", "#d6a07a", "#b97f5c", "#cf9873")]
EYE = material("#1c1410", 0.2)
HAIR = material("#1d1512", 0.6)
WHITE_CLOTH = material("#f5f2ea", 0.85)
CHAIR = material("#a9c9e2", 0.35, "chair")
TABLE_TOP = material("#dcdcdc", 0.45)
METAL_BLACK = material("#1b1b1d", 0.4)
SOCK = material("#2a2a2e", 0.9)
BOY_CLOTH = ["#f5f2ea", "#f5f2ea", "#e3e9f0", "#efe7d6", "#f5f2ea"]
GIRL_CLOTH = ["#f5f2ea", "#f1d9de", "#e9e4f3", "#f5f2ea", "#efe7d6"]
TUDUNG = ["#f7f5f0", "#f7f5f0", "#cfd1d8", "#f7f5f0", "#34343a"]
STATIONERY = ["#f06f9b", "#4fb7e6", "#7ccf6b", "#f2b233", "#9a6fd6", "#ef6a4c"]


# Room ---------------------------------------------------------------------


def build_room():
    box("floor", (9.4, 10.5, 0.1), (0, -1.0, -0.05), carpet_material(), bevel=0)
    box("wall-front", (9.4, 0.2, 3.3), (0, 4.1, 1.65), WALL, bevel=0)
    box("wall-left", (0.2, 10.5, 3.3), (-4.6, -1.0, 1.65), WALL, bevel=0)
    box("wall-right", (0.2, 10.5, 3.3), (4.6, -1.0, 1.65), WALL, bevel=0)
    skirting = material("#d9d2c4", 0.6)
    box("skirting-front", (9.2, 0.03, 0.1), (0, 3.985, 0.05), skirting)
    box("skirting-left", (0.03, 10.3, 0.1), (-4.485, -1.0, 0.05), skirting)

    # Window with daylight, and grey curtains drawn to each side.
    box("window", (0.04, 2.3, 1.5), (-4.48, 1.3, 1.75), glow_material("#eef6ff", 3.0, "daylight"), bevel=0)
    box("window-frame", (0.06, 2.42, 0.06), (-4.47, 1.3, 0.98), WALL)
    box("window-bar", (0.05, 0.05, 1.5), (-4.47, 1.3, 1.75), WALL)
    curtain = material("#8b8792", 0.9, "curtain")
    for start in (-1.2, 2.35):
        for i in range(9):
            y = start + i * 0.15
            cone("pleat", 0.085, 0.085, 2.7, (-4.4, y, 1.42), curtain, scale=(0.7, 1, 1))
    limb("curtain-rod", (-4.4, -1.5, 2.82), (-4.4, 3.8, 2.82), 0.02, material("#6b4a3a", 0.5))

    # Whiteboard on a stand, with hijaiyah letters.
    frame = material("#b9bcc2", 0.35)
    box("board-frame", (1.96, 0.04, 1.26), (-1.0, 3.55, 1.5), frame)
    box("board", (1.86, 0.02, 1.16), (-1.0, 3.525, 1.5), material("#fdfdfb", 0.25), bevel=0)
    box("board-tray", (1.6, 0.08, 0.03), (-1.0, 3.5, 0.9), frame)
    for x in (-1.85, -0.15):
        limb("board-leg", (x, 3.58, 0.03), (x, 3.58, 0.95), 0.022, METAL_BLACK)
        limb("board-foot", (x, 3.3, 0.03), (x, 3.86, 0.03), 0.022, METAL_BLACK)
    write_on_board("ث  ت  ب  ا", (-1.0, 3.512, 1.5), 0.5, "#16302a")
    write_on_board("خ  ح  ج", (-1.0, 3.512, 1.08), 0.34, "#1f4fa3")

    # Wall clock, air conditioner, poster and framed certificates.
    clock_rot = (math.radians(90), 0, 0)
    cone("clock-rim", 0.19, 0.19, 0.04, (1.25, 3.97, 2.55), material("#f2a3c0", 0.4), rot=clock_rot)
    cone("clock-face", 0.155, 0.155, 0.045, (1.25, 3.968, 2.55), material("#ffffff", 0.4), rot=clock_rot)
    box("clock-hand", (0.012, 0.01, 0.1), (1.25, 3.94, 2.59), METAL_BLACK, bevel=0)
    box("clock-hand", (0.08, 0.01, 0.012), (1.28, 3.94, 2.55), METAL_BLACK, bevel=0)
    box("aircon", (1.05, 0.24, 0.3), (-2.9, 3.86, 2.8), material("#fbfbfb", 0.35), bevel=0.03)
    box("aircon-vent", (0.95, 0.02, 0.03), (-2.9, 3.74, 2.7), material("#c9c9c9", 0.5), bevel=0)

    box("poster", (1.5, 0.015, 1.05), (2.9, 3.985, 1.9), material("#62b85c", 0.7), bevel=0)
    box("poster-panel", (0.6, 0.016, 0.8), (3.28, 3.98, 1.9), material("#f4f7ea", 0.7), bevel=0)
    for i, colour in enumerate(("#f2b233", "#4fb7e6", "#ef6a4c")):
        ball("poster-dot", 0.11, (2.42 + i * 0.16, 3.98, 2.15 - i * 0.24), material(colour, 0.6), scale=(1, 0.08, 1))

    gold = material("#b08a3c", 0.4)
    for row in range(2):
        for col in range(3):
            x, z = -3.95 + col * 0.52, 1.95 - row * 0.52
            box("certificate-frame", (0.42, 0.02, 0.34), (x, 3.985, z), gold)
            box("certificate", (0.34, 0.022, 0.26), (x, 3.983, z), material("#fbf6e6", 0.6), bevel=0)

    # A plant in the corner.
    cone("pot", 0.13, 0.17, 0.34, (-4.0, 3.5, 0.17), material("#f4f1ea", 0.4))
    leaf = material("#3f8a4c", 0.6)
    for i in range(9):
        angle = i * 2.4
        ball("leaf", 0.16, (-4.0 + 0.16 * math.cos(angle), 3.5 + 0.16 * math.sin(angle), 0.55 + 0.07 * i),
             leaf, scale=(0.75, 0.75, 1.0))


def write_on_board(text, loc, size, colour):
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if not os.path.exists(font_path):
        return  # no font with Arabic letters on this computer: leave the board blank
    curve = bpy.data.curves.new("board-text", "FONT")
    curve.body = text  # isolated letters, typed right to left
    curve.font = bpy.data.fonts.load(font_path, check_existing=True)
    curve.size = size
    curve.align_x = "CENTER"
    curve.extrude = 0.002
    obj = bpy.data.objects.new("board-text", curve)
    scene.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = (math.radians(90), 0, 0)
    curve.materials.append(material(colour, 0.5))


def build_table(x, y):
    root = empty("table", (x, y, 0))
    box("table-top", (1.24, 0.6, 0.03), (0, 0, 0.66), TABLE_TOP, root, bevel=0.008)
    for sx in (-0.56, 0.56):
        limb("table-leg", (sx, -0.24, 0.02), (sx, -0.24, 0.645), 0.013, METAL_BLACK, root)
        limb("table-leg", (sx, 0.24, 0.02), (sx, 0.24, 0.645), 0.013, METAL_BLACK, root)
        limb("table-bar", (sx, -0.24, 0.2), (sx, 0.24, 0.2), 0.011, METAL_BLACK, root)

    # Things on the table for each of the two seats.
    for seat in (-0.32, 0.32):
        tilt = (0, 0, random.uniform(-0.25, 0.25))
        box("paper", (0.21, 0.29, 0.003), (seat, -0.08, 0.677), material("#ffffff", 0.6), root, tilt, bevel=0)
        colour = material(random.choice(STATIONERY), 0.45)
        if random.random() < 0.6:
            box("folder", (0.24, 0.33, 0.012), (seat + random.uniform(-0.05, 0.05), 0.12, 0.682), colour, root,
                (0, 0, random.uniform(-0.5, 0.5)))
        else:
            box("pencil-case", (0.2, 0.07, 0.04), (seat, 0.2, 0.695), colour, root,
                (0, 0, random.uniform(-0.3, 0.3)), bevel=0.015)


# People -------------------------------------------------------------------


def build_chair(root):
    box("seat", (0.4, 0.4, 0.03), (0, -0.02, 0.4), CHAIR, root, bevel=0.012)
    box("seat-back", (0.38, 0.03, 0.3), (0, -0.215, 0.66), CHAIR, root, bevel=0.012)
    for sx in (-0.17, 0.17):
        limb("chair-leg", (sx, 0.15, 0.01), (sx, 0.15, 0.39), 0.016, CHAIR, root)
        limb("chair-leg", (sx, -0.2, 0.01), (sx, -0.215, 0.8), 0.016, CHAIR, root)


def build_face(head, skin, with_mouth=False):
    ball("skull", 0.105, (0, 0, 0.11), skin, head)
    for sx in (-0.037, 0.037):
        ball("eye", 0.011, (sx, 0.094, 0.125), EYE, head)
    if with_mouth:
        ball("mouth", 0.02, (0, 0.097, 0.075), material("#8f4a45", 0.5), head, scale=(1, 0.3, 0.3))


def build_student(index, x, y, girl, raised_side=0):
    """raised_side: -1 or 1 gives that arm a shoulder joint so it can be raised."""
    root = empty(f"student-{index}", (x, y, 0), rot=(0, 0, random.uniform(-0.08, 0.08)))
    build_chair(root)
    skin = random.choice(SKIN)
    cloth = material(random.choice(GIRL_CLOTH if girl else BOY_CLOTH), 0.85)

    ball("torso", 1, (0, 0, 0.64), cloth, root, scale=(0.165, 0.125, 0.25))
    ball("lap", 1, (0, 0.14, 0.47), cloth, root, scale=(0.16, 0.2, 0.085))
    for sx in (-0.08, 0.08):
        limb("shin", (sx, 0.3, 0.44), (sx, 0.32, 0.1), 0.05, cloth, root)
        ball("foot", 1, (sx, 0.36, 0.04), SOCK, root, scale=(0.045, 0.09, 0.04))

    arm = None
    for side in (-1, 1):
        if side == raised_side:
            # One straight arm on a shoulder joint, so it can swing up.
            arm = empty("shoulder", (side * 0.17, 0.0, 0.8), root)
            limb("arm", (0, 0, 0), (0.0, 0.4, 0.0), 0.04, cloth, arm)
            ball("hand", 0.038, (0.0, 0.45, 0.0), skin, arm)
        else:
            elbow = (side * 0.2, 0.14, 0.69)
            limb("upper-arm", (side * 0.17, 0.0, 0.8), elbow, 0.042, cloth, root)
            limb("forearm", elbow, (side * 0.11, 0.34, 0.705), 0.038, cloth, root)
            ball("hand", 0.036, (side * 0.1, 0.385, 0.708), skin, root)

    head = empty("head", (0, 0.01, 0.9), root)
    build_face(head, skin)
    if girl:
        tudung = material(random.choice(TUDUNG), 0.85)
        ball("tudung", 0.122, (0, -0.028, 0.112), tudung, head)
        cone("tudung-drape", 0.215, 0.1, 0.34, (0, -0.005, 0.8), tudung, root, scale=(1, 0.85, 1))
    else:
        ball("hair", 0.108, (0, -0.014, 0.117), HAIR, head)
        cone("kopiah", 0.099, 0.09, 0.075, (0, -0.006, 0.2), WHITE_CLOTH, head)

    return {"head": head, "arm": arm, "phase": random.uniform(0, TAU)}


def build_teacher(x, y):
    # Built facing +y, then turned to face the class.
    root = empty("ustazah", (x, y, 0), rot=(0, 0, math.pi + 0.2))
    skin = SKIN[1]
    dress = patterned_material("#4a2a66", "#b9a3d6", "dress")
    khimar = material("#5a2a5f", 0.85, "khimar")

    cone("dress", 0.27, 0.16, 1.22, (0, 0, 0.62), dress, root, scale=(1, 0.8, 1))
    cone("khimar", 0.27, 0.12, 0.52, (0, -0.01, 1.16), khimar, root, scale=(1, 0.82, 1))

    head = empty("head", (0, 0.0, 1.4), root)
    build_face(head, skin, with_mouth=True)
    ball("khimar-head", 0.125, (0, -0.027, 0.114), khimar, head)

    # Left arm holds a book against the body.
    elbow = (-0.25, 0.1, 1.04)
    limb("upper-arm", (-0.2, 0.0, 1.28), elbow, 0.045, dress, root)
    limb("forearm", elbow, (-0.09, 0.22, 1.07), 0.04, dress, root)
    ball("hand", 0.04, (-0.06, 0.25, 1.08), skin, root)
    box("book", (0.17, 0.035, 0.23), (0.0, 0.24, 1.1), material("#1f5539", 0.6), root, (0.25, 0, 0.1), bevel=0.004)

    # Right arm points at the whiteboard and moves.
    arm = empty("shoulder", (0.2, 0.0, 1.28), root)
    limb("upper-arm", (0, 0, 0), (0.27, 0.05, -0.03), 0.045, dress, arm)
    limb("forearm", (0.27, 0.05, -0.03), (0.5, 0.1, 0.06), 0.04, dress, arm)
    ball("hand", 0.04, (0.545, 0.11, 0.075), skin, arm)
    limb("marker", (0.56, 0.11, 0.08), (0.66, 0.12, 0.13), 0.012, material("#1f4fa3", 0.4), arm)

    return {"root": root, "head": head, "arm": arm}


# Scene --------------------------------------------------------------------

build_room()

TABLES = [(-1.3, 1.45), (1.3, 1.45), (-1.3, 0.05), (1.3, 0.05), (0.0, -1.35)]
students = []
for table_index, (tx, ty) in enumerate(TABLES):
    build_table(tx, ty)
    for seat_index, seat in enumerate((-0.32, 0.32)):
        # Girls on the left tables, boys on the right, one of each at the back.
        girl = tx < 0 or (tx == 0 and seat < 0)
        number = table_index * 2 + seat_index
        # The boy by the aisle in the second row puts his hand up.
        raised = -1 if number == 6 else 0
        students.append(build_student(number, tx + seat, ty - 0.45, girl, raised))

teacher = build_teacher(0.75, 3.05)

target = empty("camera-target", (0.0, 1.6, 0.95))
camera_data = bpy.data.cameras.new("camera")
camera_data.lens = 32
camera = bpy.data.objects.new("camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
track = camera.constraints.new("TRACK_TO")
track.target = target
track.track_axis = "TRACK_NEGATIVE_Z"
track.up_axis = "UP_Y"
CAMERA_HOME = Vector((2.4, -4.0, 2.25))


def add_area_light(name, loc, rot, size, watts, colour):
    data = bpy.data.lights.new(name, "AREA")
    data.size = size
    data.energy = watts
    data.color = colour
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    return obj


add_area_light("ceiling", (0, 0.5, 3.7), (0, 0, 0), 7.0, 560, (1.0, 0.96, 0.9))
add_area_light("window-fill", (-4.2, 1.3, 1.8), (0, math.radians(-90), 0), 2.2, 320, (0.9, 0.95, 1.0))

world = bpy.data.worlds.new("world")
scene.world = world
try:
    world.use_nodes = True
except Exception:
    pass
background = next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)
if background:
    background.inputs[0].default_value = (0.86, 0.91, 1.0, 1.0)
    background.inputs[1].default_value = 0.45


# Motion: every value repeats after one loop, so the video loops cleanly ------


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def pose(t):
    """Places everything for a moment t between 0 and 1 through the loop."""
    wave = math.sin(TAU * t)
    camera.location = CAMERA_HOME + Vector((0.3 * wave, 0.15 * math.cos(TAU * t), 0.04 * wave))

    teacher["arm"].rotation_euler = (0.0, -0.38 + 0.13 * math.sin(2 * TAU * t), 0.12 * math.sin(TAU * t + 1.0))
    teacher["head"].rotation_euler = (0.03 * math.sin(2 * TAU * t), 0.0, 0.18 * math.sin(TAU * t + 0.6))
    teacher["root"].rotation_euler = (0, 0, math.pi + 0.2 + 0.06 * wave)

    for student in students:
        phase = student["phase"]
        student["head"].rotation_euler = (
            0.05 * math.sin(2 * TAU * t + phase),
            0.0,
            0.1 * math.sin(TAU * t + phase),
        )
        if student["arm"]:
            up = smooth((t - 0.18) / 0.14) * (1 - smooth((t - 0.66) / 0.14))
            student["arm"].rotation_euler = (-0.25 + 1.75 * up, 0.0, 0.05 * up)


# Render -------------------------------------------------------------------

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = args.samples
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.05
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 4
scene.cycles.diffuse_bounces = 2
scene.cycles.glossy_bounces = 2
scene.cycles.transmission_bounces = 0
scene.cycles.caustics_reflective = False
scene.cycles.caustics_refractive = False
scene.render.use_persistent_data = True
scene.render.resolution_x = args.width
scene.render.resolution_y = args.height
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
try:
    scene.view_settings.look = "AgX - Punchy"  # livelier colours
except Exception:
    pass

total = round(args.fps * args.seconds)
end = total if args.end is None else min(args.end, total)
os.makedirs(args.out, exist_ok=True)

for frame in range(args.start, end, args.step):
    path = os.path.join(args.out, f"frame_{frame:04d}.png")
    if os.path.exists(path):
        continue  # lets a stopped render carry on where it left off
    pose(frame / total)
    bpy.context.view_layer.update()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f"rendered {frame + 1}/{total}", flush=True)
