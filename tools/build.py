#!/usr/bin/env python3
"""
Portfolio generator.

tools/projects.json se:
  - har project ka folder:  projects/<category>/<slug>/index.html   (e.g. projects/laravel/businesspal/)
  - dummy thumbnail (sirf tab jab aap ne apni image nahi rakhi)
  - js/projects-data.js  (home page ki listing ke liye)
banata hai.

Chalane ka tareeqa (Python 3 chahiye):
    python tools/build.py

Naya project add karna ho to:
    python tools/new_project.py react "My App" --url https://myapp.com --summary "Short description"

Agar kisi project ka detail page aap ne hath se customize kar liya hai to us folder mein
ek khali file ".manual" bana dein, phir build.py us ka index.html overwrite nahi karega.

LOGO THUMBNAIL (sirf logo, koi text nahi):
  Project folder mein logo ko "logo.svg" (ya logo.png / logo.webp / logo.jpg) ke naam se rakh dein, phir
  python tools/build.py chalayein. Logo apne asli aspect ratio mein, bina stretch kiye, beech mein lagta hai.
  Background logo ke rang dekh kar khud chunta hai (light logo -> dark background, warna light), taake
  transparent logo background mein ghul na jaye. Zaroorat ho to projects.json mein:
      "logo_bg": "light" | "dark" | "#0b1220"     (default "auto")
      "logo_scale": 100                            (logo bara/chhota: 80, 120 ...)
"""
import html
import json
import os
import re
from urllib.parse import urlparse

try:
    from PIL import Image  # sirf PNG/JPG/WebP logos ke liye chahiye (pip install pillow); SVG ke bagair bhi chalta hai
