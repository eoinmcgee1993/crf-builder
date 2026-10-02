# StreetSweeperCustoms brand marks

Every mark here is generated — `build-marks.py` for the red system,
`build-hero.py` for the phantom, `build-sticker.py` for the card. Edit the
script, not the SVG. Output lands in `kit/` and `stickers/`.

Real vector files. The type is Oswald Bold converted to outlines, so nothing
here needs a font installed to render correctly — hand any of these to a vinyl
printer or an embroiderer as-is.

| File | Use |
|---|---|
| `kit/logo-primary.svg` | The mark. Dark backgrounds. Stacked lockup. |
| `kit/logo-primary-light.svg` | Same lockup for light backgrounds and print on white. |
| `kit/logo-horizontal.svg` | One line, for a site header or a jersey collar. |
| `kit/monogram.svg` | Square. Social avatar, sticker, app tile. |
| `kit/favicon.svg` | 32px. Copied to `public/favicon.svg`. |
| `kit/badge.svg` | Circular emblem for stickers and garment labels. |

## Colour

| Token | Hex | Use |
|---|---|---|
| Ink | `#EEF0F2` | Type on dark. Never pure white. |
| Near-black | `#121316` | Backgrounds, type on light. Never pure black. |
| Red | `#E2231A` | The sweep. One accent per composition. |
| Orange | `#FF8A1E` | Secondary accent, eyebrows and labels only. |

Red on near-black is about 3.7:1, so it carries display type and marks but
never body copy. Ink on near-black clears 4.5:1 comfortably.

## Type

Oswald Bold for display, Inter for everything else — the same pair the
storefront already loads, so the site and the printed goods match.

## Rules

- One red sweep per composition. Two competes with itself.
- The sweep always runs low-left to high-right. It reads as motion; reversed it
  reads as a strikethrough.
- `CUSTOMS` is tracked to the exact width of `STREETSWEEPER` above it. If you
  rebuild the lockup, keep that; it is the whole discipline of the mark.
- Clear space around any mark is the cap height of `S`.
- Below about 90px wide use the monogram, not the lockup. `CUSTOMS` closes up.

## Rebuilding

`python3 build-marks.py` regenerates every file from the Oswald source. It
needs `fonttools` and `Oswald-Bold.ttf` beside it (fetch from Google Fonts).

## The night palette

A second expression, for the phantom marks, the stickers and anything on a
dark surface. The red system above still owns the storefront chrome; these are
not a replacement, they are the other half.

| Token | Hex | Contrast on black | Use |
|---|---|---|---|
| Violet | `#A855F7` | 5.03:1 | The phantom. Carries type. |
| Violet deep | `#7E22CE` | 2.85:1 | **Glow and fills only. Never type.** |
| Rose | `#F43F5E` | 5.42:1 | The sweep, in place of red on dark. |
| Ink | `#EEF0F2` | 17.4:1 | Type on dark. |

Measured, not guessed. Violet deep fails even the large-text floor, which is
why it is confined to the bloom; put a label in it and it disappears for
anyone reading in daylight.

The black stays `#121316`. `#09090B` is 1.07:1 away from it — the same colour
to any eye — so adopting it would mean rebuilding every mark for a difference
nobody can see.

## The phantom

The mark is the one thing the reference images actually do, separated from the
character that cannot be used: **a face that is pure negative space.** No body,
no outline, no silhouette — only the eyes and the grin catch light, and the
black of the page is the creature. A grinning phantom in the dark is a horror
archetype a century older than any of its modern uses; the shapes here are
drawn from scratch and are ours.

| File | Use |
|---|---|
| `kit/hero-phantom.svg` | Animated. Site header, social cover. 10 KB. |
| `kit/phantom-avatar.svg` | Animated square. Avatar, app tile. 4 KB. |
| `graffiti/phantom-on-black.png` | Keyed to `#121316`. Drop on any dark field. |
| `graffiti/phantom-full.png` | Full frame. Poster, print. |
| `graffiti/phantom-alt.png` | Sharper eyes, smaller grin. |

