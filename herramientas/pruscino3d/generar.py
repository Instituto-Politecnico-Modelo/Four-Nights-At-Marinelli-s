"""Orquestador: construye Pruscino 3D en Blender y exporta a .glb para Godot.

Uso (desde la raiz del proyecto):
    blender -b -P herramientas/pruscino3d/generar.py -- exportar
    blender -b -P herramientas/pruscino3d/generar.py -- previa <carpeta_salida> [rapido]
"""
import math
import os
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import bpy
from mathutils import Vector

import texturas
import geometria as G
import modelo
import rig

RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
SALIDA = os.path.join(RAIZ, "assets", "Animatronicos", "Prus3D", "Pruscino", "modelo3d")


def limpiar():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def construir():
    tmp = tempfile.mkdtemp(prefix="pruscino_tex_")
    texturas.generar_todas(tmp)
    M = modelo.crear_materiales(tmp)
    modelo.construir_todo(M)
    malla = modelo.ensamblar()
    arm = rig.crear_armadura()
    rig.enlazar(malla, arm)
    bpy.context.scene.render.fps = 30
    rig.crear_animaciones(arm)
    return malla, arm


def exportar(malla, arm):
    os.makedirs(SALIDA, exist_ok=True)
    ruta = os.path.join(SALIDA, "pruscino.glb")
    bpy.ops.object.select_all(action="DESELECT")
    malla.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.gltf(
        filepath=ruta, export_format="GLB", use_selection=True,
        export_animations=True, export_animation_mode="ACTIONS", export_force_sampling=True,
        export_skins=True, export_yup=True, export_apply=False, export_image_format="AUTO",
        export_materials="EXPORT", export_normals=True, export_texcoords=True,
        export_optimize_animation_size=False, export_extras=False)
    print("EXPORTADO", ruta, os.path.getsize(ruta) // 1024, "KB")


# ---------------------------------------------------------------- previsualizacion
def escena_estudio():
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 40
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 800, 1000
    w = bpy.data.worlds.new("Mundo")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.014, 0.02, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    sc.view_settings.view_transform = "Filmic" if "Filmic" in [
        i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "AgX"
    # suelo
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0))
    suelo = bpy.context.active_object
    m = bpy.data.materials.new("Suelo")
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.12, 0.12, 0.13, 1)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
    suelo.data.materials.append(m)
    # luces
    def luz(tipo, loc, energia, color, tam=1.0, apunta=(0, 0, 1.0)):
        d = bpy.data.lights.new("l", tipo)
        d.energy = energia
        d.color = color
        if tipo == "AREA":
            d.size = tam
        o = bpy.data.objects.new("l", d)
        bpy.context.collection.objects.link(o)
        o.location = loc
        dirv = Vector(apunta) - Vector(loc)
        o.rotation_euler = dirv.to_track_quat("-Z", "Y").to_euler()
        return o
    luz("AREA", (2.2, -3.0, 2.6), 380, (0.85, 0.9, 1.0), 1.6)
    luz("AREA", (-3.0, 2.0, 2.2), 260, (0.5, 0.55, 0.9), 1.5)
    luz("AREA", (-2.0, -2.5, 0.6), 60, (1.0, 0.85, 0.75), 1.5)
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    bpy.context.collection.objects.link(cam)
    sc.camera = cam
    return cam


def apuntar(cam, pos, objetivo, lente=50):
    cam.location = pos
    cam.data.lens = lente
    cam.rotation_euler = (Vector(objetivo) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()


def render(ruta):
    bpy.context.scene.render.filepath = ruta
    bpy.ops.render.render(write_still=True)


def previa(malla, arm, carpeta, rapido=False):
    os.makedirs(carpeta, exist_ok=True)
    cam = escena_estudio()
    sc = bpy.context.scene
    if rapido:
        sc.cycles.samples = 16
        sc.render.resolution_percentage = 60
    vistas = [
        ("frente", "idle-loop", 0, (0, -4.3, 1.05), (0, 0, 1.02), 50),
        ("tres_cuartos", "idle-loop", 0, (2.8, -3.4, 1.25), (0, 0, 1.02), 50),
        ("perfil", "idle-loop", 0, (4.3, 0, 1.05), (0, 0, 1.02), 50),
        ("cara", "idle-loop", 0, (0.55, -1.05, 1.66), (0, 0, 1.62), 55),
        ("cara_frente", "idle-loop", 0, (0.0, -1.1, 1.62), (0, 0, 1.62), 60),
        ("camina_a", "caminar-loop", 4, (2.9, -3.5, 1.1), (0, 0, 0.95), 50),
        ("camina_b", "caminar-loop", 19, (2.9, -3.5, 1.1), (0, 0, 0.95), 50),
        ("ataque_a", "ataque", 16, (1.4, -4.4, 1.1), (0, -0.3, 1.1), 50),
        ("ataque_b", "ataque", 30, (0.0, -3.4, 1.4), (0, -0.4, 1.4), 45),
    ]
    solo = os.environ.get("VISTAS")
    for nombre, anim, fr, pos, tgt, lente in vistas:
        if solo and nombre not in solo.split(","):
            continue
        rig.aplicar_pose(arm, anim, fr)
        apuntar(cam, pos, tgt, lente)
        render(os.path.join(carpeta, nombre + ".png"))
        print("RENDER", nombre)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["exportar"]
    limpiar()
    malla, arm = construir()
    print("TRIS", sum(len(p.vertices) - 2 for p in malla.data.polygons), "VERTS", len(malla.data.vertices))
    if argv[0] == "exportar":
        exportar(malla, arm)
    elif argv[0] == "previa":
        previa(malla, arm, argv[1], "rapido" in argv)
    elif argv[0] == "ambos":
        exportar(malla, arm)
        previa(malla, arm, argv[1], "rapido" in argv)


main()
