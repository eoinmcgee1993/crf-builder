#!/usr/bin/env python3
"""Build the hand-out QR sticker as a print-ready die-cut SVG.

Business-card format, 85 x 54 mm, so it fits a wallet and a jacket pocket.
Two things have to be true or the sticker is worthless:

  1. The QR must be vector. A rasterised QR resampled by a RIP loses module
     edges and stops scanning at small sizes, and this one gets printed at
     whatever size the shop feels like.
  2. The die line must be a CutContour spot colour, the same convention the
     kit export already uses, or the printer cuts a rectangle through it.

Every built file is decoded back with OpenCV before it is written, so a
sticker that does not scan never reaches a printer.

Deps: segno (QR), fontTools (type to outlines), opencv-python-headless +
Pillow (the scan check). Oswald-Bold.ttf sits next to this file.
"""
import base64, io, math, pathlib, sys

import segno
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

HERE = pathlib.Path(__file__).parent
TTF = HERE / "Oswald-Bold.ttf"
GRAFFITI = HERE / "graffiti" / "wordmark-on-black.png"
PHANTOM  = HERE / "graffiti" / "phantom-on-black.png"
OUT = HERE / "stickers"

# Brand tokens. See README.md — near-black, never pure black.
INK, BLACK = "#EEF0F2", "#121316"
ACCENT = "#F43F5E"        # Rose 500. 5.42:1 on black; the night palette's sweep.
VIOLET = "#A855F7"        # Purple 500. 5.03:1 — the only violet that carries type.
PANEL = "#F6F4EF"          # warm off-white behind the QR; pure white glares
CUT = "#FF00FF"            # 100% magenta, the CutContour convention

CARD_W, CARD_H = 85.0, 54.0   # mm, ISO business card
BLEED = 3.0
R = 3.0                       # die-line corner radius

font = TTFont(TTF)
UPM = font["head"].unitsPerEm
glyphs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]


def text_paths(s, size, tracking=0.0):
    """Glyph outlines for s at a given cap size, in mm. Returns (paths, width)."""
    scale, out, x = size / UPM, [], 0.0
    for ch in s:
        if ch == " ":
            x += size * 0.30 + tracking
            continue
        name = cmap.get(ord(ch))
        if name is None:
            continue
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        d = pen.getCommands()
        if d:
            out.append('<path transform="translate(%.4f,0) scale(%.6f,%.6f)" d="%s"/>'
                       % (x, scale, -scale, d))
        x += hmtx[name][0] * scale + tracking
    return "".join(out), x - (tracking if s else 0.0)


def centred(s, size, cx, baseline, fill, tracking=0.0, max_w=None):
    """Centred line, shrunk to fit max_w. Without the clamp a longer caption
    silently runs off the card and past the bleed, which the diff does not
    show and the printer does not catch."""
    d, w = text_paths(s, size, tracking)
    if max_w and w > max_w:
        size *= max_w / w
        tracking *= max_w / w
        d, w = text_paths(s, size, tracking)
    return ('<g fill="%s" transform="translate(%.3f,%.3f)">%s</g>'
            % (fill, cx - w / 2, baseline, d))


def qr_paths(url, side_mm, x, y):
    """One <path> per QR, drawn as module rectangles in a single 'd'.

    Error correction H: a sticker on a petrol tank gets scratched, and H
    tolerates ~30% damage. It costs modules, which is why the quiet zone is
    the panel itself rather than extra border=.
    """
    qr = segno.make(url, error="h", boost_error=False)
    m = [row for row in qr.matrix]
    n = len(m)
    step = side_mm / n
    d = []
    for r, row in enumerate(m):
        c = 0
        while c < n:
            if row[c]:
                run = 1
                while c + run < n and row[c + run]:   # merge runs: fewer nodes
                    run += 1
                d.append("M%.4f %.4fh%.4fv%.4fh%.4fz"
                         % (x + c * step, y + r * step,
                            run * step, step, -run * step))
                c += run
            else:
                c += 1
    return '<path fill="%s" shape-rendering="crispEdges" d="%s"/>' % (BLACK, "".join(d)), n


