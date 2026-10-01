#!/usr/bin/env python3
"""Generador procedural de sprites de Pruscino (fusion Bonnie + Pruscino).

Genera SVG por frame y los exporta a PNG con Inkscape.
Uso:  python3 herramientas/generar_pruscino.py [--sin-png]

Salida (dentro de assets/xp/Animatronicos/Pruscino/):
    hojas/<animacion>.png            <- hoja de sprites (grilla) para Godot
    fuente/svg|png/<animacion>/...   <- frames sueltos (con .gdignore)
Animaciones: idle, caminar_abajo, caminar_arriba, caminar_izquierda,
             caminar_derecha, ataque
"""
import math
import random
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "assets/xp/Animatronicos/Pruscino"

W, H = 512, 768
W_ATAQUE, H_ATAQUE = 1024, 768
SUELO = 748


# --------------------------------------------------------------- defs
def grad_h(id_, stops):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="1" y2="0">{s}</linearGradient>'


def grad_r(id_, stops, cx=0.4, cy=0.3, r=0.8):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return (f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r="{r}" '
            f'fx="{cx}" fy="{cy}">{s}</radialGradient>')


DEFS = "<defs>" + "".join([
    grad_h("gPur", [(0, "#1a1430"), (.28, "#54468a"), (.55, "#3e3270"), (1, "#141028")]),
    grad_h("gPurF", [(0, "#110d22"), (.3, "#33295a"), (.6, "#281f48"), (1, "#0d0a1a")]),
    grad_h("gKh", [(0, "#332c20"), (.3, "#85775a"), (.6, "#665a42"), (1, "#2f261a")]),
    grad_h("gKhF", [(0, "#241f17"), (.3, "#5a5039"), (.6, "#463e2e"), (1, "#211c14")]),
    grad_h("gMetal", [(0, "#22222a"), (.4, "#8c8c9c"), (1, "#20202a")]),
    grad_r("rHead", [(0, "#6a5aa0"), (.55, "#43367a"), (1, "#181236")]),
    grad_r("rHeadB", [(0, "#54468a"), (.6, "#372c66"), (1, "#151030")], .5, .35, .8),
    grad_r("rMuz", [(0, "#aaa5c0"), (.65, "#79738f"), (1, "#3a364c")], .45, .3, .75),
    '<radialGradient id="rShade" cx=".5" cy=".42" r=".72"><stop offset="0" stop-color="#000" stop-opacity="0"/>'
    '<stop offset=".6" stop-color="#000" stop-opacity=".18"/><stop offset="1" stop-color="#000" stop-opacity=".62"/></radialGradient>',
    '<radialGradient id="rSocket" cx=".5" cy=".5" r=".55"><stop offset="0" stop-color="#000"/>'
    '<stop offset=".75" stop-color="#050309"/><stop offset="1" stop-color="#050309" stop-opacity="0"/></radialGradient>',
    grad_r("rHair", [(0, "#5a4237"), (.6, "#33241d"), (1, "#150e0b")], .4, .3, .8),
    grad_r("rMouth", [(0, "#5a0c16"), (.7, "#2a050a"), (1, "#0a0103")], .5, .3, .8),
    grad_r("rEar", [(0, "#4a3a78"), (1, "#1c1638")], .5, .4, .8),
    '<linearGradient id="gRed" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#e5343f"/><stop offset=".5" stop-color="#a51824"/>'
    '<stop offset="1" stop-color="#5a0b13"/></linearGradient>',
    '<linearGradient id="gTooth" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#e2d9bd"/><stop offset="1" stop-color="#8f8468"/></linearGradient>',
    '<filter id="fur" x="-5%" y="-5%" width="110%" height="110%">'
    '<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="4" result="n"/>'
    '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.3 0.85" result="d"/>'
    '<feComposite in="d" in2="SourceAlpha" operator="in" result="d2"/>'
    '<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="d2"/></feMerge></filter>',
    '<radialGradient id="rFondoRojo" cx=".5" cy=".45" r=".75"><stop offset="0" stop-color="#b0101c" stop-opacity=".85"/>'
    '<stop offset=".55" stop-color="#500509" stop-opacity=".6"/><stop offset="1" stop-color="#000" stop-opacity=".85"/></radialGradient>',
    '<filter id="glow" x="-100%" y="-100%" width="300%" height="300%">'
    '<feGaussianBlur stdDeviation="4" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
    '<filter id="blur8" x="-30%" y="-100%" width="160%" height="300%">'
    '<feGaussianBlur stdDeviation="8"/></filter>',
]) + "</defs>"

OUT = 'stroke="#120d24" stroke-opacity=".55" stroke-width="2.5" stroke-linejoin="round"'


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">{DEFS}{body}</svg>')


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


# --------------------------------------------------------------- partes comunes
def sombra(cx=256, cy=SUELO + 4, rx=125, ry=15, op=.4):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#000" '
            f'opacity="{op}" filter="url(#blur8)"/>')


def seg(w, L, fill, y0=0, r=None):
    r = r if r is not None else w / 2.6
    return (f'<rect x="{-w/2}" y="{y0}" width="{w}" height="{L}" rx="{r}" '
            f'fill="url(#{fill})" {OUT}/>')


def junta(r=21, y=0):
    return (f'<circle cx="0" cy="{y}" r="{r}" fill="url(#gMetal)" {OUT}/>'
            f'<circle cx="0" cy="{y}" r="{r*0.42}" fill="#15151b"/>')


def manga(far=False, w=50, largo=62):
    g = "gKhF" if far else "gKh"
    hw = w / 2
    return (f'<path d="M {-hw} 8 C {-hw} -12, {hw} -12, {hw} 8 L {hw+3} {largo} '
            f'Q 0 {largo+7} {-hw-3} {largo} Z" fill="url(#{g})" {OUT}/>'
            f'<path d="M {-hw-3} {largo-3} Q 0 {largo+4} {hw+3} {largo-3}" fill="none" '
            f'stroke="#2e2618" stroke-opacity=".6" stroke-width="3"/>')


