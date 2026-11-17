#!/usr/bin/env python3
"""Builds the home page classroom scene in Blender and renders it as PNG frames.

An ustazah teaches ten students. The people are made with MPFB (the MakeHuman
plug-in for Blender), which gives real human proportions; their clothes, the
room and the furniture are built by this file. The motion repeats exactly, so
the finished video loops without a jump. Nobody in it is a real person.

Setup and the commands that turn the frames into the files the page uses are
in README.md beside this file.

    python3 classroom.py --out frames            # every frame
    python3 classroom.py --out test --end 1      # one frame, for a quick look
"""

import argparse
import math
import os
import random
import sys

import bpy
import bmesh  # only importable after bpy
from mathutils import Matrix, Quaternion, Vector

parser = argparse.ArgumentParser()
parser.add_argument("--out", default="frames")
parser.add_argument("--width", type=int, default=960)
parser.add_argument("--height", type=int, default=540)
parser.add_argument("--samples", type=int, default=32)
parser.add_argument("--fps", type=int, default=16)
parser.add_argument("--seconds", type=float, default=5.0)
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--end", type=int, default=None, help="one past the last frame")
parser.add_argument("--step", type=int, default=1)
args = parser.parse_args()

random.seed(11)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
TAU = math.tau
X_AXIS, Z_AXIS = Vector((1, 0, 0)), Vector((0, 0, 1))

import addon_utils  # noqa: E402  (must follow read_factory_settings)

if not addon_utils.enable("bl_ext.user_default.mpfb", default_set=True):
    sys.exit("MPFB is not installed in Blender. See README.md beside this file.")
from bl_ext.user_default.mpfb.services.humanservice import HumanService  # noqa: E402
from bl_ext.user_default.mpfb.services.targetservice import TargetService  # noqa: E402


# Materials ----------------------------------------------------------------


def rgb(hex_color, gain=1.0):
    """A web colour such as '#1f5539' as the linear values Blender expects."""
    h = hex_color.lstrip("#")
    srgb = [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*[min(c * gain, 1.0) for c in linear], 1.0)


MATERIALS = {}


def principled(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def set_input(node, name, value):
    if name in node.inputs:
        node.inputs[name].default_value = value


def material(hex_color, rough=0.6, name=None, **inputs):
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
    set_input(bsdf, "Base Color", rgb(hex_color))
    set_input(bsdf, "Roughness", rough)
    for input_name, value in inputs.items():
        set_input(bsdf, input_name.replace("_", " "), value)
    MATERIALS[key] = mat
    return mat


def textured(mat, low, high, scale, bump=0.0, kind="ShaderNodeTexNoise", stops=(0.35, 0.65)):
    """Gives a material a soft two-tone variation and, optionally, a surface relief."""
    tree = mat.node_tree
    bsdf = principled(mat)
    try:
        texture = tree.nodes.new(kind)
        texture.inputs["Scale"].default_value = scale
        ramp = tree.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = stops[0]
        ramp.color_ramp.elements[0].color = low
        ramp.color_ramp.elements[1].position = stops[1]
        ramp.color_ramp.elements[1].color = high
        tree.links.new(texture.outputs[0], ramp.inputs[0])
        tree.links.new(ramp.outputs[0], bsdf.inputs["Base Color"])
        if bump:
            relief = tree.nodes.new("ShaderNodeBump")
            relief.inputs["Strength"].default_value = bump
            tree.links.new(texture.outputs[0], relief.inputs["Height"])
            tree.links.new(relief.outputs[0], bsdf.inputs["Normal"])
    except Exception:
        pass  # plain colour is fine if a node name changes in a future Blender
    return mat


def fabric(hex_color, name=None):
    """Cloth: matt, with faint uneven shading that reads as soft folds."""
    key = name or f"fabric-{hex_color}"
    if key in MATERIALS:
        return MATERIALS[key]
    mat = material(hex_color, 0.85, key, Sheen_Weight=0.25)
    return textured(mat, rgb(hex_color, 0.86), rgb(hex_color, 1.05), 9.0, bump=0.25)


def floral(base, flower, name):
    """A dark cloth scattered with small light flowers."""
    mat = material(base, 0.8, name, Sheen_Weight=0.25)
    return textured(mat, rgb(flower), rgb(base), 70.0, kind="ShaderNodeTexVoronoi", stops=(0.1, 0.24))


def skin_material(hex_color):
    return material(
        hex_color, 0.5, f"skin-{hex_color}",
        Subsurface_Weight=0.12, Subsurface_Scale=0.012, Subsurface_Radius=(1.0, 0.4, 0.25),
    )


def glow_material(hex_color, strength, name):
    mat = material(hex_color, 0.5, name)
    bsdf = principled(mat)
    for socket in ("Emission Color", "Emission"):
        if socket in bsdf.inputs:
            bsdf.inputs[socket].default_value = rgb(hex_color)
            break
    set_input(bsdf, "Emission Strength", strength)
    return mat


def eye_material():
    mat = material("#ffffff", 0.15, "eye")
    tree = mat.node_tree
    attribute = tree.nodes.new("ShaderNodeAttribute")
    attribute.attribute_name = "Col"
    tree.links.new(attribute.outputs["Color"], principled(mat).inputs["Base Color"])
    return mat


# Shapes -------------------------------------------------------------------


def add_object(name, build, loc=(0, 0, 0), mat=None, parent=None, rot=(0, 0, 0), bevel=0.0, smooth=False):
    bm = bmesh.new()
    build(bm)
    if smooth:
        for face in bm.faces:
            face.smooth = True
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
        modifier.segments = 3
    return obj


def box(name, size, loc, mat, parent=None, rot=(0, 0, 0), bevel=0.006):
    def build(bm):
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)

    return add_object(name, build, loc, mat, parent, rot, bevel)


def ball(name, radius, loc, mat, parent=None, scale=(1, 1, 1)):
    def build(bm):
        bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=radius)
        bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)

    return add_object(name, build, loc, mat, parent, smooth=True)


