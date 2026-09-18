/* CRF kit mockup — wraps a customer's artwork onto the panels of a photographed
   stock CRF and re-lights it from the photo's own shading.

   Panel geometry is a Coons patch: four cubic Béziers round the panel edge.
   A flat quad cannot follow a fender, and hand-drawn polygon masks cannot be
   nudged once the photo changes; four curves can do both. Open the page with
   #calibrate to drag the control points and copy the corrected JSON out. */

const VIEWS = [
  {
    id: 'front3q', label: 'Front 3/4', src: 'bike/front3q.jpg', w: 1500, h: 2039,
    panels: {
      front_fender: {
        top:    [[400,722],[500,703],[605,692],[708,686]],
        right:  [[708,686],[705,730],[701,775],[695,820]],
        bottom: [[262,880],[400,872],[550,858],[695,820]],
        left:   [[400,722],[355,775],[305,828],[262,878]],
      },
      right_shroud: {
        top:    [[978,744],[990,748],[1001,752],[1012,756]],
        right:  [[1012,756],[1010,866],[1007,978],[1004,1090]],
        bottom: [[974,1078],[984,1082],[994,1086],[1004,1090]],
        left:   [[978,744],[976,856],[975,967],[974,1078]],
      },
      tail: {
        top:    [[1010,856],[1072,848],[1136,854],[1196,882]],
        right:  [[1196,882],[1192,946],[1186,1011],[1180,1076]],
        bottom: [[1008,1105],[1065,1098],[1122,1088],[1180,1076]],
        left:   [[1008,848],[1008,934],[1008,1020],[1008,1105]],
      },
    },
  },
  {
    id: 'front', label: 'Front', src: 'bike/front.jpg', w: 1500, h: 2038,
    panels: {
      // Only the fender from this angle. The shroud is a 25px sliver seen
      // edge-on here, and a graphic laid on it reads as a rectangle floating
      // beside the bike rather than as a decal on a panel.
      front_fender: {
        top:    [[345,612],[450,578],[560,566],[690,592]],
        right:  [[690,592],[691,635],[691,678],[690,722]],
        bottom: [[350,732],[450,758],[560,762],[690,722]],
        left:   [[345,612],[346,652],[348,692],[350,732]],
      },
    },
  },
];

const PANEL_LABELS = {
  front_fender: 'Front Fender',
  right_shroud: 'Right Shroud',
  tail:         'Rear Panel / Tail',
};
const PRESETS = ['race', 'rally', 'retro', 'splatter'];

// panelId -> { img, scale, rot, u, v }
const decals = Object.create(null);
let viewIndex = 0;
let selected = 'front_fender';
const baseImages = Object.create(null);

const stage = document.getElementById('stage');
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d', { willReadFrequently: true });
const busy = document.getElementById('busy');

const view = () => VIEWS[viewIndex];
const panelsHere = () => Object.keys(view().panels);
const clamp = (x, a, b) => x < a ? a : x > b ? b : x;

/* ---------------- geometry ---------------- */
function bez(p, t) {
  const u = 1 - t, a = u*u*u, b = 3*u*u*t, c = 3*u*t*t, d = t*t*t;
  return [a*p[0][0] + b*p[1][0] + c*p[2][0] + d*p[3][0],
          a*p[0][1] + b*p[1][1] + c*p[2][1] + d*p[3][1]];
}
function coons(P, u, v) {
  const T = bez(P.top, u), B = bez(P.bottom, u), L = bez(P.left, v), R = bez(P.right, v);
  const c00 = P.top[0], c10 = P.top[3], c01 = P.bottom[0], c11 = P.bottom[3];
  const mix = (t, b, l, r, a, bb, cc, dd) =>
    (1-v)*t + v*b + (1-u)*l + u*r
    - ((1-u)*(1-v)*a + u*(1-v)*bb + (1-u)*v*cc + u*v*dd);
  return [mix(T[0],B[0],L[0],R[0], c00[0],c10[0],c01[0],c11[0]),
          mix(T[1],B[1],L[1],R[1], c00[1],c10[1],c01[1],c11[1])];
}