def mano(far=False, w=40):
    g = "gPurF" if far else "gPur"
    dedos = ""
    for i, dx in enumerate((-13, -1, 11)):
        dedos += (f'<rect x="{dx-6}" y="22" width="13" height="{24 - abs(dx)*0.4}" rx="6.5" '
                  f'fill="url(#{g})" {OUT}/>')
    garras = "".join(
        f'<path d="M {dx-4.5} {44 - abs(dx)*0.4} L {dx+4.5} {44 - abs(dx)*0.4} L {dx+1} {60 - abs(dx)*0.3} Z" '
        f'fill="#b8b8c8" stroke="#15151b" stroke-width="1.5"/>' for dx in (-13, -1, 11))
    dedos += garras
    return (f'<g>{dedos}<ellipse cx="0" cy="14" rx="{w/2}" ry="20" fill="url(#{g})" {OUT}/>'
            f'<ellipse cx="-19" cy="14" rx="9" ry="14" fill="url(#{g})" {OUT}/></g>')


def oreja(largo=128, angulo=0, doblada=False, lado=1, far=False):
    ext = "gPurF" if far else "gPur"
    if doblada:
        p = ("M -20 0 C -26 -40 -22 -75 -8 -95 C 5 -110 40 -118 62 -104 "
             "C 70 -96 66 -84 56 -84 C 40 -84 30 -78 24 -60 C 22 -30 20 -10 20 0 Z")
        ip = ("M -10 -4 C -14 -40 -12 -72 -2 -88 C 8 -98 36 -104 52 -96 "
              "C 40 -92 30 -86 22 -66 C 16 -40 12 -14 10 -4 Z")
    else:
        k = largo / 128
        p = (f"M -20 0 C -27 {-50*k} -22 {-108*k} -4 {-127*k} C 12 {-134*k} 26 {-108*k} 22 {-60*k} "
             f"C 21 {-30*k} 20 -10 20 0 Z")
        ip = (f"M -10 -6 C -15 {-46*k} -12 {-98*k} -3 {-116*k} C 6 {-122*k} 14 {-100*k} 11 {-58*k} "
              f"C 10 {-30*k} 10 -12 10 -6 Z")
    return (f'<g transform="rotate({angulo})">'
            f'<path d="{p}" fill="url(#{ext})" {OUT}/>'
            f'<path d="{ip}" fill="url(#rEar)" opacity=".95"/></g>')


def dientes(x0, x1, y, alto, n, inv=False):
    ancho = (x1 - x0) / n
    s = ""
    for i in range(n):
        x = x0 + i * ancho
        s += (f'<rect x="{x+0.8:.1f}" y="{y}" width="{ancho-1.6:.1f}" height="{alto}" '
              f'rx="2.5" fill="url(#gTooth)" stroke="#3a3326" stroke-width="1"/>')
    return s


def dientes_af(x0, x1, y, alto, n, abajo=True):
    """Dientes triangulares. abajo=True: cuelgan desde y; False: apuntan hacia arriba."""
    ancho = (x1 - x0) / n
    s = ""
    for i in range(n):
        x = x0 + i * ancho
        h = alto * (1.0 if i % 2 == 0 else 0.68) * (1.15 if i in (1, n - 2) else 1)
        punta = y + h if abajo else y - h
        s += (f'<path d="M {x:.1f} {y} L {x+ancho:.1f} {y} L {x+ancho/2:.1f} {punta:.1f} Z" '
              f'fill="url(#gTooth)" stroke="#2a2418" stroke-width="1.2" stroke-linejoin="round"/>')
    return s


def parche_endo():
    """Zona del rostro sin pelaje: se ve el endoesqueleto."""
    return ('<g><path d="M -20 -30 L -4 -36 L 6 -20 L 18 -26 L 24 -6 L 12 6 L 16 24 L 0 22 L -8 34 '
            'L -24 14 L -26 -8 Z" fill="#0a0812" stroke="#150f2c" stroke-width="2"/>'
            '<path d="M -14 -22 L 10 -18 L 12 6 L -8 12 L -18 0 Z" fill="url(#gMetal)" '
            'stroke="#08060e" stroke-width="1.5"/>'
            '<circle cx="-8" cy="-12" r="2.6" fill="#15151b"/><circle cx="4" cy="-8" r="2.6" fill="#15151b"/>'
            '<circle cx="-4" cy="4" r="2.6" fill="#15151b"/>'
            '<path d="M -6 14 C -12 30 -2 40 -8 56 M 4 12 C 12 26 4 40 10 52" fill="none" '
            'stroke="#a01822" stroke-width="2.5" stroke-linecap="round"/>'
            '<path d="M 0 12 C -2 28 6 36 2 50" fill="none" stroke="#1e3f7a" stroke-width="2.2" '
            'stroke-linecap="round"/></g>')


# --------------------------------------------------------------- cabeza frontal
def ojo_frontal(x, glow, glitch, look=0, r=7):
    o = (f'<ellipse cx="{x}" cy="-10" rx="25" ry="22" fill="url(#rSocket)"/>')
    if glitch:
        return o + f'<circle cx="{x+look}" cy="-10" r="2.4" fill="#fff"/>'
    rr = r + (6 if glow else 0)
    ray = ""
    if glow:
        ray = "".join(
            f'<path d="M {x+look} -10 L {x+look+math.cos(a)*(rr+16):.1f} {-10+math.sin(a)*(rr+16):.1f}" '
            f'stroke="#ff3030" stroke-width="1.6" opacity=".7"/>'
            for a in (i * math.pi / 4 + 0.2 for i in range(8)))
    return (o + f'<g filter="url(#glow)">{ray}<circle cx="{x+look}" cy="-10" r="{rr}" fill="#ff2a2a"/>'
            f'<circle cx="{x+look}" cy="-10" r="{rr*0.42:.1f}" fill="#ffe4d8"/></g>')


def sangre_ojo(x, largo=54):
    return (f'<path d="M {x-7} 8 C {x-12} 28 {x-4} {largo-16} {x-9} {largo}" fill="none" '
            f'stroke="#12040a" stroke-width="6" stroke-linecap="round" opacity=".9"/>'
            f'<path d="M {x-7} 8 C {x-12} 28 {x-4} {largo-16} {x-9} {largo}" fill="none" '
            f'stroke="#7a0c16" stroke-width="2.4" stroke-linecap="round"/>'
            f'<path d="M {x+8} 10 C {x+12} 24 {x+8} 34 {x+10} {largo-22}" fill="none" '
            f'stroke="#12040a" stroke-width="4" stroke-linecap="round" opacity=".85"/>')


