#!/usr/bin/env python3
"""Build the StreetSweeperCustoms brand marks as real SVG.

Type is converted to outlines rather than left as <text>: a logo that needs a
font installed to render correctly is not a logo file, it is a document. The
outlines come from Oswald Bold, which is what the storefront already sets.
"""
import re, subprocess, pathlib
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

HERE = pathlib.Path(__file__).parent
TTF = HERE / "Oswald-Bold.ttf"

INK   = "#EEF0F2"   # off-white
BLACK = "#121316"   # near-black
RED   = "#E2231A"   # Honda red
ORANGE= "#FF8A1E"

# ── outlines ─────────────────────────────────────────────────────────────
font = TTFont(TTF)
UPM = font["head"].unitsPerEm
glyphs = font.getGlyphSet()
cmap = font.getBestCmap()
hmtx = font["hmtx"]


def text_paths(s, size, tracking=0.0):
    """Glyph outlines for s at a given cap size. Returns (paths, advance).

    tracking is in the same units as size, added between glyphs — condensed
    display type needs it opened up slightly or the counters close at small
    sizes.
    """
    scale = size / UPM
    out, x = [], 0.0
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
            # Font space has y up; SVG has y down.
            out.append('<path transform="translate(%.3f,0) scale(%.5f,%.5f)" d="%s"/>'
                       % (x, scale, -scale, d))
        x += hmtx[name][0] * scale + tracking
    return "".join(out), x - tracking


def width_of(s, size, tracking=0.0):
    return text_paths(s, size, tracking)[1]


def fit(s, target_w, size_guess, tracking=0.0):
    """Cap size that makes s exactly target_w wide, so two stacked lines flush."""
    w = width_of(s, size_guess, tracking)
    return size_guess * target_w / w


# ── marks ────────────────────────────────────────────────────────────────
def primary(bg=BLACK, ink=INK, accent=RED):
    """Stacked lockup. CUSTOMS is tracked out to the exact width of the word
    above it, which is the whole discipline of the mark."""
    W, H = 1600, 640
    top_size = 200
    top_w = width_of("STREETSWEEPER", top_size)
    # Track CUSTOMS out to match, rather than scaling it up and breaking weight.
    bot_size = 96
    raw = width_of("CUSTOMS", bot_size)
    tracking = (top_w - raw) / (len("CUSTOMS") - 1)
    top_d, _ = text_paths("STREETSWEEPER", top_size)
    bot_d, _ = text_paths("CUSTOMS", bot_size, tracking)
    x0, y_top, y_bot = (W - top_w) / 2, 300, 430
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="StreetSweeperCustoms">
<rect width="{W}" height="{H}" fill="{bg}"/>
<g fill="{ink}"><g transform="translate({x0},{y_top})">{top_d}</g><g transform="translate({x0},{y_bot})">{bot_d}</g></g>
<path d="M{x0} 486 L{x0+top_w} 486 L{x0+top_w-54} 530 L{x0-54} 530 Z" fill="{accent}"/>
</svg>'''


def horizontal(bg=BLACK, ink=INK, accent=RED):
    """One line, for a site header or a jersey collar where height is scarce."""
    size = 150
    d1, w1 = text_paths("STREETSWEEPER", size)
    gap = 42
    d2, w2 = text_paths("CUSTOMS", size * 0.62, 6)
    W, H = w1 + gap + w2 + 160, 300
    x0 = (W - (w1 + gap + w2)) / 2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H}" width="{W:.0f}" height="{H}" role="img" aria-label="StreetSweeperCustoms">
<rect width="{W:.0f}" height="{H}" fill="{bg}"/>
<g fill="{ink}" transform="translate({x0:.1f},195)">{d1}</g>
<rect x="{x0+w1+gap/2-5:.1f}" y="70" width="10" height="130" fill="{accent}"/>
<g fill="{ink}" transform="translate({x0+w1+gap:.1f},195)">{d2}</g>
</svg>'''


