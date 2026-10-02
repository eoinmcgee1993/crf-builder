#!/usr/bin/env python3
"""Build the animated phantom hero as a self-contained SVG.

The mark is what the references actually do, stripped of the character that
cannot be used: a face that is pure negative space, where only the eyes and
the grin catch light. No body, no outline, no silhouette — the black of the
page IS the creature. That is why it sits on any dark surface, and why it
costs two colours to print.

Animation is CSS inside the SVG, so the file drops into an <img>, an
<object>, a CSS background or straight inline, with no script and no
dependency. Motion is disabled under prefers-reduced-motion.

Type is Oswald Bold converted to outlines — see build-marks.py.
"""
import pathlib

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

HERE = pathlib.Path(__file__).parent
TTF = HERE / "Oswald-Bold.ttf"
OUT = HERE / "kit"

INK      = "#EEF0F2"
BLACK    = "#121316"
VIOLET   = "#A855F7"   # Purple 500. 5.03:1 on black, so it can carry type.
VIOLET_D = "#7E22CE"   # Purple 700. 2.85:1 — glow and fills only, never type.
ROSE     = "#F43F5E"   # Rose 500. 5.42:1.

font = TTFont(TTF)
UPM = font["head"].unitsPerEm
glyphs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]


def text_paths(s, size, tracking=0.0):
    """Glyph outlines for s at a given cap size. Returns (paths, advance)."""
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
            out.append('<path transform="translate(%.3f,0) scale(%.5f,%.5f)" d="%s"/>'
                       % (x, scale, -scale, d))
        x += hmtx[name][0] * scale + tracking
    return "".join(out), x - (tracking if s else 0.0)


# ── the face ─────────────────────────────────────────────────────────────
# Drawn around (0,0) in a roughly 460-wide box, so it can be dropped into any
# viewBox with one translate.

EYE_L = ("M -46 18 C -78 -26 -138 -74 -186 -56 C -168 -4 -96 38 -46 18 Z")
EYE_R = ("M 46 18 C 78 -26 138 -74 186 -56 C 168 -4 96 38 46 18 Z")

GRIN = ("M -206 58 C -128 112 -64 130 0 130 C 64 130 128 112 206 58 "
        "C 150 182 76 206 0 206 C -76 206 -150 182 -206 58 Z")

# Teeth are black bars over the grin, clipped to it. Drawing the gaps instead
# would mean booleaning the crescent, which SVG cannot do without a library.
TEETH_X = [-150, -100, -52, -4, 44, 92, 142]

# Ectoplasm. Deliberately asymmetric and curling: mirrored arcs over the brow
# read as a spiked crown, which is the one silhouette this mark exists to
# avoid. Each wisp drifts on its own period so the mass never pulses as a
# single object, which is what makes smoke read as smoke.
WISPS = [
    ("M -184 -62 C -232 -108 -214 -170 -158 -186 C -196 -156 -200 -116 -168 -92", 0),
    ("M  -96 -98 C -118 -156 -82 -212 -22 -214 C -74 -188 -88 -146 -78 -112", 1),
    ("M   24 -104 C  18 -172 66 -214 122 -206 C 70 -178 50 -140 50 -110", 2),
    ("M  148 -84 C  186 -130 240 -132 262 -96 C 220 -104 188 -88 170 -66", 3),
    ("M  206 -34 C  258 -42 290 -8 278 34 C 258 0 232 -12 200 -12", 4),
    ("M -210 -16 C -264 -10 -288 26 -270 62 C -254 26 -232 10 -202 6", 0),
]

def face(scale=1.0, tx=0.0, ty=0.0):
    teeth = "".join(
        '<rect x="%.1f" y="46" width="13" height="172"/>' % x for x in TEETH_X)
    wisps = "".join(
        '<path class="w w%d" d="%s"/>' % (i, d) for d, i in WISPS)
    return f'''<g class="face" transform="translate({tx:.1f},{ty:.1f}) scale({scale:.4f})">
  <g class="smoke" fill="none" stroke="{VIOLET_D}" stroke-width="7"
     stroke-linecap="round" opacity="0.5">{wisps}</g>
  <g class="glow" filter="url(#bloom)">
    <g fill="{VIOLET}">
      <path d="{EYE_L}"/><path d="{EYE_R}"/>
      <g clip-path="url(#grinclip)"><path d="{GRIN}"/>
        <g fill="{BLACK}">{teeth}</g>
      </g>
    </g>
  </g>
  <g fill="{ROSE}" opacity="0.9" class="spark">
    <path d="M -150 -42 C -140 -30 -118 -14 -96 -6 C -124 -8 -146 -22 -150 -42 Z"/>
    <path d="M  150 -42 C  140 -30 118 -14 96 -6 C 124 -8 146 -22 150 -42 Z"/>
  </g>
</g>'''