def tube(name, start, end, radius, mat, parent=None, end_radius=None):
    """A round bar between two points: a table leg, a chair leg, a curtain rod."""
    a, b = Vector(start), Vector(end)
    direction = b - a

    def build(bm):
        bmesh.ops.create_cone(
            bm, cap_ends=True, segments=16, radius1=radius,
            radius2=end_radius or radius, depth=direction.length,
        )
        for face in bm.faces:
            face.smooth = len(face.verts) == 4

    obj = add_object(name, build, (a + b) / 2, mat, parent)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Z_AXIS.rotation_difference(direction.normalized())
    return obj


def disc(name, radius, depth, loc, mat, rot=(0, 0, 0)):
    def build(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=40, radius1=radius, radius2=radius, depth=depth)

    return add_object(name, build, loc, mat, rot=rot)


def curtain(name, x, y_start, width, z_low, z_high, mat):
    """A hanging cloth with pleats, built as a wavy sheet."""
    columns, rows = 48, 6

    def build(bm):
        grid = [
            [
                bm.verts.new((
                    x + 0.035 * math.sin(TAU * c / 6.0) * (0.6 + 0.4 * r / rows),
                    y_start + width * c / columns,
                    z_low + (z_high - z_low) * r / rows,
                ))
                for c in range(columns + 1)
            ]
            for r in range(rows + 1)
        ]
        for r in range(rows):
            for c in range(columns):
                bm.faces.new((grid[r][c], grid[r][c + 1], grid[r + 1][c + 1], grid[r + 1][c]))

    return add_object(name, build, mat=mat, smooth=True)


def empty(name, loc, parent=None, rot=(0, 0, 0)):
    obj = bpy.data.objects.new(name, None)
    scene.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    if parent:
        obj.parent = parent
    return obj


def refresh():
    bpy.context.view_layer.update()
    return bpy.context.evaluated_depsgraph_get()


# People -------------------------------------------------------------------

EYE_GROUPS = {"helper-l-eye", "helper-r-eye"}


