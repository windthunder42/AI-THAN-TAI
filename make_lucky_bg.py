"""
Generates lucky_bg.jpg: a red & gold 'lucky' background (Tết style).
Crimson radial gradient, faint coin pattern, gold bokeh, yellow apricot blossoms (hoa mai)
in the corners, calm centre so the app content stays readable.

Run: .venv/bin/python make_lucky_bg.py
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080
SEED = 88
rng = random.Random(SEED)


def radial_gradient():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W * 0.5, H * 0.38
    d = np.sqrt(((x - cx) / W) ** 2 + ((y - cy) / H) ** 2) / 0.75
    d = np.clip(d, 0, 1) ** 1.2
    inner = np.array([196, 24, 32], np.float32)   # crimson
    outer = np.array([58, 4, 10], np.float32)     # deep maroon
    img = inner * (1 - d[..., None]) + outer * d[..., None]

    # warm golden glow near the top centre
    g = np.exp(-(((x - cx) / (W * 0.28)) ** 2 + ((y - H * 0.12) / (H * 0.30)) ** 2))
    img += np.array([90, 55, 0], np.float32) * g[..., None] * 0.55
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def coin_pattern():
    """Faint tiled ancient-coin motif (circle with a square hole)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    step = 120
    for row, y in enumerate(range(-step, H + step, step)):
        for x in range(-step, W + step, step):
            ox = x + (step // 2 if row % 2 else 0)
            r, s = 26, 8
            d.ellipse([ox - r, y - r, ox + r, y + r], outline=(255, 200, 80, 22), width=2)
            d.rectangle([ox - s, y - s, ox + s, y + s], outline=(255, 200, 80, 22), width=2)
    return layer


def bokeh():
    """Soft gold light orbs, denser toward the edges and bottom."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(170):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        # keep the central reading column calmer
        centre = math.exp(-(((x - W / 2) / (W * 0.22)) ** 2))
        if rng.random() < centre * 0.8:
            continue
        r = rng.choice([6, 10, 14, 22, 34, 50, 70])
        a = int(rng.uniform(25, 90) * (0.6 if r > 40 else 1))
        col = rng.choice([(255, 215, 90), (255, 190, 60), (255, 235, 150), (255, 160, 70)])
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))
    return layer.filter(ImageFilter.GaussianBlur(6))


def sparkles():
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(90):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        L = rng.uniform(4, 12)
        a = int(rng.uniform(120, 230))
        col = (255, 236, 170, a)
        d.line([x - L, y, x + L, y], fill=col, width=2)
        d.line([x, y - L, x, y + L], fill=col, width=2)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 250, 220, 255))
    return layer.filter(ImageFilter.GaussianBlur(0.8))


def flower(d, x, y, r, rot):
    """Five-petal yellow apricot blossom (hoa mai)."""
    for k in range(5):
        ang = rot + k * 2 * math.pi / 5
        px, py = x + math.cos(ang) * r * 0.62, y + math.sin(ang) * r * 0.62
        pr = r * 0.52
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(255, 205, 40, 255), outline=(230, 150, 20, 255), width=2)
    d.ellipse([x - r * 0.28, y - r * 0.28, x + r * 0.28, y + r * 0.28], fill=(230, 110, 20, 255))
    for k in range(8):  # stamens
        ang = rot + k * 2 * math.pi / 8
        sx, sy = x + math.cos(ang) * r * 0.42, y + math.sin(ang) * r * 0.42
        d.line([x, y, sx, sy], fill=(200, 70, 10, 255), width=2)
        d.ellipse([sx - 2.5, sy - 2.5, sx + 2.5, sy + 2.5], fill=(255, 240, 160, 255))


def branch(d, x, y, ang, length, width, depth, blossoms):
    if depth == 0 or length < 18:
        blossoms.append((x, y))
        return
    x2, y2 = x + math.cos(ang) * length, y + math.sin(ang) * length
    # slightly bent segment
    mx = (x + x2) / 2 + rng.uniform(-length * 0.12, length * 0.12)
    my = (y + y2) / 2 + rng.uniform(-length * 0.12, length * 0.12)
    for (ax, ay), (bx, by) in [((x, y), (mx, my)), ((mx, my), (x2, y2))]:
        d.line([ax, ay, bx, by], fill=(70, 30, 20, 255), width=int(width))
        d.ellipse([bx - width / 2, by - width / 2, bx + width / 2, by + width / 2], fill=(70, 30, 20, 255))
    if rng.random() < 0.7:
        blossoms.append((mx, my))
    for _ in range(rng.choice([1, 2, 2, 3])):
        branch(d, x2, y2, ang + rng.uniform(-0.6, 0.6), length * rng.uniform(0.6, 0.78),
               max(2, width * 0.68), depth - 1, blossoms)


def apricot_branch(origin, ang, scale):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    blossoms = []
    branch(d, origin[0], origin[1], ang, 170 * scale, 16 * scale, 5, blossoms)
    for bx, by in blossoms:
        if rng.random() < 0.85:
            flower(d, bx + rng.uniform(-10, 10), by + rng.uniform(-10, 10),
                   rng.uniform(13, 22) * scale, rng.uniform(0, math.pi))
        else:  # buds
            r = 6 * scale
            d.ellipse([bx - r, by - r, bx + r, by + r], fill=(255, 190, 40, 255))
    glow = layer.filter(ImageFilter.GaussianBlur(10))
    return Image.alpha_composite(glow, layer)


def vignette():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    a = np.clip((d - 0.75) / 0.7, 0, 1) * 150
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def main():
    img = radial_gradient()
    for layer in (coin_pattern(), bokeh(), vignette(),
                  apricot_branch((-20, 60), 0.25, 1.15),
                  apricot_branch((W + 20, H - 40), math.pi + 0.35, 1.2),
                  sparkles()):
        img = Image.alpha_composite(img, layer)
    img.convert("RGB").save("lucky_bg.jpg", quality=86, optimize=True, progressive=True)
    print("saved lucky_bg.jpg")


if __name__ == "__main__":
    main()