DEFS = f'''<defs>
  <filter id="bloom" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="14" result="b1"/>
    <feGaussianBlur stdDeviation="34" result="b2"/>
    <feMerge>
      <feMergeNode in="b2"/><feMergeNode in="b2"/>
      <feMergeNode in="b1"/><feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
  <clipPath id="grinclip"><path d="{GRIN}"/></clipPath>
  <radialGradient id="haze" cx="50%" cy="50%" r="50%">
    <stop offset="0%"  stop-color="{VIOLET_D}" stop-opacity="0.30"/>
    <stop offset="100%" stop-color="{VIOLET_D}" stop-opacity="0"/>
  </radialGradient>
</defs>'''

CSS = '''<style>
  .glow  { animation: breathe 4.2s ease-in-out infinite; transform-origin: center; }
  .spark { animation: flick 5.5s ease-in-out infinite; }
  .haze  { animation: swell 6.8s ease-in-out infinite; transform-origin: center; }
  .w     { animation: drift 7s ease-in-out infinite; transform-origin: center; }
  .w1 { animation-duration: 8.4s; animation-delay: -1.1s; }
  .w2 { animation-duration: 6.2s; animation-delay: -2.7s; }
  .w3 { animation-duration: 9.1s; animation-delay: -0.6s; }
  .w4 { animation-duration: 7.6s; animation-delay: -3.4s; }
  @keyframes breathe { 0%,100% { opacity:.86; } 50% { opacity:1; } }
  @keyframes flick   { 0%,88%,100% { opacity:.25; } 92% { opacity:.95; } 95% { opacity:.4; } }
  @keyframes swell   { 0%,100% { opacity:.55; } 50% { opacity:1; } }
  @keyframes drift   { 0%,100% { opacity:.25; transform: translateY(0); }
                       50%     { opacity:.65; transform: translateY(-16px); } }
  /* A logo that moves is decoration; a logo that moves when someone asked it
     not to is a bug. Everything above is suppressed, nothing is hidden. */
  @media (prefers-reduced-motion: reduce) {
    .glow, .spark, .haze, .w { animation: none; }
    .spark { opacity: .45; }
  }
</style>'''


def hero(w=1600, h=620):
    """Wide lockup: the face left, the name right. Site header, social cover."""
    cx, cy = 400, h / 2
    x0, pad = 752, 56
    avail = w - x0 - pad

    # Size the name to the space it actually has. A hard-coded cap size fit
    # this canvas once and silently overflowed the moment the name changed.
    probe = text_paths("STREETSWEEPER", 100)[1]
    top_size = 100 * avail / probe
    top, tw = text_paths("STREETSWEEPER", top_size)

    bot_size = top_size * 0.485
    raw = text_paths("CUSTOMS", bot_size)[1]
    tracking = (tw - raw) / (len("CUSTOMS") - 1)   # set to match. See README.
    bot, _ = text_paths("CUSTOMS", bot_size, tracking)

    y_top = cy - 6
    y_bot = y_top + top_size * 0.60
    y_rule = y_bot + top_size * 0.24
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"
 width="{w}" height="{h}" role="img" aria-label="StreetSweeperCustoms">
<title>StreetSweeperCustoms</title>
{DEFS}{CSS}
<rect width="{w}" height="{h}" fill="{BLACK}"/>
<ellipse class="haze" cx="{cx}" cy="{cy}" rx="420" ry="330" fill="url(#haze)"/>
{face(0.92, cx, cy)}
<g fill="{INK}"><g transform="translate({x0},{y_top:.1f})">{top}</g>
<g transform="translate({x0},{y_bot:.1f})">{bot}</g></g>
<path d="M{x0} {y_rule:.1f} L{x0 + tw:.1f} {y_rule:.1f} L{x0 + tw - 30:.1f} {y_rule + 26:.1f} L{x0 - 30} {y_rule + 26:.1f} Z" fill="{ROSE}"/>
</svg>'''


def avatar(size=640):
    """Square. Social avatar, app tile, the sticker's centre."""
    c = size / 2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}"
 width="{size}" height="{size}" role="img" aria-label="StreetSweeperCustoms phantom">
<title>StreetSweeperCustoms</title>
{DEFS}{CSS}
<rect width="{size}" height="{size}" rx="{size*0.16:.0f}" fill="{BLACK}"/>
<ellipse class="haze" cx="{c}" cy="{c}" rx="{size*0.46:.0f}" ry="{size*0.42:.0f}" fill="url(#haze)"/>
{face(size / 880, c, c + size * 0.045)}
</svg>'''


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, svg in [("hero-phantom.svg", hero()),
                      ("phantom-avatar.svg", avatar())]:
        (OUT / name).write_text(svg, encoding="utf-8")
        print("%-24s %6d bytes" % (name, len(svg)))
