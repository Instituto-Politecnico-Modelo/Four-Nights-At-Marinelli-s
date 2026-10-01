"""Modelo 3D de Pruscino (Bonnie de FNAF 1 fusionado con Pruscino). Se ejecuta dentro de Blender."""
import math
import random
import bpy
from mathutils import Vector, Euler, Matrix

import geometria as G
from geometria import V


# ---------------------------------------------------------------- materiales
def lin(c):
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c)


def hexc(h):
    h = h.lstrip("#")
    return lin(tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))


def material(nombre, color="#808080", tex=None, dir_tex=None, rough=0.8, metal=0.0,
             emis=None, emis_fuerza=0.0, alpha=1.0, normal_fuerza=1.0, tile=0.4, ior_spec=0.5,
             sheen=0.0):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    salida = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(p.outputs["BSDF"], salida.inputs["Surface"])
    p.inputs["Base Color"].default_value = (*hexc(color), 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Specular IOR Level"].default_value = ior_spec
    if sheen:
        p.inputs["Sheen Weight"].default_value = sheen
    if emis:
        p.inputs["Emission Color"].default_value = (*hexc(emis), 1)
        p.inputs["Emission Strength"].default_value = emis_fuerza
    if alpha < 1.0:
        p.inputs["Alpha"].default_value = alpha
        m.blend_method = "BLEND"
    if tex:
        it = nt.nodes.new("ShaderNodeTexImage")
        it.image = bpy.data.images.load(f"{dir_tex}/{tex}_c.png")
        nt.links.new(it.outputs["Color"], p.inputs["Base Color"])
        inn = nt.nodes.new("ShaderNodeTexImage")
        inn.image = bpy.data.images.load(f"{dir_tex}/{tex}_n.png")
        inn.image.colorspace_settings.name = "Non-Color"
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = normal_fuerza
        nt.links.new(inn.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], p.inputs["Normal"])
    m.use_backface_culling = False
    m["tile"] = tile
    return m


def crear_materiales(dir_tex):
    M = type("M", (), {})()
    d = dir_tex
    M.pelaje = material("Pelaje", tex="pelaje", dir_tex=d, rough=0.92, tile=0.45, normal_fuerza=0.8, sheen=0.12)
    M.hocico = material("Hocico", tex="hocico", dir_tex=d, rough=0.88, tile=0.45, normal_fuerza=0.7, sheen=0.1)
    M.oreja_int = material("OrejaInterior", tex="oreja_int", dir_tex=d, rough=0.95, tile=0.3)
    M.metal = material("Metal", tex="metal", dir_tex=d, rough=0.42, metal=1.0, tile=0.3)
    M.camisa = material("Camisa", tex="camisa", dir_tex=d, rough=1.0, tile=0.6, normal_fuerza=1.0)
    M.pelo = material("Pelo", tex="pelo", dir_tex=d, rough=0.55, tile=0.25, normal_fuerza=1.4)
    M.barba = material("Barba", tex="barba", dir_tex=d, rough=0.8, tile=0.25, normal_fuerza=1.4)
    M.mono = material("Monio", color="#5c0810", rough=0.65, sheen=0.0, tile=1.0)
    M.dientes = material("Dientes", color="#c9c1a4", rough=0.3, tile=1.0)
    M.blanco_ojo = material("OjoBlanco", color="#a9a3a0", rough=0.15, tile=1.0)
    M.iris = material("Iris", color="#6e0a18", rough=0.2, emis="#d0102a", emis_fuerza=0.7, tile=1.0)
    M.pupila = material("Pupila", color="#020102", rough=0.1, tile=1.0)
    M.nariz = material("Nariz", color="#0b0810", rough=0.18, tile=1.0)
    M.boca = material("Boca", color="#1a0308", rough=1.0, tile=1.0)
    M.lengua = material("Lengua", color="#4a0a14", rough=0.5, tile=1.0)
    M.marco = material("MarcoAnteojos", color="#070709", rough=0.28, metal=0.2, tile=1.0)
    M.vidrio = material("VidrioAnteojos", color="#c8d8f0", rough=0.03, alpha=0.09, ior_spec=1.0, tile=1.0)
    M.goma = material("Goma", color="#0c0b10", rough=0.85, tile=1.0)
    return M