def cabeza_frontal(mouth=0.0, glow=False, glitch=False, brow=8, ear_l=0, ear_r=0,
                   look=0, tilt=0):
    m = clamp(mouth)
    o = []
    # orejas (detras)
    o.append(f'<g transform="translate(-50,-58)">{oreja(angulo=-8+ear_l)}</g>')
    o.append(f'<g transform="translate(50,-58)">{oreja(angulo=12+ear_r, doblada=True)}</g>')
    # craneo
    o.append('<path d="M -84 -10 C -88 -60 -50 -84 0 -84 C 50 -84 88 -60 84 -10 '
             'C 82 30 70 70 40 88 C 20 98 -20 98 -40 88 C -70 70 -82 30 -84 -10 Z" '
             f'fill="url(#rHead)" {OUT}/>')
    o.append('<path d="M -84 -10 C -88 -60 -50 -84 0 -84 C 50 -84 88 -60 84 -10 '
             'C 82 30 70 70 40 88 C 20 98 -20 98 -40 88 C -70 70 -82 30 -84 -10 Z" fill="url(#rShade)"/>')
    # pelo de Pruscino
    o.append('<path d="M -58 -68 C -54 -98 -22 -104 -6 -92 C 6 -110 38 -108 52 -76 '
             'C 40 -82 26 -74 14 -78 L 8 -64 C -6 -72 -12 -66 -18 -74 C -30 -70 -44 -72 -58 -68 Z" '
             f'fill="url(#rHair)" {OUT}/>')
    o.append('<path d="M -40 -84 l 6 -14 l 5 12 M -10 -92 l 4 -16 l 6 14 M 22 -90 l 8 -14 l 2 16" '
             'fill="none" stroke="#2a1c15" stroke-width="5" stroke-linecap="round"/>')
    # hocico
    o.append('<path d="M -56 30 C -58 6 -30 -2 0 -2 C 30 -2 58 6 56 30 '
             'C 54 60 30 78 0 78 C -30 78 -54 60 -56 30 Z" '
             f'fill="url(#rMuz)" {OUT}/>')
    # barba (contorno mandibula)
    o.append('<path d="M -80 6 C -78 56 -50 92 0 97 C 50 92 78 56 80 6 '
             'C 70 46 52 62 30 66 L -30 66 C -52 62 -70 46 -80 6 Z" '
             'fill="#2a1c16" opacity=".88"/>')
    o.append('<path d="M -74 22 l 6 6 M -66 42 l 7 5 M -52 62 l 8 3 M 74 22 l -6 6 M 66 42 l -7 5 '
             'M 52 62 l -8 3 M -36 78 l 5 3 M 36 78 l -5 3" stroke="#0f0906" stroke-width="2" '
             'stroke-linecap="round" opacity=".7"/>')
    o.append(f'<g transform="translate(-58,14) scale(1.1)">{parche_endo()}</g>')
    o.append(f'<g transform="translate(58,40) rotate(12) scale(.6)">{parche_endo()}</g>')
    o.append('<path d="M -14 -76 C -10 -46 -22 -34 -14 -14 M 20 -74 C 24 -56 18 -50 22 -38" fill="none" '
             'stroke="#5a0a12" stroke-width="4" stroke-linecap="round" opacity=".85"/>'
             '<circle cx="-14" cy="-10" r="3" fill="#5a0a12"/><circle cx="22" cy="-36" r="2.4" fill="#5a0a12"/>'
             '<circle cx="40" cy="14" r="2" fill="#5a0a12"/><circle cx="-30" cy="44" r="2.6" fill="#5a0a12"/>')
    # nariz
    o.append(f'<ellipse cx="0" cy="22" rx="12" ry="8" fill="#231a2e" {OUT}/>'
             '<ellipse cx="-3" cy="19" rx="4" ry="2.2" fill="#fff" opacity=".35"/>')
    # boca (sonrisa desgarrada, mas ancha que el hocico)
    if m > 0.08:
        alto = 56 + m * 50
        o.append(f'<path d="M -54 52 Q -62 {alto-8} 0 {alto} Q 62 {alto-8} 54 52 Z" '
                 f'fill="url(#rMouth)" {OUT}/>')
        o.append(f'<ellipse cx="0" cy="{alto-14}" rx="28" ry="{5+m*11}" fill="#5a1220" opacity=".9"/>')
        o.append(f'<ellipse cx="0" cy="{alto+12}" rx="68" ry="24" fill="url(#rHeadB)" {OUT}/>')
        o.append(dientes_af(-50, 50, alto + 2, 19 + m * 6, 9, abajo=False))
        o.append(dientes_af(-52, 52, 52, 19 + m * 10, 9, abajo=True))
        o.append('<path d="M -54 52 L -70 36 M -54 52 L -72 48 M 54 52 L 70 36 M 54 52 L 72 48" '
                 'stroke="#6a0c14" stroke-width="3" stroke-linecap="round"/>')
        o.append(f'<path d="M -30 {alto} C -28 {alto+14} -34 {alto+26} -30 {alto+40} M 34 {alto} '
                 f'C 36 {alto+18} 30 {alto+30} 34 {alto+52}" fill="none" stroke="#7a0c16" '
                 f'stroke-width="4" stroke-linecap="round"/>')
        gy = alto - 50
    else:
        o.append('<path d="M -56 46 Q 0 68 56 46 Q 0 100 -56 46 Z" fill="url(#rMouth)" '
                 'stroke="#0d0812" stroke-width="2.5"/>')
        o.append(dientes_af(-52, 52, 55, 15, 10, abajo=True))
        o.append(dientes_af(-46, 46, 79, 11, 9, abajo=False))
        o.append('<path d="M -56 46 L -70 32 M -56 46 L -72 44 M 56 46 L 70 32 M 56 46 L 72 44" '
                 'stroke="#6a0c14" stroke-width="3" stroke-linecap="round"/>')
        o.append('<path d="M 30 70 C 34 88 26 98 30 114 M -22 72 C -20 84 -25 90 -22 100" fill="none" '
                 'stroke="#7a0c16" stroke-width="4" stroke-linecap="round"/>')
        gy = 0
    # bigote
    o.append('<path d="M -34 42 C -18 30 -5 38 0 40 C 5 38 18 30 34 42 C 22 55 8 47 0 47 '
             'C -8 47 -22 55 -34 42 Z" fill="#20140f" stroke="#0f0906" stroke-width="1.5"/>')
    # candado (perilla)
    o.append(f'<g transform="translate(0,{gy})"><path d="M -24 64 C -22 84 -10 100 0 103 '
             'C 10 100 22 84 24 64 C 12 72 -12 72 -24 64 Z" fill="#2a1c16" '
             'stroke="#0f0906" stroke-width="1.5"/>'
             '<path d="M -10 78 l 3 8 M 0 82 l 0 10 M 10 78 l -3 8" stroke="#0f0906" '
             'stroke-width="2" stroke-linecap="round" opacity=".7"/></g>')
    # ojos
    o.append(ojo_frontal(-38, glow, glitch, look, r=10))
    o.append(ojo_frontal(38, glow, glitch, look, r=4))
    o.append(sangre_ojo(-38))
    o.append(sangre_ojo(38, 40))
    o.append('<ellipse cx="-38" cy="10" rx="22" ry="6" fill="#0a0612" opacity=".45"/><ellipse cx="38" cy="10" rx="22" ry="6" fill="#0a0612" opacity=".45"/>')
    # cejas
    o.append(f'<path d="M -68 {-38+brow*0.2} L -12 {-34-brow*0.9}" stroke="#171029" stroke-width="9" '
             'stroke-linecap="round"/>'
             f'<path d="M 68 {-38+brow*0.2} L 12 {-34-brow*0.9}" stroke="#171029" stroke-width="9" '
             'stroke-linecap="round"/>')
    # anteojos
    for cx in (-38, 38):
        o.append(f'<g transform="rotate({-3 if cx < 0 else 0} {cx} -14)"><rect x="{cx-30}" y="-36" width="60" height="44" rx="9" fill="#bcd6f0" '
                 f'fill-opacity=".10" stroke="#100d18" stroke-width="5.5"/></g>'
                 f'<path d="M {cx-22} -30 L {cx-8} -30 L {cx-16} 0 L {cx-24} 0 Z" fill="#fff" opacity=".22"/>')
    o.append('<path d="M 24 -34 L 40 -14 L 32 -2 M 40 -14 L 58 -22 M 40 -14 L 46 4" fill="none" '
             'stroke="#e8f0ff" stroke-width="1.6" opacity=".75"/>')
    o.append('<path d="M -8 -20 Q 0 -27 8 -20" fill="none" stroke="#100d18" stroke-width="5"/>')
    o.append('<path d="M -68 -20 L -86 -16 M 68 -20 L 86 -16" stroke="#100d18" stroke-width="5" '
             'stroke-linecap="round"/>')
    return f'<g transform="rotate({tilt})">{"".join(o)}</g>'


