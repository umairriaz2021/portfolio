/* Portfolio main script - no dependencies */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };

  /* Theme toggle */
  var root = document.documentElement;
  $$('[data-theme-toggle]').forEach(function (b) {
    b.addEventListener('click', function () {
      var next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  });

  /* Mobile menu */
  var burger = $('.burger');
  if (burger) burger.addEventListener('click', function () { document.body.classList.toggle('menu-open'); });
  $$('.menu a').forEach(function (a) {
    a.addEventListener('click', function () { document.body.classList.remove('menu-open'); });
  });

  /* Year */
  var yr = $('#year'); if (yr) yr.textContent = new Date().getFullYear();

  /* Projects listing (home page only) */
  var grid = $('#projectGrid');
  if (grid && window.PROJECTS && window.TECH) {
    var P = window.PROJECTS, T = window.TECH;
    var active = 'all', query = '';
    var filters = $('#filters'), empty = $('#empty'), skillGrid = $('#skillGrid');
    var keys = Object.keys(T);

    var count = function (k) { return k === 'all' ? P.length : P.filter(function (p) { return p.category === k; }).length; };

    var drawChips = function () {
      filters.innerHTML = ['all'].concat(keys).map(function (k) {
        return '<button class="chip' + (k === active ? ' active' : '') + '" data-k="' + k + '">' +
          (k === 'all' ? 'All' : esc(T[k].name)) + '<span>' + count(k) + '</span></button>';
      }).join('');
    };

    var drawCards = function () {
      var q = query.trim().toLowerCase();
      var list = P.filter(function (p) {
        if (active !== 'all' && p.category !== active) return false;
        if (!q) return true;
        var hay = [p.title, p.summary, p.client, T[p.category].name].concat(p.tags || []).join(' ').toLowerCase();
        return hay.indexOf(q) !== -1;
      });
      grid.innerHTML = list.map(function (p, i) {
        var t = T[p.category];
        return '<a class="card" style="--c:' + t.color + ';animation-delay:' + (i * 60) + 'ms" href="' + esc(p.url) + '">' +
          '<div class="card-img"><img loading="lazy" src="' + esc(p.thumb) + '" alt="' + esc(p.title) + '">' +
          '<span class="badge">' + esc(t.name) + '</span>' + (p.featured ? '<span class="star">&#9733; Featured</span>' : '') + '</div>' +
          '<div class="card-body"><div class="card-meta"><span>' + esc(p.client || '') + '</span><span>' + esc(p.year || '') + '</span></div>' +
          '<h3>' + esc(p.title) + '</h3><p>' + esc(p.summary) + '</p>' +
          '<div class="tags">' + (p.tags || []).slice(0, 4).map(function (x) { return '<span>' + esc(x) + '</span>'; }).join('') + '</div>' +
          '<span class="more">View details</span></div></a>';
      }).join('');
      empty.hidden = list.length > 0;
    };

    var setActive = function (k) { active = k; drawChips(); drawCards(); };

    filters.addEventListener('click', function (e) {
      var b = e.target.closest('.chip'); if (b) setActive(b.dataset.k);
    });
    $('#search').addEventListener('input', function (e) { query = e.target.value; drawCards(); });

    if (skillGrid) {
      skillGrid.innerHTML = keys.map(function (k) {
        var t = T[k], n = count(k);
        return '<button class="skill" style="--c:' + t.color + '" data-k="' + k + '">' +
          '<span class="skill-ico">' + esc(t.short || t.name.slice(0, 2)) + '</span><b>' + esc(t.name) + '</b>' +
          '<small>' + n + ' project' + (n === 1 ? '' : 's') + '</small></button>';
      }).join('');
      skillGrid.addEventListener('click', function (e) {
        var b = e.target.closest('.skill'); if (!b) return;
        setActive(b.dataset.k);
        $('#projects').scrollIntoView({ behavior: 'smooth' });
      });
    }

    var sp = $('#statProjects'), st = $('#statTech');
    if (sp) { sp.dataset.count = P.length; sp.textContent = P.length; }
    if (st) { st.dataset.count = keys.length; st.textContent = keys.length; }

    drawChips(); drawCards();
  }

  /* Lightbox (detail page) */
  var imgs = $$('[data-lightbox]');
  if (imgs.length) {
    var lb = document.createElement('div');
    lb.className = 'lb'; lb.innerHTML = '<img alt="">';
    document.body.appendChild(lb);
    var lbImg = $('img', lb);
    imgs.forEach(function (im) {
      im.addEventListener('click', function () { lbImg.src = im.currentSrc || im.src; lbImg.alt = im.alt; lb.classList.add('open'); });
    });
    lb.addEventListener('click', function () { lb.classList.remove('open'); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') lb.classList.remove('open'); });
  }

  /* Scroll reveal + counters */
  var animateCount = function (el) {
    var end = parseInt(el.dataset.count, 10); if (isNaN(end)) return;
    var suf = el.dataset.suffix || '', start = null;
    var step = function (ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / 900, 1);
      el.textContent = Math.round(end * p) + (p === 1 ? suf : '');
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  var reveals = $$('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('in');
        $$('[data-count]', en.target).forEach(animateCount);
        io.unobserve(en.target);
      });
    }, { threshold: 0.12 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }
})();