# ---------------------------------------------------------------- utilidades
def elipse_pts(rx, ry, z, n=36, cy=0.0):
    return [V(rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n), z) for i in range(n)]


def dir_a_euler(d):
    return d.normalized().to_track_quat("Z", "Y").to_euler()


def suave(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- cabeza
HC = V(0, 0, 1.60)
PIV = V(0, -0.005, 1.47)      # articulacion del cuello
ESC = 1.2                     # cabeza grande estilo Bonnie


def H(x, y, z):
    return HC + V(x, y, z)


def construir_cabeza(M):
    G_ = G
    n0 = len(G.PARTES)
    # craneo y mejillas
    G_.elipsoide("craneo", H(0, 0.01, 0), (0.20, 0.18, 0.165), M.pelaje, "cabeza", seg=40, anillos=24)
    for s in (1, -1):
        G_.elipsoide("mejilla", H(s * 0.115, -0.08, -0.07), (0.10, 0.10, 0.085), M.pelaje, "cabeza")
        G_.caja("ceja", H(s * 0.088, -0.163, 0.082), (0.10, 0.045, 0.032), M.pelaje, "cabeza",
                rot=(0.0, -s * 0.30, 0), bisel=0.5, sub=2)
    # hocico
    G_.caja("hocico", H(0, -0.185, -0.075), (0.21, 0.15, 0.105), M.hocico, "cabeza", bisel=0.42, sub=2)
    G_.elipsoide("puente", H(0, -0.14, -0.015), (0.075, 0.09, 0.062), M.hocico, "cabeza")
    G_.elipsoide("nariz", H(0, -0.262, -0.026), (0.032, 0.02, 0.024), M.nariz, "cabeza")
    # interior de la boca y mandibula
    G_.elipsoide("boca_interior", H(0, -0.16, -0.122), (0.088, 0.088, 0.026), M.boca, "cabeza")
    G_.caja("mandibula", H(0, -0.165, -0.156), (0.19, 0.16, 0.052), M.pelaje, "mandibula", bisel=0.32, sub=2)
    G_.elipsoide("lengua", H(0, -0.14, -0.14), (0.05, 0.062, 0.013), M.lengua, "mandibula")
    # dientes
    for i in range(8):
        x = -0.0805 + i * 0.023
        q = (x / 0.085) ** 2
        G_.caja("diente_sup", H(x, -0.258 + 0.04 * q, -0.14), (0.02, 0.012, 0.027), M.dientes, "cabeza",
                bisel=0.3, sub=1)
        G_.caja("diente_inf", H(x * 0.9, -0.238 + 0.034 * q, -0.128), (0.017, 0.011, 0.022), M.dientes,
                "mandibula", bisel=0.3, sub=1)
    # ojos
    for s in (1, -1):
        c = H(s * 0.088, -0.152, 0.03)
        G_.elipsoide("ojo", c, (0.042, 0.042, 0.042), M.blanco_ojo, "cabeza")
        G_.elipsoide("iris", c + V(0, -0.033, 0), (0.026, 0.012, 0.026), M.iris, "cabeza")
        G_.elipsoide("pupila", c + V(0, -0.041, 0), (0.0115, 0.0055, 0.0115), M.pupila, "cabeza")
        # parpado superior pesado (mirada de Bonnie)
        G_.casquete("parpado", c, (0.0465, 0.0465, 0.0465), M.pelaje, "cabeza", z_corte=0.12,
                    rot=(0.0, -s * 0.18, 0), grosor=0.005)
        G_.elipsoide("cuenca", c + V(0, 0.012, -0.004), (0.052, 0.03, 0.052), M.boca, "cabeza")
    # pelo de Pruscino
    centro = H(0, 0.034, 0.086)
    rad = (0.198, 0.186, 0.098)
    G_.elipsoide("pelo_base", centro, rad, M.pelo, "cabeza", seg=36, anillos=20)
    rng = random.Random(11)
    for i in range(16):
        while True:
            v = V(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0.15, 1))
            if v.length > 0.3:
                break
        v.normalize()
        p = centro + V(v.x * rad[0], v.y * rad[1], v.z * rad[2])
        d = V(v.x, v.y * 1.2 - 0.25, v.z) + V(rng.uniform(-.3, .3), rng.uniform(-.3, .3), 0)
        G_.elipsoide("mechon", p, (0.014, 0.014, 0.036 * rng.uniform(0.7, 1.3)), M.pelo, "cabeza",
                     rot=tuple(dir_a_euler(d)), seg=12, anillos=8)
    # barba de Pruscino
    for s in (1, -1):
        G_.elipsoide("barba_mejilla", H(s * 0.118, -0.085, -0.128), (0.103, 0.100, 0.062), M.barba, "cabeza")
    G_.elipsoide("barba_mentón", H(0, -0.175, -0.192), (0.088, 0.078, 0.03), M.barba, "mandibula")
    G_.elipsoide("perilla", H(0, -0.228, -0.2), (0.036, 0.03, 0.052), M.barba, "mandibula")
    pts = []
    for i in range(9):
        x = -0.078 + i * 0.0195
        q = (x / 0.08) ** 2
        pts.append((V(x, HC.y - 0.256 + 0.034 * q, HC.z - 0.094 - 0.013 * (1 - q)), 0.017, 0.012))
    G_.tubo("bigote", pts, M.barba, "cabeza", ref=(0, 1, 0), seg=10)
    # anteojos
    ancho, alto, r_esq = 0.106, 0.076, 0.016
    ymarco = HC.y - 0.222
    for s in (1, -1):
        cx = s * 0.088
        cz = HC.z + 0.032
        lazo = []
        pares = [(ancho / 2 - r_esq, alto / 2 - r_esq, 0), (-(ancho / 2 - r_esq), alto / 2 - r_esq, 90),
                 (-(ancho / 2 - r_esq), -(alto / 2 - r_esq), 180), (ancho / 2 - r_esq, -(alto / 2 - r_esq), 270)]
        for ox, oz, a0 in pares:
            for k in range(7):
                a = math.radians(a0 + 90 * k / 6)
                lazo.append(V(cx + ox + r_esq * math.cos(a), ymarco, cz + oz + r_esq * math.sin(a)))
        G_.cinta_cerrada("marco", lazo, 0.0048, M.marco, "cabeza", ref=(0, 1, 0), seg=10)
        lente = [(p.x - cx, p.z - cz) for p in lazo]
        G_.poligono_extruido("lente", lente, 0.0018, V(cx, ymarco, cz), M.vidrio, "cabeza")
        # patilla del anteojo siguiendo el craneo
        base = V(s * (0.088 + ancho / 2), ymarco, HC.z + 0.05)
        cam = [base]
        k_ = math.sqrt(1 - (0.05 / 0.165) ** 2)
        t0 = math.asin(min(0.99, base.x * s / (0.2 * k_ * 1.03)))
        cam.append(V(base.x, HC.y + 0.01 - 0.18 * k_ * 1.03 * math.cos(t0) - 0.004, base.z))
        for t in (t0 + 0.25, t0 + 0.5, t0 + 0.75):
            cam.append(V(s * 0.2 * k_ * 1.03 * math.sin(t), HC.y + 0.01 - 0.18 * k_ * 1.03 * math.cos(t), base.z))
        G_.tubo("patilla_anteojo", [(p, 0.0046, 0.0046) for p in cam], M.marco, "cabeza", ref=(0, 0, 1), seg=8)
    puente = [(V(0.088 - ancho / 2 + 0.002, ymarco, HC.z + 0.05), 0.0055, 0.0055),
              (V(0.0, ymarco - 0.004, HC.z + 0.056), 0.0055, 0.0055),
              (V(-(0.088 - ancho / 2 + 0.002), ymarco, HC.z + 0.05), 0.0055, 0.0055)]
    G_.tubo("puente_anteojos", puente, M.marco, "cabeza", ref=(0, 1, 0), seg=8)
    # apoyanarices
    for s in (1, -1):
        G_.elipsoide("apoyo", V(s * 0.03, ymarco + 0.004, HC.z + 0.0), (0.006, 0.004, 0.014), M.marco, "cabeza",
                     seg=8, anillos=6)