# --------------------------------------------------------------- cabeza trasera
def cabeza_trasera(ear_l=0, ear_r=0, tilt=0):
    o = []
    o.append(f'<g transform="translate(-50,-58)">{oreja(angulo=-8+ear_l)}</g>')
    o.append(f'<g transform="translate(50,-58)">{oreja(angulo=12+ear_r, doblada=True)}</g>')
    o.append('<path d="M -84 -10 C -88 -60 -50 -84 0 -84 C 50 -84 88 -60 84 -10 '
             'C 82 30 70 70 40 88 C 20 98 -20 98 -40 88 C -70 70 -82 30 -84 -10 Z" '
             f'fill="url(#rHeadB)" {OUT}/>')
    o.append('<path d="M -84 -10 C -88 -60 -50 -84 0 -84 C 50 -84 88 -60 84 -10 '
             'C 82 30 70 70 40 88 C 20 98 -20 98 -40 88 C -70 70 -82 30 -84 -10 Z" fill="url(#rShade)"/>')
    # pelo (parte superior/trasera de la cabeza)
    o.append('<path d="M -74 -12 C -84 -62 -44 -92 0 -92 C 44 -92 84 -62 74 -12 '
             'C 66 8 44 12 26 6 C 10 14 -10 14 -26 6 C -44 12 -66 8 -74 -12 Z" '
             f'fill="url(#rHair)" {OUT}/>')
    o.append('<path d="M -50 -60 q 6 20 2 40 M -20 -74 q 4 24 0 50 M 16 -76 q 4 24 0 52 '
             'M 46 -60 q -2 22 -6 38" fill="none" stroke="#0e0806" stroke-width="3" opacity=".6" '
             'stroke-linecap="round"/>')
    # patillas de los anteojos
    o.append('<path d="M -84 -18 L -70 -14 M 84 -18 L 70 -14" stroke="#100d18" stroke-width="5" '
             'stroke-linecap="round"/>')
    return f'<g transform="rotate({tilt})">{"".join(o)}</g>'


