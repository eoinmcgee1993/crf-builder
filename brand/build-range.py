#!/usr/bin/env python3
"""Build the StreetSweeper clothing range: finished garment designs.

The racewear builder used to ask a customer for artwork, then check its
resolution, place it, and get it approved. That is the slowest path to a sale
and every garment it produced advertised somebody else's club. A fixed range
with a name-and-number panel sells faster, and every piece carries the brand.

Each design is a flat: a base texture, the mark, and deliberate empty space
where the page prints the rider's name and number live. The number zone is
left clear here on purpose — baking a placeholder in would mean every flat had
to be rebuilt to change the type.

Depends on build-ghostflame.py for the textures and public/brand for the marks.
"""
import pathlib

from PIL import Image, ImageEnhance

HERE = pathlib.Path(__file__).parent
PUB = HERE.parent / "public"
KITS = PUB / "kits"
MARKS = PUB / "brand"
OUT = PUB / "range"

W, H = 700, 750                 # matches the jersey photos' proportions
STEALTH = (0x0A, 0x0A, 0x0C)

# (id, label, texture or None for plain Stealth Black, texture opacity)
DESIGNS = [
    ("stormveil",  "Stormveil",   "stormveil.jpg",  0.95),
    ("ghostflame", "Ghost Flame", "ghostflame.jpg", 0.85),
    ("hauntwire",  "Hauntwire",   "hauntwire.jpg",  0.38),
    ("stealth",    "Stealth",     None,             0.0),
]


def base(texture, opacity):
    img = Image.new("RGB", (W, H), STEALTH)
    if not texture:
        return img
    tex = Image.open(KITS / texture).convert("RGB")
    # Cover, then take the middle: the textures run wide for a bike sheet and
    # a garment is close to square, so fitting them would squash the veins.
    s = max(W / tex.width, H / tex.height)
    tex = tex.resize((int(tex.width * s), int(tex.height * s)), Image.LANCZOS)
    x = (tex.width - W) // 2
    y = (tex.height - H) // 2
    tex = tex.crop((x, y, x + W, y + H))
    return Image.blend(img, tex, opacity)


def scrim(img, cx_frac, cy_frac, w_frac, h_frac, strength=0.82):
    """Knock the texture back behind a mark so it always reads.

    Printed apparel does this with a solid panel. A soft radial scrim keeps
    the texture visible at the edges while giving the type a clean field, and
    it means one wordmark works on every base instead of needing a light
    version for the busy ones.
    """
    from PIL import ImageDraw, ImageFilter
    w, h = int(W * w_frac), int(H * h_frac)
    # Pad before blurring. Without it the blur is cut off at the mask's own
    # canvas edge and the soft ellipse comes back as a hard-edged rectangle,
    # which is more obvious on a busy texture than no scrim at all.
    pad = int(w * 0.30)
    mw, mh = w + pad * 2, h + pad * 2
    m = Image.new("L", (mw, mh), 0)
    ImageDraw.Draw(m).ellipse((pad, pad, pad + w, pad + h), fill=int(255 * strength))
    m = m.filter(ImageFilter.GaussianBlur(w * 0.11))
    dark = Image.new("RGB", (mw, mh), STEALTH)
    img.paste(dark, (int(W * cx_frac) - mw // 2, int(H * cy_frac) - mh // 2), m)
    return img


def place(img, mark_path, width_frac, cx_frac, cy_frac, alpha=1.0):
    """Drop a transparent mark on the flat, sized as a fraction of the width."""
    m = Image.open(mark_path).convert("RGBA")
    w = int(W * width_frac)
    h = int(m.height * w / m.width)
    m = m.resize((w, h), Image.LANCZOS)
    if alpha < 1.0:
        m.putalpha(ImageEnhance.Brightness(m.getchannel("A")).enhance(alpha))
    img.paste(m, (int(W * cx_frac) - w // 2, int(H * cy_frac) - h // 2), m)
    return img


def build(did, texture, opacity):
    # Front: the mark across the chest, high enough to clear a neck line.
    front = base(texture, opacity)
    if texture:
        scrim(front, 0.5, 0.315, 0.86, 0.30)
    place(front, MARKS / "wordmark.png", 0.62, 0.5, 0.30)
    place(front, MARKS / "kanji.png",    0.09, 0.5, 0.44, alpha=0.85)

    # Back: the mark small at the yoke, then nothing. The rest of the back is
    # the rider's — the page draws the name and the number into it.
    back = base(texture, opacity)
    if texture:
        scrim(back, 0.5, 0.175, 0.60, 0.19, strength=0.70)
    place(back, MARKS / "wordmark.png", 0.40, 0.5, 0.17)

    OUT.mkdir(parents=True, exist_ok=True)
    for view, im in (("front", front), ("back", back)):
        p = OUT / f"{did}-{view}.jpg"
        im.save(p, quality=90)
        im.resize((W // 4, H // 4), Image.LANCZOS).save(
            OUT / f"{did}-{view}-thumb.jpg", quality=84)
    return front, back


if __name__ == "__main__":
    for did, label, tex, op in DESIGNS:
        build(did, tex, op)
        print(f"  {label:12s} -> {did}-front.jpg / {did}-back.jpg")