def escalar_desde(n0):
    for ob in G.PARTES[n0:]:
        ob.data.transform(Matrix.Translation(PIV) @ Matrix.Scale(ESC, 4) @ Matrix.Translation(-PIV))


def escala_p(p):
    return PIV + (Vector(p) - PIV) * ESC


def construir_orejas(M):
    for s, nombre in ((1, "L"), (-1, "R")):
        h1, h2 = f"oreja_{nombre}_1", f"oreja_{nombre}_2"

        def pesos(co, h1=h1, h2=h2):
            w2 = suave(1.80, 1.90, co.z)
            return [(h1, 1 - w2), (h2, w2)]
        if s == 1:
            pts = [((0.09, 0.02, 1.72), 0.052, 0.025), ((0.096, 0.02, 1.80), 0.056, 0.023),
                   ((0.104, 0.015, 1.88), 0.055, 0.021), ((0.125, 0.0, 1.945), 0.05, 0.019),
                   ((0.16, -0.05, 1.975), 0.045, 0.017), ((0.20, -0.105, 1.965), 0.04, 0.015),
                   ((0.232, -0.15, 1.925), 0.034, 0.013)]
        else:
            pts = [((-0.09, 0.02, 1.72), 0.052, 0.025), ((-0.093, 0.02, 1.80), 0.056, 0.023),
                   ((-0.097, 0.02, 1.88), 0.055, 0.021), ((-0.101, 0.02, 1.93), 0.049, 0.018),
                   ((-0.104, 0.02, 1.975), 0.037, 0.014)]
        pts = [(V(*p[0]), p[1], p[2]) for p in pts]
        G.tubo(f"oreja_{nombre}", pts, M.pelaje, h1, ref=(1, 0, 0), seg=24, pesos=pesos)
        # interior (cara frontal, tono oscuro)
        cent = [p[0] for p in pts]
        T, U, W = G._marcos(cent, (1, 0, 0))
        pin = []
        for i, (c, rx, ry) in enumerate(pts):
            pin.append((c - W[i] * (ry * 0.85), rx * 0.62, ry * 0.55))
        G.tubo(f"oreja_int_{nombre}", pin, M.oreja_int, h1, ref=(1, 0, 0), seg=20, pesos=pesos)