# --------------------------------------------------------------- cabeza lateral (mira a la izquierda)
def cabeza_lateral(mouth=0.0, glow=False, glitch=False, ear_a=0, tilt=0, brow=4):
    m = clamp(mouth)
    o = []
    o.append(f'<g transform="translate(34,-58)">{oreja(angulo=16+ear_a, far=True)}</g>')
    o.append(f'<g transform="translate(6,-62)">{oreja(angulo=6+ear_a*0.6, doblada=False)}</g>')
    # craneo
    o.append('<path d="M -60 -10 C -64 -56 -30 -78 8 -76 C 52 -74 74 -44 70 0 '
             'C 68 40 50 70 16 80 C -10 84 -30 76 -44 62 Z" '
             f'fill="url(#rHead)" {OUT}/>')
    o.append('<path d="M -60 -10 C -64 -56 -30 -78 8 -76 C 52 -74 74 -44 70 0 '
             'C 68 40 50 70 16 80 C -10 84 -30 76 -44 62 Z" fill="url(#rShade)"/>')
    # nuca con pelo
    o.append('<path d="M -34 -74 C 10 -92 66 -72 72 -26 C 62 -46 40 -54 14 -52 '
             'C -6 -50 -24 -58 -34 -74 Z" '
             f'fill="url(#rHair)" {OUT}/>')
    o.append('<path d="M -20 -76 l 4 -14 l 6 12 M 8 -80 l 6 -14 l 3 14" fill="none" '
             'stroke="#2a1c15" stroke-width="5" stroke-linecap="round"/>')
    # hocico
    if m > 0.08:
        oy = 24 + m * 26
        o.append(f'<path d="M -106 22 C -108 6 -70 0 -40 6 L -34 44 L -104 40 Z" '
                 f'fill="url(#rMuz)" {OUT}/>')
        o.append(f'<path d="M -104 40 L -34 44 L -34 {44+m*26} L -100 {40+m*22} Z" fill="url(#rMouth)"/>')
        o.append(dientes_af(-100, -38, 40, 11, 7))
        o.append(f'<g transform="rotate({m*16} -34 46)"><path d="M -100 46 C -104 60 -70 74 -30 66 '
                 f'L -34 44 Z" fill="url(#rMuz)" {OUT}/>'
                 f'{dientes_af(-96, -40, 44, 10, 7, abajo=False)}</g>')
    else:
        o.append(f'<path d="M -106 22 C -108 4 -70 -2 -38 6 L -30 60 C -60 74 -100 60 -104 40 Z" '
                 f'fill="url(#rMuz)" {OUT}/>')
        o.append('<path d="M -104 40 Q -70 54 -34 46 Q -70 66 -104 40 Z" fill="url(#rMouth)"/>')
        o.append(dientes_af(-100, -40, 41, 10, 8))
        o.append(dientes_af(-92, -42, 52, 7, 6, abajo=False))
        o.append('<path d="M -104 42 Q -70 50 -34 46" fill="none" stroke="#0d0812" stroke-width="3.5" '
                 'stroke-linecap="round"/>')
    o.append(f'<ellipse cx="-104" cy="20" rx="11" ry="9" fill="#231a2e" {OUT}/>'
             '<ellipse cx="-106" cy="17" rx="4" ry="2.2" fill="#fff" opacity=".35"/>')
    o.append(f'<g transform="translate(24,20) scale(.9)">{parche_endo()}</g>')
    # barba
    o.append('<path d="M -96 50 C -80 74 -40 90 0 84 C 30 78 56 60 68 20 C 50 52 30 62 0 62 '
             'C -30 62 -60 58 -96 50 Z" fill="#2a1c16" opacity=".9"/>')
    o.append('<path d="M -92 52 C -90 70 -80 84 -72 88 C -62 82 -56 70 -56 58 Z" fill="#2a1c16" '
             'stroke="#0f0906" stroke-width="1.5"/>')
    # bigote
    o.append('<path d="M -102 32 C -84 26 -62 30 -44 36 C -60 46 -84 44 -102 32 Z" fill="#20140f"/>')
    # ojo
    o.append('<ellipse cx="-30" cy="-10" rx="19" ry="17" fill="url(#rSocket)"/>')
    if glitch:
        o.append('<circle cx="-33" cy="-10" r="2.4" fill="#fff"/>')
    else:
        rr = 8 + (5 if glow else 0)
        o.append(f'<g filter="url(#glow)"><circle cx="-34" cy="-10" r="{rr}" fill="#ff2a2a"/>'
                 f'<circle cx="-34" cy="-10" r="{rr*0.42:.1f}" fill="#ffe4d8"/></g>')
    o.append(f'<path d="M -56 {-32+brow*0.3} L -8 {-30-brow*0.8}" stroke="#171029" stroke-width="9" '
             'stroke-linecap="round"/>')
    # anteojos
    o.append('<rect x="-58" y="-36" width="54" height="44" rx="9" fill="#bcd6f0" fill-opacity=".14" '
             'stroke="#100d18" stroke-width="5.5"/>'
             '<path d="M -50 -30 L -36 -30 L -44 0 L -52 0 Z" fill="#fff" opacity=".22"/>'
             '<path d="M -4 -22 L 58 -14" stroke="#100d18" stroke-width="5" stroke-linecap="round"/>')
    return f'<g transform="rotate({tilt})">{"".join(o)}</g>'


# --------------------------------------------------------------- torso
def camisa(path_forma, cuello_y=-14, front=True, rip=True):
    o = [f'<path d="{path_forma}" fill="url(#gKh)" {OUT}/>']
    # pliegues
    o.append('<path d="M -40 40 q 6 30 -2 70 M 30 30 q -8 40 2 84 M 0 60 q 3 30 -1 66" '
             'fill="none" stroke="#2c2416" stroke-opacity=".28" stroke-width="5" stroke-linecap="round"/>')
    o.append('<ellipse cx="34" cy="120" rx="20" ry="28" fill="#4a0a10" opacity=".55"/>'
             '<ellipse cx="0" cy="8" rx="30" ry="10" fill="#4a0a10" opacity=".5"/>'
             '<circle cx="-60" cy="60" r="4" fill="#4a0a10" opacity=".6"/><circle cx="52" cy="70" r="5" fill="#4a0a10" opacity=".6"/>'
             '<path d="M 26 100 C 28 130 24 150 30 176 L 40 176 C 36 150 42 130 40 104 Z" fill="#4a0a10" opacity=".4"/>')
    if rip:
        o.append('<path d="M 30 30 L 44 24 L 52 38 L 62 30 L 64 56 L 52 66 L 56 80 L 38 72 L 28 56 Z" '
                 'fill="#0d0a16" stroke="#050308" stroke-width="2"/>'
                 '<path d="M 34 40 Q 46 36 58 42 M 34 54 Q 46 50 58 56" fill="none" stroke="#7d7d90" '
                 'stroke-width="3.5" stroke-linecap="round"/>')
        o.append('<path d="M -50 104 L -36 96 L -28 110 L -16 98 L -8 120 L -16 144 L -10 170 L -34 160 '
                 'L -46 174 L -56 140 Z" fill="#0d0a16" stroke="#050308" stroke-width="2"/>'
                 '<path d="M -44 118 Q -28 112 -14 120 M -46 134 Q -28 128 -12 136 M -44 150 Q -28 144 -14 152" '
                 'fill="none" stroke="#7d7d90" stroke-width="3.5" stroke-linecap="round"/>'
                 '<path d="M -30 106 L -30 166" stroke="#5d5d70" stroke-width="3"/>'
                 '<path d="M -22 150 C -12 160 -18 172 -8 184" fill="none" stroke="#a01822" stroke-width="2.5"/>'
                 '<path d="M 14 186 l 4 -14 l 6 10 l 6 -18 l 8 20 l 6 -10 l 6 12 Z" fill="#171226" '
                 'stroke="#0a0812" stroke-width="1.5"/>')
    return "".join(o)


