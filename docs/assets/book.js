/* Qt6 Widgets 入門 — ページの挙動
   外部ライブラリは使っていない。読み込むのはこの 1 ファイルだけ。 */
(function () {
  'use strict';

  var root = document.documentElement;

  /* --- 配色の切り替え --------------------------------------------------- */
  function currentTheme() {
    if (root.dataset.theme) return root.dataset.theme;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  var themeButton = document.querySelector('.theme-toggle');
  if (themeButton) {
    themeButton.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('qt6book-theme', next); } catch (e) { /* 保存できなくても動く */ }
      themeButton.setAttribute('aria-label',
        next === 'dark' ? '明るい配色に切り替える' : '暗い配色に切り替える');
    });
  }

  /* --- 目次の開閉（画面が狭いとき） ------------------------------------- */
  var navToggle = document.querySelector('.nav-toggle');
  var scrim = document.querySelector('.sidebar-scrim');

  function setNav(open) {
    document.body.classList.toggle('nav-open', open);
    if (navToggle) navToggle.setAttribute('aria-expanded', String(open));
    if (scrim) scrim.hidden = !open;
  }

  if (navToggle) navToggle.addEventListener('click', function () {
    setNav(!document.body.classList.contains('nav-open'));
  });
  if (scrim) scrim.addEventListener('click', function () { setNav(false); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setNav(false);
  });

  /* --- コードのコピー --------------------------------------------------- */
  document.querySelectorAll('.code-block [data-copy]').forEach(function (button) {
    button.addEventListener('click', function () {
      var code = button.closest('.code-block').querySelector('code');
      // innerText だと空行が落ちてしまう（中身のないブロックが無視されるため）。
      // 行ごとの要素から組み立てて、元のファイルと 1 文字も違わないようにする。
      var lines = code ? code.querySelectorAll('.cl') : [];
      var text = lines.length
        ? Array.prototype.map.call(lines, function (el) { return el.textContent; }).join('\n')
        : (code ? code.textContent : '');
      var done = function () {
        var original = button.textContent;
        button.textContent = 'コピーしました';
        button.classList.add('is-done');
        setTimeout(function () {
          button.textContent = original;
          button.classList.remove('is-done');
        }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { button.textContent = 'コピー失敗'; });
      } else {
        var ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); done(); } catch (e) { button.textContent = 'コピー失敗'; }
        document.body.removeChild(ta);
      }
    });
  });

  /* --- 現在の章の小見出しをサイドバーに差し込む ------------------------- */
  var currentItem = document.querySelector('.nav-list li.is-current');
  var headings = Array.prototype.slice.call(document.querySelectorAll('.prose h2[id]'));

  if (currentItem && headings.length > 1) {
    var sub = document.createElement('ul');
    sub.className = 'subnav';
    headings.forEach(function (h) {
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent;
      a.dataset.target = h.id;
      li.appendChild(a);
      sub.appendChild(li);
    });
    currentItem.appendChild(sub);

    var links = {};
    sub.querySelectorAll('a').forEach(function (a) { links[a.dataset.target] = a; });
    var activeId = null;

    var markActive = function (id) {
      if (id === activeId) return;
      if (activeId && links[activeId]) links[activeId].classList.remove('is-active');
      activeId = id;
      if (id && links[id]) links[id].classList.add('is-active');
    };

    // 画面の上寄りに来た見出しを「現在地」とみなす。
    var observer = new IntersectionObserver(function () {
      var best = null;
      headings.forEach(function (h) {
        var top = h.getBoundingClientRect().top;
        if (top <= 140 && (!best || top > best.getBoundingClientRect().top)) best = h;
      });
      markActive(best ? best.id : headings[0].id);
    }, { rootMargin: '-120px 0px -70% 0px', threshold: [0, 1] });

    headings.forEach(function (h) { observer.observe(h); });
  }

  /* --- 読書進捗バー ----------------------------------------------------- */
  var bar = document.getElementById('reading-bar');
  var article = document.querySelector('.chapter');
  if (bar && article) {
    var update = function () {
      var start = article.offsetTop;
      var span = article.offsetHeight - window.innerHeight;
      var ratio = span > 0 ? (window.scrollY - start) / span : 1;
      bar.style.width = Math.min(100, Math.max(0, ratio * 100)) + '%';
    };
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () { update(); ticking = false; });
    }, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();
  }

  /* --- 表は横スクロールできるように包む -------------------------------- */
  document.querySelectorAll('.prose > table').forEach(function (table) {
    var wrap = document.createElement('div');
    wrap.className = 'table-wrap';
    table.parentNode.insertBefore(wrap, table);
    wrap.appendChild(table);
  });

  /* --- 現在の章をサイドバー内で見えるようにする ------------------------- */
  if (currentItem) {
    var sidebar = document.getElementById('sidebar');
    if (sidebar && sidebar.scrollHeight > sidebar.clientHeight) {
      var offset = currentItem.offsetTop - sidebar.clientHeight / 3;
      sidebar.scrollTop = Math.max(0, offset);
    }
  }
})();