# ---------------------------------------------------------------- cuerpo
def construir_torso(M):
    sec = [(0.90, .165, .112), (1.0, .175, .118), (1.12, .198, .126), (1.24, .232, .135),
           (1.31, .245, .134), (1.36, .19, .115), (1.395, .10, .085)]
    G.tubo("torso", [(V(0, 0, z), rx, ry) for z, rx, ry in sec], M.pelaje, "torso", cap0="plano", cap1="domo",
           dom1=0.02, seg=36)
    # pelvis y caderas
    G.elipsoide("pelvis", V(0, 0, 0.875), (0.185, 0.125, 0.105), M.pelaje, "caderas", seg=32)
    for s in (1, -1):
        G.elipsoide("cadera", V(s * 0.115, 0, 0.85), (0.108, 0.108, 0.108), M.pelaje, "caderas")
        G.elipsoide("hombro", V(s * 0.278, 0, 1.285), (0.07, 0.07, 0.07), M.pelaje, "torso")
    lazo = elipse_pts(0.172, 0.12, 0.905)
    G.cinta_cerrada("cintura", lazo, 0.022, M.metal, "caderas", ref=(0, 0, 1), seg=12)
    # cuello
    G.tubo("cuello", [(V(0, 0, 1.37), .075, .07), (V(0, -0.003, 1.42), .07, .065),
                      (V(0, -0.006, 1.48), .068, .064)], M.metal, "cuello", cap0=None, cap1=None, seg=24)
    for z in (1.395, 1.425, 1.455):
        G.toro("cuello_anillo", V(0, -0.003 * (z - 1.37) / 0.05, z), 0.07, 0.0095, "z", M.metal, "cuello")