def monogram(bg=BLACK, ink=INK, accent=RED, size=512):
    """Square mark. Three letters on one baseline with a sweep cut through —
    at 32px the letters are still three distinct shapes, which an interlocked
    monogram would not be."""
    cap = size * 0.46
    d, w = text_paths("SSC", cap, size * 0.012)
    x0, y0 = (size - w) / 2, size * 0.66
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img" aria-label="StreetSweeperCustoms monogram">
<rect width="{size}" height="{size}" rx="{size*0.16:.0f}" fill="{bg}"/>
<path d="M0 {size*0.80:.0f} L{size} {size*0.685:.0f} L{size} {size*0.775:.0f} L0 {size*0.89:.0f} Z" fill="{accent}"/>
<g fill="{ink}" transform="translate({x0:.1f},{y0:.1f})">{d}</g>
</svg>'''


def favicon():
    """32px. The wordmark is unreadable here, so the sweep does the work and a
    single S carries the name."""
    s = 32
    cap = 21
    d, w = text_paths("S", cap)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}" width="{s}" height="{s}" role="img" aria-label="StreetSweeperCustoms">
<rect width="{s}" height="{s}" rx="6" fill="{BLACK}"/>
<path d="M0 24 L{s} 19 L{s} 24 L0 29 Z" fill="{RED}"/>
<g fill="{INK}" transform="translate({(s-w)/2:.2f},23)">{d}</g>
</svg>'''


def badge(size=640):
    """Circular emblem for stickers, jersey labels and the shop front."""
    import math
    r_out, r_in = size*0.47, size*0.355
    cx = size/2

    def ring(s, cap, radius, centre_deg, flip=False):
        """Set s along a circle. Each glyph's angular width is its advance
        divided by the radius — mapping a string onto a fixed arc instead is
        what made the letters pile up."""
        advs = []
        for ch in s:
            n = cmap.get(ord(ch))
            advs.append((hmtx[n][0] * cap / UPM) if n else cap*0.34)
        total_ang = sum(a / radius for a in advs) * 180 / math.pi
        # Reading direction reverses on the bottom of the ring.
        ang = centre_deg - total_ang/2 if not flip else centre_deg + total_ang/2
        parts = []
        for ch, adv in zip(s, advs):
            step = (adv / radius) * 180 / math.pi
            mid = ang + step/2 if not flip else ang - step/2
            n = cmap.get(ord(ch))
            if n:
                pen = SVGPathPen(glyphs); glyphs[n].draw(pen); d = pen.getCommands()
                sc = cap / UPM
                # Always offset upward: the rotate() about the centre is what
                # carries a bottom glyph to the bottom. Offsetting down as well
                # rotated it straight back to the top.
                ry = cx - radius
                inner = "" if not flip else " rotate(180)"
                parts.append(
                    f'<g transform="rotate({mid:.3f} {cx:.1f} {cx:.1f}) '
                    f'translate({cx:.1f} {ry:.1f}){inner} '
                    f'translate({-adv/2:.3f} 0) scale({sc:.5f} {-sc:.5f})">'
                    f'<path d="{d}"/></g>')
            ang = ang + step if not flip else ang - step
        return "".join(parts)

    top = ring("STREETSWEEPER CUSTOMS", size*0.062, r_in + size*0.052, 0)
    bot = ring("THAILAND", size*0.052, r_in + size*0.045, 180, flip=True)
    ch_w, ch_h = size*0.17, size*0.095
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img" aria-label="StreetSweeperCustoms badge">
<circle cx="{cx}" cy="{cx}" r="{r_out:.1f}" fill="{BLACK}"/>
<circle cx="{cx}" cy="{cx}" r="{r_out:.1f}" fill="none" stroke="{RED}" stroke-width="{size*0.022:.1f}"/>
<circle cx="{cx}" cy="{cx}" r="{r_in:.1f}" fill="none" stroke="{INK}" stroke-width="{size*0.005:.1f}" opacity="0.35"/>
<g fill="{INK}">{top}{bot}</g>
<path d="M{cx-ch_w:.1f} {cx-ch_h:.1f} L{cx:.1f} {cx-ch_h:.1f} L{cx+ch_w*0.62:.1f} {cx:.1f} L{cx:.1f} {cx+ch_h:.1f} L{cx-ch_w:.1f} {cx+ch_h:.1f} L{cx-ch_w*0.38:.1f} {cx:.1f} Z" fill="{RED}"/>
<circle cx="{cx - r_in*0.995:.1f}" cy="{cx:.1f}" r="{size*0.015:.1f}" fill="{ORANGE}"/>
<circle cx="{cx + r_in*0.995:.1f}" cy="{cx:.1f}" r="{size*0.015:.1f}" fill="{ORANGE}"/>
</svg>'''

OUT = HERE / "kit"
OUT.mkdir(exist_ok=True)
files = {
    "logo-primary.svg":         primary(),
    "logo-primary-light.svg":   primary(bg="#FBFBF8", ink=BLACK, accent=RED),
    "logo-horizontal.svg":      horizontal(),
    "monogram.svg":             monogram(),
    "favicon.svg":              favicon(),
    "badge.svg":                badge(),
}
for name, svg in files.items():
    (OUT / name).write_text(svg, encoding="utf-8")
    print("%-26s %6d bytes" % (name, len(svg)))
