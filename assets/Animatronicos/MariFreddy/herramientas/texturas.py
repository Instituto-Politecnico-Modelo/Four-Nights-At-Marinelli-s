"""Texturas procedurales (numpy) para MariFreddy 3D (Freddy Fazbear + Nestor). Se ejecuta dentro de Blender."""
import numpy as np
import bpy


def vnoise(n, fx, fy, seed):
    """Ruido de valor periodico (tileable) de n x n con fx * fy celdas."""
    rng = np.random.default_rng(seed)
    g = rng.random((fy, fx))
    y = np.arange(n) / n * fy
    x = np.arange(n) / n * fx
    y0 = np.floor(y).astype(int)
    x0 = np.floor(x).astype(int)
    ty = y - y0
    tx = x - x0
    ty = ty * ty * (3 - 2 * ty)
    tx = tx * tx * (3 - 2 * tx)
    y1 = (y0 + 1) % fy
    x1 = (x0 + 1) % fx
    y0 %= fy
    x0 %= fx
    a = g[np.ix_(y0, x0)]
    b = g[np.ix_(y0, x1)]
    c = g[np.ix_(y1, x0)]
    d = g[np.ix_(y1, x1)]
    tx = tx[None, :]
    ty = ty[:, None]
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


def fbm(n, fx, fy, octaves, seed, pers=0.5):
    t = np.zeros((n, n))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        t += amp * vnoise(n, fx * 2 ** o, fy * 2 ** o, seed + o * 17)
        tot += amp
        amp *= pers
    return t / tot


def normal_from_height(h, fuerza):
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * fuerza
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * fuerza
    nrm = np.dstack([-dx, -dy, np.ones_like(h)])
    nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    return nrm * 0.5 + 0.5


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def guardar(nombre, rgb, ruta, no_color=False):
    n = rgb.shape[0]
    img = bpy.data.images.new(nombre, n, n, alpha=False)
    rgba = np.dstack([np.clip(rgb, 0, 1), np.ones((n, n))])
    # Blender guarda de abajo hacia arriba
    img.pixels = rgba[::-1].astype(np.float32).ravel()
    img.filepath_raw = ruta
    img.file_format = "PNG"
    img.save()
    if no_color:
        img.colorspace_settings.name = "Non-Color"
    return img


def hebras(n, seed, fx=220, fy=10):
    """Hebras verticales (pelaje)."""
    return (0.6 * vnoise(n, fx, fy, seed) + 0.4 * vnoise(n, fx * 2, fy * 2, seed + 3))


def pelaje(nombre, color, ruta_dir, n=1024, seed=1, suciedad=0.35, contraste=0.5):
    base = hex_rgb(color)
    manchas = fbm(n, 4, 4, 5, seed)
    h_ = hebras(n, seed + 5)
    lum = 0.78 + contraste * (manchas - 0.5) * 0.9 + 0.20 * (h_ - 0.5)
    sucio = np.clip((fbm(n, 3, 3, 4, seed + 40) - 0.5) * 3 + 0.5, 0, 1)
    lum = lum * (1 - suciedad * sucio * 0.55)
    rgb = base[None, None, :] * lum[:, :, None]
    guardar(nombre + "_c", rgb, f"{ruta_dir}/{nombre}_c.png")
    alto = 0.65 * h_ + 0.35 * fbm(n, 30, 30, 3, seed + 9)
    guardar(nombre + "_n", normal_from_height(alto, 5.0), f"{ruta_dir}/{nombre}_n.png", True)