def torso_frontal():
    forma = ("M -88 12 C -88 -6 -50 -16 0 -16 C 50 -16 88 -6 88 12 L 80 92 "
             "C 76 130 66 160 60 186 L -60 186 C -66 160 -76 130 -80 92 Z")
    o = [f'<path d="{forma}" fill="url(#gPur)" {OUT}/>']
    o.append(camisa(forma))
    # cuello de la remera
    o.append('<ellipse cx="0" cy="-8" rx="36" ry="17" fill="#2f2660" stroke="#2a2214" stroke-width="4"/>')
    return "".join(o)


def mono_rojo(y=8):
    return (f'<g transform="translate(0,{y})">'
            f'<path d="M -3 0 L -52 -22 C -60 -6 -60 14 -52 26 Z" fill="url(#gRed)" {OUT}/>'
            f'<path d="M 3 0 L 52 -22 C 60 -6 60 14 52 26 Z" fill="url(#gRed)" {OUT}/>'
            f'<path d="M -34 -8 L -10 -2 M 34 -8 L 10 -2 M -34 14 L -10 4 M 34 14 L 10 4" '
            f'stroke="#3a0810" stroke-width="2" opacity=".6"/>'
            f'<rect x="-11" y="-13" width="22" height="26" rx="8" fill="url(#gRed)" {OUT}/></g>')


def torso_trasero():
    forma = ("M -88 12 C -88 -6 -50 -16 0 -16 C 50 -16 88 -6 88 12 L 80 92 "
             "C 76 130 66 160 60 186 L -60 186 C -66 160 -76 130 -80 92 Z")
    o = [f'<path d="{forma}" fill="url(#gPur)" {OUT}/>']
    o.append(camisa(forma, rip=False))
    o.append('<path d="M -34 -14 Q 0 6 34 -14" fill="none" stroke="#2a2214" stroke-width="5"/>')
    o.append('<path d="M -40 -8 Q 0 14 40 -8 L 40 -2 Q 0 20 -40 -2 Z" fill="url(#gRed)" opacity=".9"/>')
    return "".join(o)


def torso_lateral():
    forma = ("M -44 12 C -44 -6 -20 -16 8 -16 C 36 -16 50 -4 50 14 L 46 92 "
             "C 44 130 40 160 40 186 L -40 186 C -44 160 -46 130 -46 92 Z")
    o = [f'<path d="{forma}" fill="url(#gPur)" {OUT}/>']
    o.append(camisa(forma, rip=False))
    o.append('<path d="M -24 -12 q 22 12 44 0" fill="none" stroke="#2a2214" stroke-width="5"/>')
    return "".join(o)


def pelvis(ancho=130):
    return (f'<rect x="{-ancho/2}" y="176" width="{ancho}" height="40" rx="16" '
            f'fill="url(#gPur)" {OUT}/>')


# --------------------------------------------------------------- extremidades frontal
def brazo_frontal(x, y, lado, a1, a2, sy=1.0, far=False):
    """lado: -1 = izquierdo del espectador, +1 = derecho. angulos positivos = hacia -x."""
    g = "gPurF" if far else "gPur"
    return (f'<g transform="translate({x},{y}) rotate({a1}) scale(1,{sy})">'
            f'{seg(46, 100, g, y0=-6)}{manga(far)}'
            f'<g transform="translate(0,96) rotate({a2})">{junta(20)}'
            f'{seg(38, 96, g, y0=6)}'
            + (('<g transform="translate(0,40)"><path d="M -17 -16 L 8 -22 L 18 2 L 8 20 L -14 14 Z" '
                'fill="#0a0812" stroke="#150f2c" stroke-width="2"/>'
                '<rect x="-9" y="-10" width="18" height="20" fill="url(#gMetal)" stroke="#08060e"/>'
                '<circle cx="0" cy="0" r="3" fill="#15151b"/>'
                '<path d="M 4 18 C 12 30 2 38 8 48" fill="none" stroke="#a01822" stroke-width="2.5"/></g>')
               if lado < 0 and not far else '') +
            f'<g transform="translate(0,92)">{mano(far)}</g></g></g>')


def pie_frontal(atras=False):
    dedos = "".join(
        f'<path d="M {x-9} 28 Q {x} 44 {x+9} 28" fill="none" stroke="#150f2c" stroke-width="2.5" '
        f'opacity=".8"/>' for x in (-20, 0, 20))
    talon = ('<ellipse cx="0" cy="8" rx="30" ry="10" fill="#150f2c" opacity=".35"/>'
             if atras else "")
    return (f'<path d="M -30 -2 C -42 16 -46 32 -32 38 L 32 38 C 46 32 42 16 30 -2 Z" '
            f'fill="url(#gPur)" {OUT}/>{dedos}{talon}'
            f'<path d="M -24 20 Q 0 12 24 20" fill="none" stroke="#a89ad8" stroke-opacity=".3" '
            f'stroke-width="3"/>')


def pierna_frontal(x, y, sx=1.0, sy=1.0, dy=0, atras=False):
    return (f'<g transform="translate({x},{y+dy}) scale({sx},{sy})">'
            f'{seg(66, 110, "gPur", y0=-8)}'
            f'<g transform="translate(0,108)">{junta(24)}{seg(56, 104, "gPur", y0=6)}'
            f'<g transform="translate(0,104)">{junta(20)}'
            f'<g transform="translate(0,4)">{pie_frontal(atras)}</g></g></g></g>')