def smoothstep(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


class Person:
    """One MPFB human with a skeleton, plus the tools to pose and dress it.

    Coordinates are in the skeleton's own space: metres, feet on the ground,
    facing -Y, the person's left hand on +X.
    """

    def __init__(self, name, age, gender, weight=0.5):
        macro = TargetService.get_default_macro_info_dict()
        macro.update(age=age, gender=gender, weight=weight, muscle=0.4)
        macro["race"] = {"asian": 1.0, "caucasian": 0.0, "african": 0.0}
        source = HumanService.create_human(scale=0.1, macro_detail_dict=macro)
        rig = HumanService.add_builtin_rig(source, "default")
        source.name, rig.name = f"{name}-source", name
        self.name, self.rig, self.source = name, rig, source

        # Freeze the body shape into the mesh, so pieces of it can be copied.
        for modifier in list(source.modifiers):
            source.modifiers.remove(modifier)
        shaped = [v.co.copy() for v in source.evaluated_get(refresh()).data.vertices]
        source.shape_key_clear()
        for vertex, co in zip(source.data.vertices, shaped):
            vertex.co = co
        source.data.update()
        self.rest = shaped
        source.modifiers.new("armature", "ARMATURE").object = rig
        source.hide_render = True
        for bone in rig.pose.bones:
            bone.rotation_mode = "QUATERNION"

        self._classify()
        self._measure()

    def _classify(self):
        """Works out which part of the body each vertex belongs to."""
        bones = self.rig.data.bones

        def under(bone):
            return {bone} | {child.name for child in bones[bone].children_recursive}

        hand = under("wrist.L") | under("wrist.R")
        foot = under("foot.L") | under("foot.R")
        region_of = {}
        for names, region in (
            (under("head"), "head"),
            ({"neck01", "neck02", "neck03"}, "neck"),
            (hand, "hand"),
            (foot, "foot"),
            ((under("clavicle.L") | under("clavicle.R")) - hand, "arm"),
            ((under("pelvis.L") | under("pelvis.R")) - foot, "leg"),
        ):
            for bone in names:
                region_of[bone] = region

        names = [group.name for group in self.source.vertex_groups]
        is_bone = [name in bones for name in names]
        self.region, self.dominant, self.flags = [], [], []
        for vertex in self.source.data.vertices:
            best, best_weight, flags = "", 0.0, set()
            for entry in vertex.groups:
                if is_bone[entry.group]:
                    if entry.weight > best_weight:
                        best, best_weight = names[entry.group], entry.weight
                elif entry.weight > 0:
                    flags.add(names[entry.group])
            self.dominant.append(best)
            self.flags.append(flags)
            self.region.append(region_of.get(best, "torso") if best else "")

    def _measure(self):
        joint = lambda bone: self.rig.data.bones[bone].head_local  # noqa: E731
        self.eye = joint("eye.L").copy()
        face = [i for i in range(len(self.rest)) if self.region[i] == "head" and self.is_body(i)]
        self.top_z = max(self.rest[i].z for i in face)
        self.head_size = self.top_z - self.eye.z
        self.chin_z = min(
            self.rest[i].z for i in face
            if abs(self.rest[i].x) < self.eye.x * 0.8 and self.rest[i].y < self.eye.y + 0.01
        )
        self.shoulder_z = joint("upperarm01.L").z
        self.waist_z = joint("spine03").z
        self.hip_z = joint("upperleg01.L").z
        self.knee_z = joint("lowerleg01.L").z
        self.neck_z = joint("neck02").z
        face_top = self.eye.z + 0.3 * self.head_size
        self.face_centre_z = (face_top + self.chin_z) / 2
        self.face_half_height = (face_top - self.chin_z) / 2
        self.face_half_width = 0.62 * self.head_size

    def is_body(self, i):
        return "body" in self.flags[i]

    def in_face(self, co, grow=1.0, back=0.045):
        """True for points on the part of the face a tudung leaves open."""
        across = co.x / (self.face_half_width * grow)
        up = (co.z - self.face_centre_z) / (self.face_half_height * grow)
        return co.y < self.eye.y + back and across * across + up * up < 1.0

    # Posing. Directions are given in the skeleton's space, not per bone.

    def turn(self, bone, axis, angle):
        pose_bone = self.rig.pose.bones[bone]
        refresh()
        matrix = pose_bone.matrix.copy()
        pivot = matrix.translation.copy()
        rotation = Quaternion(axis, angle).to_matrix().to_4x4()
        pose_bone.matrix = Matrix.Translation(pivot) @ rotation @ Matrix.Translation(-pivot) @ matrix
        refresh()

    def aim(self, bone, toward, direction):
        """Swings a limb so that it points from `bone` to `toward` along `direction`."""
        refresh()
        pose = self.rig.pose.bones
        current = (pose[toward].head - pose[bone].head).normalized()
        swing = current.rotation_difference(Vector(direction).normalized())
        self.turn(bone, swing.axis, swing.angle)

    def joint(self, bone):
        refresh()
        return self.rig.pose.bones[bone].head.copy()

    def snapshot(self, bones):
        return {bone: self.rig.pose.bones[bone].rotation_quaternion.copy() for bone in bones}

    def apply(self, pose):
        for bone, rotation in pose.items():
            self.rig.pose.bones[bone].rotation_quaternion = rotation

    def blend(self, first, second, amount):
        for bone in first:
            self.rig.pose.bones[bone].rotation_quaternion = first[bone].slerp(second[bone], amount)

    def remember_head(self):
        bone = self.rig.pose.bones["head"]
        refresh()
        self.head_rest = bone.rotation_quaternion.copy()
        self.head_world = bone.matrix.to_quaternion()

    def nod(self, yaw, pitch):
        """Turns the head a little away from its resting direction."""
        world = self.head_world
        offset = Quaternion(Z_AXIS, yaw) @ Quaternion(X_AXIS, pitch)
        self.rig.pose.bones["head"].rotation_quaternion = self.head_rest @ world.inverted() @ offset @ world

    def capture(self):
        """Records where the posed body is, for clothes that are draped over it."""
        evaluated = self.source.evaluated_get(refresh()).data
        self.posed = [v.co.copy() for v in evaluated.vertices]
        self.normal = [v.normal.copy() for v in evaluated.vertices]
        self.skin = {
            bone.name: bone.matrix @ bone.bone.matrix_local.inverted() for bone in self.rig.pose.bones
        }

    # Clothes and body parts.

    def _finish(self, obj, mat, displace=0.0, smooth=0, thickness=0.0):
        obj.data.materials.append(mat)
        obj.parent = self.rig
        obj.modifiers.new("armature", "ARMATURE").object = self.rig
        if displace:
            modifier = obj.modifiers.new("offset", "DISPLACE")
            modifier.strength, modifier.mid_level = displace, 0.0
        if smooth:
            modifier = obj.modifiers.new("smooth", "SMOOTH")
            modifier.factor, modifier.iterations = 0.5, smooth
        if thickness:
            modifier = obj.modifiers.new("thickness", "SOLIDIFY")
            modifier.thickness, modifier.offset = thickness, -1.0
        return obj

    def extract(self, name, keep, mat, displace=0.0, smooth=0):
        """Copies part of the body's surface: skin, or a close-fitting garment."""
        bm = bmesh.new()
        bm.from_mesh(self.source.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not keep(v.index)], context="VERTS")
        for face in bm.faces:
            face.smooth = True
            face.material_index = 0
        mesh = bpy.data.meshes.new(f"{self.name}-{name}")
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(mesh.name, mesh)
        scene.collection.objects.link(obj)
        for group in self.source.vertex_groups:  # same order, so the copied weights still match
            obj.vertex_groups.new(name=group.name)
        return self._finish(obj, mat, displace, smooth)

    def drape(self, name, keep, offset, mat, weights, hole=None, thickness=0.0, voxel=0.009):
        """Makes a loose garment by stretching cloth around part of the posed body.

        `weights(point)` says which bones each point of the cloth follows.
        `hole(point)` marks an opening, such as the face of a tudung.
        """
        bm = bmesh.new()
        for i in range(len(self.posed)):
            if keep(i):
                bm.verts.new(self.posed[i] + self.normal[i] * offset)
        bmesh.ops.convex_hull(bm, input=list(bm.verts))
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        rough = bpy.data.meshes.new("hull")
        bm.to_mesh(rough)
        bm.free()

        # Even out the surface, then round it off.
        temporary = bpy.data.objects.new("hull", rough)
        scene.collection.objects.link(temporary)
        remesh = temporary.modifiers.new("remesh", "REMESH")
        remesh.mode, remesh.voxel_size = "VOXEL", voxel
        soften = temporary.modifiers.new("smooth", "SMOOTH")
        soften.factor, soften.iterations = 0.5, 10
        mesh = bpy.data.meshes.new_from_object(temporary.evaluated_get(refresh()))
        mesh.name = f"{self.name}-{name}"
        bpy.data.objects.remove(temporary)
        bpy.data.meshes.remove(rough)

        # The cloth was shaped on the posed body. Move each point back to where it
        # would be on the unposed body, so that the skeleton can carry it from there.
        bm = bmesh.new()
        bm.from_mesh(mesh)
        if hole:
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if hole(f.calc_center_median())], context="FACES")
        layer = bm.verts.layers.deform.verify()
        bones = {}
        for vertex in bm.verts:
            blend = None
            for bone, weight in weights(vertex.co).items():
                if weight <= 0.001:
                    continue
                vertex[layer][bones.setdefault(bone, len(bones))] = weight
                part = self.skin[bone] * weight
                blend = part if blend is None else blend + part
            vertex.co = blend.inverted() @ vertex.co
        for face in bm.faces:
            face.smooth = True
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new(mesh.name, mesh)
        scene.collection.objects.link(obj)
        for bone in bones:
            obj.vertex_groups.new(name=bone)
        return self._finish(obj, mat, thickness=thickness)

    def attach(self, name, bone, build, mat, bevel=0.0):
        """Fixes a rigid object, built in unposed coordinates, to one bone."""
        obj = add_object(f"{self.name}-{name}", build, smooth=True)
        obj.vertex_groups.new(name=bone).add(range(len(obj.data.vertices)), 1.0, "REPLACE")
        self._finish(obj, mat)
        if bevel:
            modifier = obj.modifiers.new("bevel", "BEVEL")
            modifier.width, modifier.segments = bevel, 3
        return obj

    def place(self, x, y, z, facing):
        self.rig.location = (x, y, z)
        self.rig.rotation_euler = (0, 0, facing)

    def finish(self):
        bpy.data.objects.remove(self.source)