def construir_camisa(M):
    sec = [(0.93, .189, .131), (1.02, .192, .133), (1.12, .214, .141), (1.24, .247, .150),
           (1.31, .260, .149), (1.355, .212, .131), (1.383, .152, .109)]
    ob = G.tubo("camisa", [(V(0, 0, z), rx, ry) for z, rx, ry in sec], M.camisa, "torso", cap0=None, cap1=None,
                seg=48)
    rng = random.Random(3)
    for v in ob.data.vertices:
        if v.co.z < 0.96:
            ang = math.atan2(v.co.y, v.co.x)
            v.co.z += 0.012 * math.sin(ang * 5.0) + rng.uniform(-0.018, 0.02)
            if 1.7 < ang < 2.5:                       # rasgadura en un costado
                v.co.z += 0.06 * (1 - abs(ang - 2.1) / 0.4)
    G.ruido_superficie(ob, 0.004, 22, 5)
    lazo = elipse_pts(0.152, 0.109, 1.386)
    G.cinta_cerrada("cuello_camisa", lazo, 0.011, M.camisa, "torso", ref=(0, 0, 1), seg=8)
    # mangas
    for s, n in ((1, "L"), (-1, "R")):
        pts = [(V(s * 0.298, 0, 1.345), .080, .078), (V(s * 0.306, 0, 1.29), .084, .082),
               (V(s * 0.316, 0, 1.19), .080, .078), (V(s * 0.322, 0, 1.105), .078, .076)]
        m = G.tubo("manga", pts, M.camisa, f"brazo_{n}", cap0="domo", cap1=None, seg=32)
        rng2 = random.Random(9 + s)
        for v in m.data.vertices:
            if v.co.z < 1.12:
                v.co.z += rng2.uniform(-0.012, 0.012)
        G.ruido_superficie(m, 0.003, 26, 6 + s)
    # moño rojo de Bonnie
    yb = -0.166
    for s in (1, -1):
        pol = [(s * 0.012, 0.011), (s * 0.05, 0.038), (s * 0.082, 0.042), (s * 0.088, 0.0), (s * 0.082, -0.042),
               (s * 0.05, -0.038), (s * 0.012, -0.011)]
        if s == -1:
            pol = pol[::-1]
        G.poligono_extruido("mono_ala", pol, 0.02, V(0, yb, 1.30), M.mono, "torso",
                            rot=(0, s * 0.05, s * -0.12), sub=1, bisel=0.004)
    G.elipsoide("mono_nudo", V(0, yb - 0.006, 1.30), (0.019, 0.017, 0.026), M.mono, "torso", seg=16, anillos=10)