# --------------------------------------------------------------- figuras
def figura_frontal(bob=0, tilt=0, mouth=0, ear_l=0, ear_r=0, brazo_i=(6, -10), brazo_d=(-6, 10),
                   pierna_i=(1, 1, 0), pierna_d=(1, 1, 0), brow=8, glow=False, glitch=False,
                   sway=0, look=0, brazo_sy=(1, 1), trasera=False, cab_dy=0, fur=True):
    tx = 256
    o = [sombra()]
    piernas = (pierna_frontal(222, 496, *pierna_i, atras=trasera),
               pierna_frontal(290, 496, *pierna_d, atras=trasera))
    o.append(f'<g transform="translate(0,{bob})">')
    o.extend(piernas)
    o.append(f'<g transform="rotate({sway} {tx} 490)">')
    o.append(f'<g transform="translate({tx},300)">{pelvis()}</g>')
    o.append(f'<g transform="translate({tx},300)">'
             f'{torso_trasero() if trasera else torso_frontal()}</g>')
    if not trasera:
        o.append(f'<g transform="translate({tx},300)">{mono_rojo(22)}</g>')
    o.append(brazo_frontal(tx - 90, 322, -1, *brazo_i, sy=brazo_sy[0]))
    o.append(brazo_frontal(tx + 90, 322, 1, *brazo_d, sy=brazo_sy[1]))
    o.append(f'<g transform="translate({tx},316)"><rect x="-30" y="-24" width="60" height="30" '
             f'fill="url(#gPur)"/></g>')
    cab = (cabeza_trasera(ear_l, ear_r, tilt) if trasera
           else cabeza_frontal(mouth, glow, glitch, brow, ear_l, ear_r, look, tilt))
    o.append(f'<g transform="translate({tx},{218+cab_dy})">{cab}</g>')
    o.append('</g></g>')
    if not fur:
        return o[0] + "".join(o[1:])
    return o[0] + f'<g filter="url(#fur)">{"".join(o[1:])}</g>'


# ---- lateral
def pie_lateral(far=False):
    g = "gPurF" if far else "gPur"
    return (f'<path d="M -12 -8 C -52 -2 -70 14 -66 30 C -64 42 -20 44 22 42 C 32 40 32 20 26 -8 Z" '
            f'fill="url(#{g})" {OUT}/>'
            f'<path d="M -60 22 q 6 12 16 16 M -46 10 q 6 18 18 26" fill="none" stroke="#150f2c" '
            f'stroke-width="2.5" opacity=".7"/>')


def pierna_lateral(x, y, a, b, fa, far=False):
    g = "gPurF" if far else "gPur"
    return (f'<g transform="translate({x},{y}) rotate({a})">'
            f'{seg(60, 108, g, y0=-8)}'
            f'<g transform="translate(0,106) rotate({b})">{junta(23)}{seg(50, 104, g, y0=6)}'
            f'<g transform="translate(0,104) rotate({fa})">{junta(18)}'
            f'<g transform="translate(0,2)">{pie_lateral(far)}</g></g></g></g>')


def brazo_lateral(x, y, a1, a2, far=False):
    g = "gPurF" if far else "gPur"
    return (f'<g transform="translate({x},{y}) rotate({a1})">'
            f'{seg(44, 100, g, y0=-6)}{manga(far, w=50)}'
            f'<g transform="translate(0,96) rotate({a2})">{junta(19)}{seg(36, 96, g, y0=6)}'
            f'<g transform="translate(0,92)">{mano(far, w=34)}</g></g></g>')


def altura_pie(a, b, fa):
    r = math.radians
    return 106 * math.cos(r(a)) + 106 * math.cos(r(a + b)) + 40 * math.cos(r(a + b + fa))


def figura_lateral(pn, pf, an, af, lean=0, tilt=0, mouth=0, ear_a=0, glow=False, glitch=False,
                   brow=4, cab_dy=0):
    """pn/pf: (a,b) pierna cercana/lejana. an/af: (a1,a2) brazos. Mira a la izquierda."""
    hx, hy = 272, 496
    fan = -(pn[0] + pn[1]) * 0.8
    faf = -(pf[0] + pf[1]) * 0.8
    lowest = max(altura_pie(pn[0], pn[1], fan), altura_pie(pf[0], pf[1], faf))
    dy = (SUELO - 6) - (hy + lowest)
    o = [f'<g transform="translate(0,{dy:.2f})">']
    o.append(pierna_lateral(hx, hy, pf[0], pf[1], faf, far=True))
    o.append(f'<g transform="rotate({-lean} {hx} {hy})">')
    o.append(brazo_lateral(hx, 318, af[0], af[1], far=True))
    o.append(f'<g transform="translate({hx},300)">{pelvis(96)}{torso_lateral()}</g>')
    o.append(pierna_lateral(hx, hy, pn[0], pn[1], fan))
    o.append(f'<g transform="translate({hx},316)"><rect x="-26" y="-24" width="52" height="30" '
             f'fill="url(#gPur)"/></g>')
    o.append(f'<g transform="translate({hx-10},{218+cab_dy})">'
             f'{cabeza_lateral(mouth, glow, glitch, ear_a, tilt, brow)}</g>')
    o.append(brazo_lateral(hx, 318, an[0], an[1]))
    o.append('</g></g>')
    return sombra(cx=hx - 10, rx=120) + f'<g filter="url(#fur)">{"".join(o)}</g>'


# --------------------------------------------------------------- animaciones
def anim_idle(n=8):
    frames = []
    for i in range(n):
        t = 2 * math.pi * i / n
        glitch = (i == 5)
        frames.append(svg(W, H, figura_frontal(
            bob=round(2.5 * math.sin(t), 2),
            tilt=(-8 if i == 6 else round(4 * math.sin(t + 0.6), 2)),
            ear_l=round(3 * math.sin(t * 2), 2), ear_r=(9 if i in (3, 4) else 0),
            brazo_i=(6 + 2 * math.sin(t), -10 + 3 * math.sin(t + 1)),
            brazo_d=(-6 - 2 * math.sin(t), 10 - 3 * math.sin(t + 1)),
            mouth=(0.4 if i == 6 else 0.0), glitch=glitch,
            look=round(3 * math.sin(t * 1.0), 2))))
    return frames


def anim_caminar_frontal(n=8, trasera=False):
    frames = []
    for i in range(n):
        t = 2 * math.pi * i / n
        s = math.sin(t)          # >0: pierna izq adelante
        c = abs(math.cos(t))
        # frontal: pierna que avanza crece y baja; la que sube se acorta
        def pierna(sg):
            adelante = sg
            if adelante >= 0:
                escala = 1 + 0.05 * adelante
                sy = 1 + (0.03 if not trasera else -0.03) * adelante
                dy = 8 * adelante * (1 if not trasera else -0.4)
            else:
                escala = 1 - 0.03 * (-adelante)
                sy = 1 - 0.13 * (-adelante)
                dy = -4 * (-adelante)
            return (escala, sy, dy)
        pi = pierna(s)
        pd = pierna(-s)
        frames.append(svg(W, H, figura_frontal(
            bob=round(-5 * c, 2), tilt=round(3 * s, 2), sway=round(-2.5 * s, 2),
            brazo_i=(6 - 10 * s, -10 - 6 * abs(s)),
            brazo_d=(-6 - 10 * s, 10 + 6 * abs(s)),
            brazo_sy=(1 + 0.05 * s, 1 - 0.05 * s),
            pierna_i=pi, pierna_d=pd, trasera=trasera, ear_l=round(5 * s, 2),
            ear_r=round(-4 * s, 2), brow=8)))
    return frames