def paint_eyes(obj):
    """Colours each eyeball: white, with a brown iris and dark pupil at the front."""
    mesh = obj.data
    colours = mesh.color_attributes.new("Col", "BYTE_COLOR", "POINT")
    for side in (1, -1):
        vertices = [v for v in mesh.vertices if v.co.x * side > 0]
        if not vertices:
            continue
        centre = sum((v.co for v in vertices), Vector()) / len(vertices)
        radius = max((v.co - centre).length for v in vertices)
        for vertex in vertices:
            front = (centre.y - vertex.co.y) / radius
            colours.data[vertex.index].color = (
                (0.02, 0.015, 0.01, 1) if front > 0.9 else (0.12, 0.06, 0.03, 1) if front > 0.62 else (0.85, 0.83, 0.8, 1)
            )


SKIN_TONES = ["#c58c68", "#b97f5c", "#cf9a76", "#b07552"]
SOCKS = ["#f1f1ee", "#2b2b30", "#f1f1ee", "#8d8f98"]
HAIR = material("#17110e", 0.55, "hair")
EYE = eye_material()


def dress_basics(person, skin, socks):
    person.extract(
        "skin",
        lambda i: person.is_body(i)
        and (person.region[i] in ("head", "neck", "hand") or person.dominant[i].startswith("lowerarm02")),
        skin,
    )
    paint_eyes(person.extract("eyes", lambda i: bool(person.flags[i] & EYE_GROUPS), EYE))
    person.extract(
        "socks",
        lambda i: person.is_body(i)
        and (person.region[i] == "foot" or person.dominant[i].startswith("lowerleg02")),
        socks, displace=0.004, smooth=2,
    )


def dress_top(person, mat, hem):
    """A long-sleeved top. `hem` is how far down the thigh it reaches, 0 to 1."""
    hem_z = person.hip_z - hem * (person.hip_z - person.knee_z)
    person.extract(
        "top",
        lambda i: person.is_body(i)
        and (
            person.region[i] in ("torso", "arm")
            or (person.region[i] == "neck" and person.rest[i].z < person.neck_z)
            or (person.region[i] == "leg" and person.rest[i].z > hem_z)
        ),
        mat, displace=0.017, smooth=5,
    )


def dress_trousers(person, mat):
    person.extract(
        "trousers",
        lambda i: person.is_body(i)
        and (person.region[i] == "leg" or (person.region[i] == "torso" and person.rest[i].z < person.waist_z)),
        mat, displace=0.008, smooth=3,
    )


def dress_skirt(person, mat):
    person.drape(
        "skirt",
        lambda i: person.is_body(i)
        and (person.region[i] == "leg" or (person.region[i] == "torso" and person.rest[i].z < person.waist_z)),
        0.009, mat, lambda point: {"root": 1.0},
    )


def dress_tudung(person, mat, length, sleeves=("clavicle", "shoulder01", "upperarm01")):
    """A headscarf. `length` is how far it hangs from shoulder to hip, 0 to 1."""
    cape_z = person.shoulder_z - length * (person.shoulder_z - person.hip_z)
    chin = (person.skin["head"] @ Vector((0, person.eye.y, person.chin_z))).z
    shoulder = person.joint("upperarm01.L").z
    to_unposed_head = person.skin["head"].inverted()

    def weights(point):
        head = smoothstep((point.z - shoulder) / (chin - shoulder))
        return {"head": head, "spine01": 1.0 - head}

    person.drape(
        "tudung",
        lambda i: person.is_body(i)
        and (
            (person.region[i] == "head" and not person.in_face(person.rest[i]))
            or person.region[i] == "neck"
            or (
                person.rest[i].z > cape_z
                and (person.region[i] == "torso" or person.dominant[i].startswith(sleeves))
            )
        ),
        0.018, mat, weights,
        hole=lambda point: person.in_face(to_unposed_head @ point, grow=0.93, back=0.012),
        thickness=0.005, voxel=0.008,
    )


def dress_kopiah(person, mat):
    """A boy's cap and the hair that shows beneath it."""
    person.extract("hair", lambda i: person.is_body(i) and "scalp" in person.flags[i], HAIR, displace=0.005)
    base = person.eye.z + 0.42 * person.head_size
    band = [
        person.rest[i] for i in range(len(person.rest))
        if "scalp" in person.flags[i] and person.is_body(i) and abs(person.rest[i].z - base) < 0.012
    ]
    half_width = max(abs(co.x) for co in band) + 0.006
    front, back = min(co.y for co in band), max(co.y for co in band)
    height = person.top_z + 0.014 - base
    shape = Matrix.Translation((0, (front + back) / 2, base + height / 2)) @ Matrix.Diagonal(
        (half_width, (back - front) / 2 + 0.006, 1.0, 1.0)
    )
    person.attach(
        "kopiah", "head",
        lambda bm: bmesh.ops.create_cone(
            bm, cap_ends=True, segments=40, radius1=1.0, radius2=0.93, depth=height, matrix=shape
        ),
        mat, bevel=0.012,
    )


# Room ---------------------------------------------------------------------

SEAT, TABLE = 0.36, 0.60  # child-sized: height of the chair seat and of the table top
ROOM = {"left": -4.5, "right": 4.5, "front": 4.0, "back": -6.2, "height": 3.0}
WINDOWS = [(0.3, 2.5), (-2.7, -0.5)]  # along the left wall: start and end of each opening
WINDOW_LOW, WINDOW_HIGH = 1.0, 2.4

