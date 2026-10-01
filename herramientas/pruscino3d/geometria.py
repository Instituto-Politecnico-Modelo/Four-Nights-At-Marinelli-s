"""Primitivas de modelado (bmesh) para Pruscino 3D. Se ejecuta dentro de Blender.

Convenciones: Z arriba, el personaje mira hacia -Y (vista frontal de Blender).
Todas las partes se crean en coordenadas de mundo y con una unica pose de reposo.
"""
import math
import random
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

PARTES = []          # objetos creados (se unen al final)
_RNG = random.Random(7)


def V(*a):
    return Vector(a)


# ---------------------------------------------------------------- objetos
def _obj_desde_bm(bm, nombre, mat, hueso, suave=True):
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    if suave:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.collection.objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    ob["hueso"] = hueso
    PARTES.append(ob)
    return ob


def _ganchos(ob, hueso, pesos=None):
    """Asigna vertex groups. pesos: callable(co)->[(hueso, peso)] o None para rigido."""
    me = ob.data
    if pesos is None:
        vg = ob.vertex_groups.new(name=hueso)
        vg.add(list(range(len(me.vertices))), 1.0, "REPLACE")
        return
    grupos = {}
    for v in me.vertices:
        for h, w in pesos(v.co):
            if w <= 1e-4:
                continue
            if h not in grupos:
                grupos[h] = ob.vertex_groups.new(name=h)
            grupos[h].add([v.index], w, "REPLACE")


def _modificadores(ob, bevel=None, sub=None):
    if bevel:
        m = ob.modifiers.new("Bisel", "BEVEL")
        m.width = bevel
        m.segments = 3
        m.limit_method = "NONE"
    if sub:
        m = ob.modifiers.new("Sub", "SUBSURF")
        m.levels = sub
        m.render_levels = sub


def terminar(ob):
    """Aplica modificadores."""
    if ob.modifiers:
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        dg = bpy.context.evaluated_depsgraph_get()
        ev = ob.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(ev)
        for p in me.polygons:
            p.use_smooth = True
        old = ob.data
        ob.modifiers.clear()
        ob.data = me
        me.materials.clear()
        for m in old.materials:
            me.materials.append(m)
        bpy.data.meshes.remove(old)


# ---------------------------------------------------------------- primitivas
def elipsoide(nombre, c, r, mat, hueso, rot=(0, 0, 0), seg=28, anillos=16, pesos=None, sub=0):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=anillos, radius=1.0)
    rm = Euler(rot, "XYZ").to_matrix().to_4x4()
    for v in bm.verts:
        v.co = rm @ Vector((v.co.x * r[0], v.co.y * r[1], v.co.z * r[2])) + Vector(c)
    ob = _obj_desde_bm(bm, nombre, mat, hueso)
    if sub:
        _modificadores(ob, sub=sub)
    _ganchos(ob, hueso, pesos)
    return ob