def anim_caminar_lateral(derecha=False, n=8):
    frames = []
    for i in range(n):
        t = 2 * math.pi * i / n

        def pierna(ph):
            a = 30 * math.sin(ph)
            b = -52 * max(0.0, math.cos(ph))
            return (a, b)
        pn = pierna(t)
        pf = pierna(t + math.pi)
        an = (-26 * math.sin(t), 22 + 14 * max(0, math.sin(t)))
        af = (26 * math.sin(t), 22 + 14 * max(0, -math.sin(t)))
        body = figura_lateral(pn, pf, an, af, lean=5, tilt=round(2 * math.sin(t * 2), 2),
                              ear_a=round(-8 * abs(math.sin(t)), 2))
        if derecha:
            body = f'<g transform="translate({W},0) scale(-1,1)">{body}</g>'
        frames.append(svg(W, H, body))
    return frames


def anim_ataque(n=12):
    rnd = random.Random(1987)
    frames = []
    for i in range(n):
        u = i / (n - 1)
        e = u ** 1.4
        s = 0.9 + 3.1 * e
        fy = 380 - 145 * clamp(u * 1.7)
        m = clamp((u - 0.12) * 2.1)
        alz = 125 * clamp(u * 2.2)
        j = 0 if i == 0 else (3 + 22 * u)
        jx, jy = rnd.uniform(-j, j), rnd.uniform(-j, j)
        jr = rnd.uniform(-j, j) * 0.35
        body = figura_frontal(
            bob=0, tilt=round(rnd.uniform(-4, 4) * u, 2), mouth=m, glow=(u > 0.08),
            brow=16 if u > 0.05 else 8, ear_l=round(-10 * u, 2), ear_r=round(12 * u, 2),
            brazo_i=(6 + alz, -22 * clamp(u * 2)), brazo_d=(-6 - alz, 22 * clamp(u * 2)),
            pierna_i=(1, 1, 0), pierna_d=(1, 1, 0), cab_dy=round(-14 * clamp(u * 2), 2), fur=False)
        def camara(dx, dy, dr):
            return (f'<g transform="translate({512 + dx:.1f},{384 + dy:.1f}) rotate({dr:.2f}) '
                    f'scale({s:.3f}) translate(-256,{-fy:.1f})">{body}</g>')
        fondo = (f'<rect width="{W_ATAQUE}" height="{H_ATAQUE}" fill="url(#rFondoRojo)" '
                 f'opacity="{clamp(u * 1.4):.2f}"/>')
        fantasma = ""
        if u > 0.25:
            fantasma = (f'<g opacity="{0.28:.2f}" style="mix-blend-mode:screen">'
                        f'{camara(-jx * 1.8 - 10 * u, jy * 1.2, -jr * 2)}</g>')
        frames.append(svg(W_ATAQUE, H_ATAQUE,
                          fondo + f'<g filter="url(#fur)">{fantasma}{camara(jx, jy, jr)}</g>'))
    return frames


ANIMACIONES = {
    "idle": (anim_idle, W, H),
    "caminar_abajo": (lambda: anim_caminar_frontal(), W, H),
    "caminar_arriba": (lambda: anim_caminar_frontal(trasera=True), W, H),
    "caminar_izquierda": (lambda: anim_caminar_lateral(False), W, H),
    "caminar_derecha": (lambda: anim_caminar_lateral(True), W, H),
    "ataque": (anim_ataque, W_ATAQUE, H_ATAQUE),
}


COLUMNAS = {"idle": 4, "caminar_abajo": 4, "caminar_arriba": 4, "caminar_izquierda": 4,
            "caminar_derecha": 4, "ataque": 4}


def armar_hoja(rutas, columnas, destino):
    from PIL import Image
    ims = [Image.open(r).convert("RGBA") for r in rutas]
    fw, fh = ims[0].size
    filas = math.ceil(len(ims) / columnas)
    hoja = Image.new("RGBA", (fw * columnas, fh * filas), (0, 0, 0, 0))
    for i, im in enumerate(ims):
        hoja.paste(im, ((i % columnas) * fw, (i // columnas) * fh))
    hoja.save(destino)
    return fw, fh, filas


def main():
    render = "--sin-png" not in sys.argv
    solo = [a for a in sys.argv[1:] if not a.startswith("--")]
    fuente = SALIDA / "fuente"
    hojas = SALIDA / "hojas"
    hojas.mkdir(parents=True, exist_ok=True)
    fuente.mkdir(parents=True, exist_ok=True)
    # la carpeta fuente/ no debe importarse en Godot
    (fuente / ".gdignore").write_text("", encoding="utf-8")
    for nombre, (fn, w, h) in ANIMACIONES.items():
        if solo and nombre not in solo:
            continue
        d_svg = fuente / "svg" / nombre
        d_png = fuente / "png" / nombre
        d_svg.mkdir(parents=True, exist_ok=True)
        d_png.mkdir(parents=True, exist_ok=True)
        rutas = []
        for k, contenido in enumerate(fn()):
            ruta_svg = d_svg / f"frame_{k:02d}.svg"
            ruta_svg.write_text(contenido, encoding="utf-8")
            ruta_png = d_png / f"frame_{k:02d}.png"
            if render:
                subprocess.run(["inkscape", str(ruta_svg), "-o", str(ruta_png),
                                "-w", str(w), "-h", str(h)],
                               check=True, capture_output=True)
            rutas.append(ruta_png)
        if render:
            fw, fh, filas = armar_hoja(rutas, COLUMNAS[nombre], hojas / f"{nombre}.png")
            print(f"{nombre}: {len(rutas)} frames de {fw}x{fh} | horizontal={COLUMNAS[nombre]} vertical={filas}")


if __name__ == "__main__":
    main()