def construir_brazos(M):
    for s, n in ((1, "L"), (-1, "R")):
        b, a, m = f"brazo_{n}", f"antebrazo_{n}", f"mano_{n}"
        G.tubo("brazo", [(V(s * .30, 0, 1.30), .068, .068), (V(s * .312, 0, 1.16), .064, .064),
                         (V(s * .325, 0, 1.0), .057, .057)], M.pelaje, b, cap0="domo", cap1=None, seg=24)
        G.elipsoide("codo", V(s * .325, 0, 1.0), (0.06, 0.06, 0.06), M.metal, b)
        G.tubo("antebrazo", [(V(s * .325, 0, 1.0), .057, .057), (V(s * .328, -.01, .88), .056, .056),
                             (V(s * .33, -.02, .765), .046, .046)], M.pelaje, a, cap0=None, cap1=None, seg=24)
        G.toro("muneca", V(s * .33, -.02, .755), 0.045, 0.014, "z", M.metal, a)
        # mano
        cx = s * .335
        G.caja("palma", V(cx, -.03, .69), (.085, .058, .10), M.pelaje, m, bisel=0.33, sub=1)
        for i, (dx, largo) in enumerate(((-.031, .8), (-.0102, 1.0), (.0108, .95), (.0318, .75))):
            x = cx + dx
            pts = [(V(x, -.03, .65), .0145, .0145), (V(x, -.044, .65 - .046 * largo), .0135, .0135),
                   (V(x, -.072, .65 - .078 * largo), .0122, .0122)]
            G.tubo("dedo", pts, M.pelaje, m, seg=10)
        ts = -s
        G.tubo("pulgar", [(V(cx + ts * .03, -.02, .715), .0145, .0145), (V(cx + ts * .05, -.03, .685), .0135, .0135),
                          (V(cx + ts * .046, -.05, .662), .0125, .0125)], M.pelaje, m, seg=10)


def construir_piernas(M):
    for s, n in ((1, "L"), (-1, "R")):
        mu, pa, pi = f"muslo_{n}", f"pantorrilla_{n}", f"pie_{n}"
        x = s * .115
        G.tubo("muslo", [(V(x, 0, .87), .104, .108), (V(x, -.004, .70), .102, .106), (V(x, -.008, .55), .084, .088),
                         (V(x, -.011, .49), .074, .074)], M.pelaje, mu, cap0="domo", cap1=None, seg=28)
        G.tubo("rodilla", [(V(x - .066, -.012, .48), .06, .06), (V(x + .066, -.012, .48), .06, .06)],
               M.metal, mu, ref=(0, 1, 0), cap0="plano", cap1="plano", seg=20)
        G.tubo("pantorrilla", [(V(x, -.012, .48), .074, .076), (V(x, -.008, .36), .084, .086),
                               (V(x, -.002, .22), .07, .072), (V(x, 0, .13), .058, .06)], M.pelaje, pa,
               cap0=None, cap1="domo", seg=28)
        G.elipsoide("tobillo", V(x, 0, .118), (0.056, 0.056, 0.056), M.metal, pa)
        # pie
        G.caja("pie", V(x, -.085, .056), (.15, .30, .10), M.pelaje, pi, bisel=0.38, sub=2)
        G.elipsoide("talon", V(x, .04, .056), (.07, .065, .054), M.pelaje, pi)
        for dx in (-.05, 0.0, .05):
            G.elipsoide("dedo_pie", V(x + dx, -.226, .05), (.037, .046, .036), M.pelaje, pi)
        G.caja("suela", V(x, -.087, .014), (.14, .295, .028), M.goma, pi, bisel=0.3, sub=1)


def construir_todo(M):
    n0 = len(G.PARTES)
    construir_cabeza(M)
    construir_orejas(M)
    escalar_desde(n0)
    construir_torso(M)
    construir_camisa(M)
    construir_brazos(M)
    construir_piernas(M)


def ensamblar(nombre="Pruscino"):
    """Aplica modificadores, genera UVs y une todas las partes en un solo mesh."""
    for ob in G.PARTES:
        G.terminar(ob)
        tile = ob.data.materials[0]["tile"] if ob.data.materials else 0.5
        G.uv_caja(ob, tile)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in G.PARTES:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = G.PARTES[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = nombre
    ob.data.name = nombre
    return ob
