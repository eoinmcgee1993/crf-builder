# StreetSweeperCustoms brand marks

Real vector files. The type is Oswald Bold converted to outlines, so nothing
here needs a font installed to render correctly — hand any of these to a vinyl
printer or an embroiderer as-is.

| File | Use |
|---|---|
| `logo-primary.svg` | The mark. Dark backgrounds. Stacked lockup. |
| `logo-primary-light.svg` | Same lockup for light backgrounds and print on white. |
| `logo-horizontal.svg` | One line, for a site header or a jersey collar. |
| `monogram.svg` | Square. Social avatar, sticker, app tile. |
| `favicon.svg` | 32px. Shipped as `public/favicon.svg`. |
| `badge.svg` | Circular emblem for stickers and garment labels. |

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

## Graffiti lockup

`graffiti/` holds the Chicano-lettering treatment of **STREET SWEEPER GARAGE**.
This is a *second* name — the bike-and-socials identity — not the storefront's.
`StreetSweeperCustoms` is what a buyer sees at checkout; the graffiti is what
gets handed out at a petrol station. Keep them apart, or one of them stops
meaning anything.

| File | Use |
|---|---|
| `wordmark-on-black.png` | Keyed to `#121316`. Drop it on any near-black field. |
| `wordmark-wall-a.png` | Full frame, dark wall. Social header, poster. |
| `wordmark-wall-b.png` | Full frame, lit wall. The cleaner hierarchy of the two. |
| `mascot-calavera.png` | Goggled calavera. An original mark, free to own. |

Raster, 1280x720. Big enough for a 50 mm sticker and a social post; not big
enough for a jersey back or an A2 poster. Regenerate larger before print at
that size — do not upscale these.

## Stickers

`build-sticker.py` builds the hand-out card: 85 x 54 mm, 3 mm bleed, die line
on a `CutContour` spot colour, QR as vector paths at error-correction H.

```sh
./fetch-font.sh                 # once
python3 build-sticker.py        # -> stickers/sticker-garage.svg
python3 build-sticker.py "https://example.com" "LINE ONE|LINE TWO" out.svg
```

The script decodes its own QR out of a 300 dpi render before writing the file,
so a sticker that does not scan never reaches a printer. Measured: reliable
down to about 4 px per module, which is a card filling a tenth of a phone
frame. Level H survives roughly 30% damage, which is the point on a tank.

When the real domain exists, rebuild with it — the QR is generated, never
hand-placed, so it is one argument.