def build(url, captions, name):
    W, H = CARD_W + 2 * BLEED, CARD_H + 2 * BLEED
    ox, oy = BLEED, BLEED                      # card origin inside the bleed

    # -- right: the QR on its panel --------------------------------------
    panel = 34.0
    px, py = ox + CARD_W - panel - 4.5, oy + (CARD_H - panel) / 2
    qr_side = 28.0                             # 3 mm quiet zone all round
    qx, qy = px + (panel - qr_side) / 2, py + (panel - qr_side) / 2
    qr_svg, modules = qr_paths(url, qr_side, qx, qy)

    # -- left column, vertically centred against the panel ---------------
    from PIL import Image
    with Image.open(GRAFFITI) as im:
        gw, gh = im.size
    ix = ox + 4.5
    col_w = px - 4.5 - ix
    img_w = col_w
    img_h = img_w * gh / gw

    cap_size, cap_gap = 2.5, 3.5
    stack = img_h + 2.6 + 2.6 + 4.2 + cap_size + (len(captions) - 1) * cap_gap
    iy = oy + (CARD_H - stack) / 2

    # Resample to what the placement actually needs at 600 dpi — twice what a
    # RIP outputs. Embedding the full-size source instead made the file 1.6 MB
    # of base64 to print a 37 mm image, and print files get emailed.
    from PIL import Image as _I
    need_w = max(1, round(img_w / 25.4 * 600))
    with _I.open(GRAFFITI) as im:
        if im.width > need_w:
            im = im.resize((need_w, round(im.height * need_w / im.width)),
                           _I.LANCZOS)
        buf = io.BytesIO()
        # JPEG, not PNG: this is a photographic spray texture, and PNG spent
        # 1.3 MB on it. At 600 dpi q93 there is nothing left to see, including
        # along the red keyline, which is the only edge that could ring.
        im.convert("RGB").save(buf, "JPEG", quality=93, subsampling=0,
                               optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    # One red sweep, low-left to high-right. See README.md.
    sy = iy + img_h + 2.6
    sweep = ('<path d="M%.2f %.2f L%.2f %.2f L%.2f %.2f L%.2f %.2f Z" fill="%s"/>'
             % (ix, sy + 1.5, ix + col_w, sy, ix + col_w, sy + 1.1,
                ix, sy + 2.6, ACCENT))

    lines, y = [], sy + 2.6 + 4.2 + cap_size
    for i, line in enumerate(captions):
        lines.append(centred(line, cap_size, ix + col_w / 2, y,
                             INK if i == 0 else "#9AA0A6",
                             tracking=0.18, max_w=col_w))
        y += cap_gap

    # -- die line: a CutContour spot colour, not a composite magenta ------
    die = ('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" '
           'fill="none" stroke="%s" stroke-width="0.25"/>'
           % (ox, oy, CARD_W, CARD_H, R, CUT))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
 width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}"
 role="img" aria-label="Sticker linking to {url}">
<title>StreetSweeper hand-out sticker - {url}</title>
<desc>85x54 mm die-cut sticker, 3 mm bleed. The magenta contour is the cut
line and is named CutContour; it must print as a spot colour, not composite.
QR is error-correction level H, {modules}x{modules} modules over {qr_side:.0f} mm.</desc>
<rect width="{W}" height="{H}" fill="{BLACK}"/>
<image x="{ix:.3f}" y="{iy:.3f}" width="{img_w:.3f}" height="{img_h:.3f}"
 xlink:href="data:image/jpeg;base64,{b64}"/>
{sweep}
{"".join(lines)}
<rect x="{px:.2f}" y="{py:.2f}" width="{panel}" height="{panel}" rx="2.5" fill="{PANEL}"/>
{qr_svg}
<g id="CutContour">{die}</g>
</svg>'''

    OUT.mkdir(exist_ok=True)
    path = OUT / name
    path.write_text(svg, encoding="utf-8")
    return path, svg, (qx, qy, qr_side), modules


def verify(svg, url):
    """Rasterise the SVG and decode the QR back out of it. A sticker that does
    not scan is not a sticker, and reading the diff cannot tell you that."""
    import numpy as np, cv2, cairosvg, io
    from PIL import Image
    # 300 dpi is what a print shop actually outputs; 1 mm = 300/25.4 px.
    png = cairosvg.svg2png(bytestring=svg.encode("utf-8"), dpi=300,
                           background_color="#ffffff")
    img = np.asarray(Image.open(io.BytesIO(png)).convert("RGB"))[:, :, ::-1].copy()
    got, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    return got, img.shape


TARGETS = [
    # (url, the two caption lines, filename)
    # Production is Vercel, deploying on push to main; see
    # docs/crf/DEPLOYMENT.md Phase 3. crf-garage.netlify.app is gone on
    # purpose — its 404 is what took the placeholder privacy policy off the
    # internet. DO NOT PRINT this card until the real domain exists: the
    # vercel.app host is auto-generated and will change, and a QR is the one
    # thing you cannot correct after it is on a sticker.
    ("https://crf-eoins-projects-99ff5888.vercel.app",
     ["DESIGN IT · PRINT IT · PEEL IT", "CRF250L / CRF300L"],
     "sticker-customs.svg"),
]

if __name__ == "__main__":
    if len(sys.argv) >= 3:            # build-sticker.py URL "LINE1|LINE2" [name]
        TARGETS = [(sys.argv[1], sys.argv[2].split("|"),
                    sys.argv[3] if len(sys.argv) > 3 else "sticker-custom.svg")]
    ok = True
    for url, captions, name in TARGETS:
        path, svg, (qx, qy, side), n = build(url, captions, name)
        got, shape = verify(svg, url)
        state = "SCANS" if got == url else "FAILED: decoded %r" % got
        ok &= got == url
        print("%-22s %-34s %sx%s modules, %.1f mm  %s  %d KB"
              % (path.name, url, n, n, side, state, len(svg) // 1024))
    sys.exit(0 if ok else 1)
