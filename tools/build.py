#!/usr/bin/env python3
"""
Portfolio generator.

tools/projects.json se:
  - har project ka folder:  projects/<slug>/index.html (detail page)
  - dummy images (sirf tab jab aap ne apni images nahi rakhi hon)
  - js/projects-data.js (home page ki listing ke liye)
banata hai.

Chalane ka tareeqa (Python 3 chahiye):
    python tools/build.py

Agar kisi project ka detail page aap ne hath se customize kar liya hai to us folder mein
ek khali file ".manual" bana dein, phir build.py us ka index.html overwrite nahi karega.
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_EXT = ('.svg', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.avif')

# Naya technology add karna ho to yahan add karein (key, name, color, short label)
TECH = {
    "wordpress": {"name": "WordPress",    "color": "#21759b", "short": "Wp"},
    "shopify":   {"name": "Shopify",      "color": "#5e8e3e", "short": "Sh"},
    "laravel":   {"name": "Laravel",      "color": "#ff2d20", "short": "La"},
    "react":     {"name": "React",        "color": "#149eca", "short": "Re"},
    "aspnet":    {"name": "ASP.NET Core", "color": "#512bd4", "short": ".N"},
    "angular":   {"name": "Angular",      "color": "#dd0031", "short": "Ng"},
}


def esc(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def shade(hex_color, factor):
    h = hex_color.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return '#%02x%02x%02x' % (int(r * factor), int(g * factor), int(b * factor))


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
<text x="60" y="476" font-family="Arial,Helvetica,sans-serif" font-size="15" fill="#ffffff" opacity=".85">Dummy preview - apni image se replace karein</text>
</svg>
'''


def header(prefix):
    return f'''<header class="nav">
  <div class="container nav-in">
    <a class="logo" href="{prefix}index.html"><span class="logo-mark">&lt;/&gt;</span> YourName<span class="dot">.dev</span></a>
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
      <a class="btn btn-primary btn-sm hide-sm" href="{prefix}index.html#contact">Hire Me</a>
      <button class="burger icon-btn" aria-label="Menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>'''


def detail_page(p, idx, projects, thumb, shots):
    prefix = '../../'
    t = TECH[p['category']]
    li = lambda xs: ''.join(f'<li>{esc(x)}</li>' for x in xs)
    tags = ''.join(f'<span>{esc(x)}</span>' for x in p.get('tags', []))

    actions = ''
    if p.get('live'):
        actions += f'<a class="btn btn-primary" href="{esc(p["live"])}" target="_blank" rel="noopener">Live Demo &nearr;</a>'
    if p.get('github'):
        actions += f'<a class="btn btn-ghost" href="{esc(p["github"])}" target="_blank" rel="noopener">Source Code &nearr;</a>'
    actions += f'<a class="btn btn-ghost" href="{prefix}index.html#projects">&larr; All Projects</a>'

    blocks = ''
    for key, label in (('challenges', 'Challenges'), ('results', 'Results')):
        if p.get(key):
            blocks += f'<div class="panel"><h2>{label}</h2><p>{esc(p[key])}</p></div>'

    gallery = ''
    if shots:
        imgs = ''.join(f'<img loading="lazy" data-lightbox src="screenshots/{esc(s)}" alt="{esc(p["title"])} screenshot {n}">' for n, s in enumerate(shots, 1))
        gallery = f'<section class="panel reveal"><h2>Screenshots</h2><div class="gallery">{imgs}</div></section>'

    prev_p = projects[idx - 1] if idx > 0 else None
    next_p = projects[idx + 1] if idx < len(projects) - 1 else None
    prev_html = (f'<a href="../{esc(prev_p["slug"])}/index.html"><small>&larr; Previous</small><b>{esc(prev_p["title"])}</b></a>'
                 if prev_p else '<a class="ph"></a>')
    next_html = (f'<a class="next" href="../{esc(next_p["slug"])}/index.html"><small>Next &rarr;</small><b>{esc(next_p["title"])}</b></a>'
                 if next_p else '<a class="ph"></a>')

    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(p["title"])} | Your Name</title>
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
{header(prefix)}
<main class="container">
  <div class="crumbs"><a href="{prefix}index.html">Home</a><span>/</span><a href="{prefix}index.html#projects">Projects</a><span>/</span>{esc(p["title"])}</div>

  <section class="p-hero">
    <span class="badge" style="--c:{t["color"]}">{esc(t["name"])}</span>
    <h1>{esc(p["title"])}</h1>
    <p class="lead">{esc(p["summary"])}</p>
    <div class="p-actions">{actions}</div>
  </section>

  <div class="cover"><img data-lightbox src="{esc(thumb)}" alt="{esc(p["title"])} cover"></div>

  <div class="p-layout">
    <div>
      <section class="panel"><h2>Overview</h2><p>{esc(p.get("description", ""))}</p></section>
      <section class="panel"><h2>Key Features</h2><ul class="feat">{li(p.get("features", []))}</ul></section>
      {blocks}
    </div>
    <aside class="side">
      <div class="panel">
        <h2>Project Info</h2>
        <ul class="info">
          <li><span>Client</span><b>{esc(p.get("client", "-"))}</b></li>
          <li><span>Role</span><b>{esc(p.get("role", "-"))}</b></li>
          <li><span>Year</span><b>{esc(p.get("year", "-"))}</b></li>
          <li><span>Duration</span><b>{esc(p.get("duration", "-"))}</b></li>
          <li><span>Platform</span><b>{esc(t["name"])}</b></li>
        </ul>
      </div>
      <div class="panel"><h2>Tech Stack</h2><div class="tags">{tags}</div></div>
    </aside>
  </div>

  {gallery}

  <nav class="pn" aria-label="Project navigation">{prev_html}{next_html}</nav>
</main>

<footer class="footer">
  <div class="container foot-in">
    <span>&copy; <span id="year">2026</span> Your Name. All rights reserved.</span>
    <a href="{prefix}index.html#projects">&larr; Back to projects</a>
  </div>
</footer>
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

    slugs = set()
    data = []
    for i, p in enumerate(projects):
        slug = p['slug']
        if slug in slugs:
            raise SystemExit(f'Duplicate slug: {slug}')
        slugs.add(slug)
        if p['category'] not in TECH:
            raise SystemExit(f'Unknown category "{p["category"]}" in {slug}. TECH dict mein add karein.')

        t = TECH[p['category']]
        folder = os.path.join(ROOT, 'projects', slug)
        shots_dir = os.path.join(folder, 'screenshots')
        os.makedirs(shots_dir, exist_ok=True)

        # thumbnail: apni image (thumbnail.png/jpg/webp...) rakhein to wahi use hogi
        thumbs = [f for f in os.listdir(folder) if f.lower().startswith('thumbnail.') and f.lower().endswith(IMG_EXT)]
        if not thumbs:
            with open(os.path.join(folder, 'thumbnail.svg'), 'w', encoding='utf-8') as f:
                f.write(make_svg(t['color'], t['name'], p['title'], i % 3))
            thumbs = ['thumbnail.svg']
        thumb = thumbs[0]

        # screenshots
        shots = find_images(shots_dir)
        if not shots:
            for n in range(3):
                name = f'shot-{n + 1}.svg'
                with open(os.path.join(shots_dir, name), 'w', encoding='utf-8') as f:
                    f.write(make_svg(t['color'], t['name'], f'{p["title"]} screenshot {n + 1}', (i + n + 1) % 3))
            shots = find_images(shots_dir)

        # detail page
        page = os.path.join(folder, 'index.html')
        if os.path.exists(os.path.join(folder, '.manual')) and os.path.exists(page):
            print(f'  skip (manual): {slug}')
        else:
            with open(page, 'w', encoding='utf-8') as f:
                f.write(detail_page(p, i, projects, thumb, shots))

        data.append({
            'slug': slug,
            'title': p['title'],
            'category': p['category'],
            'tags': p.get('tags', []),
            'year': p.get('year', ''),
            'client': p.get('client', ''),
            'summary': p['summary'],
            'featured': bool(p.get('featured')),
            'url': f'projects/{slug}/index.html',
            'thumb': f'projects/{slug}/{thumb}',
        })

    tech_out = {k: {'name': v['name'], 'color': v['color'], 'short': v['short']} for k, v in TECH.items()}
    js_path = os.path.join(ROOT, 'js', 'projects-data.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write('/* AUTO-GENERATED by tools/build.py - is file ko hath se edit na karein, tools/projects.json edit karein */\n')
        f.write('window.TECH = ' + json.dumps(tech_out, indent=2, ensure_ascii=False) + ';\n')
        f.write('window.PROJECTS = ' + json.dumps(data, indent=2, ensure_ascii=False) + ';\n')

    print(f'Done: {len(data)} projects generated.')


if __name__ == '__main__':
    main()