except ImportError:
    Image = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_EXT = ('.svg', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.avif')

# ---- Site settings (header/footer/detail pages mein use hoti hain) ----
SITE_NAME = "Umair Riaz"
SITE_INITIALS = "UR"
WHATSAPP = "923222566149"          # country code ke saath, + ke baghair
DETAIL_HEADER_FOOTER = False       # True karein to project detail pages par header (menu) aur footer wapas aa jayenge

# Naya technology add karna ho to yahan add karein: key -> name, color, short label, optional icon
TECH = {
    "wordpress": {"name": "WordPress",    "color": "#21759b", "short": "Wp", "icon": "assets/images/icons/wordpress.png"},
    "shopify":   {"name": "Shopify",      "color": "#5e8e3e", "short": "Sh", "icon": "assets/images/icons/shopify-icon.svg"},
    "laravel":   {"name": "Laravel",      "color": "#ff2d20", "short": "La", "icon": "assets/images/icons/laravel.png"},
    "react":     {"name": "React",        "color": "#149eca", "short": "Re", "icon": "assets/images/icons/react.png"},
    "aspnet":    {"name": "ASP.NET Core", "color": "#512bd4", "short": ".N", "glyph": "dotnet"},
    "angular":   {"name": "Angular",      "color": "#dd0031", "short": "Ng"},
}


def esc(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def shade(hex_color, factor):
    h = hex_color.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return '#%02x%02x%02x' % (int(r * factor), int(g * factor), int(b * factor))


def host_of(url):
    if not url:
        return ''
    h = urlparse(url).netloc
    return h[4:] if h.startswith('www.') else h


# ---------------------------------------------------------------------------
# Logo thumbnails
# ---------------------------------------------------------------------------
LOGO_EXT = ('.svg', '.png', '.webp', '.jpg', '.jpeg', '.gif', '.avif')
LIGHT_BG, DARK_BG = '#f4f6fa', '#0f172a'
CARD_BOX = (64.0, 27.5)     # card (16:10): logo ki max width % aur max height (card width ka %)
COVER_BOX = (56.0, 24.0)    # detail page cover (21:9)
GENERATED_MARK = '<!-- generated:build.py -->'
OLD_PLACEHOLDERS = ('Placeholder - thumbnail.png', 'Dummy preview')
_NAMED = {'white': (255, 255, 255), 'black': (0, 0, 0)}
_ICONS = None


def _parse_color(s):
    s = s.strip().lower()
    if s in _NAMED:
        return _NAMED[s]
    m = re.fullmatch(r'#([0-9a-f]{3,8})', s)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = ''.join(c * 2 for c in h[:3])
        elif len(h) in (6, 8):
            h = h[:6]
        else:
            return None
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.match(r'rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)', s)
    if m:
        return tuple(min(255, int(float(x))) for x in m.groups())
    return None


def _lum(rgb):
    def f(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _decide_bg(lums):
    """Zyada-tar halka logo (aur koi gehra rang nahi) -> dark background, warna light."""
    if not lums:
        return LIGHT_BG
    light = sum(1 for l in lums if l > 0.75) / len(lums)
    dark = sum(1 for l in lums if l < 0.35) / len(lums)
    return DARK_BG if light >= 0.6 and dark < 0.05 else LIGHT_BG


def _svg_size(text):
    m = re.search(r'<svg\b[^>]*>', text, re.I | re.S)
    tag = m.group(0) if m else ''

    def num(attr):
        mm = re.search(r'(?<![-\w])%s\s*=\s*["\']\s*([0-9.]+)\s*(?:px|pt)?\s*["\']' % attr, tag)
        return float(mm.group(1)) if mm else None

    w, h = num('width'), num('height')
    if w and h:
        return w, h
    vb = re.search(r'viewBox\s*=\s*["\']\s*[-0-9.eE]+[\s,]+[-0-9.eE]+[\s,]+([0-9.eE]+)[\s,]+([0-9.eE]+)', tag)
    if vb and float(vb.group(1)) > 0 and float(vb.group(2)) > 0:
        return float(vb.group(1)), float(vb.group(2))
    return w or 300.0, h or 150.0


def _svg_auto_bg(text):
    lums = []
    for m in re.finditer(r'(?:fill|stop-color)\s*[:=]\s*["\']?\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|[a-zA-Z]+)', text):
        c = _parse_color(m.group(1))
        if c:
            lums.append(_lum(c))
    return _decide_bg(lums) if lums else LIGHT_BG  # koi fill nahi => SVG ka default kala


def _raster_info(path):
    if Image is None:
        raise SystemExit('PNG/JPG/WebP logo ke liye Pillow chahiye:  pip install pillow   (ya logo.svg istemal karein)')
    try:
        im = Image.open(path)
        w, h = im.size
        small = im.convert('RGBA')
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f'Logo parh nahi saka ({path}): {e}')
    small.thumbnail((160, 160))
    raw = small.tobytes()
    px = [tuple(raw[i:i + 4]) for i in range(0, len(raw), 4)]
    opaque = [p for p in px if p[3] > 40]
    if opaque and len(opaque) < len(px) * 0.95:           # transparent logo
        return w, h, _decide_bg([_lum(p[:3]) for p in opaque])
    sw, sh = small.size                                     # opaque image: kinaron ke rang se blend karo
    edge = [small.getpixel((x, 0)) for x in range(sw)] + [small.getpixel((x, sh - 1)) for x in range(sw)] \
        + [small.getpixel((0, y)) for y in range(sh)] + [small.getpixel((sw - 1, y)) for y in range(sh)]
    mean = tuple(sum(p[i] for p in edge) // len(edge) for i in range(3))
    if all(abs(p[i] - mean[i]) <= 14 for p in edge for i in range(3)):
        return w, h, '#%02x%02x%02x' % mean
    return w, h, LIGHT_BG


def logo_info(p, folder, cat, slug):
    """projects/<cat>/<slug>/logo.* mile to listing/cover ke liye size, background aur paths nikalta hai."""
    name = next((f'logo{e}' for e in LOGO_EXT if os.path.exists(os.path.join(folder, f'logo{e}'))), None)
    if not name:
        return None
    path = os.path.join(folder, name)
    if name.endswith('.svg'):
        with open(path, encoding='utf-8', errors='ignore') as f:
            text = f.read()
        w, h = _svg_size(text)
        auto, mw = _svg_auto_bg(text), None
    else:
        w, h, auto = _raster_info(path)
        mw = w                                              # raster logo ko uske asli size se bara nahi karte
    r = round(w / h, 4)
    scale = max(0.2, min(float(p.get('logo_scale', 100)) / 100, 2.0))
    ov = str(p.get('logo_bg', 'auto')).strip()
    if ov == 'auto':
        bg = auto
    elif ov == 'light':
        bg = LIGHT_BG
    elif ov == 'dark':
        bg = DARK_BG
    elif re.fullmatch(r'#[0-9a-fA-F]{3,8}|[a-zA-Z]+', ov):
        bg = ov
    else:
        raise SystemExit(f'{cat}/{slug}: logo_bg "{ov}" theek nahi (auto, light, dark ya #hex)')
    return {
        'file': name,
        'src': f'projects/{cat}/{slug}/{name}',
        'bg': bg,
        'r': r,
        'lw': round(min(min(CARD_BOX[0], CARD_BOX[1] * r) * scale, 82), 2),
        'cw': round(min(min(COVER_BOX[0], COVER_BOX[1] * r) * scale, 72), 2),
        'mw': mw,
    }


def logo_style(L):
    return f'--bg:{L["bg"]};--lw:{L["lw"]}%;--cw:{L["cw"]}%;--r:{L["r"]}' + (f';--mw:{L["mw"]}px' if L['mw'] else '')


def _glyph(key):
    global _ICONS
    if _ICONS is None:
        with open(os.path.join(ROOT, 'tools', 'tech-icons.json'), encoding='utf-8') as f:
            _ICONS = json.load(f)
    return _ICONS.get(key, {}).get('path')


def fallback_svg(cat):
    """Logo abhi na ho to sirf platform ka nishan (koi text nahi)."""
    t = TECH[cat]
    path = _glyph(t.get('glyph', cat))
    mark = f'<g transform="translate(340 190) scale(5)"><path d="{path}" fill="{t["color"]}" opacity=".85"/></g>' if path else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500" role="img" aria-label="{esc(t["name"])}">'
            f'{GENERATED_MARK}<rect width="800" height="500" fill="{LIGHT_BG}"/>{mark}</svg>\n')


def make_svg(color, tech_name, title, variant):
    c2 = shade(color, 0.45)
    if variant == 0:  # landing page
        body = (
            '<rect x="100" y="120" width="260" height="22" rx="6" fill="#1e293b"/>'
            '<rect x="100" y="152" width="200" height="22" rx="6" fill="#1e293b"/>'
            '<rect x="100" y="192" width="300" height="10" rx="5" fill="#cbd5e1"/>'
            '<rect x="100" y="210" width="270" height="10" rx="5" fill="#cbd5e1"/>'
            f'<rect x="100" y="244" width="120" height="38" rx="10" fill="{color}"/>'
            '<rect x="232" y="244" width="110" height="38" rx="10" fill="#e2e8f0"/>'
            f'<rect x="440" y="110" width="260" height="210" rx="16" fill="{color}" opacity=".18"/>'
            f'<circle cx="570" cy="215" r="58" fill="{color}" opacity=".55"/>'
            '<rect x="100" y="340" width="600" height="70" rx="12" fill="#f1f5f9"/>'
        )
    elif variant == 1:  # product / card grid
        cards = ''
        for r in range(2):
            for c in range(3):
                x, y = 100 + c * 205, 120 + r * 150
                cards += (
                    f'<rect x="{x}" y="{y}" width="190" height="135" rx="12" fill="#f1f5f9"/>'
                    f'<rect x="{x + 10}" y="{y + 10}" width="170" height="70" rx="8" fill="{color}" opacity="{0.25 + 0.12 * ((r + c) % 3)}"/>'
                    f'<rect x="{x + 10}" y="{y + 92}" width="110" height="9" rx="4" fill="#94a3b8"/>'
                    f'<rect x="{x + 10}" y="{y + 108}" width="60" height="9" rx="4" fill="{color}"/>'
                )
        body = cards
    else:  # dashboard
        bars = ''
        for i, h in enumerate((70, 120, 95, 160, 130, 185, 150)):
            bars += f'<rect x="{240 + i * 62}" y="{390 - h}" width="38" height="{h}" rx="6" fill="{color}" opacity="{0.35 + i * 0.09:.2f}"/>'
        body = (
            '<rect x="80" y="100" width="130" height="330" rx="10" fill="#f1f5f9"/>'
            + ''.join(f'<rect x="94" y="{118 + i * 34}" width="100" height="14" rx="5" fill="#cbd5e1"/>' for i in range(7))
            + ''.join(
                f'<rect x="{240 + i * 160}" y="112" width="145" height="70" rx="10" fill="#f1f5f9"/>'
                f'<rect x="{254 + i * 160}" y="128" width="60" height="9" rx="4" fill="#94a3b8"/>'
                f'<rect x="{254 + i * 160}" y="148" width="90" height="18" rx="5" fill="{color}"/>'
                for i in range(4)
            )
            + bars
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500" role="img" aria-label="{esc(title)}">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{color}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>
<rect width="800" height="500" fill="url(#g)"/>
<rect x="60" y="48" width="680" height="404" rx="16" fill="#ffffff"/>
<path d="M60 64a16 16 0 0 1 16-16h648a16 16 0 0 1 16 16v28H60z" fill="#eef1f6"/>
<circle cx="86" cy="70" r="6" fill="#ff5f57"/><circle cx="106" cy="70" r="6" fill="#febc2e"/><circle cx="126" cy="70" r="6" fill="#28c840"/>
<rect x="160" y="60" width="420" height="20" rx="10" fill="#ffffff"/>
{body}
<text x="740" y="476" text-anchor="end" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#ffffff" opacity=".9">{esc(tech_name)}</text>
<text x="60" y="476" font-family="Arial,Helvetica,sans-serif" font-size="15" fill="#ffffff" opacity=".85">Placeholder screenshot</text>
</svg>
'''


def header(prefix):
    return f'''<header class="nav">
  <div class="container nav-in">
    <a class="logo" href="{prefix}index.html"><span class="logo-mark">{esc(SITE_INITIALS)}</span> {esc(SITE_NAME)}</a>
    <nav class="menu" aria-label="Main">
      <a href="{prefix}index.html#home">Home</a>
      <a href="{prefix}index.html#projects">Projects</a>
      <a href="{prefix}index.html#skills">Tech Stack</a>
      <a href="{prefix}index.html#about">About</a>
      <a href="{prefix}index.html#contact">Contact</a>
    </nav>
    <div class="nav-actions">
      <button class="icon-btn" data-theme-toggle aria-label="Toggle theme" title="Toggle theme">
        <svg class="i-moon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
        <svg class="i-sun" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      </button>
      <button class="burger icon-btn" aria-label="Menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>'''


WA_ICON = '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.4 8.4 0 0 1-12.4 7.4L3 21l2.1-5.4A8.4 8.4 0 1 1 21 11.5z"/><path d="M9 9.5c.3 2 2.200 4 4.500 4.500l1.200-1.200-1.800-1-.8.600a3.500 3.500 0 0 1-1.600-1.600l.6-.8-1-1.800z"/></svg>'


def whatsapp_float():
    return f'<a class="wa-float" href="https://api.whatsapp.com/send?phone={WHATSAPP}&text=Hi%21%20{esc(SITE_NAME).replace(" ", "%20")}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{WA_ICON}</a>'


def footer(prefix):
    return f'''<footer class="footer">
  <div class="container foot-in">
    <span>&copy; <span id="year">2026</span> {esc(SITE_NAME)}. All rights reserved.</span>
    <a href="{prefix}index.html#projects">&larr; Back to projects</a>
  </div>
</footer>'''


def detail_page(p, siblings, pos, thumb, shots, logo=None):
    prefix = '../../../'
    t = TECH[p['category']]
    if logo:  # logo par lightbox nahi: gehre overlay mein transparent logo ghul sakta hai
        cover = (f'<div class="cover logo-thumb" style="{esc(logo_style(logo))}">'
                 f'<img class="logo" src="{esc(logo["file"])}" alt="{esc(p["title"])} logo"></div>')
    else:
        cover = f'<div class="cover"><img data-lightbox src="{esc(thumb)}" alt="{esc(p["title"])} cover"></div>'
    li = lambda xs: ''.join(f'<li>{esc(x)}</li>' for x in xs)
    tags = ''.join(f'<span>{esc(x)}</span>' for x in p.get('tags', []))

    actions = ''
    if p.get('live'):
        actions += f'<a class="btn btn-primary" href="{esc(p["live"])}" target="_blank" rel="noopener">Visit Website &nearr;</a>'
    if p.get('github'):
        actions += f'<a class="btn btn-ghost" href="{esc(p["github"])}" target="_blank" rel="noopener">Source Code &nearr;</a>'
    actions += f'<a class="btn btn-ghost" href="{prefix}index.html#projects">&larr; All Projects</a>'

    desc = p.get('description') or p['summary']
    sections = f'<section class="panel"><h2>Overview</h2><p>{esc(desc)}</p></section>'
    if p.get('features'):
        sections += f'<section class="panel"><h2>Key Features</h2><ul class="feat">{li(p["features"])}</ul></section>'
    for key, label in (('challenges', 'Challenges'), ('results', 'Results')):
        if p.get(key):
            sections += f'<section class="panel"><h2>{label}</h2><p>{esc(p[key])}</p></section>'

    rows = []
    if p.get('client'):
        rows.append(('Client', p['client']))
    if p.get('role'):
        rows.append(('Role', p['role']))
    if p.get('year'):
        rows.append(('Year', p['year']))
    if p.get('duration'):
        rows.append(('Duration', p['duration']))
    rows.append(('Platform', t['name']))
    if p.get('live'):
        rows.append(('Website', host_of(p['live'])))
    info = ''.join(f'<li><span>{esc(a)}</span><b>{esc(b)}</b></li>' for a, b in rows)

    gallery = ''
    if shots:
        imgs = ''.join(f'<img loading="lazy" data-lightbox src="screenshots/{esc(s)}" alt="{esc(p["title"])} screenshot {n}">' for n, s in enumerate(shots, 1))
        gallery = f'<section class="panel reveal"><h2>Screenshots</h2><div class="gallery">{imgs}</div></section>'

    # previous / next - isi category ke andar
    prev_p = siblings[pos - 1] if pos > 0 else None
    next_p = siblings[pos + 1] if pos < len(siblings) - 1 else None
    prev_html = (f'<a href="../{esc(prev_p["slug"])}/index.html"><small>&larr; Previous in {esc(t["name"])}</small><b>{esc(prev_p["title"])}</b></a>'
                 if prev_p else '<a class="ph"></a>')
    next_html = (f'<a class="next" href="../{esc(next_p["slug"])}/index.html"><small>Next in {esc(t["name"])} &rarr;</small><b>{esc(next_p["title"])}</b></a>'
                 if next_p else '<a class="ph"></a>')

    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(p["title"])} | {esc(SITE_NAME)}</title>
  <meta name="description" content="{esc(p["summary"])}">
  <meta property="og:title" content="{esc(p["title"])}">
  <meta property="og:description" content="{esc(p["summary"])}">
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefix}css/style.css">
  <script>try{{var t=localStorage.getItem('theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body style="--c:{t["color"]}">
{header(prefix) if DETAIL_HEADER_FOOTER else ''}
<main class="container">
  <div class="crumbs"><a href="{prefix}index.html">Home</a><span>/</span><a href="{prefix}index.html#projects">Projects</a><span>/</span>{esc(t["name"])}<span>/</span>{esc(p["title"])}</div>

  <section class="p-hero">
    <span class="badge" style="--c:{t["color"]}">{esc(t["name"])}</span>
    <h1>{esc(p["title"])}</h1>
    <p class="lead">{esc(p["summary"])}</p>
    <div class="p-actions">{actions}</div>
  </section>

  {cover}

  <div class="p-layout">
    <div>{sections}</div>
    <aside class="side">
      <div class="panel">
        <h2>Project Info</h2>
        <ul class="info">{info}</ul>
      </div>
      <div class="panel"><h2>Tech Stack</h2><div class="tags">{tags}</div></div>
    </aside>
  </div>

  {gallery}

  <nav class="pn" aria-label="Project navigation">{prev_html}{next_html}</nav>
</main>
{footer(prefix) if DETAIL_HEADER_FOOTER else ''}
{whatsapp_float()}
<script src="{prefix}js/main.js"></script>
</body>
</html>
'''


def find_images(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(f for f in os.listdir(folder) if f.lower().endswith(IMG_EXT))


def main():
    src = os.path.join(ROOT, 'tools', 'projects.json')
    with open(src, encoding='utf-8') as f:
        projects = json.load(f)

    seen = set()
    for p in projects:
        if p['category'] not in TECH:
            raise SystemExit(f'Unknown category "{p["category"]}" ({p["slug"]}). build.py ke TECH dict mein add karein.')
        key = (p['category'], p['slug'])
        if key in seen:
            raise SystemExit(f'Duplicate project: {p["category"]}/{p["slug"]}')
        seen.add(key)

    by_cat = {}
    for p in projects:
        by_cat.setdefault(p['category'], []).append(p)

    # listing order: TECH ki tarteeb ke mutabiq category-wise
    ordered = [p for k in TECH for p in by_cat.get(k, [])]

    data = []
    for p in ordered:
        cat, slug = p['category'], p['slug']
        t = TECH[cat]
        siblings = by_cat[cat]
        pos = siblings.index(p)
        folder = os.path.join(ROOT, 'projects', cat, slug)
        shots_dir = os.path.join(folder, 'screenshots')
        os.makedirs(shots_dir, exist_ok=True)
        variant = ordered.index(p) % 3

        # thumbnail: 1) logo.* (sirf logo), 2) apni thumbnail.* image, 3) platform ka nishan (placeholder)
        logo = logo_info(p, folder, cat, slug)
        gen_path = os.path.join(folder, 'thumbnail.svg')
        manual = []
        for f in os.listdir(folder):
            if f.lower().startswith('thumbnail.') and f.lower().endswith(IMG_EXT):
                if f.lower().endswith('.svg'):
                    with open(os.path.join(folder, f), encoding='utf-8', errors='ignore') as fh:
                        txt = fh.read()
                    if GENERATED_MARK in txt or any(m in txt for m in OLD_PLACEHOLDERS):
                        continue  # build.py ka banaya hua placeholder, aap ki image nahi
                manual.append(f)
        if logo:
            thumb = None
            if os.path.exists(gen_path) and not manual:
                os.remove(gen_path)
        elif manual:
            thumb = manual[0]
        else:
            with open(gen_path, 'w', encoding='utf-8') as f:
                f.write(fallback_svg(cat))
            thumb = 'thumbnail.svg'

        # screenshots: sirf aap ki rakhi hui images dikhti hain (placeholder gallery nahi banti)
        for f in find_images(shots_dir):  # build.py ki purani placeholder images saaf karo
            fp = os.path.join(shots_dir, f)
            if f.lower().endswith('.svg'):
                with open(fp, encoding='utf-8', errors='ignore') as fh:
                    txt = fh.read()
                if any(m in txt for m in OLD_PLACEHOLDERS + ('Placeholder screenshot',)):
                    os.remove(fp)
        shots = find_images(shots_dir)
        if not shots:
            keep = os.path.join(shots_dir, '.gitkeep')
            if not os.path.exists(keep):
                open(keep, 'w').close()

        page = os.path.join(folder, 'index.html')
        if os.path.exists(os.path.join(folder, '.manual')) and os.path.exists(page):
            print(f'  skip (manual): {cat}/{slug}')
        else:
            with open(page, 'w', encoding='utf-8') as f:
                f.write(detail_page(p, siblings, pos, thumb, shots, logo))

        data.append({
            'slug': slug,
            'title': p['title'],
            'category': cat,
            'tags': p.get('tags', []),
            'year': p.get('year', ''),
            'client': p.get('client', ''),
            'host': host_of(p.get('live', '')),
            'summary': p['summary'],
            'featured': bool(p.get('featured')),
            'url': f'projects/{cat}/{slug}/index.html',
            'thumb': f'projects/{cat}/{slug}/{thumb}' if thumb else None,
            'logo': {k: logo[k] for k in ('src', 'bg', 'r', 'lw', 'cw', 'mw')} if logo else None,
        })

    tech_out = {k: {kk: vv for kk, vv in v.items()} for k, v in TECH.items()}
    js_path = os.path.join(ROOT, 'js', 'projects-data.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write('/* AUTO-GENERATED by tools/build.py - is file ko hath se edit na karein, tools/projects.json edit karein */\n')
        f.write('window.TECH = ' + json.dumps(tech_out, indent=2, ensure_ascii=False) + ';\n')
        f.write('window.PROJECTS = ' + json.dumps(data, indent=2, ensure_ascii=False) + ';\n')

    counts = ', '.join(f'{TECH[k]["name"]}: {len(v)}' for k, v in by_cat.items())
    print(f'Done: {len(data)} projects generated ({counts}).')


if __name__ == '__main__':
    main()
