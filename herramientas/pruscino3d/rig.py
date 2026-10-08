"""Armadura y animaciones de Pruscino 3D. Se ejecuta dentro de Blender.

Convencion de ejes de cada hueso (todos con X local = X del mundo):
  * hueso que apunta hacia ARRIBA : rx + = inclinar hacia adelante (-Y); rz + = inclinar hacia -X
  * hueso que apunta hacia ABAJO  : rx + = balancear hacia ATRAS; rz + = mover el extremo hacia -X
  * hueso que apunta al frente    : rx + = bajar la punta (abrir mandibula / punta del pie hacia abajo)
El personaje mira hacia -Y; su izquierda es +X (sufijo _L) y su derecha -X (sufijo _R).
"""
import math
import bpy
from mathutils import Vector, Matrix

import geometria as G
import modelo
from geometria import V

D = math.radians


def huesos_def():
    L = []

    def add(n, h, t, p, esc=False):
        h, t = V(*h), V(*t)
        if esc:
            h, t = modelo.escala_p(h), modelo.escala_p(t)
        L.append((n, h, t, p))
    add("root", (0, 0, 0), (0, 0, 0.15), None)
    add("caderas", (0, 0, 0.90), (0, 0, 0.97), "root")
    add("torso", (0, 0, 0.92), (0, 0, 1.36), "caderas")
    add("cuello", (0, 0, 1.37), (0, -0.005, 1.47), "torso")
    add("cabeza", (0, -0.005, 1.47), (0, 0, 1.78), "cuello", True)
    add("mandibula", (0, -0.03, 1.52), (0, -0.20, 1.50), "cabeza", True)
    for s, n in ((1, "L"), (-1, "R")):
        add(f"oreja_{n}_1", (s * 0.09, 0.02, 1.70), (s * 0.096, 0.02, 1.85), "cabeza", True)
        add(f"oreja_{n}_2", (s * 0.096, 0.02, 1.85), (s * 0.10, 0.02, 1.99), f"oreja_{n}_1", True)
        add(f"brazo_{n}", (s * 0.30, 0, 1.30), (s * 0.325, 0, 1.0), "torso")
        add(f"antebrazo_{n}", (s * 0.325, 0, 1.0), (s * 0.33, -0.02, 0.755), f"brazo_{n}")
        add(f"mano_{n}", (s * 0.33, -0.02, 0.755), (s * 0.335, -0.03, 0.62), f"antebrazo_{n}")
        add(f"muslo_{n}", (s * 0.115, 0, 0.86), (s * 0.115, -0.011, 0.48), "caderas")
        add(f"pantorrilla_{n}", (s * 0.115, -0.011, 0.48), (s * 0.115, 0, 0.118), f"muslo_{n}")
        add(f"pie_{n}", (s * 0.115, 0, 0.118), (s * 0.115, -0.15, 0.05), f"pantorrilla_{n}")
    return L


def crear_armadura():
    arm_data = bpy.data.armatures.new("Armadura")
    arm = bpy.data.objects.new("Armadura", arm_data)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eds = {}
    for n, h, t, p in huesos_def():
        eb = arm_data.edit_bones.new(n)
        eb.head, eb.tail = h, t
        y = (t - h).normalized()
        z = Vector((1, 0, 0)).cross(y)
        eb.align_roll(z)
        if p:
            eb.parent = eds[p]
        eds[n] = eb
    bpy.ops.object.mode_set(mode="OBJECT")
    return arm


def enlazar(malla, arm):
    malla.parent = arm
    m = malla.modifiers.new("Armadura", "ARMATURE")
    m.object = arm


