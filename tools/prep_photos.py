"""Turn a photo of a wrapped bike into a clean mockup base.

Three steps, each independently useful:
  1. cut out   — background removed, subject on a flat studio backdrop
  2. neutralise— the wrap's colour is stripped and its pattern smoothed away,
                 leaving the panel's form (its shading and highlights) intact
  3. upscale   — handled separately; this script keeps native resolution

Step 2 is the point. A decal composited onto a holographic wrap fights the
wrap's own pattern; against a flat neutral panel it just looks printed.
"""
import sys, io
import numpy as np
from PIL import Image, ImageFilter

def cutout(im):
    from rembg import remove
    return remove(im)                      # RGBA, background alpha 0

def neutralise(rgba, base=(196, 199, 205), sat_gate=0.10, strength=1.0, lift=0.18):
    """Strip the paint's colour while keeping every bit of the bike's structure.

    Replacing saturated pixels with a flat tone also flattens the engine, the
    spokes and the fork legs, because a purple LED makes those saturated too —
    the camera cannot tell paint from metal lit by coloured light. So chroma is
    removed and luminance is kept: the wrap goes grey, the engine still reads
    as an engine.

    This does NOT remove printed graphics; they survive as grey shapes. Erasing
    those needs to know where the panels are, which is what the mockup page's
    Coons patches are for — neutralise_panel below does that part."""
    a = np.asarray(rgba.convert('RGBA')).astype(np.float32)
    rgb, alpha = a[..., :3], a[..., 3:4]

    mx, mn = rgb.max(2), rgb.min(2)
    sat = np.where(mx > 1e-3, (mx - mn) / np.maximum(mx, 1e-3), 0.0)
    w = np.clip((sat - sat_gate) / 0.16, 0, 1)[..., None] * strength

    lum = (0.2126*rgb[...,0] + 0.7152*rgb[...,1] + 0.0722*rgb[...,2])[..., None]
    tone = np.array(base, np.float32) / 200.0          # a faint cool cast
    grey = np.clip(lum * tone, 0, 255)
    grey = grey + (255.0 - grey) * lift                # lift midtones off black
    out = rgb * (1 - w) + grey * w
    return Image.fromarray(np.concatenate([np.clip(out,0,255), alpha], 2).astype(np.uint8))


def neutralise_panel(img, poly, base=(198, 201, 207), feather=6):
    """Blank one panel: flat colour carrying only the panel's large-scale
    shading, so printed graphics and holographic speckle disappear but the
    curvature and highlight stay. `poly` is a list of (x, y) in image space."""
    from PIL import ImageDraw
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in poly], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(feather))
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    lum = (0.2126*a[...,0] + 0.7152*a[...,1] + 0.0722*a[...,2])
    sigma = max(5.0, img.size[0] / 130.0)
    soft = np.asarray(Image.fromarray(lum.astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(sigma))).astype(np.float32)
    sel = np.asarray(m).astype(np.float32) / 255.0
    inside = sel > 0.5
    if not inside.any():
        return img
    pivot = max(24.0, float(np.median(soft[inside])))
    shade = np.clip(soft / pivot, 0.62, 1.20)[..., None]
    flat = np.clip(np.array(base, np.float32) * shade, 0, 255)
    out = a * (1 - sel[..., None]) + flat * sel[..., None]
    return Image.fromarray(out.clip(0,255).astype(np.uint8))


def on_backdrop(rgba, colour=(236, 238, 241)):
    bg = Image.new('RGB', rgba.size, colour)
    bg.paste(rgba, (0, 0), rgba)
    return bg

if __name__ == '__main__':
    src, stem = sys.argv[1], sys.argv[2]
    im = Image.open(src).convert('RGB')
    print(f'  {stem}: source {im.size[0]}x{im.size[1]}')
    cut = cutout(im)
    on_backdrop(cut).save(f'{stem}-cut.jpg', quality=92)
    print(f'  {stem}: cut out')
    neu = neutralise(cut)
    neu.save(f'{stem}-neutral.png')
    on_backdrop(neu).save(f'{stem}-neutral.jpg', quality=92)
    print(f'  {stem}: neutralised')