def caja(nombre, c, tam, mat, hueso, rot=(0, 0, 0), bisel=0.3, sub=1, pesos=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    rm = Euler(rot, "XYZ").to_matrix().to_4x4()
    for v in bm.verts:
        v.co = rm @ Vector((v.co.x * tam[0], v.co.y * tam[1], v.co.z * tam[2])) + Vector(c)
    ob = _obj_desde_bm(bm, nombre, mat, hueso)
    _modificadores(ob, bevel=min(tam) * bisel, sub=sub)
    _ganchos(ob, hueso, pesos)
    return ob


def _marcos(pts, ref, cerrado=False):
    n = len(pts)
    T = []
    for i in range(n):
        if cerrado:
            a, b = pts[(i - 1) % n], pts[(i + 1) % n]
        else:
            a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        t = (b - a)
        t.normalize()
        T.append(t)
    U, W = [], []
    u = Vector(ref) - Vector(ref).dot(T[0]) * T[0]
    if u.length < 1e-4:
        u = Vector((0, 1, 0)) - Vector((0, 1, 0)).dot(T[0]) * T[0]
    u.normalize()
    for i in range(n):
        u = u - u.dot(T[i]) * T[i]
        u.normalize()
        U.append(u.copy())
        W.append(T[i].cross(u))
    return T, U, W


def tubo(nombre, pts, mat, hueso, ref=(1, 0, 0), seg=20, cap0="domo", cap1="domo",
         pesos=None, sub=0, dom0=None, dom1=None):
    """pts: [(Vector centro, rx, ry)]. cap: 'domo' | 'plano' | None."""
    centros = [Vector(p[0]) for p in pts]
    T, U, W = _marcos(centros, ref)
    bm = bmesh.new()
    anillos = []

    def anillo(c, u, w, rx, ry):
        return [bm.verts.new(c + u * (rx * math.cos(2 * math.pi * k / seg)) +
                             w * (ry * math.sin(2 * math.pi * k / seg))) for k in range(seg)]
    if cap0 == "domo":
        d = dom0 if dom0 is not None else min(pts[0][1], pts[0][2])
        pasos = 4
        for j in range(pasos, 0, -1):
            phi = j / pasos * math.pi / 2
            c = centros[0] - T[0] * (d * math.sin(phi))
            s = math.cos(phi)
            anillos.append(anillo(c, U[0], W[0], max(pts[0][1] * s, 1e-4), max(pts[0][2] * s, 1e-4)))
    for i, (c, rx, ry) in enumerate(pts):
        anillos.append(anillo(centros[i], U[i], W[i], rx, ry))
    if cap1 == "domo":
        d = dom1 if dom1 is not None else min(pts[-1][1], pts[-1][2])
        pasos = 4
        for j in range(1, pasos + 1):
            phi = j / pasos * math.pi / 2
            c = centros[-1] + T[-1] * (d * math.sin(phi))
            s = math.cos(phi)
            anillos.append(anillo(c, U[-1], W[-1], max(pts[-1][1] * s, 1e-4), max(pts[-1][2] * s, 1e-4)))
    for a, b in zip(anillos[:-1], anillos[1:]):
        for k in range(seg):
            k2 = (k + 1) % seg
            try:
                bm.faces.new((a[k], a[k2], b[k2], b[k]))
            except ValueError:
                pass
    if cap0 == "plano":
        bm.faces.new(anillos[0][::-1])
    if cap1 == "plano":
        bm.faces.new(anillos[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj_desde_bm(bm, nombre, mat, hueso)
    if sub:
        _modificadores(ob, sub=sub)
    _ganchos(ob, hueso, pesos)
    return ob


def toro(nombre, c, R, r, eje, mat, hueso, seg=32, seg_r=12, pesos=None, esc=(1, 1)):
    """Toro alrededor del eje 'x','y' o 'z'. esc: escala elipse en los dos ejes del plano."""
    bm = bmesh.new()
    filas = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        fila = []
        for k in range(seg_r):
            b = 2 * math.pi * k / seg_r
            rr = R + r * math.cos(b)
            p = Vector((rr * math.cos(a) * esc[0], rr * math.sin(a) * esc[1], r * math.sin(b)))
            fila.append(bm.verts.new(p))
        filas.append(fila)
    for i in range(seg):
        for k in range(seg_r):
            bm.faces.new((filas[i][k], filas[(i + 1) % seg][k], filas[(i + 1) % seg][(k + 1) % seg_r],
                          filas[i][(k + 1) % seg_r]))
    rm = {"z": Matrix.Identity(3), "x": Euler((0, math.pi / 2, 0)).to_matrix(),
          "y": Euler((math.pi / 2, 0, 0)).to_matrix()}[eje]
    for v in bm.verts:
        v.co = rm @ v.co + Vector(c)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj_desde_bm(bm, nombre, mat, hueso)
    _ganchos(ob, hueso, pesos)
    return ob


def cinta_cerrada(nombre, pts, radio, mat, hueso, ref=(0, 1, 0), seg=10, pesos=None):
    """Tubo de seccion circular siguiendo una curva cerrada."""
    centros = [Vector(p) for p in pts]
    T, U, W = _marcos(centros, ref, cerrado=True)
    bm = bmesh.new()
    filas = []
    for i, c in enumerate(centros):
        # re-ortogonalizar con la normal al plano aproximado
        fila = [bm.verts.new(c + U[i] * (radio * math.cos(2 * math.pi * k / seg)) +
                             W[i] * (radio * math.sin(2 * math.pi * k / seg))) for k in range(seg)]
        filas.append(fila)
    n = len(centros)
    for i in range(n):
        for k in range(seg):
            bm.faces.new((filas[i][k], filas[(i + 1) % n][k], filas[(i + 1) % n][(k + 1) % seg],
                          filas[i][(k + 1) % seg]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj_desde_bm(bm, nombre, mat, hueso)
    _ganchos(ob, hueso, pesos)
    return ob


def poligono_extruido(nombre, pts2d, grosor, plano_c, mat, hueso, rot=(0, 0, 0), sub=0, bisel=0.0):
    """Polígono 2D (x,z) extruido en y. Para lentes, corbata, etc."""
    bm = bmesh.new()
    vs = [bm.verts.new((p[0], -grosor / 2, p[1])) for p in pts2d]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    verts = [e for e in r["geom"] if isinstance(e, bmesh.types.BMVert)]
    for v in verts:
        v.co.y += grosor
    rm = Euler(rot, "XYZ").to_matrix().to_4x4()
    for v in bm.verts:
        v.co = rm @ v.co + Vector(plano_c)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = _obj_desde_bm(bm, nombre, mat, hueso, suave=bool(sub))
    if bisel:
        _modificadores(ob, bevel=bisel, sub=sub)
    elif sub:
        _modificadores(ob, sub=sub)
    _ganchos(ob, hueso)
    return ob


def casquete(nombre, c, r, mat, hueso, z_corte, rot=(0, 0, 0), grosor=0.004, seg=24, anillos=14):
    """Parte superior de una esfera (parpados). z_corte en coords locales de esfera unitaria."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=anillos, radius=1.0)
    borrar = [f for f in bm.faces if f.calc_center_median().z < z_corte]
    bmesh.ops.delete(bm, geom=borrar, context="FACES")
    rm = Euler(rot, "XYZ").to_matrix().to_4x4()
    for v in bm.verts:
        v.co = rm @ Vector((v.co.x * r[0], v.co.y * r[1], v.co.z * r[2])) + Vector(c)
    ob = _obj_desde_bm(bm, nombre, mat, hueso)
    m = ob.modifiers.new("Grosor", "SOLIDIFY")
    m.thickness = grosor
    m.offset = 1
    _ganchos(ob, hueso)
    return ob


def ruido_superficie(ob, amp, freq, semilla=1, solo_z_mayor=None):
    """Desplaza vertices a lo largo de la normal con ruido (arrugas)."""
    me = ob.data
    me.calc_normals_split() if hasattr(me, "calc_normals_split") else None
    rng = random.Random(semilla)
    fases = [rng.uniform(0, 6.28) for _ in range(9)]
    for v in me.vertices:
        p = v.co
        n = (math.sin(p.x * freq * 1.0 + fases[0]) * math.sin(p.z * freq * 0.7 + fases[1]) +
             math.sin(p.y * freq * 1.3 + p.z * freq + fases[2]) * 0.6 +
             math.sin((p.x + p.y) * freq * 2.1 + fases[3]) * 0.3)
        v.co = v.co + v.normal * (amp * n)


def uv_caja(ob, tile=0.5):
    """UV por proyeccion en caja (tileable), densidad uniforme."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            p = l.vert.co
            if ax == 0:
                l[uv].uv = (p.y / tile, p.z / tile)
            elif ax == 1:
                l[uv].uv = (p.x / tile, p.z / tile)
            else:
                l[uv].uv = (p.x / tile, p.y / tile)
    bm.to_mesh(me)
    bm.free()