/* Canvas 2D has no perspective transform, so the patch is subdivided and each
   cell drawn as two affine triangles. Triangles are grown slightly about their
   centroid; at exact size the seams between cells show as hairlines. */
function drawTri(c, img, s, d) {
  const g = 1.03, cx = (d[0][0]+d[1][0]+d[2][0])/3, cy = (d[0][1]+d[1][1]+d[2][1])/3;
  const e = d.map(p => [cx + (p[0]-cx)*g, cy + (p[1]-cy)*g]);
  c.save();
  c.beginPath(); c.moveTo(e[0][0],e[0][1]); c.lineTo(e[1][0],e[1][1]); c.lineTo(e[2][0],e[2][1]);
  c.closePath(); c.clip();
  const [[sx0,sy0],[sx1,sy1],[sx2,sy2]] = s, [[dx0,dy0],[dx1,dy1],[dx2,dy2]] = d;
  const den = sx0*(sy2-sy1) - sx1*sy2 + sx2*sy1 + (sx1-sx2)*sy0;
  if (Math.abs(den) > 1e-9) {
    c.transform(
      -(sy0*(dx2-dx1) - sy1*dx2 + sy2*dx1 + (sy1-sy2)*dx0) / den,
       (sy1*dy2 + sy0*(dy1-dy2) - sy2*dy1 + (sy2-sy1)*dy0) / den,
       (sx0*(dx2-dx1) - sx1*dx2 + sx2*dx1 + (sx1-sx2)*dx0) / den,
      -(sx1*dy2 + sx0*(dy1-dy2) - sx2*dy1 + (sx2-sx1)*dy0) / den,
       (sx0*(sy2*dx1 - sy1*dx2) + sy0*(sx1*dx2 - sx2*dx1) + (sx2*sy1 - sx1*sy2)*dx0) / den,
       (sx0*(sy2*dy1 - sy1*dy2) + sy0*(sx1*dy2 - sx2*dy1) + (sx2*sy1 - sx1*sy2)*dy0) / den);
    c.drawImage(img, 0, 0);
  }
  c.restore();
}

function patchBBox(P) {
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  for (const e of ['top','bottom','left','right'])
    for (let t = 0; t <= 1.0001; t += 0.05) {
      const p = bez(P[e], t);
      x0 = Math.min(x0,p[0]); y0 = Math.min(y0,p[1]);
      x1 = Math.max(x1,p[0]); y1 = Math.max(y1,p[1]);
    }
  return [Math.floor(x0)-2, Math.floor(y0)-2, Math.ceil(x1)+2, Math.ceil(y1)+2];
}

/* ---------------- the composite ---------------- */
/* Painting the artwork straight on gives a sticker: flat colour, no form. The
   panel's own luminance carries its curvature, its highlight and the shadow
   under the fender lip, so the artwork is multiplied by that and the brightest
   part of the highlight is added back on top. The photo's red disappears
   because only luminance is used, never the photo's hue. */