WALL = textured(material("#efeae0", 0.92, "wall"), rgb("#ebe6db"), rgb("#f3efe6"), 3.0)
TRIM = material("#fbfaf6", 0.45, "trim")
CHAIR = material("#a7c6de", 0.32, "chair-plastic")
TABLE_TOP = material("#e3e3e1", 0.35, "table-top")
METAL = material("#18181a", 0.35, "table-metal", Metallic=0.8)
STATIONERY = ["#f06f9b", "#4fb7e6", "#7ccf6b", "#f2b233", "#9a6fd6", "#ef6a4c"]


def build_room():
    left, right, front, back, height = (ROOM[k] for k in ("left", "right", "front", "back", "height"))
    depth, width, mid_y, mid_x = front - back, right - left, (front + back) / 2, (left + right) / 2

    carpet = textured(
        material("#12628a", 1.0, "carpet"), rgb("#115d85"), rgb("#14678f"), 700.0, bump=0.3
    )
    box("floor", (width + 0.4, depth + 0.4, 0.1), (mid_x, mid_y, -0.05), carpet, bevel=0)
    box("ceiling", (width + 0.4, depth + 0.4, 0.1), (mid_x, mid_y, height + 0.05), TRIM, bevel=0)
    box("wall-front", (width + 0.4, 0.2, height), (mid_x, front + 0.1, height / 2), WALL, bevel=0)
    box("wall-back", (width + 0.4, 0.2, height), (mid_x, back - 0.1, height / 2), WALL, bevel=0)
    box("wall-right", (0.2, depth, height), (right + 0.1, mid_y, height / 2), WALL, bevel=0)

    # The left wall is built around its windows, so that real sunlight comes in.
    x = left - 0.1
    box("wall-left-low", (0.2, depth, WINDOW_LOW), (x, mid_y, WINDOW_LOW / 2), WALL, bevel=0)
    box("wall-left-high", (0.2, depth, height - WINDOW_HIGH), (x, mid_y, (height + WINDOW_HIGH) / 2), WALL, bevel=0)
    edges = [back] + [edge for start, end in sorted(WINDOWS) for edge in (start, end)] + [front]
    for start, end in zip(edges[0::2], edges[1::2]):
        box("wall-left-pier", (0.2, end - start, WINDOW_HIGH - WINDOW_LOW),
            (x, (start + end) / 2, (WINDOW_LOW + WINDOW_HIGH) / 2), WALL, bevel=0)

    curtain_cloth = fabric("#8d8994", "curtain")
    for start, end in WINDOWS:
        middle, span, tall = (start + end) / 2, end - start, WINDOW_HIGH - WINDOW_LOW
        box("window-sill", (0.3, span + 0.1, 0.04), (left - 0.05, middle, WINDOW_LOW), TRIM)
        for y in (start + 0.02, middle, end - 0.02):
            box("window-bar", (0.05, 0.04, tall), (left - 0.1, y, WINDOW_LOW + tall / 2), TRIM, bevel=0)
        for z in (WINDOW_LOW + 0.02, WINDOW_HIGH - 0.02):
            box("window-bar", (0.05, span, 0.04), (left - 0.1, middle, z), TRIM, bevel=0)
        curtain("curtain", left + 0.1, start - 0.5, 0.62, 0.3, 2.72, curtain_cloth)
        curtain("curtain", left + 0.1, end - 0.12, 0.62, 0.3, 2.72, curtain_cloth)
        tube("curtain-rod", (left + 0.1, start - 0.6, 2.75), (left + 0.1, end + 0.6, 2.75), 0.014, METAL)

    for name, size, loc in (
        ("skirting-front", (width, 0.02, 0.09), (mid_x, front - 0.01, 0.045)),
        ("skirting-left", (0.02, depth, 0.09), (left + 0.01, mid_y, 0.045)),
        ("skirting-right", (0.02, depth, 0.09), (right - 0.01, mid_y, 0.045)),
    ):
        box(name, size, loc, TRIM, bevel=0.004)

    build_whiteboard(-1.0, front)

    # On the front wall: clock, air conditioner, a poster and framed certificates.
    facing_room = (math.radians(90), 0, 0)
    disc("clock-rim", 0.19, 0.04, (1.3, front - 0.03, 2.5), material("#f2a3c0", 0.35), facing_room)
    disc("clock-face", 0.155, 0.045, (1.3, front - 0.032, 2.5), material("#fdfdfd", 0.4), facing_room)
    box("clock-hand", (0.012, 0.01, 0.1), (1.3, front - 0.058, 2.54), METAL, bevel=0)
    box("clock-hand", (0.08, 0.01, 0.012), (1.33, front - 0.058, 2.5), METAL, bevel=0)
    box("aircon", (1.05, 0.24, 0.3), (-2.9, front - 0.13, 2.62), material("#fbfbfb", 0.3), bevel=0.03)
    box("aircon-vent", (0.95, 0.02, 0.03), (-2.9, front - 0.25, 2.52), material("#c9c9c9", 0.5), bevel=0)

    box("poster", (1.5, 0.012, 1.05), (3.0, front - 0.006, 1.85), material("#62b85c", 0.6), bevel=0)
    box("poster-panel", (0.62, 0.014, 0.82), (3.36, front - 0.008, 1.85), material("#f4f7ea", 0.6), bevel=0)
    for i, colour in enumerate(("#f2b233", "#4fb7e6", "#ef6a4c")):
        ball("poster-dot", 0.11, (2.5 + i * 0.16, front - 0.01, 2.1 - i * 0.24),
             material(colour, 0.5), scale=(1, 0.06, 1))

    gold, paper = material("#b08a3c", 0.35, "frame-gold", Metallic=0.6), material("#fbf6e6", 0.6)
    for row in range(2):
        for col in range(3):
            fx, fz = -3.95 + col * 0.52, 1.9 - row * 0.52
            box("certificate-frame", (0.42, 0.02, 0.34), (fx, front - 0.01, fz), gold)
            box("certificate", (0.34, 0.022, 0.26), (fx, front - 0.012, fz), paper, bevel=0)

    # A plant in the corner and a low shelf of books along the right wall.
    disc("pot", 0.16, 0.34, (-4.0, 3.5, 0.17), material("#f4f1ea", 0.35))
    for i in range(11):
        angle = i * 2.4
        ball("leaf", 0.16, (-4.0 + 0.17 * math.cos(angle), 3.5 + 0.17 * math.sin(angle), 0.5 + 0.065 * i),
             material("#3f8a4c", 0.5, "leaf"), scale=(0.7, 0.7, 1.0))

    wood = textured(material("#b98e5e", 0.5, "wood"), rgb("#a87f52"), rgb("#c49a68"), 14.0)
    for z in (0.02, 0.42, 0.82):
        box("shelf", (0.34, 1.7, 0.03), (right - 0.19, 2.6, z + 0.015), wood)
    for y in (1.76, 3.44):
        box("shelf-side", (0.34, 0.03, 0.85), (right - 0.19, y, 0.425), wood)
    for level in (0.05, 0.45):
        y = 1.82
        while y < 3.3:
            thick, tall = random.uniform(0.025, 0.06), random.uniform(0.22, 0.31)
            box("book", (0.22, thick, tall), (right - 0.2, y + thick / 2, level + tall / 2),
                material(random.choice(STATIONERY + ["#1f5539", "#7a4a2b", "#f3efe6"]), 0.55), bevel=0.003)
            y += thick + random.choice((0.003, 0.003, 0.05))


