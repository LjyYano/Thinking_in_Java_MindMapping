(function () {
  'use strict';

  var root = document.documentElement;
  var body = document.body;
  var baseurl = root.dataset.baseurl || '';

  function all(selector, context) {
    return Array.prototype.slice.call((context || document).querySelectorAll(selector));
  }

  // Color theme
  var themeToggle = document.querySelector('[data-theme-toggle]');
  var themeColor = document.querySelector('meta[name="theme-color"]');

  function applyTheme(theme) {
    root.dataset.theme = theme;
    localStorage.setItem('yano-theme', theme);
    if (themeColor) themeColor.setAttribute('content', theme === 'dark' ? '#141619' : '#f6f4ef');
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      applyTheme(root.dataset.theme === 'dark' ? 'light' : 'dark');
    });
  }

  // Mobile navigation
  var navToggle = document.querySelector('[data-nav-toggle]');
  if (navToggle) {
    navToggle.addEventListener('click', function () {
      var willOpen = !body.classList.contains('nav-open');
      body.classList.toggle('nav-open', willOpen);
      navToggle.setAttribute('aria-expanded', String(willOpen));
      navToggle.setAttribute('aria-label', willOpen ? '关闭导航' : '打开导航');
    });
  }

  // Search dialog and client-side index
  var searchDialog = document.querySelector('[data-search-dialog]');
  var searchInput = document.querySelector('[data-search-input]');
  var searchResults = document.querySelector('[data-search-results]');
  var searchStatus = document.querySelector('[data-search-status]');
  var searchIndex = null;
  var searchPromise = null;
  var lastFocused = null;

  function loadSearchIndex() {
    if (searchIndex) return Promise.resolve(searchIndex);
    if (!searchPromise) {
      searchPromise = fetch(baseurl + '/search.json')
        .then(function (response) {
          if (!response.ok) throw new Error('Search index request failed');
          return response.json();
        })
        .then(function (data) {
          searchIndex = data;
          return data;
        })
        .catch(function () {
          searchStatus.textContent = '搜索索引加载失败，请刷新页面后重试';
          return [];
        });
    }
    return searchPromise;
  }

  function openSearch() {
    if (!searchDialog) return;
    lastFocused = document.activeElement;
    searchDialog.classList.add('is-open');
    searchDialog.setAttribute('aria-hidden', 'false');
    body.classList.add('search-open');
    loadSearchIndex().then(function () {
      renderSearch(searchInput.value);
    });
    window.setTimeout(function () { searchInput.focus(); }, 30);
  }

  function closeSearch() {
    if (!searchDialog) return;
    searchDialog.classList.remove('is-open');
    searchDialog.setAttribute('aria-hidden', 'true');
    body.classList.remove('search-open');
    if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
  }

  function makeResult(article) {
    var link = document.createElement('a');
    link.className = 'search-result';
    link.href = article.url;

    var copy = document.createElement('div');
    var meta = document.createElement('div');
    meta.className = 'search-result-meta';
    var category = document.createElement('span');
    category.textContent = article.category;
    var date = document.createElement('span');
    date.textContent = article.date;
    meta.appendChild(category);
    meta.appendChild(date);

    var title = document.createElement('h3');
    title.textContent = article.title;
    var excerpt = document.createElement('p');
    excerpt.textContent = article.excerpt;
    copy.appendChild(meta);
    copy.appendChild(title);
    copy.appendChild(excerpt);

    var arrow = document.createElement('span');
    arrow.setAttribute('aria-hidden', 'true');
    arrow.textContent = '↗';
    link.appendChild(copy);
    link.appendChild(arrow);
    return link;
  }

  function renderSearch(rawQuery) {
    if (!searchIndex || !searchResults) return;
    var query = rawQuery.trim().toLocaleLowerCase('zh-CN');
    var ranked = searchIndex.map(function (article, index) {
      var title = article.title.toLocaleLowerCase('zh-CN');
      var category = article.category.toLocaleLowerCase('zh-CN');
      var excerpt = article.excerpt.toLocaleLowerCase('zh-CN');
      var score = 0;
      if (!query) score = Math.max(1, 100 - index);
      if (title === query) score += 1000;
      if (title.indexOf(query) !== -1) score += 300;
      if (title.indexOf(query) === 0) score += 180;
      if (category.indexOf(query) !== -1) score += 90;
      if (excerpt.indexOf(query) !== -1) score += 30;
      return { article: article, score: score };
    }).filter(function (item) {
      return item.score > 0;
    }).sort(function (a, b) {
      return b.score - a.score;
    }).slice(0, query ? 14 : 8);

    searchResults.replaceChildren();
    if (!ranked.length) {
      var empty = document.createElement('p');
      empty.className = 'search-empty';
      empty.textContent = '没有找到与“' + rawQuery.trim() + '”相关的文章';
      searchResults.appendChild(empty);
      searchStatus.textContent = '0 条结果';
      return;
    }

    ranked.forEach(function (item) {
      searchResults.appendChild(makeResult(item.article));
    });
    searchStatus.textContent = query ? '找到 ' + ranked.length + ' 条相关结果' : '最近更新';
  }

  all('[data-search-open]').forEach(function (button) {
    button.addEventListener('click', openSearch);
  });
  all('[data-search-close]').forEach(function (button) {
    button.addEventListener('click', closeSearch);
  });
  if (searchInput) {
    searchInput.addEventListener('input', function () { renderSearch(searchInput.value); });
  }

  document.addEventListener('keydown', function (event) {
    var tag = document.activeElement && document.activeElement.tagName;
    var typing = tag === 'INPUT' || tag === 'TEXTAREA' || (document.activeElement && document.activeElement.isContentEditable);
    if ((event.key === '/' && !typing) || ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k')) {
      event.preventDefault();
      openSearch();
    }
    if (event.key === 'Escape') {
      if (body.classList.contains('search-open')) closeSearch();
      if (body.classList.contains('nav-open') && navToggle) navToggle.click();
    }
  });

  // Category and archive filters
  all('[data-list-filter]').forEach(function (input) {
    var section = input.closest('section') || document;
    var list = section.querySelector('[data-filter-list]');
    var items = all('[data-filter-item]', list);
    var count = section.querySelector('[data-list-count]');
    var empty = section.querySelector('[data-filter-empty]');

    function updateYearHeadings() {
      all('[data-year-heading]', list).forEach(function (heading) {
        var sibling = heading.nextElementSibling;
        var hasVisibleItem = false;
        while (sibling && !sibling.hasAttribute('data-year-heading')) {
          if (sibling.hasAttribute('data-filter-item') && !sibling.hidden) hasVisibleItem = true;
          sibling = sibling.nextElementSibling;
        }
        heading.hidden = !hasVisibleItem;
      });
    }

    input.addEventListener('input', function () {
      var query = input.value.trim().toLocaleLowerCase('zh-CN');
      var visible = 0;
      items.forEach(function (item) {
        var matches = !query || (item.dataset.searchText || '').indexOf(query) !== -1;
        item.hidden = !matches;
        if (matches) visible += 1;
      });
      if (count) count.textContent = query ? '找到 ' + visible + ' 篇' : '共 ' + items.length + ' 篇';
      if (empty) empty.hidden = visible !== 0;
      updateYearHeadings();
    });
  });

  // Article enhancements: lazy images, table of contents, copy buttons.
  var article = document.querySelector('[data-article-content]');
  if (article) {
    all('img', article).forEach(function (image) {
      image.loading = 'lazy';
      image.decoding = 'async';
    });

    all('a[href^="http"]', article).forEach(function (link) {
      if (link.hostname !== window.location.hostname) {
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
      }
    });

    var headings = all('h2, h3', article);
    var toc = document.querySelector('[data-toc]');
    var tocCard = document.querySelector('[data-toc-card]');
    if (toc && headings.length > 1) {
      headings.forEach(function (heading, index) {
        if (!heading.id) heading.id = 'section-' + (index + 1);
        var link = document.createElement('a');
        link.href = '#' + heading.id;
        link.dataset.level = heading.tagName.slice(1);
        link.textContent = heading.textContent;
        toc.appendChild(link);
      });

      if ('IntersectionObserver' in window) {
        var tocLinks = all('a', toc);
        var observer = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            tocLinks.forEach(function (link) { link.classList.remove('is-active'); });
            var active = toc.querySelector('a[href="#' + CSS.escape(entry.target.id) + '"]');
            if (active) active.classList.add('is-active');
          });
        }, { rootMargin: '-15% 0px -75% 0px' });
        headings.forEach(function (heading) { observer.observe(heading); });
      }
    } else if (tocCard) {
      tocCard.hidden = true;
    }

    all('.highlight, pre:not(.highlight pre)', article).forEach(function (block) {
      var pre = block.matches('pre') ? block : block.querySelector('pre');
      if (!pre || block.querySelector('.copy-code')) return;
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'copy-code';
      button.textContent = 'COPY';
      button.setAttribute('aria-label', '复制代码');
      button.addEventListener('click', function () {
        navigator.clipboard.writeText(pre.innerText).then(function () {
          button.textContent = 'COPIED';
          window.setTimeout(function () { button.textContent = 'COPY'; }, 1400);
        });
      });
      block.appendChild(button);
    });
  }
})();
