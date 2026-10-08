#!/usr/bin/env python3
"""Generate 'ghost flame' kit presets: electric crackle over matte black.

The look comes from a concept board the owner supplied. What was worth taking
from it is not on that board's garments — those carry three live trademarks —
it is the treatment underneath: branching purple lightning over a matte black
base, bright core, wide halo. That is a texture, and a texture belongs to
whoever draws it.

The veins are grown, not drawn: each one walks with a wandering heading and
occasionally splits, so the branches get thinner and dimmer with every
generation the way a real discharge does. Drawing them by hand produced
something that read as cracks in glass instead.

Colours are the board's own named swatches, sampled from it.
"""
import math, pathlib, random

from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "public" / "kits"

STEALTH = (0x0A, 0x0A, 0x0C)     # sampled from the board
HAUNTED = (0x76, 0x4B, 0x94)     # sampled from the board
GHOST   = (0xA8, 0x78, 0xD0)     # the pale flame, for the hot core

W, H = 2048, 1256                # the cut sheet's proportions


def grow(draw, x, y, heading, length, width, depth, rand, bounds):
    """One vein. Splits as it goes; each child is thinner and shorter."""
    bw, bh = bounds
    steps = max(6, int(length))
    for _ in range(steps):
        # Wander, but keep a memory of the heading or it curls into a ball.
        heading += rand.uniform(-0.34, 0.34)
        nx = x + math.cos(heading) * 7
        ny = y + math.sin(heading) * 7
        if not (-80 < nx < bw + 80 and -80 < ny < bh + 80):
            return
        draw.line((x, y, nx, ny), fill=255, width=max(1, int(width)))
        x, y = nx, ny
        # Branch. The probability has to fall with depth or one seed fills the
        # sheet and the result is a grey wash rather than lightning.
        # Branch rarely and shallowly. At depth 5 with p=0.055 this grew a
        # capillary bed — thousands of hairlines that averaged out to a flat
        # purple haze. A discharge is a few bold strokes with a handful of
        # forks, so the budget goes into width and glow instead of count.
        if depth > 0 and rand.random() < 0.030:
            grow(draw, x, y, heading + rand.choice((-1, 1)) * rand.uniform(0.45, 0.95),
                 length * 0.62, width * 0.70, depth - 1, rand, bounds)
        width *= 0.9975


def ghost_flame(seed, seeds=11, out=None):
    rand = random.Random(seed)

    # Veins are grown on a mask first so the glow can be built from blurs of
    # the same shape — a glow painted separately never lines up.
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    for i in range(seeds):
        # Enter from an edge, heading roughly across the sheet, so the pattern
        # runs the length of the bike rather than pooling in the middle.
        edge = rand.random()
        if edge < 0.5:
            x, y, head = -40, rand.uniform(0, H), rand.uniform(-0.6, 0.6)
        else:
            x, y, head = W + 40, rand.uniform(0, H), math.pi + rand.uniform(-0.6, 0.6)
        grow(d, x, y, head, rand.uniform(200, 320), rand.uniform(13, 22), 3, rand, (W, H))

    core = mask.filter(ImageFilter.GaussianBlur(2.0))
    mid  = mask.filter(ImageFilter.GaussianBlur(16))
    wide = mask.filter(ImageFilter.GaussianBlur(58))

    img = Image.new("RGB", (W, H), STEALTH)
    for layer, colour, gain in ((wide, HAUNTED, 0.80), (mid, HAUNTED, 1.15), (core, GHOST, 1.35)):
        tint = Image.new("RGB", (W, H), colour)
        lit = Image.composite(tint, Image.new("RGB", (W, H), (0, 0, 0)),
                              layer.point(lambda v, g=gain: int(min(255, v * g))))
        img = ImageChops.add(img, lit)

    if out:
        img.save(out, quality=92)
        img.resize((W // 8, H // 8), Image.LANCZOS).save(
            str(out).replace(".jpg", "-thumb.jpg"), quality=86)
    return img


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, seed, n in (("ghostflame", 20260108, 6),
                          ("stormveil", 77451, 4),
                          ("hauntwire", 310942, 9)):
        p = OUT / (name + ".jpg")
        ghost_flame(seed, n, p)
        print(f"  {p.name:18s} {p.stat().st_size // 1024:4d} KB   seed {seed}, {n} veins")