def build_whiteboard(x, wall):
    frame = material("#b4b7bd", 0.3, "aluminium", Metallic=0.9)
    y = wall - 0.42
    box("board-frame", (1.96, 0.04, 1.26), (x, y + 0.02, 1.45), frame)
    box("board", (1.86, 0.02, 1.16), (x, y - 0.005, 1.45), material("#fcfcfa", 0.18, "whiteboard"), bevel=0)
    box("board-tray", (1.6, 0.08, 0.025), (x, y - 0.04, 0.84), frame)
    for i, colour in enumerate(("#1f4fa3", "#16302a", "#c0392b")):
        tube("marker", (x - 0.5 + i * 0.17, y - 0.045, 0.864), (x - 0.38 + i * 0.17, y - 0.045, 0.864),
             0.01, material(colour, 0.35))
    box("eraser", (0.12, 0.05, 0.03), (x + 0.5, y - 0.045, 0.868), material("#2d3e50", 0.7))
    for side in (-0.85, 0.85):
        tube("board-leg", (x + side, y + 0.05, 0.03), (x + side, y + 0.05, 0.9), 0.02, METAL)
        tube("board-foot", (x + side, y - 0.25, 0.03), (x + side, y + 0.35, 0.03), 0.02, METAL)

    # Hijaiyah letters, written apart so that they read right to left.
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if not os.path.exists(font_path):
        return  # no font with Arabic letters on this computer: leave the board blank
    for text, z, size, colour in (
        ("ث  ت  ب  ا", 1.45, 0.5, "#16302a"),
        ("خ  ح  ج", 1.03, 0.34, "#1f4fa3"),
    ):
        curve = bpy.data.curves.new("board-text", "FONT")
        curve.body, curve.size, curve.align_x, curve.extrude = text, size, "CENTER", 0.001
        curve.font = bpy.data.fonts.load(font_path, check_existing=True)
        curve.materials.append(material(colour, 0.4))
        letters = bpy.data.objects.new("board-text", curve)
        scene.collection.objects.link(letters)
        letters.location = (x, y - 0.017, z)
        letters.rotation_euler = (math.radians(90), 0, 0)


def build_table(x, y):
    root = empty("table", (x, y, 0))
    box("table-top", (1.2, 0.5, 0.025), (0, 0, TABLE - 0.0125), TABLE_TOP, root, bevel=0.005)
    box("table-edge", (1.21, 0.51, 0.012), (0, 0, TABLE - 0.02), METAL, root, bevel=0.003)
    for sx in (-0.54, 0.54):
        for sy in (-0.2, 0.2):
            tube("table-leg", (sx, sy, 0.0), (sx, sy, TABLE - 0.025), 0.012, METAL, root)
        tube("table-bar", (sx, -0.2, 0.16), (sx, 0.2, 0.16), 0.01, METAL, root)

    paper = material("#fdfdfb", 0.55, "paper")
    for seat in (-0.3, 0.3):
        box("worksheet", (0.2, 0.28, 0.002), (seat, -0.06, TABLE + 0.001), paper, root,
            (0, 0, random.uniform(-0.2, 0.2)), bevel=0)
        colour = material(random.choice(STATIONERY), 0.4)
        if random.random() < 0.55:
            box("folder", (0.23, 0.31, 0.012), (seat + random.uniform(-0.04, 0.04), 0.13, TABLE + 0.006),
                colour, root, (0, 0, random.uniform(-0.5, 0.5)), bevel=0.003)
        else:
            box("pencil-case", (0.19, 0.07, 0.04), (seat, 0.18, TABLE + 0.02), colour, root,
                (0, 0, random.uniform(-0.4, 0.4)), bevel=0.015)


