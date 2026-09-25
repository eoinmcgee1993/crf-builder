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