`build-hero.py` draws the vector pair. Animation is CSS inside the SVG — no
script, no dependency — so the file works in an `<img>`, an `<object>`, a CSS
background or inline. `prefers-reduced-motion` stops every animation; a logo
that keeps moving after someone asked it not to is a bug, not a flourish.

## Graffiti lockup

`graffiti/` holds the Chicano-lettering treatment of **STREET SWEEPER
CUSTOMS** — one name now, matching the storefront and the checkout.

| File | Use |
|---|---|
| `wordmark-on-black.png` | Keyed to `#121316`. The sticker uses this. |
| `wordmark-full.png` | Full frame. Heaviest strokes, best at small sizes. |
| `wordmark-script-alt.png` | Flowing alternate. More elegant, less punchy. |

Raster, 1280x720. Enough for a sticker, an avatar and a social post; not
enough for a jersey back or an A2 poster. Regenerate larger before printing at
that size — do not upscale these.

`photo/hero-purple-hour.png` is the site hero: a dual-sport at purple hour,
2048x1152. It reads as a CRF at a glance but it is not a photograph of one —
use it for mood, and the blank-plastic shot in `public/bike/` for fitment.

## Stickers

`build-sticker.py` builds the hand-out card: 85 x 54 mm, 3 mm bleed, die line
on a `CutContour` spot colour, QR as vector paths at error-correction H.

```sh
./fetch-font.sh                 # once
python3 build-sticker.py        # -> stickers/sticker-customs.svg
python3 build-sticker.py "https://example.com" "LINE ONE|LINE TWO" out.svg
```

The script decodes its own QR out of a 300 dpi render before writing the file,
so a sticker that does not scan never reaches a printer. Measured: reliable
down to about 4 px per module, which is a card filling a tenth of a phone
frame. Level H survives roughly 30% damage, which is the point on a tank.

When the real domain exists, rebuild with it — the QR is generated, never
hand-placed, so it is one argument.

## Sliced from the brand sheet

`sheet/` holds the elements cut out of the supplied composite. Every file here
is lettering, type, a generic device or a landscape — nothing in it belongs to
anyone else. The character and the Poké Ball on that sheet are Nintendo /
The Pokémon Company marks and are not in this repository; cropping them
smaller would not have changed that, and decal kits are the category those
marks are enforced against hardest.

| File | px | Use |
|---|---|---|
| `wordmark-hero.png` | 940x232 | Full lockup with tagline and katakana. Site hero. |
| `wordmark-white.png` | 454x150 | White on dark. The cleanest of the four. |
| `wordmark-violet.png` | 466x150 | Violet with drips. Dark backgrounds. |
| `wordmark-katakana.png` | 358x90 | Wordmark over ストリートスウィーパーカスタムズ. |
| `crown.png` | 115x156 | Graffiti crown. Pairs above the monogram. |
| `monogram-ss.png` | 190x149 | Chicano SS. Fork guards, chest prints. |
| `kanji-sweep.png` | 116x156 | 掃 — sweep. Category tags, fender accents. |
| `hero-road.png` | 337x243 | Bike at purple hour with the wordmark. |
| `product-swingarm.png` | 251x243 | Swingarm decal in situ. Proof shot. |
| `scene-moon.png` | 121x251 | Palms and moon. Story background. |
| `nameplate.png` | 112x126 | Stacked name over katakana. |

**These are small.** They were cut from a 1536x1024 sheet, so the largest is
940 px wide. That is enough for the web, a social post and a sticker up to
about 70 mm. It is not enough for a jersey back, an A2 poster or a full tank
shroud. Regenerate at size before printing large — do not upscale.

The enso ring on the sheet could not be saved: the character sits on top of
the brush circle, so any crop that removes one cuts the other. Use
`kanji-sweep.png` and set a new ring around it.

Taglines, for consistency everywhere:

- BUILT DIFFERENT · SCOUR THE STREETS · CUSTOM EVERYTHING
- ストリートスウィーパーカスタムズ