def build_chair(x, y):
    """A small plastic chair facing the front of the room."""
    root = empty("chair", (x, y, 0), rot=(0, 0, random.uniform(-0.06, 0.06)))
    box("seat", (0.36, 0.36, 0.03), (0, 0, SEAT - 0.015), CHAIR, root, bevel=0.014)
    box("seat-back", (0.34, 0.03, 0.24), (0, -0.2, SEAT + 0.26), CHAIR, root, (math.radians(-8), 0, 0), bevel=0.014)
    for sx in (-0.15, 0.15):
        tube("chair-leg", (sx * 1.15, 0.17, 0.0), (sx, 0.14, SEAT - 0.02), 0.02, CHAIR, root, end_radius=0.015)
        tube("chair-leg", (sx * 1.15, -0.2, 0.0), (sx, -0.16, SEAT - 0.02), 0.02, CHAIR, root, end_radius=0.015)
        tube("chair-post", (sx, -0.165, SEAT - 0.02), (sx, -0.205, SEAT + 0.2), 0.015, CHAIR, root)
    if random.random() < 0.5:
        bag = material(random.choice(STATIONERY + ["#2b2b30", "#24406b"]), 0.7)
        side = random.choice((-0.33, 0.33))
        box("bag", (0.17, 0.3, 0.38), (side, -0.1, 0.19), bag, root, (0, 0, random.uniform(-0.3, 0.3)), bevel=0.05)
        box("bag-pocket", (0.18, 0.22, 0.17), (side, -0.1, 0.12), bag, root, (0, 0, random.uniform(-0.1, 0.1)), bevel=0.04)


# The class ----------------------------------------------------------------

BOARD_POINT = Vector((-0.9, 3.5, 1.4))
BOY_TOPS = ["#f4f1e9", "#f4f1e9", "#dfe7ef", "#ece3d0", "#f4f1e9"]
GIRL_TOPS = ["#f4f1e9", "#f0d6dc", "#e6e0f1", "#f4f1e9", "#d9e8e2"]
SKIRTS = ["#3a3f5c", "#f1ede4", "#5a4a6e", "#2f4a52", "#f1ede4"]
TUDUNGS = ["#f6f4ef", "#f6f4ef", "#cdd0d8", "#f6f4ef", "#2e2e34"]


def make_student(index, x, y, girl, looks_at, writing=False, raises=None):
    """Seats one child at a desk. `raises` is 'L' or 'R' for a child who puts a hand up."""
    person = Person(f"student-{index}", random.uniform(0.165, 0.205), 0.0 if girl else 1.0, random.uniform(0.38, 0.6))
    height = SEAT + 0.055 - person.hip_z  # lifts or lowers the skeleton so that it sits on the seat
    desk = TABLE + 0.03 - height

    person.turn("spine04", X_AXIS, math.radians(random.uniform(6, 11) + (7 if writing else 0)))
    for side, sign in (("L", 1), ("R", -1)):
        person.aim(f"upperleg01.{side}", f"lowerleg01.{side}", (sign * random.uniform(0.05, 0.16), -1, 0.02))
        person.aim(f"lowerleg01.{side}", f"foot.{side}", (sign * 0.02, random.uniform(-0.05, 0.22), -1))
        person.aim(f"upperarm01.{side}", f"lowerarm01.{side}", (sign * 0.4, -0.72, -0.5))
        hand = Vector((sign * random.uniform(0.05, 0.11), random.uniform(-0.37, -0.31), desk))
        person.aim(f"lowerarm01.{side}", f"wrist.{side}", hand - person.joint(f"lowerarm01.{side}"))

    # Turn the head toward what the child is looking at. The child faces +Y in the room.
    yaw = max(-0.6, min(0.6, math.atan2(-(looks_at.x - x), looks_at.y - y))) if not writing else random.uniform(-0.1, 0.1)
    person.turn("neck01", Z_AXIS, yaw * 0.4)
    person.turn("head", Z_AXIS, yaw * 0.6)
    person.turn("head", X_AXIS, 0.42 if writing else -0.04)
    person.remember_head()

    motion = {}
    if raises:
        arm = [f"upperarm01.{raises}", f"lowerarm01.{raises}"]
        sign = 1 if raises == "L" else -1
        down = person.snapshot(arm)
        person.aim(arm[0], arm[1], (sign * 0.3, -0.3, 0.9))
        person.aim(arm[1], f"wrist.{raises}", (sign * 0.05, -0.08, 1.0))
        motion["raise"] = (down, person.snapshot(arm))
        person.apply(down)
    if writing:
        arm = ["lowerarm01.R"]
        still = person.snapshot(arm)
        person.aim(arm[0], "wrist.R", person.joint("wrist.R") + Vector((0.035, 0.0, 0.0)) - person.joint(arm[0]))
        motion["write"] = (still, person.snapshot(arm))
        person.apply(still)

    person.capture()
    dress_basics(person, skin_material(random.choice(SKIN_TONES)), material(random.choice(SOCKS), 0.9))
    if girl:
        dress_top(person, fabric(random.choice(GIRL_TOPS)), hem=0.2)
        dress_skirt(person, fabric(random.choice(SKIRTS)))
        dress_tudung(person, fabric(random.choice(TUDUNGS)), length=0.28)
    else:
        top = random.choice(BOY_TOPS)
        dress_top(person, fabric(top), hem=0.5)
        dress_trousers(person, fabric(random.choice([top, "#3a3f5c", "#2b2b30"])))
        dress_kopiah(person, material(random.choice(["#f7f5ef", "#f7f5ef", "#efe9da"]), 0.75))
    person.place(x, y, height, math.pi)
    person.finish()
    return {"person": person, "motion": motion, "phase": random.uniform(0, TAU)}


def make_teacher(x, y, facing):
    person = Person("ustazah", 0.78, 0.0, 0.62)
    person.aim("upperarm01.R", "lowerarm01.R", (-0.86, 0.12, 0.02))
    person.aim("upperarm01.L", "lowerarm01.L", (0.2, -0.08, -0.97))
    person.aim("lowerarm01.L", "wrist.L", (-0.5, -0.62, -0.25))
    person.turn("head", Z_AXIS, -0.1)
    person.turn("head", X_AXIS, 0.1)
    person.remember_head()

    arm = ["upperarm01.R", "lowerarm01.R"]
    person.aim(arm[1], "wrist.R", (-0.8, 0.28, 0.42))
    high = person.snapshot(arm)
    person.aim(arm[0], arm[1], (-0.86, 0.12, -0.12))
    person.aim(arm[1], "wrist.R", (-0.88, 0.3, 0.12))
    low = person.snapshot(arm)
    person.blend(high, low, 0.5)

    person.capture()
    dress_basics(person, skin_material("#bd8560"), material("#2b2b30", 0.9))
    robe = fabric("#a9506b", "robe")
    dress_top(person, robe, hem=0.6)
    dress_skirt(person, robe)
    dress_tudung(person, floral("#1c2244", "#9fb4e6", "tudung-floral"), length=0.5)

    # A whiteboard marker in the pointing hand.
    wrist = person.rig.data.bones["wrist.R"]
    along = (wrist.tail_local - wrist.head_local).normalized()
    grip = Matrix.Translation(wrist.tail_local + along * 0.1) @ along.to_track_quat("Z", "Y").to_matrix().to_4x4()
    person.attach(
        "marker", "wrist.R",
        lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.009, radius2=0.009, depth=0.13, matrix=grip),
        material("#1f4fa3", 0.35),
    )
    person.place(x, y, 0.0, facing)
    person.finish()
    return {"person": person, "motion": {"point": (high, low)}}