function compositePanel(P, art) {
  const [x0, y0, x1, y1] = patchBBox(P);
  const w = x1 - x0, h = y1 - y0;
  if (w <= 0 || h <= 0) return;

  const off = document.createElement('canvas');
  off.width = w; off.height = h;
  const oc = off.getContext('2d', { willReadFrequently: true });
  oc.translate(-x0, -y0);

  const N = 22, iw = art.naturalWidth || art.width, ih = art.naturalHeight || art.height;
  for (let j = 0; j < N; j++) {
    for (let i = 0; i < N; i++) {
      const u0 = i/N, u1 = (i+1)/N, v0 = j/N, v1 = (j+1)/N;
      const d00 = coons(P,u0,v0), d10 = coons(P,u1,v0), d01 = coons(P,u0,v1), d11 = coons(P,u1,v1);
      const s00 = [u0*iw, v0*ih], s10 = [u1*iw, v0*ih], s01 = [u0*iw, v1*ih], s11 = [u1*iw, v1*ih];
      drawTri(oc, art, [s00,s10,s01], [d00,d10,d01]);
      drawTri(oc, art, [s10,s11,s01], [d10,d11,d01]);
    }
  }

  // getImageData/putImageData work in device pixels and ignore the transform
  // set above, so the offscreen is addressed from its own origin here.
  const A = oc.getImageData(0, 0, w, h);
  const B = ctx.getImageData(x0, y0, w, h);
  const a = A.data, b = B.data;

  // Pivot on the panel's own median brightness, so a dark panel is not crushed
  // and a bright one is not blown out.
  const lum = [];
  for (let k = 0; k < a.length; k += 4) {
    if (a[k+3] < 8) continue;
    lum.push(0.2126*b[k] + 0.7152*b[k+1] + 0.0722*b[k+2]);
  }
  if (!lum.length) return;
  lum.sort((p,q) => p-q);
  const pivot = Math.max(28, lum[lum.length >> 1]);

  const CONTRAST = 0.78;   // the stock bike carries printed stripes; softening
                           // the shading stops them reading through as ghosts
  for (let k = 0; k < a.length; k += 4) {
    if (a[k+3] < 8) continue;
    const L = (0.2126*b[k] + 0.7152*b[k+1] + 0.0722*b[k+2]) / pivot;
    const s = clamp(1 + (L - 1) * CONTRAST, 0.30, 1.85);
    const spec = s > 1.24 ? (s - 1.24) * 190 : 0;
    a[k]   = clamp(a[k]   * s + spec, 0, 255);
    a[k+1] = clamp(a[k+1] * s + spec, 0, 255);
    a[k+2] = clamp(a[k+2] * s + spec, 0, 255);
  }
  oc.putImageData(A, 0, 0);
  ctx.drawImage(off, x0, y0);
}

function render() {
  const v = view(), base = baseImages[v.id];
  if (!base) return;
  cv.width = v.w; cv.height = v.h;
  ctx.drawImage(base, 0, 0, v.w, v.h);
  for (const id of panelsHere()) {
    const d = decals[id];
    if (d && d.img) compositePanel(v.panels[id], transformed(d));
  }
  if (calibrating) drawCalibration();
}

/* Scale / rotate / shift happen in the artwork's own space before the warp, so
   the panel keeps its shape and only the design moves inside it. */
function transformed(d) {
  if (d.scale === 100 && d.rot === 0 && d.u === 0 && d.v === 0) return d.img;
  const S = 1024, c = document.createElement('canvas');
  c.width = c.height = S;
  const g = c.getContext('2d');
  g.translate(S/2 + d.u/100*S, S/2 + d.v/100*S);
  g.rotate(d.rot * Math.PI/180);
  const k = d.scale/100;
  g.scale(k, k);
  g.drawImage(d.img, -S/2, -S/2, S, S);
  return c;
}

/* ---------------- UI ---------------- */
function buildViewBar() {
  const bar = document.getElementById('viewbar');
  bar.innerHTML = '';
  VIEWS.forEach((v, i) => {
    const b = document.createElement('button');
    b.textContent = v.label;
    b.className = i === viewIndex ? 'on' : '';
    b.addEventListener('click', () => setView(i));
    bar.appendChild(b);
  });
}
function setView(i) {
  viewIndex = (i + VIEWS.length) % VIEWS.length;
  if (!panelsHere().includes(selected)) selected = panelsHere()[0];
  buildViewBar(); buildPanels(); render();
}