def tela(nombre, color, ruta_dir, n=1024, seed=7, sangre=True, rayas=0, color_raya="#e9edf2"):
    base = hex_rgb(color)
    yy, xx = np.mgrid[0:n, 0:n] / n
    tejido = 0.5 + 0.25 * np.sin(xx * 2 * np.pi * 160) * np.sin(yy * 2 * np.pi * 160)
    tejido += 0.15 * (vnoise(n, 320, 320, seed) - 0.5)
    manchas = fbm(n, 3, 3, 5, seed + 2)
    sucio = np.clip((manchas - 0.45) * 3.2, 0, 1)
    lum = 0.85 + 0.25 * (tejido - 0.5) - 0.45 * sucio
    rgb = base[None, None, :] * lum[:, :, None]
    if rayas:
        # camisa de rayas finas verticales (la de Nestor)
        f = (xx * rayas) % 1.0
        r = np.clip(1 - np.abs(f - 0.5) / 0.16, 0, 1)
        r = np.clip(r * 1.6, 0, 1)[:, :, None]
        rgb = rgb * (1 - r) + hex_rgb(color_raya)[None, None, :] * lum[:, :, None] * r
    if sangre:
        for k in range(5):
            cx, cy = np.random.default_rng(seed + k).random(2)
            r = 0.05 + 0.05 * np.random.default_rng(seed + 10 + k).random()
            d = np.sqrt(((xx - cx + 0.5) % 1 - 0.5) ** 2 + ((yy - cy + 0.5) % 1 - 0.5) ** 2)
            m = np.clip(1 - d / r, 0, 1) ** 0.6 * (0.6 + 0.4 * vnoise(n, 20, 20, seed + k))
            rgb = rgb * (1 - m[:, :, None] * 0.85) + m[:, :, None] * np.array([0.22, 0.02, 0.03]) * 0.85
    guardar(nombre + "_c", rgb, f"{ruta_dir}/{nombre}_c.png")
    alto = tejido * 0.6 + fbm(n, 6, 6, 4, seed + 8) * 0.4
    guardar(nombre + "_n", normal_from_height(alto, 3.0), f"{ruta_dir}/{nombre}_n.png", True)


def pelo(nombre, color, ruta_dir, n=512, seed=21):
    base = hex_rgb(color)
    h_ = hebras(n, seed, 260, 8)
    lum = 0.55 + 0.9 * (h_ - 0.4)
    rgb = base[None, None, :] * np.clip(lum, 0.15, 1.6)[:, :, None]
    guardar(nombre + "_c", rgb, f"{ruta_dir}/{nombre}_c.png")
    guardar(nombre + "_n", normal_from_height(h_, 4.0), f"{ruta_dir}/{nombre}_n.png", True)


def metal(nombre, color, ruta_dir, n=512, seed=33):
    base = hex_rgb(color)
    rayas = vnoise(n, 400, 4, seed) * 0.6 + vnoise(n, 800, 8, seed + 1) * 0.4
    manchas = fbm(n, 4, 4, 4, seed + 4)
    lum = 0.7 + 0.5 * (manchas - 0.5) + 0.25 * (rayas - 0.5)
    oxido = np.clip((fbm(n, 5, 5, 4, seed + 12) - 0.55) * 4, 0, 1)
    rgb = base[None, None, :] * lum[:, :, None]
    rgb = rgb * (1 - oxido[:, :, None] * 0.6) + oxido[:, :, None] * np.array([0.25, 0.12, 0.06]) * 0.6
    guardar(nombre + "_c", rgb, f"{ruta_dir}/{nombre}_c.png")
    guardar(nombre + "_n", normal_from_height(rayas * 0.5 + manchas * 0.5, 2.0), f"{ruta_dir}/{nombre}_n.png", True)


def generar_todas(ruta_dir):
    pelaje("pelaje", "#6e3b1a", ruta_dir, seed=1, suciedad=0.45, contraste=0.55)
    pelaje("hocico", "#b58a58", ruta_dir, seed=2, suciedad=0.45, contraste=0.4)
    pelaje("oreja_int", "#8a5a34", ruta_dir, n=512, seed=3)
    tela("camisa", "#8fa8d0", ruta_dir, seed=7, rayas=40)
    pelo("pelo", "#2f2b2a", ruta_dir, seed=21)
    pelo("barba", "#8d8d8a", ruta_dir, seed=22)
    metal("metal", "#4a4a55", ruta_dir, seed=33)
    tela("sombrero", "#121114", ruta_dir, n=512, seed=51, sangre=False)