build_room()

TABLES = [(-1.35, 1.5), (1.25, 1.5), (-1.35, 0.0), (1.25, 0.0), (-0.05, -1.5)]
TEACHER_SPOT = Vector((0.5, 3.12, 1.3))
students = []
for table_index, (tx, ty) in enumerate(TABLES):
    build_table(tx, ty)
    for seat_index, seat in enumerate((-0.3, 0.3)):
        number = table_index * 2 + seat_index
        # Girls at the left tables, boys at the right, one of each at the back.
        girl = tx < -0.5 or (abs(tx) < 0.5 and seat < 0)
        build_chair(tx + seat, ty - 0.47)
        students.append(
            make_student(
                number, tx + seat, ty - 0.42, girl,
                looks_at=TEACHER_SPOT if number % 3 else BOARD_POINT,
                writing=number in (0, 5, 8),
                raises="L" if number == 6 else None,  # the boy by the aisle in the second row
            )
        )
teacher = make_teacher(TEACHER_SPOT.x, TEACHER_SPOT.y, 0.22)


# Camera and light ---------------------------------------------------------

target = empty("camera-target", (-0.15, 1.9, 0.92))
camera_data = bpy.data.cameras.new("camera")
camera_data.lens = 30
camera_data.dof.use_dof = True
camera_data.dof.focus_object = empty("focus", (0.2, 2.4, 1.0))
camera_data.dof.aperture_fstop = 2.2
camera = bpy.data.objects.new("camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
track = camera.constraints.new("TRACK_TO")
track.target = target
track.track_axis, track.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
CAMERA_HOME = Vector((2.55, -3.7, 1.95))


def add_light(name, kind, loc, rot, energy, colour, size=1.0, size_y=None):
    data = bpy.data.lights.new(name, kind)
    data.energy, data.color = energy, colour
    if kind == "AREA":
        data.size = size
        if size_y:
            data.shape, data.size_y = "RECTANGLE", size_y
    else:
        data.angle = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location, obj.rotation_euler = loc, rot
    obj.visible_camera = False
    return obj


# Low morning sun through the windows, reaching the aisle and the front of the room,
# plus soft ceiling lights and daylight from each window.
sun = add_light("sun", "SUN", (-8, 3, 6), (0, 0, 0), 8.5, (1.0, 0.86, 0.68), size=math.radians(1.5))
sun.rotation_mode = "QUATERNION"
sun.rotation_quaternion = Vector((0.85, 0.42, -0.32)).to_track_quat("-Z", "Y")
for y in (1.6, -1.8):
    add_light("ceiling-light", "AREA", (0, y, ROOM["height"] - 0.05), (0, 0, 0), 45, (1.0, 0.97, 0.93), 4.5, 1.4)
for start, end in WINDOWS:
    add_light("daylight", "AREA", (ROOM["left"] + 0.05, (start + end) / 2, 1.7), (0, math.radians(-90), 0),
              55, (0.86, 0.93, 1.0), end - start, WINDOW_HIGH - WINDOW_LOW)

world = bpy.data.worlds.new("world")
scene.world = world
try:
    world.use_nodes = True
except Exception:
    pass
background = next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)
if background:
    background.inputs[0].default_value = (0.78, 0.88, 1.0, 1.0)
    background.inputs[1].default_value = 3.0


# Motion: every value repeats after one loop, so the video loops cleanly ------


def pose(t):
    """Places everything for a moment t between 0 and 1 through the loop."""
    wave = math.sin(TAU * t)
    camera.location = CAMERA_HOME + Vector((0.28 * wave, 0.14 * math.cos(TAU * t), 0.035 * wave))

    for student in students:
        person, motion, phase = student["person"], student["motion"], student["phase"]
        person.nod(0.07 * math.sin(TAU * t + phase), 0.035 * math.sin(2 * TAU * t + phase))
        if "raise" in motion:
            up = smoothstep((t - 0.16) / 0.16) * (1 - smoothstep((t - 0.68) / 0.16))
            person.blend(*motion["raise"], up)
        if "write" in motion:
            person.blend(*motion["write"], 0.5 + 0.5 * math.sin(5 * TAU * t + phase))

    person = teacher["person"]
    person.blend(*teacher["motion"]["point"], 0.5 + 0.5 * math.sin(2 * TAU * t))
    person.nod(0.16 * math.sin(TAU * t + 0.5), 0.03 * math.sin(2 * TAU * t))


# Render -------------------------------------------------------------------

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = args.samples
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.04
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 5
scene.cycles.diffuse_bounces = 3
scene.cycles.glossy_bounces = 2
scene.cycles.transmission_bounces = 0
scene.cycles.sample_clamp_indirect = 4.0
scene.cycles.caustics_reflective = False
scene.cycles.caustics_refractive = False
scene.render.use_persistent_data = True
scene.render.resolution_x = args.width
scene.render.resolution_y = args.height
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.view_settings.exposure = 1.1  # the room is lit for the sun patches, so brighten the rest
try:
    scene.view_settings.look = "AgX - Medium High Contrast"
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
    refresh()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f"rendered {frame + 1}/{total}", flush=True)