# ---------------------------------------------------------------- animacion
def sm(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def pulso(t, c, w):
    return math.exp(-((t - c) / w) ** 2)


def ruido(f, semilla, freq=1.0):
    """Ruido pseudo-aleatorio determinista en [-1, 1]."""
    x = f * freq
    return (math.sin(x * 12.9898 + semilla * 78.233) * 0.5 + math.sin(x * 7.13 + semilla * 3.1) * 0.35 +
            math.sin(x * 23.7 + semilla * 1.7) * 0.15)


class Pose(dict):
    def r(self, hueso, x=0.0, y=0.0, z=0.0):
        a = self.setdefault(hueso, {"rot": [0, 0, 0], "loc": [0, 0, 0]})
        a["rot"][0] += D(x)
        a["rot"][1] += D(y)
        a["rot"][2] += D(z)

    def l(self, hueso, x=0.0, y=0.0, z=0.0):
        a = self.setdefault(hueso, {"rot": [0, 0, 0], "loc": [0, 0, 0]})
        a["loc"][0] += x
        a["loc"][1] += y
        a["loc"][2] += z


def pose_idle(f, n):
    t = f / n
    ph = 2 * math.pi * t
    P = Pose()
    P.l("caderas", 0, 0, 0.004 * math.sin(ph))
    P.r("caderas", 0, 0, 0.6 * math.sin(ph))
    P.r("torso", 1.5 + 0.9 * math.sin(ph - 0.4), 0, 0.6 * math.sin(ph + 1))
    tw = pulso(t, 0.62, 0.018)                 # tic nervioso: giro brusco de cabeza
    P.r("cabeza", 3 + 1.4 * math.sin(ph + 0.8), -12 * tw + 3 * math.sin(ph + 1), 9 * tw + 2.5 * math.sin(ph + 2))
    P.r("cuello", 1.0, 0, 0)
    P.r("mandibula", 1.0 + 8 * tw)
    P.r("oreja_L_1", 2 * math.sin(ph + 1) + 14 * tw)
    P.r("oreja_L_2", 3 * math.sin(ph + 1.7) + 10 * tw)
    P.r("oreja_R_1", 2 * math.sin(ph + 0.3) - 6 * tw)
    P.r("oreja_R_2", 3 * math.sin(ph + 0.9) - 4 * tw)
    for s, n in ((1, "L"), (-1, "R")):
        P.r(f"brazo_{n}", -5 + 1.5 * math.sin(ph + 0.5), 0, -s * 5)
        P.r(f"antebrazo_{n}", -16 + 2 * math.sin(ph + 1), 0, 0)
        P.r(f"mano_{n}", -6, 0, 0)
    return P


def pose_caminar(f, n):
    t = f / n
    ph = 2 * math.pi * t
    P = Pose()
    P.l("caderas", 0, 0, -0.022 * abs(math.cos(ph)) - 0.01)
    P.r("caderas", 0, 4 * math.sin(ph), 2.2 * math.cos(ph))
    P.r("torso", 5, -4 * math.sin(ph), -1.6 * math.cos(ph))
    P.r("cabeza", -3, 3 * math.sin(ph), 1.4 * math.cos(ph))
    P.r("mandibula", 2)
    for s, n_, off in ((1, "L", 0.0), (-1, "R", math.pi)):
        p = ph + off
        muslo = -26 * math.sin(p)                    # adelante = negativo
        flex = 48 * max(0.0, math.cos(p)) ** 1.2      # rodilla flexiona en el balanceo
        P.r(f"muslo_{n_}", muslo)
        P.r(f"pantorrilla_{n_}", flex)
        pie = -(muslo + flex) * 0.9 + 16 * max(0.0, -math.sin(p)) * (1 if math.cos(p) < 0 else 0.4)
        P.r(f"pie_{n_}", pie)
        P.r(f"brazo_{n_}", 20 * math.sin(p), 0, -s * 4)
        P.r(f"antebrazo_{n_}", -24 - 14 * max(0.0, -math.sin(p)))
        P.r(f"mano_{n_}", -8)
        P.r(f"oreja_{n_}_1", 4 * math.sin(2 * ph + 0.9 + off))
        P.r(f"oreja_{n_}_2", 6 * math.sin(2 * ph + 1.6 + off))
    return P


def pose_ataque(f, n):
    """Jumpscare: anticipacion, embestida y temblor. n = frames totales (no es loop)."""
    t = f / 30.0
    P = Pose()
    ant = sm(0.0, 0.20, t) * (1 - sm(0.20, 0.26, t))
    lung = sm(0.20, 0.46, t)
    sacudida = sm(0.40, 0.7, t)
    k = 1.0 * sacudida
    P.l("caderas", 0, -0.42 * lung - 0.0, -0.03 * ant - 0.16 * lung)
    P.r("torso", -7 * ant + 40 * lung + 3.5 * k * ruido(f, 1, 1.9), 3 * k * ruido(f, 2, 1.7), 4 * k * ruido(f, 3, 1.5))
    P.r("cuello", 8 * lung + 3 * k * ruido(f, 4, 2.2))
    P.r("cabeza", -9 * ant - 40 * lung + 5 * k * ruido(f, 5, 2.4), 8 * k * ruido(f, 6, 2.1), 9 * k * ruido(f, 7, 2.6))
    apert = 52 * lung * (0.82 + 0.18 * (0.5 + 0.5 * math.sin(f * 1.9)) * sacudida + 0.0)
    P.r("mandibula", apert + 4 * k * ruido(f, 8, 3.1))
    for s, n_ in ((1, "L"), (-1, "R")):
        P.r(f"brazo_{n_}", -20 * ant - 80 * lung + 6 * k * ruido(f, 10 + s, 2.3), 0, -s * (10 * ant + 62 * lung) + 4 * k * ruido(f, 12 + s, 2.0))
        P.r(f"antebrazo_{n_}", -18 * lung + 6 * k * ruido(f, 14 + s, 2.6))
        P.r(f"mano_{n_}", -30 * lung + 10 * k * ruido(f, 16 + s, 3.0))
        P.r(f"oreja_{n_}_1", -22 * lung + 6 * k * ruido(f, 20 + s, 3.4))
        P.r(f"oreja_{n_}_2", -30 * lung + 10 * k * ruido(f, 22 + s, 3.9))
    # zancada de embestida
    P.r("muslo_L", -42 * lung)
    P.r("pantorrilla_L", 34 * lung)
    P.r("pie_L", (42 - 34) * lung + 4)
    P.r("muslo_R", 18 * lung)
    P.r("pantorrilla_R", 12 * lung)
    P.r("pie_R", -30 * lung)
    return P


ANIMS = {
    "idle-loop": (pose_idle, 90, True),
    "caminar-loop": (pose_caminar, 30, True),
    "ataque": (pose_ataque, 48, False),
}


def crear_animaciones(arm):
    arm.animation_data_create()
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"
    for nombre, (fn, n, loop) in ANIMS.items():
        acc = bpy.data.actions.new(nombre)
        acc.use_fake_user = True
        arm.animation_data.action = acc
        for f in range(0, n + 1):
            fr = f + 1
            P = fn(f % n if loop else f, n)
            for pb in arm.pose.bones:
                d = P.get(pb.name)
                pb.rotation_euler = tuple(d["rot"]) if d else (0, 0, 0)
                pb.location = tuple(d["loc"]) if d else (0, 0, 0)
                pb.keyframe_insert("rotation_euler", frame=fr, group=pb.name)
                if pb.name in ("caderas", "root"):
                    pb.keyframe_insert("location", frame=fr, group=pb.name)
        acc.frame_range = (1, n + 1)
    arm.animation_data.action = bpy.data.actions["idle-loop"]


def aplicar_pose(arm, nombre, frame):
    """Deja la armadura en la pose del frame indicado (para previsualizar)."""
    fn, n, loop = ANIMS[nombre]
    P = fn(frame % n if loop else frame, n)
    arm.animation_data.action = None
    for pb in arm.pose.bones:
        d = P.get(pb.name)
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = tuple(d["rot"]) if d else (0, 0, 0)
        pb.location = tuple(d["loc"]) if d else (0, 0, 0)
    bpy.context.view_layer.update()
