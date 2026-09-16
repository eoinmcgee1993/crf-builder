#!/usr/bin/env python3
"""Set the trading name across every storefront page.

The name moved four times before it settled, so it lives in one place and is
applied by running this rather than by hand-editing eight files.

Each footer already carries its own page detail — which models an ECU file
suits, that racewear is priced in baht. The brand is swapped in front of that
detail and nothing else is touched. An earlier version tried to recognise and
drop the old tagline too, and ate the ECU page's model list.

"CRF250L" stays in the product copy throughout. Naming the model you make kits
for is descriptive use; only the trading name moved.
"""
import pathlib, re, sys

BRAND = sys.argv[1] if len(sys.argv) > 1 else "Gengar81"
OLD_BRANDS = ["CRF Garage", "StreetSweeperCustoms &middot; by Gengar81",
              "StreetSweeperCustoms", "Gengar81 &middot; street sweeper customs", "Gengar81"]

TITLES = {
    'public/index.html':   'CRF250L Kit Builder',
    'public/apparel.html': 'Custom Racewear Builder',
    'public/ecu.html':     'CRF ECU Template Builder',
    'public/mods.html':    'Modifications Guide',
    'public/approve.html': 'Approve your kit',
    'public/desk.html':    'Order desk',
    'public/3d.html':      '3D decal preview',
    'public/mockup.html':  'Kit Mockup',
}
FOOTER_RE = re.compile(r'(<footer[^>]*>)(.*?)(</footer>)', re.S)

changed = []
for f, page_title in TITLES.items():
    p = pathlib.Path(f)
    if not p.exists():
        continue
    s = before = p.read_text(encoding='utf-8')
    s = re.sub(r'<title>[^<]*</title>', f'<title>{BRAND} — {page_title}</title>', s, count=1)

    def fix(m):
        inner = m.group(2).strip()
        for ob in OLD_BRANDS:                       # swap an existing brand out
            if inner.startswith(ob):
                inner = inner[len(ob):].lstrip()
                inner = inner[len('&middot;'):].lstrip() if inner.startswith('&middot;') else inner
                break
        return m.group(1) + (f'{BRAND} &middot; {inner}' if inner else BRAND) + m.group(3)

    s = FOOTER_RE.sub(fix, s, count=1)
    if s != before:
        p.write_text(s, encoding='utf-8'); changed.append(f)

ap = pathlib.Path('public/apparel.html')            # this footer is rebuilt in JS
if ap.exists():
    s = ap.read_text(encoding='utf-8')
    s2 = re.sub(r'"[^"]*?(\\u00b7 custom racewear \\u00b7 priced in Thai baht)',
                f'"{BRAND} \\\\u00b7 custom racewear \\\\u00b7 priced in Thai baht', s, count=1)
    if s2 != s:
        ap.write_text(s2, encoding='utf-8')
        if 'public/apparel.html' not in changed: changed.append('public/apparel.html')

print(f'brand = {BRAND!r}')
for c in changed: print('  updated', c)