function buildPanels() {
  const grid = document.getElementById('panel-grid');
  const here = panelsHere();
  grid.innerHTML = '';
  for (const id of Object.keys(PANEL_LABELS)) {
    const on = here.includes(id);
    const t = document.createElement('div');
    t.className = 'panel-tile' + (on ? '' : ' off') + (id === selected ? ' active' : '')
                + (decals[id] ? ' has-decal' : '');
    t.tabIndex = on ? 0 : -1;
    t.setAttribute('role', 'option');
    t.setAttribute('aria-selected', id === selected ? 'true' : 'false');
    const dot = document.createElement('span'); dot.className = 'dot';
    const nm = document.createElement('span'); nm.className = 'name';
    nm.textContent = PANEL_LABELS[id] + (on ? '' : ' — other side');
    t.append(dot, nm);
    if (on) {
      const x = document.createElement('button');
      x.className = 'clear'; x.type = 'button'; x.textContent = '×';
      x.setAttribute('aria-label', 'Clear ' + PANEL_LABELS[id]);
      x.addEventListener('click', e => { e.stopPropagation(); delete decals[id]; buildPanels(); render(); });
      t.appendChild(x);
      const pick = () => { selected = id; syncSliders(); buildPanels(); };
      t.addEventListener('click', pick);
      t.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(); }
      });
    }
    grid.appendChild(t);
  }
}

function buildPresets() {
  const row = document.getElementById('preset-row');
  row.innerHTML = '';
  for (const k of PRESETS) {
    const b = document.createElement('button');
    b.className = 'preset'; b.type = 'button'; b.dataset.preset = k;
    const th = document.createElement('div');
    th.className = 'preset-thumb';
    th.style.backgroundImage = `url("kits/${k}-thumb.jpg")`;
    const s = document.createElement('span'); s.textContent = k;
    b.append(th, s);
    b.addEventListener('click', async () => {
      try {
        const img = await loadImage(`kits/${k}.jpg`);
        document.querySelectorAll('.preset').forEach(p => p.classList.toggle('sel', p === b));
        for (const id of Object.keys(PANEL_LABELS)) decals[id] = { img, scale:100, rot:0, u:0, v:0 };
        syncSliders(); buildPanels(); render();
      } catch { busyFor('Could not load that design'); }
    });
    row.appendChild(b);
  }
}

const SLIDERS = [['s-scale','v-scale','scale',v=>v+'%'], ['s-rot','v-rot','rot',v=>v+'°'],
                 ['s-u','v-u','u',v=>v], ['s-v','v-v','v',v=>v]];
function syncSliders() {
  const d = decals[selected];
  for (const [sid, vid, key, fmt] of SLIDERS) {
    const el = document.getElementById(sid);
    el.value = d ? d[key] : (key === 'scale' ? 100 : 0);
    el.disabled = !d;
    document.getElementById(vid).textContent = fmt(el.value);
  }
}
for (const [sid, vid, key, fmt] of SLIDERS) {
  document.getElementById(sid).addEventListener('input', e => {
    document.getElementById(vid).textContent = fmt(e.target.value);
    const d = decals[selected];
    if (!d) return;
    d[key] = +e.target.value;
    render();
  });
}

function loadImage(src) {
  return new Promise((res, rej) => {
    const i = new Image();
    i.onload = () => res(i);
    i.onerror = () => rej(new Error('load failed: ' + src));
    i.src = src;
  });
}
function readFile(file) {
  return new Promise((res, rej) => {
    const r = new FileReader();
    r.onerror = () => rej(new Error('Could not read that file'));
    r.onload = ev => { const i = new Image(); i.onload = () => res(i);
      i.onerror = () => rej(new Error('That file is not an image we can read')); i.src = ev.target.result; };
    r.readAsDataURL(file);
  });
}
document.getElementById('single').addEventListener('change', async e => {
  const f = e.target.files[0]; e.target.value = '';
  if (!f) return;
  try { decals[selected] = { img: await readFile(f), scale:100, rot:0, u:0, v:0 };
        syncSliders(); buildPanels(); render(); }
  catch (err) { busyFor(err.message); }
});
document.getElementById('kitwide').addEventListener('change', async e => {
  const f = e.target.files[0]; e.target.value = '';
  if (!f) return;
  try {
    const img = await readFile(f);
    for (const id of Object.keys(PANEL_LABELS)) decals[id] = { img, scale:100, rot:0, u:0, v:0 };
    document.querySelectorAll('.preset').forEach(p => p.classList.remove('sel'));
    syncSliders(); buildPanels(); render();
  } catch (err) { busyFor(err.message); }
});
document.getElementById('clear-all').addEventListener('click', () => {
  for (const k of Object.keys(decals)) delete decals[k];
  document.querySelectorAll('.preset').forEach(p => p.classList.remove('sel'));
  syncSliders(); buildPanels(); render();
});

