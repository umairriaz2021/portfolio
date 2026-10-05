#!/usr/bin/env python3
"""
Naya project jaldi add karne ka tool.

Examples:
    python tools/new_project.py wordpress "My Client Site" --url https://client.com --summary "What the site does."
    python tools/new_project.py laravel "School ERP" --url https://erp.example.com --tags "Laravel,MySQL,Livewire"
    python tools/new_project.py aspnet "Inventory API" --summary "Short text"

Ye tools/projects.json mein entry add karta hai aur build.py chala kar
projects/<category>/<slug>/ folder bana deta hai.

Categories: wordpress, shopify, laravel, react, aspnet, angular
(naye technology ke liye build.py ke TECH dict mein add karein)
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402


def slugify(text):
    s = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return s or 'project'


def main():
    ap = argparse.ArgumentParser(description='Add a new project to the portfolio')
    ap.add_argument('category', choices=list(build.TECH.keys()))
    ap.add_argument('title')
    ap.add_argument('--slug', help='folder name (default: title se auto)')
    ap.add_argument('--url', default='', help='live website URL')
    ap.add_argument('--github', default='', help='source code URL')
    ap.add_argument('--summary', default='', help='short description (1-2 lines)')
    ap.add_argument('--tags', default='', help='comma separated, e.g. "Laravel,MySQL"')
    ap.add_argument('--year', default='')
    args = ap.parse_args()

    path = os.path.join(build.ROOT, 'tools', 'projects.json')
    with open(path, encoding='utf-8') as f:
        projects = json.load(f)

    slug = args.slug or slugify(args.title)
    if any(p['category'] == args.category and p['slug'] == slug for p in projects):
        raise SystemExit(f'{args.category}/{slug} pehle se maujood hai. --slug se doosra naam dein.')

    entry = {
        'slug': slug,
        'title': args.title,
        'category': args.category,
        'tags': [t.strip() for t in args.tags.split(',') if t.strip()] or [build.TECH[args.category]['name']],
        'summary': args.summary or f'{args.title} - short description yahan likhein.',
        'live': args.url,
    }
    if args.github:
        entry['github'] = args.github
    if args.year:
        entry['year'] = int(args.year)

    # same category ke aakhri project ke baad insert karein (listing tarteeb saaf rahe)
    last = max((i for i, p in enumerate(projects) if p['category'] == args.category), default=len(projects) - 1)
    projects.insert(last + 1, entry)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)
        f.write('\n')

    build.main()
    print(f'\nAdded: projects/{args.category}/{slug}/')
    print('Apni image: projects/%s/%s/thumbnail.png (ya .jpg/.webp), screenshots: .../screenshots/' % (args.category, slug))
    print('Image rakhne ke baad dobara chalayein: python tools/build.py')


if __name__ == '__main__':
    main()
