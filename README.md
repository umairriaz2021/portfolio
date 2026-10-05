# Umair Riaz - Portfolio (Static HTML / CSS / JS)

GitHub Pages par seedha chalne wali static site. Koi framework ya build step zaroori nahi.
Projects technology-wise filter hote hain: **WordPress, Shopify, Laravel, React, ASP.NET Core, Angular**.

## Folder structure (category-wise)

```
portfolio/
├── index.html                      # Home (hero, projects, tech stack, about, contact)
├── 404.html
├── .nojekyll
├── css/style.css
├── js/
│   ├── main.js                     # filters, search, theme, lightbox, show-more
│   └── projects-data.js            # AUTO-GENERATED (hath se edit na karein)
├── assets/
│   ├── favicon.svg
│   └── images/
│       ├── umair.jpeg
│       └── icons/                  # wordpress / shopify / laravel / react icons
├── projects/
│   ├── wordpress/<slug>/           # 28 projects
│   ├── shopify/<slug>/             # 4 projects
│   ├── laravel/<slug>/             # 2 projects
│   ├── react/<slug>/               # 1 project
│   ├── aspnet/<slug>/              # dummy (replace karein)
│   └── angular/<slug>/             # dummy (replace karein)
│       └── <slug>/
│           ├── index.html          # us project ka detail page
│           ├── thumbnail.svg       # placeholder -> thumbnail.png/jpg/webp rakh dein
│           └── screenshots/        # gallery images yahan rakhein
└── tools/
    ├── projects.json               # <-- sara project data yahan
    ├── build.py                    # folders/pages/listing generate karta hai
    └── new_project.py              # naya project add karne ka shortcut
```

URL ka format: `/projects/<category>/<slug>/` - jaise `projects/laravel/businesspal/`,
`projects/aspnet/hr-portal/`. Slug sirf apni category ke andar unique hona chahiye.

## Naya project add karna

**Sab se aasan - command se:**

```
python tools/new_project.py aspnet "Inventory System" --url https://example.com --summary "Short description"
python tools/new_project.py angular "Admin Panel" --tags "Angular,NgRx,Material"
```

Ye `projects.json` mein entry daal kar `projects/aspnet/inventory-system/` bana deta hai.

**Ya hath se:**

1. `tools/projects.json` mein naya object add karein (kisi purane ko copy kar lein).
   - `category`: `wordpress | shopify | laravel | react | aspnet | angular`
   - `slug`: folder ka naam (lowercase, `-` ke saath)
   - Zaroori: `slug`, `title`, `category`, `summary`. Baqi optional hain
     (`live`, `github`, `tags`, `year`, `client`, `role`, `duration`, `description`, `features`, `challenges`, `results`).
     Jo field khali ho, detail page par wo section nazar nahi aata.
2. `python tools/build.py` chalayein.

**Images:** `projects/<category>/<slug>/thumbnail.png` (1600x1000 behtar) aur
`screenshots/` mein jitni chahein. Phir `python tools/build.py` dobara chalayein.

## Logo thumbnail (sirf logo, koi text nahi)

Listing card aur detail page ke cover ke liye bas logo file project folder mein `logo.*` ke naam se rakhein:

```
projects/wordpress/routica/logo.svg      (ya logo.png / logo.webp / logo.jpg)
```

phir `python tools/build.py` chalayein. Is se:

- Logo apne **asli aspect ratio** mein beech mein lagta hai, kabhi stretch nahi hota.
  SVG box ke andar fit hoti hai; PNG/JPG apne asli pixel size se bari nahi hoti (blur nahi hoti).
- **Background logo ke rang se khud chunta hai**: halka/safed logo -> gehra background, baqi logo -> halka background,
  taake transparent logo background mein ghul na jaye. Opaque JPG ho to uske kinaron ke rang se blend hota hai.
- Logo par zoom (lightbox) nahi lagta, warna gehre overlay mein transparent logo ghul sakta hai.
- Logo na ho to sirf platform ka nishan (WordPress/Shopify/...) dikhta hai, koi text nahi.

Zaroorat ho to `tools/projects.json` mein us project par:

```json
"logo_bg": "light",        // "auto" (default) | "light" | "dark" | "#0b1220"
"logo_scale": 120          // logo bara (120) ya chhota (80), default 100
```

Raster logos (PNG/JPG/WebP) ke liye Pillow chahiye: `pip install pillow` (SVG ke liye zaroori nahi).
`tools/sample-logos/` mein 5 test logos hain (gehra, safed, rangeen PNG, opaque JPG, safed PNG): kisi project folder mein
`logo.svg`/`logo.png` ke naam se copy kar ke dekh lein, phir hata dein.

## Dummy projects

`aspnet/hr-portal`, `aspnet/inventory-api`, `angular/erp-frontend`, `angular/booking-app` dummy hain
(`projects.json` mein `"dummy": true`). Real project aane par inhe edit/delete kar dein.
Dummy projects ki placeholder gallery bhi banti hai; real projects ki gallery tab dikhti hai jab `screenshots/` mein images hon.

## Hath se edit kiye hue page ko bachana

Kisi project ka detail page hath se customize kar liya ho to us folder mein khali file `.manual` bana dein;
phir `build.py` us ka `index.html` overwrite nahi karega.

## Settings

- Naam, initials, WhatsApp number: `tools/build.py` ke top par (`SITE_NAME`, `SITE_INITIALS`, `WHATSAPP`).
- Home page ka text/links: `index.html`.
- Naya technology: `build.py` ke `TECH` dict mein ek line add karein, filter chips aur Tech Stack cards khud ban jayenge.
- Rang: `css/style.css` ke top ke `--primary` variables.

## GitHub Pages

Repo mein saari files push karein. Settings → Pages mein branch aur `/ (root)` select karein
(ya aap ka purana `.github/workflows/static.yml` workflow chalne dein). Saare links relative hain,
is liye `username.github.io/repo-name/` par bhi theek chalte hain.

Local mein: `index.html` double-click karein ya `python -m http.server 8000`.