let busyTimer = null;
function busyFor(msg) {
  busy.textContent = msg; busy.style.display = 'flex';
  clearTimeout(busyTimer);
  busyTimer = setTimeout(() => { busy.style.display = 'none'; }, 1800);
}

// Drag across the stage to change angle, the way a turntable behaves.
let dragX = null;
stage.addEventListener('pointerdown', e => { dragX = e.clientX; stage.setPointerCapture(e.pointerId); });
stage.addEventListener('pointerup',   () => { dragX = null; });
stage.addEventListener('pointermove', e => {
  if (dragX === null || calibrating) return;
  const dx = e.clientX - dragX;
  if (Math.abs(dx) > 70) { setView(viewIndex + (dx < 0 ? 1 : -1)); dragX = e.clientX; }
});

/* ---------------- calibrate (#calibrate) ---------------- */
let calibrating = location.hash === '#calibrate';
let dragPt = null;
function allPoints() {
  const out = [];
  const ps = view().panels;
  for (const id of Object.keys(ps))
    for (const edge of ['top','bottom','left','right'])
      ps[id][edge].forEach((p, i) => out.push({ id, edge, i, p }));
  return out;
}
function drawCalibration() {
  ctx.save();
  ctx.lineWidth = 4; ctx.strokeStyle = '#3ddc84';
  for (const id of panelsHere()) {
    const P = view().panels[id];
    ctx.beginPath();
    for (let t = 0; t <= 1.0001; t += 0.02) { const q = bez(P.top,t); t ? ctx.lineTo(...q) : ctx.moveTo(...q); }
    for (let t = 0; t <= 1.0001; t += 0.02) ctx.lineTo(...bez(P.right,t));
    for (let t = 1; t >= -0.0001; t -= 0.02) ctx.lineTo(...bez(P.bottom,t));
    for (let t = 1; t >= -0.0001; t -= 0.02) ctx.lineTo(...bez(P.left,t));
    ctx.closePath(); ctx.stroke();
  }
  for (const q of allPoints()) {
    ctx.fillStyle = (q.i === 0 || q.i === 3) ? '#e2231a' : '#ff8a1e';
    ctx.beginPath(); ctx.arc(q.p[0], q.p[1], 11, 0, 7); ctx.fill();
  }
  ctx.restore();
}
function toImageXY(e) {
  const r = cv.getBoundingClientRect();
  return [(e.clientX - r.left) / r.width * cv.width, (e.clientY - r.top) / r.height * cv.height];
}
if (calibrating) {
  stage.addEventListener('pointerdown', e => {
    const [x, y] = toImageXY(e);
    let best = null, bd = 1e9;
    for (const q of allPoints()) {
      const d = Math.hypot(q.p[0]-x, q.p[1]-y);
      if (d < bd) { bd = d; best = q; }
    }
    if (bd < 40) dragPt = best;
  });
  stage.addEventListener('pointermove', e => {
    if (!dragPt) return;
    const [x, y] = toImageXY(e);
    dragPt.p[0] = Math.round(x); dragPt.p[1] = Math.round(y);
    render();
  });
  stage.addEventListener('pointerup', () => {
    if (dragPt) console.log(JSON.stringify(view().panels, null, 2));
    dragPt = null;
  });
}

/* ---------------- boot ---------------- */
(async function boot() {
  buildViewBar(); buildPanels(); buildPresets(); syncSliders();
  document.getElementById('credits').innerHTML =
    'Bike photography from Unsplash, used under the Unsplash licence (free for commercial use). '
    + 'Manufacturer badging removed — the base is a mockup surface, not a Honda advertisement.';
  try {
    await Promise.all(VIEWS.map(async v => { baseImages[v.id] = await loadImage(v.src); }));
    busy.style.display = 'none';
    render();
    window.__ready = true;
  } catch (err) {
    busy.textContent = 'Could not load the bike photos.';
    console.error(err);
  }
})();
